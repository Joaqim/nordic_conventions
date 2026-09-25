"""DHL Freight Sweden trade-document advisories for Swedish shippers."""

import typing

import karrio.core.models as models

import karrio.plugins.nordic_conventions.lanes as lanes
import karrio.plugins.nordic_conventions.sources as sources
from karrio.plugins.nordic_conventions.rules import advisory

CUSTOMS_MODE_MISSING = "nordic_dhl_freight_sweden_customs_mode_missing"
INVOICE_COPY = "nordic_dhl_freight_sweden_invoice_copy"
ATTACHED_DOCUMENTS = "nordic_dhl_freight_sweden_attached_documents"

PARCEL_CONNECT_SERVICES: typing.FrozenSet[str] = frozenset(
    {"dhl_freight_sweden_parcel_connect_b2c", "109"}
)

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
            CUSTOMS_MODE_MISSING,
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
            INVOICE_COPY,
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
            ATTACHED_DOCUMENTS,
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
