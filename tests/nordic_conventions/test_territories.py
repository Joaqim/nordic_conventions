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


if __name__ == "__main__":
    unittest.main()
