"""EU VAT area membership, mirroring the PostNord and DHL Freight Sweden connectors.

The table follows Tullverket's list of EU customs and fiscal territories as
applied by both connectors: member states are inside, with Greece under its
ISO code ``GR`` as well as its VAT prefix ``EL``; special fiscal territories
are outside either by their own country code (``AX``, ``IC``, ``GP``, ``GF``,
``MQ``, ``RE``, ``YT``), which is absent from the member-state set, or by
postal-code range within a member state.
"""

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
    ("IT", 23041, 23041),  # Livigno
    ("IT", 22061, 22061),  # Campione d'Italia
)


def in_eu_vat_area(
    country_code: typing.Optional[str],
    postal_code: typing.Optional[str],
) -> bool:
    """Whether an address lies inside the EU VAT area.

    A postal code is compared after removing spaces and only when it is
    purely numeric; otherwise the country-level decision stands.
    """
    country = (country_code or "").upper()
    postal = str(postal_code or "").replace(" ", "")
    postal_number = int(postal) if postal.isdigit() else None

    return country in EU_VAT_AREA_COUNTRIES and not any(
        country == range_country
        and postal_number is not None
        and low <= postal_number <= high
        for range_country, low, high in NON_EU_VAT_POSTAL_RANGES
    )
