"""DHL Freight Sweden trade-document advisories for Swedish shippers."""

import typing

import karrio.core.models as models

import karrio.plugins.advisor_nordic_conventions.lanes as lanes
import karrio.plugins.advisor_nordic_conventions.sources as sources
from karrio.plugins.advisor_nordic_conventions.codes import AdvisoryClassification
from karrio.plugins.advisor_nordic_conventions.rules import advisory

PARCEL_CONNECT_SERVICES: typing.FrozenSet[str] = frozenset(
    {"dhl_freight_sweden_parcel_connect_b2c", "109"}
)
PARCEL_CONNECT_FAMILY: typing.FrozenSet[str] = frozenset(
    {
        "dhl_freight_sweden_parcel_connect_b2c",
        "109",
        "dhl_freight_sweden_parcel_connect_plus",
        "112",
        "dhl_freight_sweden_parcel_return_connect_c2b",
        "107",
    }
)
PARCEL_RETURN_CONNECT: typing.FrozenSet[str] = frozenset(
    {"dhl_freight_sweden_parcel_return_connect_c2b", "107"}
)
PARCEL_CONNECT_BY_AGREEMENT: typing.FrozenSet[str] = PARCEL_CONNECT_FAMILY - PARCEL_RETURN_CONNECT
SWITZERLAND = "CH"
GREAT_BRITAIN = "GB"
NOT_SERVED: typing.Dict[str, typing.Tuple[typing.FrozenSet[str], str]] = {
    SWITZERLAND: (
        PARCEL_CONNECT_FAMILY,
        " ".join(
            [
                "DHL Freight Sweden Parcel Connect (109), Parcel Connect Plus (112), and Parcel Return Connect (107)",
                "do not serve Switzerland.",
                "Book Switzerland on a product that serves it, such as Home Delivery International B2C (601),",
                "Road Freight Standard (202), Road Freight Direct (205), or Road Freight Priority (233).",
            ]
        ),
    ),
    GREAT_BRITAIN: (
        PARCEL_RETURN_CONNECT,
        "DHL Freight Sweden Parcel Return Connect (107) does not serve Great Britain.",
    ),
}

REMINDER_FEES: typing.Dict[str, str] = {"GB": "650 kr"}
DEFAULT_REMINDER_FEE = "390 kr"


def _dhl_freight_sweden(lane: typing.Optional[lanes.Lane]) -> bool:
    return lane is not None and lane.carrier_name == lanes.DHL_FREIGHT_SWEDEN


def customs_mode_missing(request, context) -> typing.List[models.Message]:
    lane = lanes.lane_of(request, context)

    if not (_dhl_freight_sweden(lane) and not lane.dhl_customs_options):
        return []

    return [
        advisory(
            AdvisoryClassification.dhl_freight_sweden_customs_mode_missing,
            "warning",
            " ".join(
                [
                    "DHL Freight Sweden requires customs handling (standard or full service) or an own declaration",
                    "to be selected for destinations outside the EU VAT area, and this booking selects none.",
                    "Set the shipment option dhl_freight_sweden_customs_handling_standard,",
                    "dhl_freight_sweden_customs_handling_full_service, or dhl_freight_sweden_customs_own_declaration;",
                    "the connector selects none implicitly because each carries a DHL fee.",
                ]
            ),
            lane,
            [
                sources.DFS_CUSTOMS_SERVICES_OPT_IN,
                sources.DHL_MAN_CUSTOMS_SELECTION,
                sources.DHL_PRL_NO_FEE_FREE_MODE,
                sources.DHL_OWN_DECLARATION_FEE_INFERENCE,
            ],
            fees="No fee-free customs mode exists for destinations outside the EU VAT area.",
        )
    ]


def invoice_copy(request, context) -> typing.List[models.Message]:
    lane = lanes.lane_of(request, context)

    if not _dhl_freight_sweden(lane):
        return []

    fee = REMINDER_FEES.get(lane.recipient_country, DEFAULT_REMINDER_FEE)

    return [
        advisory(
            AdvisoryClassification.dhl_freight_sweden_invoice_copy,
            "warning",
            " ".join(
                [
                    "DHL Freight Sweden requires a copy of the invoice even when complete customs data is sent with the booking:",
                    "email it to dhlfreight.int.se@dhl.com shortly after booking or upload it in myDHL Freight,",
                    "one document per shipment with a clear reference, because the DHL API has no document upload.",
                    f"Missing documents stop the shipment with a reminder fee of {fee}.",
                ]
            ),
            lane,
            [
                sources.DHL_MAN_INVOICE_COPY,
                sources.DHL_CIE_INVOICE_ROUTES,
                sources.DHL_CIE_REMINDER_FEES,
                sources.DHL_API_NO_UPLOAD,
            ],
        )
    ]


def attached_documents(request, context) -> typing.List[models.Message]:
    lane = lanes.lane_of(request, context)

    if not (_dhl_freight_sweden(lane) and lane.service in PARCEL_CONNECT_SERVICES):
        return []

    return [
        advisory(
            AdvisoryClassification.dhl_freight_sweden_attached_documents,
            "warning",
            " ".join(
                [
                    "DHL Freight Sweden requires two copies of the customs documents attached on the outside of the package",
                    "for Parcel Connect (109) to destinations outside the EU VAT area.",
                ]
            ),
            lane,
            [sources.DHL_MAN_OUTSIDE_COPIES, sources.DHL_OUTSIDE_COPIES_UNCONFIRMED],
            unconfirmed=(
                "The requirement is unconfirmed for Parcel Connect Plus (112) and road-freight products, "
                "which receive no such advisory."
            ),
        )
    ]


def voec_marking(request, context) -> typing.List[models.Message]:
    lane = lanes.lane_of(request, context)

    if not (_dhl_freight_sweden(lane) and lane.to_norway and lane.voec_number):
        return []

    return [
        advisory(
            AdvisoryClassification.dhl_freight_sweden_voec_marking,
            "warning",
            " ".join(
                [
                    "The connector sends the VOEC number to DHL Freight Sweden as the VOEC service,",
                    "and DHL also requires the VOEC ID printed on the package or the label for Norway.",
                ]
            ),
            lane,
            [
                sources.DFS_VOEC_SERVICE,
                sources.DHL_MAN_VOEC_MARKING,
                sources.DHL_MAN_VOEC_PARCEL_CONNECT,
            ],
        )
    ]


def parcel_connect_not_served(request, context) -> typing.List[models.Message]:
    lane = lanes.lane_of(request, context)

    if not _dhl_freight_sweden(lane):
        return []

    services, text = NOT_SERVED.get(lane.recipient_country, (frozenset(), ""))

    if lane.service not in services:
        return []

    return [
        advisory(
            AdvisoryClassification.dhl_freight_sweden_parcel_connect_not_served,
            "warning",
            text,
            lane,
            [sources.DHL_MAN_PARCEL_CONNECT_COUNTRIES],
        )
    ]


def parcel_connect_gb_agreement(request, context) -> typing.List[models.Message]:
    lane = lanes.lane_of(request, context)

    if not (
        _dhl_freight_sweden(lane)
        and lane.recipient_country == GREAT_BRITAIN
        and lane.service in PARCEL_CONNECT_BY_AGREEMENT
    ):
        return []

    return [
        advisory(
            AdvisoryClassification.dhl_freight_sweden_parcel_connect_gb_agreement,
            "warning",
            " ".join(
                [
                    "DHL Freight Sweden serves Great Britain on Parcel Connect (109) and Parcel Connect Plus (112)",
                    "only by separate agreement with DHL; book Great Britain on them only under such an agreement.",
                ]
            ),
            lane,
            [sources.DHL_MAN_PARCEL_CONNECT_COUNTRIES, sources.DHL_CONNECTOR_SANDBOX_112_GB_REJECTED],
        )
    ]
