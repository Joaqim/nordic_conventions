import importlib
import unittest

import karrio.plugins.advisor_nordic_conventions.exclusions as exclusions


def _connector_units():
    try:
        return importlib.import_module("karrio.providers.dhl_freight_sweden.units")
    except ImportError:
        return None


def _excluded(product, country, postal_code, party="recipient"):
    found = exclusions.excluded_party(product, {party: (country, postal_code)})
    return None if found is None else (found.party, found.exclusion.excluded_codes())


class TestNordicConventionsDHLPostalCodeExclusions(unittest.TestCase):
    def test_numeric_ranges_compare_in_the_country_format(self):
        cases = [
            ("109", "ES", "35001", ("recipient", "ES postal codes 35000-35999 (Canary Islands)")),
            ("109", "ES", "ES-38100", ("recipient", "ES postal codes 38000-38999 (Canary Islands)")),
            ("109", "ES", "28001", None),
            ("112", "IT", "04020", ("recipient", "IT postal codes 04020 (Campione d'Italia, Livigno, Trepalle, San Marino, Ventotene, Ponza, Serle, Isola Bella, and Giglio)")),
            ("109", "NO", "9171", ("recipient", "NO postal codes 9170-9179 (Jan Mayen and Svalbard)")),
            ("109", "PT", "9000-123", ("recipient", "PT postal codes 9000-9999 (the Azores, Madeira, and other islands)")),
            ("109", "PT", "1000-123", None),
            ("202", "UA", "95000", ("recipient", "UA postal codes 95000-99999 (Crimea/Sebastopol region)")),
        ]
        for product, country, postal_code, expected in cases:
            with self.subTest(product=product, country=country, postal_code=postal_code):
                self.assertEqual(_excluded(product, country, postal_code), expected)

    def test_danish_territories_are_excluded_by_prefix_or_faroese_format(self):
        for postal_code in ("3900", "FO-100", "100", "GL 3900"):
            with self.subTest(postal_code=postal_code):
                self.assertIsNotNone(_excluded("112", "DK", postal_code))
        self.assertIsNone(_excluded("112", "DK", "2100"))

    def test_patterns_match_the_whole_normalised_code(self):
        cases = [
            ("112", "GB", "JE2 3AB", True),
            ("109", "GB", "GY1 1AA", True),
            ("109", "GB", "SW1A 1AA", False),
            ("202", "GB", "JE2 3AB", True),
            ("233", "GB", "JE2 3AB", False),
            ("601", "DK", "100", True),
            ("109", "CW", "", True),
        ]
        for product, country, postal_code, excluded in cases:
            with self.subTest(product=product, country=country, postal_code=postal_code):
                self.assertEqual(_excluded(product, country, postal_code) is not None, excluded)

    def test_malformed_or_missing_codes_are_not_advised(self):
        for postal_code in (None, "", "ABC"):
            with self.subTest(postal_code=postal_code):
                self.assertIsNone(_excluded("109", "ES", postal_code))

    def test_parties_follow_the_exclusion(self):
        self.assertIsNone(_excluded("107", "ES", "35001"))
        self.assertEqual(_excluded("107", "ES", "35001", party="shipper")[0], "shipper")
        self.assertEqual(_excluded("202", "UA", "95000", party="shipper")[0], "shipper")

    def test_exclusions_match_connector(self):
        units = _connector_units()
        if units is None:
            self.skipTest("dhl_freight_sweden connector is not importable")

        self.assertDictEqual(
            {country: tuple(postal_format) for country, postal_format in exclusions.POSTAL_CODE_FORMATS.items()},
            {country: tuple(postal_format) for country, postal_format in units.POSTAL_CODE_FORMATS.items()},
        )
        self.assertTupleEqual(
            tuple(map(tuple, exclusions.POSTAL_CODE_EXCLUSIONS)),
            tuple(map(tuple, units.POSTAL_CODE_EXCLUSIONS)),
        )
        self.assertTupleEqual(
            tuple(map(tuple, exclusions.POSTAL_CODE_PATTERN_EXCLUSIONS)),
            tuple(map(tuple, units.POSTAL_CODE_PATTERN_EXCLUSIONS)),
        )


if __name__ == "__main__":
    unittest.main()
