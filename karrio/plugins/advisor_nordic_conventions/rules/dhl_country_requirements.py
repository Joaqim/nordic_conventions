"""DHL Freight Sweden country-specific shipping requirement advisories."""

import typing

import karrio.core.models as models
import karrio.core.units as units

import karrio.plugins.advisor_nordic_conventions.lanes as lanes
import karrio.plugins.advisor_nordic_conventions.sources as sources
from karrio.plugins.advisor_nordic_conventions.codes import AdvisoryClassification
from karrio.plugins.advisor_nordic_conventions.rules import advisory

# The DHL Freight Sweden connector's PARTY_TAX_ID_PRODUCTS,
# TRANSPORT_DECLARATION_PRODUCTS, and TRANSPORT_DECLARATION_FREE_WEIGHT_LIMIT_KG
# (karrio-dhl-freight-sweden 62c1f46, units.py), copied as literals because the
# plugin installs and runs standalone; parity tests compare the copies against
# the connector and skip when it is not importable.
GREEK_TAX_ID_PRODUCTS: typing.FrozenSet[str] = frozenset({"202", "SPI", "601"})
TRANSPORT_DECLARATION_PRODUCTS: typing.FrozenSet[str] = frozenset(
    {"202", "205", "233", "SPI", "601"}
)
TRANSPORT_DECLARATION_FREE_WEIGHT_LIMIT_KG = 500.0

CYPRUS = "CY"
GREECE = "GR"
POLAND = "PL"
ROMANIA = "RO"
SPAIN = "ES"
HUNGARY = "HU"


def _dhl_freight_sweden(lane: typing.Optional[lanes.Lane]) -> bool:
    return lane is not None and lane.carrier_name == lanes.DHL_FREIGHT_SWEDEN


def total_weight_kg(request: typing.Any) -> float:
    """The shipment's total gross weight in kg, each parcel weight converted by the SDK."""
    return sum(
        units.Weight(parcel.weight, parcel.weight_unit).KG or 0.0
        for parcel in getattr(request, "parcels", None) or []
    )


def is_private_individual(recipient: typing.Any) -> bool:
    """Whether the recipient address reads as a private individual: residential, or no company name."""
    return bool(getattr(recipient, "residential", False)) or not str(
        getattr(recipient, "company_name", None) or ""
    ).strip()


def _tax_id_of(party: typing.Any) -> typing.Optional[str]:
    return (
        str(getattr(party, "federal_tax_id", None) or "").strip()
        or str(getattr(party, "state_tax_id", None) or "").strip()
        or None
    )


def greek_tax_ids(request, context) -> typing.List[models.Message]:
    lane = lanes.country_lane_of(request, context)

    if not (_dhl_freight_sweden(lane) and lane.recipient_country == GREECE):
        return []

    if lanes.dhl_product_code(lane.service) not in GREEK_TAX_ID_PRODUCTS:
        return []

    missing = " and ".join(
        name
        for name, party in (
            ("the sender", request.shipper),
            ("the recipient", request.recipient),
        )
        if _tax_id_of(party) is None
    )

    if not missing:
        return []

    return [
        advisory(
            AdvisoryClassification.dhl_freight_sweden_greek_tax_ids,
            "warning",
            " ".join(
                [
                    "DHL Freight Sweden requires a VAT number or TIN",
                    f"from {missing} on shipments to Greece on this product,",
                    f"and this booking provides none for {missing}.",
                    "The connector reads each party's number from federal_tax_id or state_tax_id",
                    "and refuses the booking without one;",
                    "EL000000000 can be used for a private individual.",
                ]
            ),
            lane,
            [
                sources.DHL_CSR_GREEK_TAX_IDS,
                sources.DHL_MAN_GREEK_TAX_ID_PRODUCTS,
                sources.DHL_CONNECTOR_GREEK_TAX_ID_PRODUCTS,
            ],
        )
    ]


def cyprus_documents(request, context) -> typing.List[models.Message]:
    lane = lanes.country_lane_of(request, context)

    if not (_dhl_freight_sweden(lane) and lane.recipient_country == CYPRUS):
        return []

    return [
        advisory(
            AdvisoryClassification.dhl_freight_sweden_cyprus_documents,
            "warning",
            " ".join(
                [
                    "DHL Freight Sweden requires a commercial invoice and a packing list on shipments to Cyprus",
                    "to prove the Union status of the goods, and a T2L document where applicable;",
                    "the documents can be uploaded in myDHL Freight.",
                    *(
                        [
                            "The recipient appears to be a private individual,",
                            "so copies of the recipient's ID documents, front and back, must also be provided.",
                        ]
                        if is_private_individual(request.recipient)
                        else []
                    ),
                ]
            ),
            lane,
            [sources.DHL_CSR_CYPRUS_DOCUMENTS],
        )
    ]
