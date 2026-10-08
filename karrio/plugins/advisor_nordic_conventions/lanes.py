"""Scope gate and shipment lane shared by every Nordic conventions advisory."""

import typing

import attr
import karrio.lib as lib
import karrio.core.units as units

import karrio.plugins.advisor_nordic_conventions.territories as territories

POSTNORD = "postnord"
DHL_FREIGHT_SWEDEN = "dhl_freight_sweden"
NORWAY = "NO"

SHIPPER_COUNTRIES: typing.Dict[str, typing.FrozenSet[str]] = {
    POSTNORD: frozenset({"SE", "DK", "FI"}),
    DHL_FREIGHT_SWEDEN: frozenset({"SE"}),
}

LETTER = "letter"
INTERNATIONAL_PARCEL = "international_parcel"
PARCEL = "parcel"

# The PostNord connector's LETTER_SERVICES and INTERNATIONAL_PARCEL_SERVICE
# (karrio develop 7a56ffa5b, postnord units.py:264-285), as unified name and
# carrier code pairs.
POSTNORD_LETTER_SERVICES: typing.Dict[str, str] = {
    "postnord_tracked": "04",
    "postnord_tracked_letter": "34",
    "postnord_export_letter": "UX",
    "postnord_varubrev_first_class": "86",
    "postnord_expressbrev": "LX",
    "postnord_rek": "RR",
    "postnord_rek_retur": "RK",
    "postnord_rek_extra": "RL",
    "postnord_rekommanderet_brev": "RE",
    "postnord_rekommanderet_quickbrev": "RQ",
    "postnord_varde": "VV",
    "postnord_afleveringsattest": "AF",
}
POSTNORD_INTERNATIONAL_PARCEL: typing.Tuple[str, str] = (
    "postnord_postpaket_utrikes",
    "91",
)


class DHLCustomsOption(lib.Enum):
    """The DHL Freight Sweden connector's customs service selectors.

    Parsed with karrio's option helper exactly as the connector's
    ``shipping_options_initializer`` does, so only unified option names are
    recognised and a selector counts as set whenever karrio's bool option
    parsing selects it.
    """

    dhl_freight_sweden_customs_handling_standard = lib.OptionEnum(
        "customsHandlingStandard", bool
    )
    dhl_freight_sweden_customs_handling_full_service = lib.OptionEnum(
        "customsHandlingFullService", bool
    )
    dhl_freight_sweden_customs_own_declaration = lib.OptionEnum(
        "customsCustomersOwnDeclaration", bool
    )
    dhl_freight_sweden_customs_joint_declaration = lib.OptionEnum(
        "customsJointDeclaration", bool
    )



# The DHL Freight Sweden connector's PRODUCT_LANES, PRODUCT_LANE_CITATIONS,
# and ShippingService (karrio-dhl-freight-sweden b54fcdb, units.py), from the
# "Valid countries" tables of product manual v5.26 section 5. 202, 205, 233,
# SPI, and 601 "can be used to and from Sweden" (§5.4 p22, §5.9 p41, §5.10
# p46, §5.11 p51, §5.19 p81), and 107 returns a 109 shipment to its original
# sender in Sweden (§5.15 p65).
def _countries(codes: str) -> typing.List[str]:
    return codes.split()


PARCEL_CONNECT_B2C_COUNTRIES = _countries(
    "AT BE BG CZ DE DK EE ES FI FR GB HR HU IE IT LT LU LV NL NO PL PT RO SI SK"
)  # §5.14 p63
PARCEL_CONNECT_PLUS_COUNTRIES = _countries(
    "AT BE BG CZ DE DK EE ES FI FR GB HR HU IE IT LT LU LV NL NO PL PT RO SI SK"
)  # §5.3 p18
PARCEL_RETURN_CONNECT_COUNTRIES = _countries(
    "AT BE BG CZ DE DK EE ES FI FR HR HU IE IT LT LU LV NL NO PL PT RO SI SK"
)  # §5.15 p66
# 202 §5.4 p23, 205 §5.9 p43, SPI §5.11 p52.
ROAD_FREIGHT_COUNTRIES = _countries(
    "AD AL AM AT AZ BA BE BG CH CY CZ DE DK EE ES FI FR GB GE GI GR HR HU IE "
    "IT KG KZ LI LT LU LV MA MC MD ME MK MT NL NO PL PT RO RS SE SI SK SM TJ "
    "TR UA UZ XK"
)
ROAD_FREIGHT_PRIORITY_COUNTRIES = _countries(
    "AT BE BG CH CZ DE DK EE ES FI FR GB HR HU IE IT LI LT LU LV NL NO PL PT "
    "RO SE SI SK"
)  # §5.10 p47
HOME_DELIVERY_INTERNATIONAL_COUNTRIES = _countries(
    "AT BE BG CH CZ DE DK EE ES FI FR GB GR HR HU IE IT LT LU LV NL NO PL PT "
    "RO SE SI SK"
)  # §5.19 p82

SWEDEN = frozenset(["SE"])


class DHLProductLane(typing.NamedTuple):
    """Shipper and recipient countries a DHL Freight Sweden product carries shipments between."""

    origins: typing.FrozenSet[str]
    destinations: typing.FrozenSet[str]


def _from_sweden(countries: typing.Iterable[str]) -> typing.Tuple[DHLProductLane, ...]:
    return (DHLProductLane(SWEDEN, frozenset(countries) - SWEDEN),)


def _to_sweden(countries: typing.Iterable[str]) -> typing.Tuple[DHLProductLane, ...]:
    return (DHLProductLane(frozenset(countries) - SWEDEN, SWEDEN),)


def _to_and_from_sweden(countries: typing.Iterable[str]) -> typing.Tuple[DHLProductLane, ...]:
    return (*_from_sweden(countries), *_to_sweden(countries))


DHL_PRODUCT_CODES: typing.Dict[str, str] = {
    "dhl_freight_sweden_hemleverans_paket_b2c": "118",
    "dhl_freight_sweden_home_delivery_b2c": "401",
    "dhl_freight_sweden_home_delivery_c2b": "402",
    "dhl_freight_sweden_home_delivery_c2b_502": "502",
    "dhl_freight_sweden_pall": "210",
    "dhl_freight_sweden_paket": "102",
    "dhl_freight_sweden_parti": "212",
    "dhl_freight_sweden_service_point_b2c": "103",
    "dhl_freight_sweden_service_point_c2b": "104",
    "dhl_freight_sweden_special": "209",
    "dhl_freight_sweden_stycke": "211",
    "dhl_freight_sweden_road_freight_standard": "202",
    "dhl_freight_sweden_road_freight_direct": "205",
    "dhl_freight_sweden_road_freight_priority": "233",
    "dhl_freight_sweden_home_delivery_international_b2c": "601",
    "dhl_freight_sweden_parcel_connect_b2c": "109",
    "dhl_freight_sweden_parcel_return_connect_c2b": "107",
    "dhl_freight_sweden_parcel_connect_plus": "112",
    "dhl_freight_sweden_standard_pallet_international": "SPI",
}

DHL_DOMESTIC_PRODUCTS = ("102", "209", "210", "211", "212", "103", "104", "118", "401", "402", "502")

DHL_PRODUCT_LANES: typing.Dict[str, typing.Tuple[DHLProductLane, ...]] = {
    **{code: (DHLProductLane(SWEDEN, SWEDEN),) for code in DHL_DOMESTIC_PRODUCTS},
    "109": _from_sweden(PARCEL_CONNECT_B2C_COUNTRIES),
    "112": _from_sweden(PARCEL_CONNECT_PLUS_COUNTRIES),
    "107": _to_sweden(PARCEL_RETURN_CONNECT_COUNTRIES),
    "202": _to_and_from_sweden(ROAD_FREIGHT_COUNTRIES),
    "205": _to_and_from_sweden(ROAD_FREIGHT_COUNTRIES),
    "SPI": _to_and_from_sweden(ROAD_FREIGHT_COUNTRIES),
    "233": _to_and_from_sweden(ROAD_FREIGHT_PRIORITY_COUNTRIES),
    "601": _to_and_from_sweden(HOME_DELIVERY_INTERNATIONAL_COUNTRIES),
}

DHL_PRODUCT_LANE_CITATIONS: typing.Dict[str, str] = {
    "102": "§5.2 p15",
    "112": "§5.3 p18",
    "202": "§5.4 p23",
    "209": "§5.5 p27",
    "210": "§5.6 p30",
    "211": "§5.7 p34",
    "212": "§5.8 p38",
    "205": "§5.9 p43",
    "233": "§5.10 p47",
    "SPI": "§5.11 p52",
    "103": "§5.12 p56",
    "104": "§5.13 p59",
    "109": "§5.14 p63",
    "107": "§5.15 p66",
    "118": "§5.16 p68",
    "401": "§5.17 p72",
    "402": "§5.18 p76",
    "502": "§5.18 p76",
    "601": "§5.19 p82",
}


# The DHL Freight Sweden connector's TERRITORY_PARENTS (karrio-dhl-freight-sweden
# 9e2b98f, units.py): the country DHL serves a territory code under, which the
# connector sends instead of the territory code before its customs-area, lane,
# and excluded postal code checks.
DHL_TERRITORY_PARENTS: typing.Dict[str, str] = {
    **territories.NUMERIC_POSTAL_TERRITORY_PARENTS,
    "JE": "GB",  # Jersey
    "GG": "GB",  # Guernsey
    "IM": "GB",  # Isle of Man
    "XI": "GB",  # Northern Ireland
}


def dhl_parent_country(country_code: str) -> str:
    """The country DHL Freight Sweden books a territory code under; other codes unchanged."""
    return DHL_TERRITORY_PARENTS.get(country_code.upper(), country_code)


def dhl_product_code(service: typing.Optional[str]) -> typing.Optional[str]:
    """The DHL Freight Sweden product code a unified name or carrier code names, if any."""
    if service in DHL_PRODUCT_LANES:
        return service
    return DHL_PRODUCT_CODES.get(service or "")


def dhl_lane_served(product_code: str, origin: str, destination: str) -> bool:
    """Whether the product carries shipments from ``origin`` to ``destination``, as given."""
    return any(
        origin in lane.origins and destination in lane.destinations
        for lane in DHL_PRODUCT_LANES.get(product_code, ())
    )

NOT_SALE_LIKE_CONTENT: typing.FrozenSet[str] = frozenset(
    {
        units.CustomsContentType.gift.name,
        units.CustomsContentType.sample.name,
        units.CustomsContentType.documents.name,
        units.CustomsContentType.return_merchandise.name,
    }
)


@attr.s(auto_attribs=True, frozen=True)
class Lane:
    """An in-scope shipment reduced to the facts the advisories depend on."""

    carrier_name: str
    shipper_country: str
    recipient_country: str
    to_norway: bool
    service: typing.Optional[str]
    postnord_product_group: typing.Optional[str]
    has_customs: bool
    commercial_invoice: bool
    content_type: typing.Optional[str]
    voec_number: typing.Optional[str]
    dhl_customs_options: typing.FrozenSet[str]
    sale_like: bool
    commercial: bool


def postnord_product_group(service: typing.Optional[str]) -> str:
    """Classify a PostNord service name or carrier code by product group."""
    if service in POSTNORD_INTERNATIONAL_PARCEL:
        return INTERNATIONAL_PARCEL

    if service in {*POSTNORD_LETTER_SERVICES.keys(), *POSTNORD_LETTER_SERVICES.values()}:
        return LETTER

    return PARCEL


def content_type_of(customs: typing.Optional[typing.Any]) -> typing.Optional[str]:
    """The customs content type lower-cased, so names and values compare alike."""
    content_type = getattr(customs, "content_type", None)
    return (str(content_type).strip().lower() or None) if content_type else None


def sale_like(customs: typing.Optional[typing.Any]) -> bool:
    """Whether customs data describes goods for sale."""
    return customs is not None and content_type_of(customs) not in NOT_SALE_LIKE_CONTENT


def commercial(customs: typing.Optional[typing.Any]) -> bool:
    """Whether customs data describes a commercial shipment."""
    return customs is not None and (
        bool(customs.commercial_invoice) or sale_like(customs)
    )


def selected_dhl_customs_options(options: typing.Optional[dict]) -> typing.FrozenSet[str]:
    parsed = lib.to_shipping_options(
        dict(options or {}),
        option_type=DHLCustomsOption,
        items_filter=lambda key: key in DHLCustomsOption,
    )
    return frozenset(key for key, option in parsed.items() if option.state)


def lane_of(request: typing.Any, context: typing.Any) -> typing.Optional[Lane]:
    """The shipment lane when the plugin advises on it, else None.

    The plugin advises only at shipment creation, for PostNord shippers in
    Sweden, Denmark, or Finland and DHL Freight Sweden shippers in Sweden,
    sending from inside to outside the EU VAT area.
    """
    if getattr(context, "operation", None) != "shipping":
        return None

    carrier_name = getattr(context, "carrier_name", None)
    shipper = getattr(request, "shipper", None)
    recipient = getattr(request, "recipient", None)
    shipper_country = (getattr(shipper, "country_code", None) or "").upper()
    recipient_country = (getattr(recipient, "country_code", None) or "").upper()

    in_scope = (
        shipper_country in SHIPPER_COUNTRIES.get(carrier_name, frozenset())
        and territories.in_eu_vat_area(
            shipper_country, getattr(shipper, "postal_code", None)
        )
        and not territories.in_eu_vat_area(
            recipient_country, getattr(recipient, "postal_code", None)
        )
    )

    if not in_scope:
        return None

    customs = getattr(request, "customs", None)
    service = getattr(request, "service", None)

    return Lane(
        carrier_name=carrier_name,
        shipper_country=shipper_country,
        recipient_country=recipient_country,
        to_norway=recipient_country == NORWAY,
        service=service,
        postnord_product_group=(
            postnord_product_group(service) if carrier_name == POSTNORD else None
        ),
        has_customs=customs is not None,
        commercial_invoice=bool(getattr(customs, "commercial_invoice", False)),
        content_type=content_type_of(customs),
        voec_number=(getattr(customs, "options", None) or {}).get("voec_number") or None,
        dhl_customs_options=selected_dhl_customs_options(getattr(request, "options", None)),
        sale_like=sale_like(customs),
        commercial=commercial(customs),
    )
