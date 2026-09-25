"""PostNord trade-document advisories for Swedish, Danish, and Finnish shippers."""

import typing

import karrio.core.models as models

import karrio.plugins.nordic_conventions.lanes as lanes
import karrio.plugins.nordic_conventions.sources as sources
from karrio.plugins.nordic_conventions.rules import advisory

SE_NO_DIGITAL_INVOICE = "nordic_postnord_se_no_digital_invoice"

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
