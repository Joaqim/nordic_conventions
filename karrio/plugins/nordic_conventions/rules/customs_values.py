"""Advisories on declared commodity values: discounted lines to Switzerland and zero-value lines."""

import typing

import karrio.core.models as models

import karrio.plugins.nordic_conventions.lanes as lanes
import karrio.plugins.nordic_conventions.sources as sources
from karrio.plugins.nordic_conventions.codes import AdvisoryClassification
from karrio.plugins.nordic_conventions.rules import advisory

SWITZERLAND = "CH"


def _commodities(request: typing.Any) -> typing.List[typing.Any]:
    customs = getattr(request, "customs", None)
    return list(getattr(customs, "commodities", None) or [])


def _zero_valued(commodity: typing.Any) -> bool:
    return not getattr(commodity, "value_amount", None)


def _discounted(commodity: typing.Any) -> bool:
    metadata = getattr(commodity, "metadata", None) or {}
    return metadata.get("discount_percentage") is not None or _zero_valued(commodity)


def ch_discount_on_invoice(request, context) -> typing.List[models.Message]:
    lane = lanes.lane_of(request, context)

    if lane is None or lane.recipient_country != SWITZERLAND:
        return []

    lines = [index for index, commodity in enumerate(_commodities(request)) if _discounted(commodity)]

    if not lines:
        return []

    return [
        advisory(
            AdvisoryClassification.ch_discount_on_invoice,
            "info",
            " ".join(
                [
                    "Switzerland does not tax a discount, or an item handed over with a sold item as a discount in kind or add-on,",
                    "as part of the import consideration, provided the item is directly connected to the sale;",
                    "show the discount on the commercial invoice and tie the discounted or free item to that sale.",
                ]
            ),
            lane,
            [sources.BAZG_RABATTE],
            lines=lines,
            unconfirmed="R-69-03 does not address an add-on shipped in a separate parcel from the sale it belongs to.",
        )
    ]


def zero_value_line(request, context) -> typing.List[models.Message]:
    lane = lanes.lane_of(request, context)

    if lane is None:
        return []

    lines = [index for index, commodity in enumerate(_commodities(request)) if _zero_valued(commodity)]

    if not lines:
        return []

    return [
        advisory(
            AdvisoryClassification.zero_value_line,
            "warning",
            " ".join(
                [
                    "A commodity line declares a customs value of 0 or none.",
                    "A commercial or pro forma invoice may never carry a value of 0, even for gifts or samples;",
                    "declare each line's customs value.",
                ]
            ),
            lane,
            [
                sources.PN_SE_NO_PAGE_NON_ZERO_VALUE,
                sources.TV_PROFORMA_NON_ZERO_VALUE,
                sources.DHL_EXPRESS_NO_ZERO_VALUES,
            ],
            lines=lines,
        )
    ]
