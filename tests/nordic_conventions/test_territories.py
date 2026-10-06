import importlib
import unittest

import karrio.plugins.nordic_conventions.territories as territories


def _connector_units(carrier_name: str):
    try:
        return importlib.import_module(f"karrio.providers.{carrier_name}.units")
    except ImportError:
        return None


class TestNordicConventionsTerritories(unittest.TestCase):
    def test_greece_is_inside(self):
        self.assertTrue(territories.in_eu_vat_area("GR", "10431"))

    def test_aland_by_country_code_is_outside(self):
        self.assertFalse(territories.in_eu_vat_area("AX", "22100"))

    def test_aland_by_postal_code_is_outside(self):
        self.assertFalse(territories.in_eu_vat_area("FI", "22100"))

    def test_canary_islands_by_postal_code_is_outside(self):
        self.assertFalse(territories.in_eu_vat_area("ES", "35 001"))

    def test_mainland_spain_is_inside(self):
        self.assertTrue(territories.in_eu_vat_area("ES", "28001"))

    def test_non_numeric_postal_code_falls_back_to_country(self):
        self.assertListEqual(
            [
                territories.in_eu_vat_area("FI", "AX-22100"),
                territories.in_eu_vat_area("NO", "N-0150"),
            ],
            [True, False],
        )

    def test_own_country_prefix_is_removed_before_range_checks(self):
        self.assertListEqual(
            [
                territories.in_eu_vat_area(country_code, postal_code)
                for country_code, postal_code in (
                    ("FI", "FI-22100"),
                    ("FI", "fi 22100"),
                    ("FI", "FI22100"),
                    ("FI", " FI - 22100 "),
                    ("DK", "DK-3900"),
                    ("ES", "ES-35001"),
                    ("FI", "FI-00100"),
                )
            ],
            [False, False, False, False, False, False, True],
        )

    def test_letters_that_begin_a_postal_code_are_kept(self):
        self.assertTrue(territories.in_eu_vat_area("MT", "MTF 1234"))

    def test_northern_ireland_with_country_prefix_is_inside(self):
        self.assertListEqual(
            [
                territories.in_eu_vat_area("GB", "GB-BT1 1AA"),
                territories.in_eu_vat_area("GB", "gb bt1 1aa"),
                territories.in_eu_vat_area("GB", "GB-EC1A 1BB"),
            ],
            [True, True, False],
        )

    def test_monaco_is_inside(self):
        self.assertTrue(territories.in_eu_vat_area("MC", "98000"))

    def test_france_with_monaco_postal_code_is_inside(self):
        self.assertTrue(territories.in_eu_vat_area("FR", "98000"))

    def test_northern_ireland_by_postal_prefix_is_inside(self):
        self.assertTrue(territories.in_eu_vat_area("GB", "BT1 1AA"))

    def test_great_britain_is_outside(self):
        self.assertFalse(territories.in_eu_vat_area("GB", "EC1A 1BB"))

    def test_mount_athos_by_postal_code_is_outside(self):
        self.assertListEqual(
            [
                territories.in_eu_vat_area("GR", "630 86"),
                territories.in_eu_vat_area("EL", "630 86"),
                territories.in_eu_vat_area("EL", "10431"),
            ],
            [False, False, True],
        )

    def test_french_pacific_collectivities_by_postal_code_are_outside(self):
        self.assertListEqual(
            [
                territories.in_eu_vat_area("FR", postal_code)
                for postal_code in ("98000", "98599", "98600", "98713", "98800", "98899", "98900")
            ],
            [True, True, False, False, False, False, True],
        )


    def test_french_overseas_departments_by_postal_code_are_outside(self):
        self.assertListEqual(
            [
                territories.in_eu_vat_area("FR", postal_code)
                for postal_code in ("96999", "97000", "97100", "97400", "97600", "97999", "98000")
            ],
            [True, False, False, False, False, False, True],
        )

    def test_faroe_islands_and_greenland_by_danish_postal_code_are_outside(self):
        self.assertListEqual(
            [
                territories.in_eu_vat_area("DK", postal_code)
                for postal_code in ("3799", "3800", "3900", "3999", "4000")
            ],
            [True, False, False, False, True],
        )

    def test_matches_connector_tables(self):
        for carrier_name in ("postnord", "dhl_freight_sweden"):
            with self.subTest(carrier_name=carrier_name):
                units = _connector_units(carrier_name)
                if units is None:
                    self.skipTest(f"{carrier_name} connector is not importable")

                self.assertSetEqual(
                    set(territories.EU_VAT_AREA_COUNTRIES),
                    set(units.EU_VAT_AREA_COUNTRIES),
                )
                self.assertTupleEqual(
                    territories.NON_EU_VAT_POSTAL_RANGES,
                    units.NON_EU_VAT_POSTAL_RANGES,
                )
                self.assertTupleEqual(
                    territories.EU_VAT_POSTAL_PREFIXES,
                    units.EU_VAT_POSTAL_PREFIXES,
                )


if __name__ == "__main__":
    unittest.main()
