"""Out-of-booking procedures, the advisory answering map, and expected_procedures."""

import enum
import typing

import karrio.core.models as models

import karrio.plugins.advisor_nordic_conventions.lanes as lanes
import karrio.plugins.advisor_nordic_conventions.rules.customs_values as customs_values
import karrio.plugins.advisor_nordic_conventions.rules.dhl_freight_sweden as dhl_freight_sweden
import karrio.plugins.advisor_nordic_conventions.rules.invoice_type as invoice_type
import karrio.plugins.advisor_nordic_conventions.rules.postnord as postnord
from karrio.plugins.advisor_nordic_conventions.codes import AdvisoryClassification
from karrio.plugins.advisor_nordic_conventions.rules import PLUGIN_ID

OPTION_PREFIX = f"{PLUGIN_ID}_"


class Procedure(str, enum.Enum):
    """One out-of-booking procedure, named by its shipment option key suffix."""

    commercial_invoice_paper_copy = "commercial_invoice_paper_copy"
    customs_declaration_paper_copy = "customs_declaration_paper_copy"
    customs_documents_attached_outside = "customs_documents_attached_outside"
    commercial_invoice_electronic = "commercial_invoice_electronic"
    voec_marking_printed = "voec_marking_printed"


def option_key(procedure: Procedure) -> str:
    """The shipment option key a consumer sets to true to attest the procedure."""
    return f"{OPTION_PREFIX}{procedure.value}"


Rule = typing.Callable[[typing.Any, typing.Any], typing.List[models.Message]]

RULES: typing.Tuple[Rule, ...] = (
    postnord.se_no_digital_invoice,
    postnord.se_postpaket_commercial_invoice,
    postnord.se_export_paper_invoice,
    postnord.fi_export_invoice,
    postnord.dk_export_documents,
    dhl_freight_sweden.customs_mode_missing,
    dhl_freight_sweden.aland_customs_service_rejected,
    dhl_freight_sweden.invoice_copy,
    dhl_freight_sweden.attached_documents,
    dhl_freight_sweden.voec_marking,
    invoice_type.invoice_type_content_mismatch,
    dhl_freight_sweden.parcel_connect_not_served,
    dhl_freight_sweden.parcel_connect_gb_agreement,
    dhl_freight_sweden.territory_postal_code_mismatch,
    dhl_freight_sweden.joint_declaration_destination,
    customs_values.ch_discount_on_invoice,
    customs_values.zero_value_line,
)

AnsweringSet = typing.Callable[[lanes.Lane], typing.FrozenSet[Procedure]]


def _always(*procedures: Procedure) -> AnsweringSet:
    fixed = frozenset(procedures)

    def answering(lane: lanes.Lane) -> typing.FrozenSet[Procedure]:
        return fixed

    return answering


def _se_postpaket(lane: lanes.Lane) -> typing.FrozenSet[Procedure]:
    if lane.to_norway:
        return frozenset(
            {
                Procedure.customs_declaration_paper_copy,
                Procedure.commercial_invoice_electronic,
            }
        )

    return frozenset(
        {
            Procedure.customs_declaration_paper_copy,
            Procedure.commercial_invoice_paper_copy,
        }
    )


def _fi_export(lane: lanes.Lane) -> typing.FrozenSet[Procedure]:
    if lane.to_norway:
        return frozenset({Procedure.commercial_invoice_electronic})

    return frozenset({Procedure.commercial_invoice_paper_copy})


DK_PAPER_ONLY_DESTINATIONS: typing.FrozenSet[str] = frozenset({"NO", "CH", "LI", "GB"})


def _dk_export(lane: lanes.Lane) -> typing.FrozenSet[Procedure]:
    if lane.recipient_country in DK_PAPER_ONLY_DESTINATIONS:
        return frozenset({Procedure.commercial_invoice_paper_copy})

    return frozenset(
        {
            Procedure.customs_declaration_paper_copy,
            Procedure.commercial_invoice_paper_copy,
        }
    )


ANSWERING: typing.Dict[AdvisoryClassification, AnsweringSet] = {
    AdvisoryClassification.postnord_se_no_digital_invoice: _always(
        Procedure.commercial_invoice_electronic
    ),
    AdvisoryClassification.postnord_se_postpaket_commercial_invoice: _se_postpaket,
    AdvisoryClassification.postnord_se_export_paper_invoice: _always(
        Procedure.commercial_invoice_paper_copy
    ),
    AdvisoryClassification.postnord_fi_export_invoice: _fi_export,
    AdvisoryClassification.postnord_dk_export_documents: _dk_export,
    AdvisoryClassification.dhl_freight_sweden_customs_mode_missing: _always(),
    AdvisoryClassification.dhl_freight_sweden_aland_customs_service_rejected: _always(),
    AdvisoryClassification.dhl_freight_sweden_invoice_copy: _always(
        Procedure.commercial_invoice_electronic
    ),
    AdvisoryClassification.dhl_freight_sweden_attached_documents: _always(
        Procedure.customs_documents_attached_outside
    ),
    AdvisoryClassification.dhl_freight_sweden_voec_marking: _always(
        Procedure.voec_marking_printed
    ),
    AdvisoryClassification.invoice_type_content_mismatch: _always(),
    AdvisoryClassification.attestation_conflict: _always(),
    AdvisoryClassification.ch_discount_on_invoice: _always(),
    AdvisoryClassification.zero_value_line: _always(),
    AdvisoryClassification.dhl_freight_sweden_parcel_connect_not_served: _always(),
    AdvisoryClassification.dhl_freight_sweden_parcel_connect_gb_agreement: _always(),
    AdvisoryClassification.dhl_freight_sweden_territory_postal_code_mismatch: _always(),
    AdvisoryClassification.dhl_freight_sweden_joint_declaration_destination: _always(),
    AdvisoryClassification.dhl_freight_sweden_cyprus_documents: _always(),
    AdvisoryClassification.dhl_freight_sweden_greek_tax_ids: _always(),
    AdvisoryClassification.dhl_freight_sweden_sent_information: _always(),
    AdvisoryClassification.dhl_freight_sweden_uit_information: _always(),
    AdvisoryClassification.dhl_freight_sweden_ekaer_information: _always(),
    AdvisoryClassification.dhl_freight_sweden_spain_dg_documents: _always(),
}


def answering_procedures(
    classification: AdvisoryClassification, lane: lanes.Lane
) -> typing.FrozenSet[Procedure]:
    """The procedures whose performance answers one advisory classification on a lane."""
    return ANSWERING[classification](lane)


def expected_procedures(
    request: typing.Any, context: typing.Any
) -> typing.FrozenSet[Procedure]:
    """The procedures the conventions expect for a request, before any booking.

    Empty outside the plugin's scope; otherwise the union of the answering sets
    of the advisories the unwrapped rules emit with no attestations, so the
    utility and the advisories cannot disagree.
    """
    lane = lanes.lane_of(request, context)

    if lane is None:
        return frozenset()

    return frozenset(
        procedure
        for rule in RULES
        for message in rule(request, context)
        for procedure in answering_procedures(AdvisoryClassification(message.code), lane)
    )
