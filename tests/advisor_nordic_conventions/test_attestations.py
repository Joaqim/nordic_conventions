import unittest

import karrio.plugins.advisor_nordic_conventions.attestations as attestations
import karrio.plugins.advisor_nordic_conventions.lanes as lanes
import karrio.plugins.advisor_nordic_conventions.rules.postnord as postnord
import karrio.plugins.advisor_nordic_conventions.sources as sources
from karrio.plugins.advisor_nordic_conventions.procedures import Procedure
from . import fixture

PAPER = "advisor_nordic_conventions_commercial_invoice_paper_copy"
CUSTOMS_DECLARATION = "advisor_nordic_conventions_customs_declaration_paper_copy"
ELECTRONIC = "advisor_nordic_conventions_commercial_invoice_electronic"

PAPER_PROCEDURE = Procedure.commercial_invoice_paper_copy
ELECTRONIC_PROCEDURE = Procedure.commercial_invoice_electronic

CONFLICT_SOURCES = [
    sources.PN_SE_SERVICE_POINT_TERMS_NORWAY.to_dict(),
    sources.PN_SE_NORWAY_CHANNELS.to_dict(),
    sources.PNS_PARCEL_CUSTOMS_INVOICE.to_dict(),
]


def _parse(options, **kwargs) -> frozenset:
    return attestations.parse(
        fixture.shipment("SE", "CH", "postnord_mypack_home", options=options, **kwargs)
    )


def _lane(carrier, shipper, recipient, service, **kwargs) -> lanes.Lane:
    return lanes.lane_of(
        fixture.shipment(shipper, recipient, service, **kwargs),
        fixture.context(carrier),
    )


class TestNordicConventionsAttestationParsing(unittest.TestCase):
    def test_boolean_true_attests(self):
        self.assertSetEqual(
            _parse({PAPER: True}), frozenset({PAPER_PROCEDURE})
        )

    def test_boolean_false_is_no_claim(self):
        self.assertSetEqual(_parse({PAPER: False}), frozenset())

    def test_string_false_is_no_claim(self):
        self.assertSetEqual(_parse({PAPER: "false"}), frozenset())

    def test_string_true_is_no_claim(self):
        self.assertSetEqual(_parse({PAPER: "true"}), frozenset())

    def test_unknown_namespaced_option_is_no_claim(self):
        self.assertSetEqual(
            _parse({"advisor_nordic_conventions_unknown_procedure": True}), frozenset()
        )

    def test_no_options_attest_nothing(self):
        self.assertSetEqual(_parse(None), frozenset())


class TestNordicConventionsAttestationContradictions(unittest.TestCase):
    def test_paper_invoice_from_sweden_to_norway_is_contradicted(self):
        lane = _lane(
            "postnord", "SE", "NO", "postnord_parcel", customs=fixture.customs()
        )

        self.assertSetEqual(
            attestations.contradicted_on(lane, frozenset({PAPER_PROCEDURE})),
            frozenset({PAPER_PROCEDURE}),
        )

    def test_paper_invoice_from_sweden_to_switzerland_is_not_contradicted(self):
        lane = _lane("postnord", "SE", "CH", "postnord_parcel")

        self.assertSetEqual(
            attestations.contradicted_on(lane, frozenset({PAPER_PROCEDURE})), frozenset()
        )

    def test_paper_invoice_from_finland_to_norway_is_not_contradicted(self):
        lane = _lane("postnord", "FI", "NO", "postnord_parcel")

        self.assertSetEqual(
            attestations.contradicted_on(lane, frozenset({PAPER_PROCEDURE})), frozenset()
        )

    def test_electronic_invoice_from_sweden_to_norway_is_not_contradicted(self):
        lane = _lane(
            "postnord", "SE", "NO", "postnord_parcel", customs=fixture.customs()
        )

        self.assertSetEqual(
            attestations.contradicted_on(lane, frozenset({ELECTRONIC_PROCEDURE})),
            frozenset(),
        )
        self.assertSetEqual(
            attestations.effective_attestations(
                lane, frozenset({PAPER_PROCEDURE, ELECTRONIC_PROCEDURE})
            ),
            frozenset({ELECTRONIC_PROCEDURE}),
        )


class TestNordicConventionsAttestationResolver(unittest.TestCase):
    def test_full_coverage_omits_the_advisory(self):
        wrapped = attestations.with_attestations(postnord.se_export_paper_invoice)
        request = fixture.shipment(
            "SE", "CH", "postnord_mypack_home", options={PAPER: True}
        )

        self.assertListEqual(
            fixture.messages(wrapped, request, fixture.context("postnord")), []
        )

    def test_partial_coverage_keeps_the_advisory_unchanged(self):
        wrapped = attestations.with_attestations(postnord.se_postpaket_commercial_invoice)
        attested = fixture.shipment(
            "SE",
            "NO",
            "postnord_postpaket_utrikes",
            customs=fixture.customs(commercial_invoice=True),
            options={ELECTRONIC: True},
        )
        bare = fixture.shipment(
            "SE",
            "NO",
            "postnord_postpaket_utrikes",
            customs=fixture.customs(commercial_invoice=True),
        )

        self.assertListEqual(
            fixture.messages(wrapped, attested, fixture.context("postnord")),
            fixture.messages(
                postnord.se_postpaket_commercial_invoice, bare, fixture.context("postnord")
            ),
        )

    def test_contradicted_attestation_keeps_the_advisory(self):
        wrapped = attestations.with_attestations(postnord.se_no_digital_invoice)
        attested = fixture.shipment(
            "SE",
            "NO",
            "postnord_parcel",
            customs=fixture.customs("merchandise"),
            options={PAPER: True},
        )
        bare = fixture.shipment(
            "SE", "NO", "postnord_parcel", customs=fixture.customs("merchandise")
        )

        self.assertListEqual(
            fixture.messages(wrapped, attested, fixture.context("postnord")),
            fixture.messages(
                postnord.se_no_digital_invoice, bare, fixture.context("postnord")
            ),
        )

    def test_contradicted_attestation_covers_nothing(self):
        wrapped = attestations.with_attestations(postnord.se_postpaket_commercial_invoice)
        request = fixture.shipment(
            "SE",
            "NO",
            "postnord_postpaket_utrikes",
            customs=fixture.customs(commercial_invoice=True),
            options={PAPER: True, CUSTOMS_DECLARATION: True, ELECTRONIC: True},
        )

        self.assertListEqual(
            fixture.messages(wrapped, request, fixture.context("postnord")), []
        )
        self.assertListEqual(
            [
                message["code"]
                for message in fixture.messages(
                    attestations.attestation_conflicts, request, fixture.context("postnord")
                )
            ],
            ["advisor_nordic_conventions_attestation_conflict"],
        )

    def test_unknown_namespaced_option_changes_no_advisory(self):
        wrapped = attestations.with_attestations(postnord.se_export_paper_invoice)
        unknown = fixture.shipment(
            "SE", "CH", "postnord_mypack_home", options={"advisor_nordic_conventions_unknown": True}
        )
        bare = fixture.shipment("SE", "CH", "postnord_mypack_home")

        self.assertListEqual(
            fixture.messages(wrapped, unknown, fixture.context("postnord")),
            fixture.messages(
                postnord.se_export_paper_invoice, bare, fixture.context("postnord")
            ),
        )


class TestNordicConventionsAttestationConflicts(unittest.TestCase):
    def test_paper_invoice_attested_from_sweden_to_norway(self):
        request = fixture.shipment(
            "SE",
            "NO",
            "postnord_parcel",
            customs=fixture.customs(),
            options={PAPER: True},
        )

        self.assertListEqual(
            fixture.messages(
                attestations.attestation_conflicts, request, fixture.context("postnord")
            ),
            [
                dict(
                    code="advisor_nordic_conventions_attestation_conflict",
                    level="warning",
                    message=(
                        "The attested procedure advisor_nordic_conventions_commercial_invoice_paper_copy "
                        "does not hold on this lane: PostNord requires the commercial invoice "
                        "from Sweden to Norway digitally, not on paper with the parcel."
                    ),
                    details=dict(
                        plugin="advisor_nordic_conventions",
                        lane="SE-NO",
                        procedure="advisor_nordic_conventions_commercial_invoice_paper_copy",
                        sources=CONFLICT_SOURCES,
                    ),
                )
            ],
        )

    def test_no_contradiction_no_conflict(self):
        cases = [
            fixture.shipment(
                "SE", "CH", "postnord_mypack_home", options={PAPER: True}
            ),
            fixture.shipment("FI", "NO", "postnord_parcel", options={PAPER: True}),
            fixture.shipment(
                "SE",
                "NO",
                "postnord_parcel",
                customs=fixture.customs(),
                options={ELECTRONIC: True},
            ),
            fixture.shipment("SE", "NO", "postnord_parcel", customs=fixture.customs()),
        ]

        for request in cases:
            with self.subTest(lane=request.recipient.country_code):
                self.assertListEqual(
                    fixture.messages(
                        attestations.attestation_conflicts,
                        request,
                        fixture.context("postnord"),
                    ),
                    [],
                )


if __name__ == "__main__":
    unittest.main()
