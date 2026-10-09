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
