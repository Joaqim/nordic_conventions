import unittest

from karrio.plugins.nordic_conventions.codes import AdvisoryClassification


class TestNordicConventionsCodes(unittest.TestCase):
    def test_eleven_classifications_follow_the_namespace_rule(self):
        self.assertEqual(len(AdvisoryClassification), 11)
        self.assertListEqual(
            [
                classification
                for classification in AdvisoryClassification
                if not classification.value.startswith("nordic_conventions_")
            ],
            [],
        )


if __name__ == "__main__":
    unittest.main()
