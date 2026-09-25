"""DHL Freight Sweden trade-document advisories for Swedish shippers."""

import typing

import karrio.core.models as models

import karrio.plugins.nordic_conventions.lanes as lanes
import karrio.plugins.nordic_conventions.sources as sources
from karrio.plugins.nordic_conventions.rules import advisory

CUSTOMS_MODE_MISSING = "nordic_dhl_freight_sweden_customs_mode_missing"


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
