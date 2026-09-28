"""Per-shipment procedure attestations and their conflicts with lane conventions."""

import typing

import attr
import karrio.core.models as models

import karrio.plugins.nordic_conventions.lanes as lanes
import karrio.plugins.nordic_conventions.sources as sources
from karrio.plugins.nordic_conventions.codes import AdvisoryClassification
from karrio.plugins.nordic_conventions.procedures import (
    Procedure,
    answering_procedures,
    option_key,
)
from karrio.plugins.nordic_conventions.rules import advisory


def parse(request: typing.Any) -> typing.FrozenSet[Procedure]:
    """The procedures attested for one shipment; only boolean true counts as a claim.

    A total function over any option value shape, because the advisor contract
    turns exceptions into shipment_advisor_failed warnings.
    """
    options = getattr(request, "options", None) or {}
    return frozenset(
        procedure
        for procedure in Procedure
        if options.get(option_key(procedure)) is True
    )


@attr.s(auto_attribs=True, frozen=True)
class Contradiction:
    """One convention that rejects an attested procedure on the lanes it governs."""

    applies: typing.Callable[[lanes.Lane], bool]
    convention: str
    sources: typing.Tuple[sources.Source, ...]


def _postnord_sweden_to_norway(lane: lanes.Lane) -> bool:
    return (
        lane.carrier_name == lanes.POSTNORD
        and lane.shipper_country == "SE"
        and lane.to_norway
    )


SE_NO_DIGITAL_ONLY_INVOICE = Contradiction(
    applies=_postnord_sweden_to_norway,
    convention=(
        "PostNord requires the commercial invoice from Sweden to Norway digitally, "
        "not on paper with the parcel"
    ),
    sources=(
        sources.PN_SE_SERVICE_POINT_TERMS_NORWAY,
        sources.PN_SE_NORWAY_CHANNELS,
        sources.PNS_PARCEL_CUSTOMS_INVOICE,
    ),
)

CONTRADICTIONS: typing.Dict[Procedure, typing.Tuple[Contradiction, ...]] = {
    Procedure.commercial_invoice_paper_copy: (SE_NO_DIGITAL_ONLY_INVOICE,)
}


def contradicted_on(
    lane: typing.Optional[lanes.Lane], attested: typing.FrozenSet[Procedure]
) -> typing.FrozenSet[Procedure]:
    """The attested procedures the conventions governing the lane reject."""
    if lane is None:
        return frozenset()

    return frozenset(
        procedure
        for procedure in attested
        if any(
            contradiction.applies(lane)
            for contradiction in CONTRADICTIONS.get(procedure, ())
        )
    )


def effective_attestations(
    lane: typing.Optional[lanes.Lane], attested: typing.FrozenSet[Procedure]
) -> typing.FrozenSet[Procedure]:
    """The attestations that hold on the lane: attested minus contradicted."""
    return attested - contradicted_on(lane, attested)


def _answered(
    message: models.Message, lane: lanes.Lane, effective: typing.FrozenSet[Procedure]
) -> bool:
    answering = answering_procedures(AdvisoryClassification(message.code), lane)
    return bool(answering) and answering <= effective


def with_attestations(
    rule: typing.Callable
) -> typing.Callable[[typing.Any, typing.Any], typing.List[models.Message]]:
    """Wrap one rule so an advisory fully answered by effective attestations is omitted.

    Partial coverage and coverage by a contradicted attestation omit nothing, and
    a request with no attestation passes the rule's messages through unchanged.
    """

    def advise(request: typing.Any, context: typing.Any) -> typing.List[models.Message]:
        messages = rule(request, context)
        attested = parse(request)

        if not attested:
            return messages

        lane = lanes.lane_of(request, context)

        if lane is None:
            return messages

        effective = effective_attestations(lane, attested)
        return [message for message in messages if not _answered(message, lane, effective)]

    return advise


def attestation_conflicts(
    request: typing.Any, context: typing.Any
) -> typing.List[models.Message]:
    """One warning per attestation the conventions governing the lane contradict."""
    lane = lanes.lane_of(request, context)

    if lane is None:
        return []

    contradicted = contradicted_on(lane, parse(request))

    return [
        advisory(
            "nordic_conventions_attestation_conflict",
            "warning",
            f"The attested procedure {option_key(procedure)} does not hold on this lane: "
            f"{contradiction.convention}.",
            lane,
            contradiction.sources,
            procedure=option_key(procedure),
        )
        for procedure in Procedure
        if procedure in contradicted
        for contradiction in CONTRADICTIONS[procedure]
        if contradiction.applies(lane)
    ]
