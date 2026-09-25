"""PostNord trade-document advisories for Swedish, Danish, and Finnish shippers."""

import typing

import karrio.core.models as models

import karrio.plugins.nordic_conventions.lanes as lanes
import karrio.plugins.nordic_conventions.sources as sources
from karrio.plugins.nordic_conventions.rules import advisory

SE_NO_DIGITAL_INVOICE = "nordic_postnord_se_no_digital_invoice"
SE_POSTPAKET_COMMERCIAL_INVOICE = "nordic_postnord_se_postpaket_commercial_invoice"
SE_EXPORT_PAPER_INVOICE = "nordic_postnord_se_export_paper_invoice"
FI_EXPORT_INVOICE = "nordic_postnord_fi_export_invoice"
DK_EXPORT_DOCUMENTS = "nordic_postnord_dk_export_documents"

DK_DOCUMENT_COPIES: typing.Dict[str, str] = {
    "NO": "2 commercial invoices",
    "CH": "3 commercial invoices",
    "LI": "3 commercial invoices",
    "GB": "2 commercial invoices",
}
DK_DEFAULT_DOCUMENT_COPIES = (
    "1 CN23 and 2 commercial invoices, the invoice not required but recommended by PostNord"
)

# Letter services named in the letters table of the PostNord SE Swedish
# customs documents page that map to a connector code with clear evidence.
NORWAY_NAMED_LETTER_SERVICES: typing.FrozenSet[str] = frozenset(
    {"postnord_export_letter", "UX", "postnord_rek", "RR"}
)

NORWAY_ROUTES = (
    "PostNord Skicka Direkt Business, email to foravisering.export@postnord.com, "
    "or upload in PostNord MyCustoms"
)


def _postnord_from(lane: typing.Optional[lanes.Lane], country: str) -> bool:
    return (
        lane is not None
        and lane.carrier_name == lanes.POSTNORD
        and lane.shipper_country == country
    )


def postpaket_commercial_applies(lane: typing.Optional[lanes.Lane]) -> bool:
    """Whether a Swedish commercial Postpaket Utrikes advisory applies.

    Shared by the Postpaket Utrikes and the Norway digital invoice advisories,
    so a Swedish shipment to Norway receives the Norway invoice routes once.
    """
    return (
        _postnord_from(lane, "SE")
        and lane.postnord_product_group == lanes.INTERNATIONAL_PARCEL
        and lane.commercial
    )


def se_no_digital_invoice(request, context) -> typing.List[models.Message]:
    lane = lanes.lane_of(request, context)

    if not (
        _postnord_from(lane, "SE")
        and lane.to_norway
        and not postpaket_commercial_applies(lane)
    ):
        return []

    transmitted = lane.postnord_product_group == lanes.PARCEL and lane.has_customs
    norway_named_letter = lane.service in NORWAY_NAMED_LETTER_SERVICES

    text = " ".join(
        [
            "PostNord requires the commercial invoice for shipments from Sweden to Norway digitally, not on paper with the parcel.",
            "Digital routes are the booking itself (the connector sends the customs invoice data for a parcel product booked with customs data), "
            f"{NORWAY_ROUTES}.",
            *(
                [
                    "For letters to Norway PostNord requires a commercial invoice and a VOEC number from SEK 0, the invoice sent digitally through the same routes."
                ]
                if norway_named_letter
                else []
            ),
            (
                "This booking carries customs data for a parcel product, so the connector has already transmitted the invoice data."
                if transmitted
                else "This booking does not transmit a customs invoice, so send the invoice through one of the other routes."
            ),
        ]
    )

    return [
        advisory(
            SE_NO_DIGITAL_INVOICE,
            "info" if transmitted else "warning",
            text,
            lane,
            [
                sources.PN_SE_SERVICE_POINT_TERMS_NORWAY,
                sources.PN_SE_NORWAY_CHANNELS,
                sources.PN_SE_NORWAY_ONLY_CHANNELS,
                sources.PNS_PARCEL_CUSTOMS_INVOICE,
                *([sources.PN_SE_SV_PAGE_NORWAY_LETTERS] if norway_named_letter else []),
            ],
        )
    ]


def se_postpaket_commercial_invoice(request, context) -> typing.List[models.Message]:
    lane = lanes.lane_of(request, context)

    if not postpaket_commercial_applies(lane):
        return []

    connector_note = (
        "The connector currently sends CN22 declaration data and no invoice for International Parcel, "
        "so supply the CN23 and the invoice yourself."
    )
    text = (
        " ".join(
            [
                "Commercial PostNord Postpaket Utrikes (International Parcel, 91) to Norway needs the CN23 export declaration,",
                "and PostNord requires the commercial invoice for Norway digitally, not attached to the parcel:",
                f"send it through the Booking API, {NORWAY_ROUTES}.",
                connector_note,
            ]
        )
        if lane.to_norway
        else " ".join(
            [
                "Commercial PostNord Postpaket Utrikes (International Parcel, 91) outside the EU VAT area needs the CN23 export declaration",
                "and a commercial invoice in three copies with the parcel.",
                "Three copies satisfies both the Postpaket Utrikes terms (two copies above SEK 2 000 or for commercial purposes)",
                "and the PostNord web pages (triplicate above SEK 2 000).",
                connector_note,
            ]
        )
    )

    return [
        advisory(
            SE_POSTPAKET_COMMERCIAL_INVOICE,
            "warning",
            text,
            lane,
            [
                sources.PN_SE_POSTPAKET_TERMS,
                sources.PN_SE_EN_PAGE_POSTPAKET,
                sources.PN_SE_SV_PAGE_POSTPAKET,
                *([sources.PN_SE_NORWAY_CHANNELS] if lane.to_norway else []),
                sources.PNS_INTERNATIONAL_PARCEL_CN22,
                sources.PN_POSTPAKET_CODE_91,
                sources.PN_POSTPAKET_CODE_95,
            ],
        )
    ]


def se_export_paper_invoice(request, context) -> typing.List[models.Message]:
    lane = lanes.lane_of(request, context)

    if not (
        _postnord_from(lane, "SE")
        and lane.postnord_product_group == lanes.PARCEL
        and not lane.to_norway
    ):
        return []

    return [
        advisory(
            SE_EXPORT_PAPER_INVOICE,
            "warning",
            " ".join(
                [
                    "PostNord requires a commercial invoice in English in triplicate to accompany parcels from Sweden",
                    "to destinations outside the EU VAT area, in a plastic pocket on parcel no. 1.",
                    "The digital customs data sent with the booking prevails over the paper invoice on any discrepancy.",
                ]
            ),
            lane,
            [
                sources.PN_SE_EN_PAGE_PARCEL_TRIPLICATE,
                sources.PN_SE_SV_PAGE_PARCEL_TWO_COPIES,
                sources.PN_SE_SERVICE_POINT_TERMS_PAPER,
                sources.PN_SE_PLASTIC_POCKET_ORIGIN,
            ],
        )
    ]


def fi_export_invoice(request, context) -> typing.List[models.Message]:
    lane = lanes.lane_of(request, context)

    if not (_postnord_from(lane, "FI") and lane.postnord_product_group == lanes.PARCEL):
        return []

    text = (
        " ".join(
            [
                "PostNord Finland requires the invoice for Norway electronically, and it must reach PostNord before the shipment.",
                "A copy of the invoice can be emailed to tullaus.fi@postnord.com.",
            ]
        )
        if lane.to_norway
        else " ".join(
            [
                "PostNord Finland clears customs primarily from the electronic customs data sent with the booking,",
                "and a copy of the invoice can be emailed to tullaus.fi@postnord.com.",
                "PostNord Finland's special terms for parcels also require a signed commercial invoice in English in triplicate",
                "to accompany parcels to destinations outside the EU VAT area, which is stricter than its web page.",
            ]
        )
    )

    return [
        advisory(
            FI_EXPORT_INVOICE,
            "warning",
            text,
            lane,
            (
                [
                    sources.PN_FI_WEB_PAGE_NORWAY,
                    sources.PN_FI_SPECIAL_TERMS,
                    sources.PN_FI_WEB_PAGE,
                ]
                if lane.to_norway
                else [
                    sources.PN_FI_WEB_PAGE,
                    sources.PN_FI_SPECIAL_TERMS,
                    sources.PN_FI_GOVERNING_UNRESOLVED,
                ]
            ),
        )
    ]


def dk_export_documents(request, context) -> typing.List[models.Message]:
    lane = lanes.lane_of(request, context)

    if not (_postnord_from(lane, "DK") and lane.postnord_product_group == lanes.PARCEL):
        return []

    copies = DK_DOCUMENT_COPIES.get(lane.recipient_country, DK_DEFAULT_DOCUMENT_COPIES)

    return [
        advisory(
            DK_EXPORT_DOCUMENTS,
            "warning",
            " ".join(
                [
                    "PostNord Denmark requires the export documents in a plastic pocket visible on the parcel:",
                    f"{copies} for {lane.recipient_country}.",
                    "If an export declaration was lodged, send a copy of it to eksport@postnord.com.",
                ]
            ),
            lane,
            [sources.PN_DK_EXPORT_PAGE],
        )
    ]
