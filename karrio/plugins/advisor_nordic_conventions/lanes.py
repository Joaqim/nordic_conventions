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
