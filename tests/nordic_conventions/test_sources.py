import unittest

import karrio.plugins.nordic_conventions.sources as sources


class TestNordicConventionsSources(unittest.TestCase):
    def test_every_source_is_tagged_and_referenced(self):
        self.assertGreater(len(sources.ALL), 0)
        self.assertListEqual(
            [
                source
                for source in sources.ALL
                if source.tag not in sources.EVIDENCE_TAGS
                or not source.reference.strip()
                or not source.statement.strip()
            ],
            [],
        )

    def test_dhl_manual_sources_cite_v5_26_with_a_page(self):
        manual_sources = [source for source in sources.ALL if sources.DHL_MAN_URL in source.reference]

        self.assertIn("v5.26", sources.DHL_MAN_URL)
        self.assertGreater(len(manual_sources), 0)
        self.assertListEqual(
            [
                source
                for source in manual_sources
                if "v5.23" in source.reference + source.statement or " p." not in source.reference
            ],
            [],
        )

    def test_source_serialises_tag_reference_and_statement(self):
        self.assertDictEqual(
            sources.Source("W", "FN:1; https://example.org", "stated").to_dict(),
            dict(tag="W", reference="FN:1; https://example.org", statement="stated"),
        )


if __name__ == "__main__":
    unittest.main()
