import unittest

import karrio.lib as lib

import karrio.plugins.advisor_nordic_conventions.rules.customs_values as customs_values
import karrio.plugins.advisor_nordic_conventions.rules.dhl_freight_sweden as dhl_freight_sweden
import karrio.plugins.advisor_nordic_conventions.sources as sources
from . import fixture

PAID = dict(
    description="Whey 1 kg",
    quantity=2,
    weight=1.0,
    weight_unit="KG",
    value_amount=100.0,
    value_currency="SEK",
    origin_country="SE",
    hs_code="21069098",
)
FREE = dict(
    description="Shaker 700 ml (free with purchase, 100% discount)",
    quantity=1,
    weight=0.15,
    weight_unit="KG",
    value_amount=49.0,
    value_currency="SEK",
    origin_country="CN",
    hs_code="39249000",
    metadata=dict(discount_percentage=100),
)
ZERO = dict(
    description="Shaker 700 ml",
    quantity=1,
    weight=0.15,
    weight_unit="KG",
    value_amount=0.0,
    value_currency="SEK",
    origin_country="CN",
    hs_code="39249000",
)
UNVALUED = dict(
    description="Shaker 700 ml",
    quantity=1,
    weight=0.15,
    weight_unit="KG",
    value_currency="SEK",
    origin_country="CN",
    hs_code="39249000",
)

CH_DISCOUNT_TEXT = (
    "Switzerland does not tax a discount, or an item handed over with a sold item as a discount in kind or add-on, "
    "as part of the import consideration, provided the item is directly connected to the sale; "
    "show the discount on the commercial invoice and tie the discounted or free item to that sale."
)
CH_DISCOUNT_UNCONFIRMED = (
    "R-69-03 does not address an add-on shipped in a separate parcel from the sale it belongs to."
)
ZERO_VALUE_TEXT = (
    "A commodity line declares a customs value of 0 or none. "
    "A commercial or pro forma invoice may never carry a value of 0, even for gifts or samples; "
    "declare each line's customs value."
)
SWITZERLAND_ALTERNATIVES = (
    "Book Switzerland on a product that serves it, such as Home Delivery International B2C (601), "
    "Road Freight Standard (202), Road Freight Direct (205), or Road Freight Priority (233)."
)
RETURN_TO_SWEDEN = "Parcel Return Connect (107) only returns a parcel from abroad to its original sender in Sweden."
CH_NOT_SERVED_TEXT = {
    "109": f"DHL Freight Sweden Parcel Connect (109) does not ship from SE to CH. {SWITZERLAND_ALTERNATIVES}",
    "112": f"DHL Freight Sweden Parcel Connect Plus (112) does not ship from SE to CH. {SWITZERLAND_ALTERNATIVES}",
    "107": (
        f"DHL Freight Sweden Parcel Return Connect (107) does not ship from SE to CH. "
        f"{RETURN_TO_SWEDEN} {SWITZERLAND_ALTERNATIVES}"
    ),
}
GB_NOT_SERVED_TEXT = f"DHL Freight Sweden Parcel Return Connect (107) does not ship from SE to GB. {RETURN_TO_SWEDEN}"
GB_AGREEMENT_TEXT = (
    "DHL Freight Sweden serves Great Britain on Parcel Connect (109) and Parcel Connect Plus (112) "
    "only by separate agreement with DHL; book Great Britain on them only under such an agreement."
)


def _customs(*commodities) -> dict:
    return lib.to_dict(
        dict(commodities=list(commodities), content_type="merchandise", commercial_invoice=True)
    )


def _advise(advisor, carrier, recipient, service, *commodities) -> list:
    request = fixture.shipment("SE", recipient, service, customs=_customs(*commodities))
    return fixture.messages(advisor, request, fixture.context(carrier))


class TestNordicConventionsSwitzerlandDiscount(unittest.TestCase):
    def test_free_line_in_a_sale_to_switzerland(self):
        self.assertListEqual(
            _advise(customs_values.ch_discount_on_invoice, "postnord", "CH", "postnord_parcel", PAID, FREE),
            [
                dict(
                    code="advisor_nordic_conventions_ch_discount_on_invoice",
                    level="info",
                    message=CH_DISCOUNT_TEXT,
                    details=dict(
                        plugin="advisor_nordic_conventions",
                        lane="SE-CH",
                        sources=[sources.BAZG_RABATTE.to_dict()],
                        lines=[1],
                        unconfirmed=CH_DISCOUNT_UNCONFIRMED,
                    ),
                )
            ],
        )

    def test_zero_valued_line_to_switzerland_on_dhl(self):
        messages = _advise(
            customs_values.ch_discount_on_invoice,
            "dhl_freight_sweden",
            "CH",
            "dhl_freight_sweden_home_delivery_international_b2c",
            ZERO,
            PAID,
        )
        self.assertListEqual([message["details"]["lines"] for message in messages], [[0]])

    def test_discounted_line_to_norway_is_not_advised(self):
        self.assertListEqual(
            _advise(customs_values.ch_discount_on_invoice, "postnord", "NO", "postnord_parcel", PAID, FREE),
            [],
        )

    def test_fully_valued_lines_are_not_advised(self):
        self.assertListEqual(
            _advise(customs_values.ch_discount_on_invoice, "postnord", "CH", "postnord_parcel", PAID),
            [],
        )


class TestNordicConventionsZeroValueLine(unittest.TestCase):
    def test_zero_valued_line_to_norway(self):
        self.assertListEqual(
            _advise(customs_values.zero_value_line, "postnord", "NO", "postnord_parcel", PAID, ZERO),
            [
                dict(
                    code="advisor_nordic_conventions_zero_value_line",
                    level="warning",
                    message=ZERO_VALUE_TEXT,
                    details=dict(
                        plugin="advisor_nordic_conventions",
                        lane="SE-NO",
                        sources=[
                            sources.PN_SE_NO_PAGE_NON_ZERO_VALUE.to_dict(),
                            sources.TV_PROFORMA_NON_ZERO_VALUE.to_dict(),
                            sources.DHL_EXPRESS_NO_ZERO_VALUES.to_dict(),
                        ],
                        lines=[1],
                    ),
                )
            ],
        )

    def test_line_without_a_value(self):
        self.assertListEqual(
            [
                message["code"]
                for message in _advise(
                    customs_values.zero_value_line,
                    "dhl_freight_sweden",
                    "GB",
                    "dhl_freight_sweden_home_delivery_international_b2c",
                    UNVALUED,
                )
            ],
            ["advisor_nordic_conventions_zero_value_line"],
        )

    def test_inside_the_eu_vat_area(self):
        self.assertListEqual(
            _advise(customs_values.zero_value_line, "postnord", "DE", "postnord_parcel", ZERO),
            [],
        )

    def test_all_lines_valued(self):
        self.assertListEqual(
            _advise(customs_values.zero_value_line, "postnord", "NO", "postnord_parcel", PAID, FREE),
            [],
        )


class TestNordicConventionsParcelConnectDestinations(unittest.TestCase):
    def _expected(self, code, text, lane, cited=(sources.DHL_MAN_PRODUCT_LANES,)):
        return [
            dict(
                code=code,
                level="warning",
                message=text,
                details=dict(
                    plugin="advisor_nordic_conventions",
                    lane=lane,
                    sources=[source.to_dict() for source in cited],
                ),
            )
        ]

    def test_parcel_connect_family_to_switzerland_is_not_served(self):
        for service, code in (
            ("dhl_freight_sweden_parcel_connect_b2c", "109"),
            ("109", "109"),
            ("dhl_freight_sweden_parcel_connect_plus", "112"),
            ("112", "112"),
            ("dhl_freight_sweden_parcel_return_connect_c2b", "107"),
            ("107", "107"),
        ):
            with self.subTest(service=service):
                self.assertListEqual(
                    _advise(dhl_freight_sweden.parcel_connect_not_served, "dhl_freight_sweden", "CH", service, PAID),
                    self._expected(
                        "advisor_nordic_conventions_dhl_freight_sweden_parcel_connect_not_served",
                        CH_NOT_SERVED_TEXT[code],
                        "SE-CH",
                    ),
                )

    def test_parcel_return_connect_to_great_britain_is_not_served(self):
        for service in ("dhl_freight_sweden_parcel_return_connect_c2b", "107"):
            with self.subTest(service=service):
                self.assertListEqual(
                    _advise(dhl_freight_sweden.parcel_connect_not_served, "dhl_freight_sweden", "GB", service, PAID),
                    self._expected(
                        "advisor_nordic_conventions_dhl_freight_sweden_parcel_connect_not_served", GB_NOT_SERVED_TEXT, "SE-GB"
                    ),
                )

    def test_parcel_return_connect_from_sweden_is_never_served(self):
        for recipient in ("NO", "US", "LI"):
            with self.subTest(recipient=recipient):
                self.assertListEqual(
                    _advise(dhl_freight_sweden.parcel_connect_not_served, "dhl_freight_sweden", recipient, "107", PAID),
                    self._expected(
                        "advisor_nordic_conventions_dhl_freight_sweden_parcel_connect_not_served",
                        f"DHL Freight Sweden Parcel Return Connect (107) does not ship from SE to {recipient}. {RETURN_TO_SWEDEN}",
                        f"SE-{recipient}",
                    ),
                )

    def test_products_to_countries_outside_their_lists_are_not_served(self):
        for service, recipient, text in (
            ("dhl_freight_sweden_paket", "NO", "DHL Freight Sweden Paket (102) does not ship from SE to NO."),
            ("118", "GB", "DHL Freight Sweden Hemleverans Paket (118) does not ship from SE to GB."),
            ("109", "US", "DHL Freight Sweden Parcel Connect (109) does not ship from SE to US."),
            ("233", "UA", "DHL Freight Sweden Road Freight Priority (233) does not ship from SE to UA."),
            (
                "dhl_freight_sweden_road_freight_standard",
                "US",
                "DHL Freight Sweden Road Freight Standard (202) does not ship from SE to US.",
            ),
            ("601", "LI", "DHL Freight Sweden Home Delivery International B2C (601) does not ship from SE to LI."),
            ("SPI", "IS", "DHL Freight Sweden Standard Pallet International (SPI) does not ship from SE to IS."),
        ):
            with self.subTest(service=service, recipient=recipient):
                self.assertListEqual(
                    _advise(dhl_freight_sweden.parcel_connect_not_served, "dhl_freight_sweden", recipient, service, PAID),
                    self._expected(
                        "advisor_nordic_conventions_dhl_freight_sweden_parcel_connect_not_served",
                        text,
                        f"SE-{recipient}",
                    ),
                )

    def test_products_on_their_lanes_are_served(self):
        for service, recipient in (
            ("202", "LI"),
            ("205", "CH"),
            ("SPI", "UA"),
            ("233", "LI"),
            ("601", "NO"),
            ("dhl_freight_sweden_parcel_connect_plus", "NO"),
        ):
            with self.subTest(service=service, recipient=recipient):
                self.assertListEqual(
                    _advise(dhl_freight_sweden.parcel_connect_not_served, "dhl_freight_sweden", recipient, service, PAID),
                    [],
                )

    def test_unknown_service_is_not_advised(self):
        for service in ("dhl_freight_sweden_unknown", "999"):
            with self.subTest(service=service):
                self.assertListEqual(
                    _advise(dhl_freight_sweden.parcel_connect_not_served, "dhl_freight_sweden", "NO", service, PAID),
                    [],
                )

    def test_parcel_connect_to_great_britain_needs_a_separate_agreement(self):
        for service in (
            "dhl_freight_sweden_parcel_connect_b2c",
            "109",
            "dhl_freight_sweden_parcel_connect_plus",
            "112",
        ):
            with self.subTest(service=service):
                self.assertListEqual(
                    _advise(dhl_freight_sweden.parcel_connect_gb_agreement, "dhl_freight_sweden", "GB", service, PAID),
                    self._expected(
                        "advisor_nordic_conventions_dhl_freight_sweden_parcel_connect_gb_agreement",
                        GB_AGREEMENT_TEXT,
                        "SE-GB",
                        (sources.DHL_MAN_PARCEL_CONNECT_COUNTRIES, sources.DHL_CONNECTOR_SANDBOX_112_GB_REJECTED),
                    ),
                )

    def test_each_destination_gets_only_its_own_reason(self):
        for advisor, recipient, service in (
            (dhl_freight_sweden.parcel_connect_not_served, "GB", "109"),
            (dhl_freight_sweden.parcel_connect_not_served, "GB", "112"),
            (dhl_freight_sweden.parcel_connect_gb_agreement, "GB", "107"),
            (dhl_freight_sweden.parcel_connect_gb_agreement, "CH", "109"),
        ):
            with self.subTest(advisor=advisor.__name__, recipient=recipient, service=service):
                self.assertListEqual(_advise(advisor, "dhl_freight_sweden", recipient, service, PAID), [])

    def test_home_delivery_international_to_switzerland_and_great_britain(self):
        for advisor in (dhl_freight_sweden.parcel_connect_not_served, dhl_freight_sweden.parcel_connect_gb_agreement):
            for recipient in ("CH", "GB"):
                with self.subTest(advisor=advisor.__name__, recipient=recipient):
                    self.assertListEqual(
                        _advise(
                            advisor,
                            "dhl_freight_sweden",
                            recipient,
                            "dhl_freight_sweden_home_delivery_international_b2c",
                            PAID,
                        ),
                        [],
                    )

    def test_parcel_connect_to_norway(self):
        for advisor in (dhl_freight_sweden.parcel_connect_not_served, dhl_freight_sweden.parcel_connect_gb_agreement):
            with self.subTest(advisor=advisor.__name__):
                self.assertListEqual(
                    _advise(advisor, "dhl_freight_sweden", "NO", "dhl_freight_sweden_parcel_connect_b2c", PAID),
                    [],
                )

    def test_territory_codes_served_under_their_parent_country_are_not_warned(self):
        for recipient, service in (("AX_CODE", "109"), ("AX_CODE", "dhl_freight_sweden_parcel_connect_plus"), ("JE", "233")):
            with self.subTest(recipient=recipient, service=service):
                self.assertListEqual(
                    _advise(dhl_freight_sweden.parcel_connect_not_served, "dhl_freight_sweden", recipient, service, PAID),
                    [],
                )

    def test_parcel_return_connect_to_jersey_reads_as_great_britain(self):
        self.assertListEqual(
            _advise(dhl_freight_sweden.parcel_connect_not_served, "dhl_freight_sweden", "JE", "107", PAID),
            self._expected(
                "advisor_nordic_conventions_dhl_freight_sweden_parcel_connect_not_served", GB_NOT_SERVED_TEXT, "SE-GB"
            ),
        )

    def test_parcel_connect_to_jersey_needs_the_great_britain_agreement(self):
        self.assertListEqual(
            _advise(
                dhl_freight_sweden.parcel_connect_gb_agreement,
                "dhl_freight_sweden",
                "JE",
                "dhl_freight_sweden_parcel_connect_plus",
                PAID,
            ),
            self._expected(
                "advisor_nordic_conventions_dhl_freight_sweden_parcel_connect_gb_agreement",
                GB_AGREEMENT_TEXT,
                "SE-GB",
                (sources.DHL_MAN_PARCEL_CONNECT_COUNTRIES, sources.DHL_CONNECTOR_SANDBOX_112_GB_REJECTED),
            ),
        )

    def test_postnord_is_not_advised(self):
        for advisor, recipient in (
            (dhl_freight_sweden.parcel_connect_not_served, "CH"),
            (dhl_freight_sweden.parcel_connect_gb_agreement, "GB"),
        ):
            with self.subTest(advisor=advisor.__name__):
                self.assertListEqual(_advise(advisor, "postnord", recipient, "109", PAID), [])


if __name__ == "__main__":
    unittest.main()
