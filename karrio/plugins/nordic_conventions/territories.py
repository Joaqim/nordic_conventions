"""EU VAT area membership for goods movements, following Tullverket.

The table matches the definition applied by the PostNord and DHL Freight
Sweden connectors: member states are inside, with Greece under its ISO code
``GR`` as well as its VAT prefix ``EL``, and Monaco (``MC``) treated as EU;
special fiscal territories are outside either by their own country code
(``AX``, ``IC``, ``GP``, ``GF``, ``MQ``, ``RE``, ``YT``), which is absent
from the member-state set, or by postal-code range within a member state,
with Mount Athos excluded by ``GR`` and ``EL`` 63086, the French overseas
departments by ``FR`` 97000-97999, Wallis and Futuna, French Polynesia, and
New Caledonia by ``FR`` 98600-98899, and the Faroe Islands and Greenland by
``DK`` 3800-3999, while Monaco's ``FR`` 980xx codes stay inside. Northern
Ireland is inside the EU VAT area for goods and outside it for services;
the plugin advises on goods shipments, so ``GB`` postal codes beginning
``BT`` are inside.
"""

import re
import typing

EU_VAT_AREA_COUNTRIES: typing.FrozenSet[str] = frozenset(
    {
        "AT",
        "BE",
        "BG",
        "HR",
        "CY",
        "CZ",
        "DK",
        "EE",
        "FI",
        "FR",
        "DE",
        "EL",
        "GR",
        "HU",
        "IE",
        "IT",
        "LV",
        "LT",
        "LU",
        "MC",
        "MT",
        "NL",
        "PL",
        "PT",
        "RO",
        "SI",
        "SK",
        "ES",
        "SE",
    }
)

NON_EU_VAT_POSTAL_RANGES: typing.Tuple[typing.Tuple[str, int, int], ...] = (
    ("FI", 22000, 22999),  # Åland
    ("ES", 35000, 35999),  # Canary Islands (Las Palmas)
    ("ES", 38000, 38999),  # Canary Islands (Santa Cruz de Tenerife)
    ("ES", 51000, 51999),  # Ceuta
    ("ES", 52000, 52999),  # Melilla
    ("DE", 78266, 78266),  # Büsingen
    ("DE", 27498, 27498),  # Heligoland
    ("GR", 63086, 63086),  # Mount Athos
    ("IT", 23041, 23041),  # Livigno
    ("IT", 22061, 22061),  # Campione d'Italia
    ("FR", 97000, 97999),  # French overseas departments
    ("DK", 3800, 3999),  # Faroe Islands and Greenland
    ("FR", 98600, 98899),  # Wallis and Futuna, French Polynesia, New Caledonia
    ("EL", 63086, 63086),  # Mount Athos
)

NUMERIC_POSTAL_TERRITORY_PARENTS: typing.Dict[str, str] = {
    "AX": "FI",  # Åland
    "FO": "DK",  # Faroe Islands
    "GL": "DK",  # Greenland
    "IC": "ES",  # Canary Islands
    "EA": "ES",  # Ceuta and Melilla
}

UK_POSTCODE_AREA_CODES: typing.FrozenSet[str] = frozenset({"JE", "GY", "IM", "BT"})

EU_VAT_POSTAL_PREFIXES: typing.Tuple[typing.Tuple[str, str], ...] = (
    ("GB", "BT"),  # Northern Ireland
)


def in_eu_vat_area(
    country_code: typing.Optional[str],
    postal_code: typing.Optional[str],
) -> bool:
    """Whether an address lies inside the EU VAT area for goods.

    A postal code is upper-cased and trimmed, loses a leading prefix code
    (see ``postal_prefix_codes``) followed by a hyphen, whitespace, or a
    digit, and loses its spaces; the exclusion ranges apply only when the
    code is then purely numeric, the inclusion prefixes in any case, and a
    code matching neither leaves the country-level decision standing.
    """
    country = (country_code or "").upper()
    postal = _postal_code(country, postal_code)
    postal_number = int(postal) if postal.isdigit() else None

    inside_member_state = country in EU_VAT_AREA_COUNTRIES and not any(
        country == range_country
        and postal_number is not None
        and low <= postal_number <= high
        for range_country, low, high in NON_EU_VAT_POSTAL_RANGES
    )
    return inside_member_state or any(
        country == prefix_country and postal.startswith(prefix)
        for prefix_country, prefix in EU_VAT_POSTAL_PREFIXES
    )


def postal_prefix_codes(country_code: str) -> typing.Tuple[str, ...]:
    """Codes that may lead a postal code of ``country_code`` and are removed.

    These are the country's own code and the codes of its territories with
    numeric postal codes. ``JE``, ``GY``, ``IM``, and ``BT`` are never
    removed, because they begin United Kingdom postcodes.
    """
    territories = (
        territory
        for territory, parent in NUMERIC_POSTAL_TERRITORY_PARENTS.items()
        if parent == country_code
    )
    return tuple(
        code for code in (country_code, *territories) if code and code not in UK_POSTCODE_AREA_CODES
    )


def _postal_code(country: str, postal_code: typing.Optional[str]) -> str:
    postal = str(postal_code or "").strip().upper()
    for code in postal_prefix_codes(country):
        separator = r"[\s-]+" if code == "GB" else r"[\s-]+|(?=\d)"
        prefix = re.match(rf"{re.escape(code)}(?:{separator})", postal)
        if prefix:
            postal = postal[prefix.end():]
            break
    return postal.replace(" ", "")
