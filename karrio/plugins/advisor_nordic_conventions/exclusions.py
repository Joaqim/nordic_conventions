"""Postal codes the DHL Freight Sweden connector excludes per product.

A copy of the connector's ``POSTAL_CODE_FORMATS``, ``POSTAL_CODE_EXCLUSIONS``,
and ``POSTAL_CODE_PATTERN_EXCLUSIONS`` (karrio-dhl-freight-sweden 142b62d,
units.py), with the same fields and product codes as strings, so a test
compares them with the connector when it is importable. The numeric ranges
are the "Excluded regions/areas" of product manual v5.26; the patterns are
the manual's areas without ranges and, for 202, 233, and 601, the Product API
catalog's ``postalCodeExcludes``.
"""

import fnmatch
import re
import typing

import karrio.plugins.advisor_nordic_conventions.territories as territories


class PostalCodeFormat(typing.NamedTuple):
    """A country's postal-code shape: ``pattern`` matches the whole code and its ``key`` group the compared digits."""

    pattern: str
    key_digits: int
    description: str


FOUR_DIGITS = PostalCodeFormat(r"(?P<key>\d{4})", 4, "4-digit")
FIVE_DIGITS = PostalCodeFormat(r"(?P<key>\d{5})", 5, "5-digit")
PORTUGUESE = PostalCodeFormat(r"(?P<key>\d{4})(-?\d{3})?", 4, "NNNN-NNN")
POSTAL_CODE_FORMATS: typing.Dict[str, PostalCodeFormat] = {
    "DK": FOUR_DIGITS,
    "ES": FIVE_DIGITS,
    "FR": FIVE_DIGITS,
    "IT": FIVE_DIGITS,
    "NO": FOUR_DIGITS,
    "PT": PORTUGUESE,
    "UA": FIVE_DIGITS,
}


def postal_code_key(country_code: str, postal_code: typing.Optional[str]) -> typing.Optional[int]:
    """The compared digits of a postal code, or None when it is malformed or missing."""
    postal_format = POSTAL_CODE_FORMATS.get(country_code)
    match = (
        re.fullmatch(postal_format.pattern, territories.normalized_postal_code(country_code, postal_code))
        if postal_format
        else None
    )
    return int(match.group("key")) if match else None


class PostalCodeExclusion(typing.NamedTuple):
    """A postal-code range of a country a product does not serve."""

    product: str
    country: str
    low: int
    high: int
    region: str
    parties: typing.Tuple[str, ...] = ("recipient",)
    danish_territories: bool = False

    def excluded_codes(self) -> str:
        width = POSTAL_CODE_FORMATS[self.country].key_digits
        low, high = f"{self.low:0{width}d}", f"{self.high:0{width}d}"
        return f"{self.country} postal codes {low if low == high else f'{low}-{high}'} ({self.region})"

    def excludes(self, postal_code: typing.Optional[str]) -> bool:
        if self.danish_territories and territories.outside_by_postal_territory(self.country, postal_code):
            return True
        key = postal_code_key(self.country, postal_code)
        return key is not None and self.low <= key <= self.high


class PostalCodePatternExclusion(typing.NamedTuple):
    """Postal codes of a country a product does not serve, as wildcard patterns matched against the whole normalised code."""

    product: str
    country: str
    patterns: typing.Tuple[str, ...]
    region: str
    parties: typing.Tuple[str, ...] = ("recipient",)

    def excluded_codes(self) -> str:
        if self.patterns == ("*",):
            return f"{self.country} ({self.region})"
        return f"{self.country} postal codes {', '.join(self.patterns)} ({self.region})"

    def excludes(self, postal_code: typing.Optional[str]) -> bool:
        code = territories.normalized_postal_code(self.country, postal_code)
        return any(fnmatch.fnmatchcase(code, pattern) for pattern in self.patterns)


Exclusion = typing.Union[PostalCodeExclusion, PostalCodePatternExclusion]


def _excluded(
    products: typing.Iterable[str],
    country: str,
    region: str,
    *ranges: typing.Union[int, typing.Tuple[int, int]],
    parties: typing.Tuple[str, ...] = ("recipient",),
    danish_territories: bool = False,
) -> typing.Tuple[PostalCodeExclusion, ...]:
    return tuple(
        PostalCodeExclusion(product, country, low, high, region, parties, danish_territories)
        for product in products
        for low, high in (code if isinstance(code, tuple) else (code, code) for code in ranges)
    )


def _patterns(
    products: typing.Iterable[str],
    country: str,
    region: str,
    patterns: str,
    parties: typing.Tuple[str, ...] = ("recipient",),
) -> typing.Tuple[PostalCodePatternExclusion, ...]:
    return tuple(
        PostalCodePatternExclusion(
            product,
            country,
            tuple(pattern.strip().upper() for pattern in patterns.split(",") if pattern.strip()),
            region,
            parties,
        )
        for product in products
    )


PARCEL_CONNECT_PLUS = ("112",)
PARCEL_CONNECT = ("109",)
PARCEL_RETURN_CONNECT = ("107",)
SHIPPER = ("shipper",)
BOTH_PARTIES = ("shipper", "recipient")
CRIMEA_PRODUCTS = ("202", "205", "SPI")

POSTAL_CODE_EXCLUSIONS: typing.Tuple[PostalCodeExclusion, ...] = (
    # 112, §5.3 p18
    *_excluded(PARCEL_CONNECT_PLUS, "DK", "Greenland and the Faroe Islands", (3800, 3999), danish_territories=True),
    *_excluded(PARCEL_CONNECT_PLUS, "ES", "Canary Islands", (35000, 35999), (38000, 38999)),
    *_excluded(PARCEL_CONNECT_PLUS, "ES", "Ceuta and Melilla", 51080, 52080),
    *_excluded(PARCEL_CONNECT_PLUS, "FR", "outside mainland France and Corsica", (97100, 99999)),
    *_excluded(
        PARCEL_CONNECT_PLUS,
        "IT",
        "Campione d'Italia, Livigno, Trepalle, San Marino, Ventotene, Ponza, "
        "Serle, Isola Bella, and Giglio",
        22061, 23041, 23030, (47890, 47899), 4020, 4027, 25080, 28838, 58012,
    ),
    *_excluded(PARCEL_CONNECT_PLUS, "NO", "Jan Mayen and Svalbard", 8099, (9170, 9179)),
    *_excluded(PARCEL_CONNECT_PLUS, "PT", "the Azores, Madeira, and other islands", (9000, 9999)),
    # 109, §5.14 p63
    *_excluded(PARCEL_CONNECT, "DK", "Greenland and the Faroe Islands", (3800, 3999), danish_territories=True),
    *_excluded(PARCEL_CONNECT, "ES", "Canary Islands", (35000, 35999), (38000, 38999)),
    *_excluded(PARCEL_CONNECT, "ES", "Ceuta and Melilla", 51080, 52080),
    *_excluded(PARCEL_CONNECT, "FR", "outside mainland France and Corsica", (97100, 99999)),
    *_excluded(
        PARCEL_CONNECT,
        "IT",
        "Vatican, Campione d'Italia, Livigno-Trepalle, and San Marino",
        120, 22061, 23041, (47890, 47899),
    ),
    *_excluded(PARCEL_CONNECT, "NO", "Jan Mayen and Svalbard", 8099, (9170, 9179)),
    *_excluded(PARCEL_CONNECT, "PT", "the Azores, Madeira, and other islands", (9000, 9999)),
    # 107, §5.15 p66
    *_excluded(
        PARCEL_RETURN_CONNECT, "DK", "Greenland and the Faroe Islands", (3800, 3999),
        parties=SHIPPER, danish_territories=True,
    ),
    *_excluded(PARCEL_RETURN_CONNECT, "ES", "Canary Islands", (35000, 35999), (38000, 38999), parties=SHIPPER),
    *_excluded(PARCEL_RETURN_CONNECT, "ES", "Ceuta and Melilla", 51080, 52080, parties=SHIPPER),
    *_excluded(
        PARCEL_RETURN_CONNECT,
        "IT",
        "Vatican, Campione d'Italia, Livigno-Trepalle, and San Marino",
        120, 22061, 23041, (47890, 47899),
        parties=SHIPPER,
    ),
    *_excluded(PARCEL_RETURN_CONNECT, "NO", "Jan Mayen and Svalbard", 8099, (9170, 9179), parties=SHIPPER),
    *_excluded(PARCEL_RETURN_CONNECT, "PT", "the Azores, Madeira, and other islands", (9000, 9999), parties=SHIPPER),
    # 202 §5.4 p23, 205 §5.9 p43, SPI §5.11 p52
    *_excluded(CRIMEA_PRODUCTS, "UA", "Crimea/Sebastopol region", (95000, 99999), parties=BOTH_PARTIES),
)

PARCEL_CONNECT_PRODUCTS = (*PARCEL_CONNECT_PLUS, *PARCEL_CONNECT)
NL_CARIBBEAN = "Aruba, Bonaire, Curaçao, Saba, Sint Maarten, and Sint Eustatius"
NL_CARIBBEAN_CODES = ("AW", "BQ", "CW", "SX")
CATALOG = "Product API catalog postalCodeExcludes"
ROAD_FREIGHT_STANDARD = ("202",)
ROAD_FREIGHT_PRIORITY = ("233",)
HOME_DELIVERY_INTERNATIONAL = ("601",)

POSTAL_CODE_PATTERN_EXCLUSIONS: typing.Tuple[PostalCodePatternExclusion, ...] = (
    *_patterns(PARCEL_CONNECT_PRODUCTS, "GB", "Jersey, Guernsey, and Northern Ireland", "JE*,GY*,BT*"),
    *(
        exclusion
        for country in NL_CARIBBEAN_CODES
        for exclusion in (
            *_patterns(PARCEL_CONNECT_PRODUCTS, country, NL_CARIBBEAN, "*"),
            *_patterns(PARCEL_RETURN_CONNECT, country, NL_CARIBBEAN, "*", parties=SHIPPER),
        )
    ),
    *_patterns(ROAD_FREIGHT_STANDARD, "DK", CATALOG, "39*, ???,2412"),
    *_patterns(ROAD_FREIGHT_STANDARD, "ES", CATALOG, "35*,38*,51*,52*"),
    *_patterns(ROAD_FREIGHT_STANDARD, "FR", CATALOG, "97*"),
    *_patterns(ROAD_FREIGHT_STANDARD, "GB", CATALOG, "GY*,JE*"),
    *_patterns(ROAD_FREIGHT_STANDARD, "NO", CATALOG, "917*,8099"),
    *_patterns(ROAD_FREIGHT_STANDARD, "PT", CATALOG, "9*"),
    *_patterns(ROAD_FREIGHT_PRIORITY, "DK", CATALOG, "39*, ???,2412"),
    *_patterns(ROAD_FREIGHT_PRIORITY, "ES", CATALOG, "35*,38*,51*,52*"),
    *_patterns(ROAD_FREIGHT_PRIORITY, "NO", CATALOG, "917*,8099"),
    *_patterns(ROAD_FREIGHT_PRIORITY, "PT", CATALOG, "9*"),
    *_patterns(HOME_DELIVERY_INTERNATIONAL, "DK", CATALOG, "39*,???,2412"),
    *_patterns(HOME_DELIVERY_INTERNATIONAL, "ES", CATALOG, "35*,38*,51*,52*"),
    *_patterns(HOME_DELIVERY_INTERNATIONAL, "FR", CATALOG, "97*"),
    *_patterns(HOME_DELIVERY_INTERNATIONAL, "GB", CATALOG, "GY*,JE*"),
    *_patterns(HOME_DELIVERY_INTERNATIONAL, "NO", CATALOG, "917*,8099"),
    *_patterns(HOME_DELIVERY_INTERNATIONAL, "PT", CATALOG, "9*"),
)


class ExcludedParty(typing.NamedTuple):
    exclusion: Exclusion
    party: str


def excluded_party(
    product_code: str,
    addresses: typing.Mapping[str, typing.Tuple[str, typing.Optional[str]]],
) -> typing.Optional[ExcludedParty]:
    """The first party whose postal code an exclusion bars the product from, if any.

    ``addresses`` maps party names to country code and postal code pairs, the
    country codes already mapped to their parent. Unlike the connector, a
    missing or malformed postal code is excluded only by the pattern ``*``.
    """
    return next(
        (
            ExcludedParty(exclusion, party)
            for exclusion in (*POSTAL_CODE_EXCLUSIONS, *POSTAL_CODE_PATTERN_EXCLUSIONS)
            if exclusion.product == product_code
            for party in exclusion.parties
            for country, postal_code in [addresses.get(party, ("", None))]
            if country.upper() == exclusion.country and exclusion.excludes(postal_code)
        ),
        None,
    )
