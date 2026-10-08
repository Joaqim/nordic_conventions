"""DHL Freight Sweden trade-document advisories for Swedish shippers."""

import typing

import karrio.core.models as models

import karrio.plugins.advisor_nordic_conventions.exclusions as exclusions
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
PARCEL_RETURN_CONNECT_CODE = "107"
DHL_PRODUCT_NAMES: typing.Dict[str, str] = {
    "102": "Paket",
    "103": "Service Point B2C",
    "104": "Service Point C2B",
    "107": "Parcel Return Connect",
    "109": "Parcel Connect",
    "112": "Parcel Connect Plus",
    "118": "Hemleverans Paket",
    "202": "Road Freight Standard",
    "205": "Road Freight Direct",
    "209": "Special",
    "210": "Pall",
    "211": "Stycke",
    "212": "Parti",
    "233": "Road Freight Priority",
    "401": "Home Delivery",
    "402": "Home Delivery Return",
    "502": "Home Delivery Return",
    "601": "Home Delivery International B2C",
    "SPI": "Standard Pallet International",
}
RETURN_TO_SWEDEN = "Parcel Return Connect (107) only returns a parcel from abroad to its original sender in Sweden."
SWITZERLAND_ALTERNATIVES = " ".join(
    [
        "Book Switzerland on a product that serves it, such as Home Delivery International B2C (601),",
        "Road Freight Standard (202), Road Freight Direct (205), or Road Freight Priority (233).",
    ]
)

ALAND_REJECTED_CUSTOMS_OPTIONS: typing.Dict[str, str] = {
    lanes.DHLCustomsOption.dhl_freight_sweden_customs_handling_standard.name: "customs handling standard",
    lanes.DHLCustomsOption.dhl_freight_sweden_customs_handling_full_service.name: "customs handling full service",
}

COUNTRY_NAMES: typing.Dict[str, str] = {"NO": "Norway", "CH": "Switzerland"}
JOINT_DECLARATION_DESTINATIONS = " or ".join(
    COUNTRY_NAMES[country] for country in lanes.DHL_JOINT_DECLARATION_COUNTRIES
)

REMINDER_FEES: typing.Dict[str, str] = {"GB": "650 kr"}
DEFAULT_REMINDER_FEE = "390 kr"


def _dhl_freight_sweden(lane: typing.Optional[lanes.Lane]) -> bool:
    return lane is not None and lane.carrier_name == lanes.DHL_FREIGHT_SWEDEN


def _to_aland(request, lane: lanes.Lane) -> bool:
    return lanes.dhl_in_aland(lane.recipient_country, getattr(request.recipient, "postal_code", None))


def customs_mode_missing(request, context) -> typing.List[models.Message]:
    lane = lanes.lane_of(request, context)

    if not (_dhl_freight_sweden(lane) and not lane.dhl_customs_options):
        return []

    if _to_aland(request, lane):
        return []

    return [
        advisory(
            AdvisoryClassification.dhl_freight_sweden_customs_mode_missing,
            "warning",
            " ".join(
                [
                    "DHL Freight Sweden requires customs handling (standard or full service), an own declaration,",
                    f"or a joint declaration to {JOINT_DECLARATION_DESTINATIONS}",
                    "to be selected for destinations outside the EU VAT area, and this booking selects none.",
                    "Set the shipment option dhl_freight_sweden_customs_handling_standard,",
                    "dhl_freight_sweden_customs_handling_full_service, dhl_freight_sweden_customs_own_declaration,",
                    "or dhl_freight_sweden_customs_joint_declaration;",
                    "the connector selects none implicitly because each carries a DHL fee.",
                ]
            ),
            lane,
            [
                sources.DFS_CUSTOMS_SERVICES_OPT_IN,
                sources.DHL_MAN_CUSTOMS_SELECTION,
                sources.DHL_MAN_JOINT_DECLARATION,
                sources.DHL_CONNECTOR_JOINT_DECLARATION_DESTINATIONS,
                sources.DHL_PRL_NO_FEE_FREE_MODE,
                sources.DHL_OWN_DECLARATION_FEE_INFERENCE,
            ],
            fees="No fee-free customs mode exists for destinations outside the EU VAT area.",
        )
    ]


def aland_customs_service_rejected(request, context) -> typing.List[models.Message]:
    lane = lanes.lane_of(request, context)

    if not (_dhl_freight_sweden(lane) and _to_aland(request, lane)):
        return []

    rejected = sorted(lane.dhl_customs_options & ALAND_REJECTED_CUSTOMS_OPTIONS.keys())

    if not rejected:
        return []

    return [
        advisory(
            AdvisoryClassification.dhl_freight_sweden_aland_customs_service_rejected,
            "warning",
            " ".join(
                [
                    "DHL Freight Sweden rejects",
                    " and ".join(f"{ALAND_REJECTED_CUSTOMS_OPTIONS[option]} ({option})" for option in rejected),
                    "to Åland (FI 22000-22999) with error 24003, and the connector refuses the selection before booking.",
                    "Book Åland with an own declaration (dhl_freight_sweden_customs_own_declaration)",
                    "or with customs data and no customs service, which DHL accepted for Parcel Connect (109)",
                    "without showing how it clears customs.",
                ]
            ),
            lane,
            [sources.DHL_MAN_CUSTOMS_SELECTION, sources.DHL_CONNECTOR_ALAND_CUSTOMS],
        )
    ]


def territory_postal_code_mismatch(request, context) -> typing.List[models.Message]:
    lane = lanes.shipper_lane_of(request, context)

    if not _dhl_freight_sweden(lane):
        return []

    recipient = request.recipient
    code = (recipient.country_code or "").upper()
    territory = lanes.DHL_TERRITORY_POSTAL_CODES.get(code)

    if territory is None or territory.matches(recipient.postal_code):
        return []

    postal_code = recipient.postal_code
    got = f"postal code {postal_code!r}" if str(postal_code or "").strip() else "no postal code"

    return [
        advisory(
            AdvisoryClassification.dhl_freight_sweden_territory_postal_code_mismatch,
            "warning",
            " ".join(
                [
                    f"DHL Freight Sweden books country code {code} ({territory.name}) as {territory.parent},",
                    f"and the connector refuses the booking unless the recipient has {territory.describe()};",
                    f"this recipient has {got}.",
                    f"Use the country code {territory.parent} for an address outside {territory.name}.",
                ]
            ),
            lane,
            [sources.DHL_CONNECTOR_TERRITORY_POSTAL_CODES],
        )
    ]


def joint_declaration_destination(request, context) -> typing.List[models.Message]:
    lane = lanes.lane_of(request, context)

    if not (
        _dhl_freight_sweden(lane)
        and lanes.DHLCustomsOption.dhl_freight_sweden_customs_joint_declaration.name in lane.dhl_customs_options
        and lane.recipient_country not in lanes.DHL_JOINT_DECLARATION_COUNTRIES
    ):
        return []

    alternatives = (
        "an own declaration (dhl_freight_sweden_customs_own_declaration) or customs data with no customs service"
        if _to_aland(request, lane)
        else "customs handling (dhl_freight_sweden_customs_handling_standard or "
        "dhl_freight_sweden_customs_handling_full_service) or an own declaration "
        "(dhl_freight_sweden_customs_own_declaration)"
    )

    return [
        advisory(
            AdvisoryClassification.dhl_freight_sweden_joint_declaration_destination,
            "warning",
            " ".join(
                [
                    "DHL Freight Sweden's customs joint declaration (dhl_freight_sweden_customs_joint_declaration)",
                    f"is valid only to {JOINT_DECLARATION_DESTINATIONS},",
                    f"and the connector refuses it to {lane.recipient_country}.",
                    f"Select {alternatives} instead.",
                ]
            ),
            lane,
            [sources.DHL_MAN_JOINT_DECLARATION, sources.DHL_CONNECTOR_JOINT_DECLARATION_DESTINATION],
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


def _excluded_party(request, lane: lanes.Lane, product_code: str) -> typing.Optional[exclusions.ExcludedParty]:
    return exclusions.excluded_party(
        product_code,
        dict(
            shipper=(lane.shipper_country, getattr(request.shipper, "postal_code", None)),
            recipient=(lane.recipient_country, getattr(request.recipient, "postal_code", None)),
        ),
    )


def parcel_connect_not_served(request, context) -> typing.List[models.Message]:
    lane = lanes.lane_of(request, context)

    if not _dhl_freight_sweden(lane):
        return []

    product_code = lanes.dhl_product_code(lane.service)

    if product_code is None:
        return []

    if lanes.dhl_lane_served(product_code, lane.shipper_country, lane.recipient_country):
        excluded = _excluded_party(request, lane, product_code)
        return [] if excluded is None else [_excluded_postal_code(lane, product_code, excluded)]

    return [
        advisory(
            AdvisoryClassification.dhl_freight_sweden_parcel_connect_not_served,
            "warning",
            " ".join(
                [
                    f"DHL Freight Sweden {DHL_PRODUCT_NAMES[product_code]} ({product_code})",
                    f"does not ship from {lane.shipper_country} to {lane.recipient_country}.",
                    *([RETURN_TO_SWEDEN] if product_code == PARCEL_RETURN_CONNECT_CODE else []),
                    *([SWITZERLAND_ALTERNATIVES] if lane.recipient_country == SWITZERLAND else []),
                ]
            ),
            lane,
            [sources.DHL_MAN_PRODUCT_LANES],
        )
    ]


def _excluded_postal_code(
    lane: lanes.Lane, product_code: str, excluded: exclusions.ExcludedParty
) -> models.Message:
    direction = "to" if excluded.party == "recipient" else "from"
    return advisory(
        AdvisoryClassification.dhl_freight_sweden_parcel_connect_not_served,
        "warning",
        f"DHL Freight Sweden {DHL_PRODUCT_NAMES[product_code]} ({product_code}) "
        f"does not ship {direction} {excluded.exclusion.excluded_codes()}.",
        lane,
        [sources.DHL_MAN_EXCLUDED_AREAS, sources.DHL_CONNECTOR_EXCLUDED_POSTAL_CODES],
    )


def parcel_connect_gb_agreement(request, context) -> typing.List[models.Message]:
    lane = lanes.lane_of(request, context)

    if not (
        _dhl_freight_sweden(lane)
        and lane.recipient_country == GREAT_BRITAIN
        and lane.service in PARCEL_CONNECT_BY_AGREEMENT
        and _excluded_party(request, lane, lanes.dhl_product_code(lane.service) or "") is None
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
