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

    def test_source_serialises_tag_reference_and_statement(self):
        self.assertDictEqual(
            sources.Source("W", "FN:1; https://example.org", "stated").to_dict(),
            dict(tag="W", reference="FN:1; https://example.org", statement="stated"),
        )


if __name__ == "__main__":
    unittest.main()
