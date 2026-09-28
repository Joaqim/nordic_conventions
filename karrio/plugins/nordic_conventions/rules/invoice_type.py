"""Advisory on an invoice type that contradicts the customs content type."""

import typing

import karrio.core.models as models
import karrio.core.units as units

import karrio.plugins.nordic_conventions.lanes as lanes
import karrio.plugins.nordic_conventions.sources as sources
from karrio.plugins.nordic_conventions.codes import AdvisoryClassification
from karrio.plugins.nordic_conventions.rules import advisory

GIFT_OR_SAMPLE: typing.FrozenSet[str] = frozenset(
    {units.CustomsContentType.gift.name, units.CustomsContentType.sample.name}
)

CARRIER_SOURCES: typing.Dict[str, typing.List[sources.Source]] = {
    lanes.POSTNORD: [
        sources.PNS_COMMERCIAL_FLAG,
        sources.PROFORMA_FOR_GOODS_NOT_SOLD,
        sources.PN_POSTPAKET_TERMS_PROFORMA,
        sources.CONNECTOR_FLAG_MAPPING,
    ],
    lanes.DHL_FREIGHT_SWEDEN: [
        sources.DFS_COMMERCIAL_FLAG,
        sources.PROFORMA_FOR_GOODS_NOT_SOLD,
        sources.CONNECTOR_FLAG_MAPPING,
    ],
}


def _carries_invoice_type(lane: typing.Optional[lanes.Lane]) -> bool:
    return (
        lane is not None
        and lane.has_customs
        and (
            lane.carrier_name == lanes.DHL_FREIGHT_SWEDEN
            or lane.postnord_product_group == lanes.PARCEL
        )
    )


def invoice_type_content_mismatch(request, context) -> typing.List[models.Message]:
    lane = lanes.lane_of(request, context)

    if not _carries_invoice_type(lane):
        return []

    if not lane.commercial_invoice and lane.sale_like:
        level, text = (
            "warning",
            " ".join(
                [
                    "The connector declares a proforma invoice because customs.commercial_invoice is not true,",
                    "but the content is described as goods for sale.",
                    "A proforma invoice is for gifts and samples for which the recipient makes no payment;",
                    "set commercial_invoice to true for goods sold.",
                ]
            ),
        )
    elif lane.commercial_invoice and lane.content_type in GIFT_OR_SAMPLE:
        level, text = (
            "info",
            " ".join(
                [
                    "A commercial invoice is declared for content described as a gift or sample,",
                    "for which a proforma invoice is the usual document.",
                ]
            ),
        )
    else:
        return []

    return [
        advisory(
            AdvisoryClassification.invoice_type_content_mismatch,
            level,
            text,
            lane,
            CARRIER_SOURCES[lane.carrier_name],
        )
    ]
