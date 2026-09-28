import unittest

import karrio.plugins.nordic_conventions.lanes as lanes
import karrio.plugins.nordic_conventions.procedures as procedures
from karrio.plugins.nordic_conventions.codes import AdvisoryClassification
from karrio.plugins.nordic_conventions.procedures import Procedure, option_key
from . import fixture

PAPER = Procedure.commercial_invoice_paper_copy
CUSTOMS_DECLARATION = Procedure.customs_declaration_paper_copy
ATTACHED_OUTSIDE = Procedure.customs_documents_attached_outside
ELECTRONIC = Procedure.commercial_invoice_electronic
VOEC_PRINTED = Procedure.voec_marking_printed


def _lane(carrier, shipper, recipient, service, **kwargs) -> lanes.Lane:
    return lanes.lane_of(
        fixture.shipment(shipper, recipient, service, **kwargs),
        fixture.context(carrier),
    )


class TestNordicConventionsProcedures(unittest.TestCase):
    def test_five_procedures_with_their_option_key_spellings(self):
        self.assertListEqual(
            [(procedure.name, option_key(procedure)) for procedure in Procedure],
            [
                (
                    "commercial_invoice_paper_copy",
                    "nordic_conventions_commercial_invoice_paper_copy",
                ),
                (
                    "customs_declaration_paper_copy",
                    "nordic_conventions_customs_declaration_paper_copy",
                ),
                (
                    "customs_documents_attached_outside",
                    "nordic_conventions_customs_documents_attached_outside",
                ),
                (
                    "commercial_invoice_electronic",
                    "nordic_conventions_commercial_invoice_electronic",
                ),
                (
                    "voec_marking_printed",
                    "nordic_conventions_voec_marking_printed",
                ),
            ],
        )

    def test_answering_map_covers_every_classification(self):
        self.assertSetEqual(set(procedures.ANSWERING), set(AdvisoryClassification))

    def test_unattestable_advisories_map_to_the_empty_set(self):
        lane = _lane("dhl_freight_sweden", "SE", "NO", "109", customs=fixture.customs())

        for classification in (
            AdvisoryClassification.dhl_freight_sweden_customs_mode_missing,
            AdvisoryClassification.invoice_type_content_mismatch,
        ):
            with self.subTest(classification=classification.name):
                self.assertSetEqual(
                    procedures.answering_procedures(classification, lane), frozenset()
                )


class TestNordicConventionsAnsweringSets(unittest.TestCase):
    def test_se_no_digital_invoice_is_answered_electronically(self):
        lane = _lane(
            "postnord", "SE", "NO", "postnord_parcel", customs=fixture.customs()
        )

        self.assertSetEqual(
            procedures.answering_procedures(
                AdvisoryClassification.postnord_se_no_digital_invoice, lane
            ),
            frozenset({ELECTRONIC}),
        )

    def test_se_postpaket_to_norway_is_answered_by_declaration_and_electronic(self):
        lane = _lane(
            "postnord",
            "SE",
            "NO",
            "postnord_postpaket_utrikes",
            customs=fixture.customs(commercial_invoice=True),
        )

        self.assertSetEqual(
            procedures.answering_procedures(
                AdvisoryClassification.postnord_se_postpaket_commercial_invoice, lane
            ),
            frozenset({CUSTOMS_DECLARATION, ELECTRONIC}),
        )

    def test_se_postpaket_elsewhere_is_answered_by_declaration_and_paper(self):
        lane = _lane(
            "postnord",
            "SE",
            "US",
            "postnord_postpaket_utrikes",
            customs=fixture.customs(commercial_invoice=True),
        )

        self.assertSetEqual(
            procedures.answering_procedures(
                AdvisoryClassification.postnord_se_postpaket_commercial_invoice, lane
            ),
            frozenset({CUSTOMS_DECLARATION, PAPER}),
        )

    def test_se_export_paper_invoice_is_answered_by_paper(self):
        lane = _lane("postnord", "SE", "CH", "postnord_mypack_home")

        self.assertSetEqual(
            procedures.answering_procedures(
                AdvisoryClassification.postnord_se_export_paper_invoice, lane
            ),
            frozenset({PAPER}),
        )

    def test_fi_export_invoice_to_norway_is_answered_electronically(self):
        lane = _lane("postnord", "FI", "NO", "postnord_parcel")

        self.assertSetEqual(
            procedures.answering_procedures(
                AdvisoryClassification.postnord_fi_export_invoice, lane
            ),
            frozenset({ELECTRONIC}),
        )

    def test_fi_export_invoice_elsewhere_is_answered_by_paper(self):
        lane = _lane("postnord", "FI", "GB", "postnord_parcel")

        self.assertSetEqual(
            procedures.answering_procedures(
                AdvisoryClassification.postnord_fi_export_invoice, lane
            ),
            frozenset({PAPER}),
        )

    def test_dk_export_documents_paper_only_destinations(self):
        for recipient in ("NO", "CH", "LI", "GB"):
            with self.subTest(recipient=recipient):
                lane = _lane("postnord", "DK", recipient, "postnord_parcel")

                self.assertSetEqual(
                    procedures.answering_procedures(
                        AdvisoryClassification.postnord_dk_export_documents, lane
                    ),
                    frozenset({PAPER}),
                )

    def test_dk_export_documents_default_destination_needs_both_paper_procedures(self):
        lane = _lane("postnord", "DK", "US", "postnord_parcel")

        self.assertSetEqual(
            procedures.answering_procedures(
                AdvisoryClassification.postnord_dk_export_documents, lane
            ),
            frozenset({CUSTOMS_DECLARATION, PAPER}),
        )

    def test_dhl_freight_sweden_answering_sets(self):
        lane = _lane(
            "dhl_freight_sweden",
            "SE",
            "NO",
            "dhl_freight_sweden_parcel_connect_b2c",
            customs=fixture.customs("merchandise", True, voec_number="VOEC2024001"),
        )

        self.assertSetEqual(
            procedures.answering_procedures(
                AdvisoryClassification.dhl_freight_sweden_invoice_copy, lane
            ),
            frozenset({ELECTRONIC}),
        )
        self.assertSetEqual(
            procedures.answering_procedures(
                AdvisoryClassification.dhl_freight_sweden_attached_documents, lane
            ),
            frozenset({ATTACHED_OUTSIDE}),
        )
        self.assertSetEqual(
            procedures.answering_procedures(
                AdvisoryClassification.dhl_freight_sweden_voec_marking, lane
            ),
            frozenset({VOEC_PRINTED}),
        )


class TestNordicConventionsExpectedProcedures(unittest.TestCase):
    def test_postnord_parcel_from_sweden_expects_the_paper_invoice(self):
        request = fixture.shipment("SE", "CH", "postnord_mypack_home")

        self.assertSetEqual(
            procedures.expected_procedures(request, fixture.context("postnord")),
            frozenset({PAPER}),
        )

    def test_postnord_postpaket_from_sweden_to_norway_expects_declaration_and_electronic(self):
        request = fixture.shipment(
            "SE",
            "NO",
            "postnord_postpaket_utrikes",
            customs=fixture.customs(commercial_invoice=True),
        )

        self.assertSetEqual(
            procedures.expected_procedures(request, fixture.context("postnord")),
            frozenset({CUSTOMS_DECLARATION, ELECTRONIC}),
        )

    def test_intra_eu_shipment_expects_nothing(self):
        request = fixture.shipment("SE", "DE", "postnord_parcel")

        self.assertSetEqual(
            procedures.expected_procedures(request, fixture.context("postnord")),
            frozenset(),
        )

    def test_out_of_scope_requests_expect_nothing(self):
        cases = [
            (
                fixture.shipment("SE", "NO", "postnord_parcel"),
                fixture.context("postnord", operation="rating"),
            ),
            (
                fixture.shipment("SE", "NO", "bring_business_parcel"),
                fixture.context("bring"),
            ),
        ]

        for request, context in cases:
            with self.subTest(carrier=context.carrier_name, operation=context.operation):
                self.assertSetEqual(
                    procedures.expected_procedures(request, context), frozenset()
                )


class TestNordicConventionsPackageExports(unittest.TestCase):
    def test_procedure_symbols_import_from_the_package_root(self):
        from karrio.plugins.nordic_conventions import Procedure, expected_procedures

        self.assertIs(Procedure, procedures.Procedure)
        self.assertIs(expected_procedures, procedures.expected_procedures)


if __name__ == "__main__":
    unittest.main()
