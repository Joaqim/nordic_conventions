import unittest

import karrio.plugins.nordic_conventions.sources as sources
import karrio.plugins.nordic_conventions.rules.postnord as postnord
from . import fixture

CONTEXT = fixture.context("postnord")

NO_DIGITAL_INVOICE_LEAD = (
    "PostNord requires the commercial invoice for shipments from Sweden to Norway digitally, not on paper with the parcel. "
    "Digital routes are the booking itself (the connector sends the customs invoice data for a parcel product booked with customs data), "
    "PostNord Skicka Direkt Business, email to foravisering.export@postnord.com, or upload in PostNord MyCustoms."
)
NO_LETTER_SEK_0 = (
    "For letters to Norway PostNord requires a commercial invoice and a VOEC number from SEK 0, "
    "the invoice sent digitally through the same routes."
)
TRANSMITTED = "This booking carries customs data for a parcel product, so the connector has already transmitted the invoice data."
NOT_TRANSMITTED = "This booking does not transmit a customs invoice, so send the invoice through one of the other routes."
NO_DIGITAL_INVOICE_SOURCES = [
    sources.PN_SE_SERVICE_POINT_TERMS_NORWAY.to_dict(),
    sources.PN_SE_NORWAY_CHANNELS.to_dict(),
    sources.PN_SE_NORWAY_ONLY_CHANNELS.to_dict(),
    sources.PNS_PARCEL_CUSTOMS_INVOICE.to_dict(),
]


def _codes(request) -> list:
    return [
        message["code"]
        for advisor in (
            postnord.se_no_digital_invoice,
            postnord.se_postpaket_commercial_invoice,
            postnord.se_export_paper_invoice,
        )
        for message in fixture.messages(advisor, request, CONTEXT)
    ]


class TestNordicConventionsPostNordSENoDigitalInvoice(unittest.TestCase):
    def test_parcel_booking_with_customs_data_is_informational(self):
        request = fixture.shipment(
            "SE", "NO", "postnord_parcel", customs=fixture.customs("merchandise", True)
        )

        self.assertListEqual(
            fixture.messages(postnord.se_no_digital_invoice, request, CONTEXT),
            [
                dict(
                    code="nordic_postnord_se_no_digital_invoice",
                    level="info",
                    message=f"{NO_DIGITAL_INVOICE_LEAD} {TRANSMITTED}",
                    details=dict(
                        plugin="nordic_conventions",
                        lane="SE-NO",
                        sources=NO_DIGITAL_INVOICE_SOURCES,
                    ),
                )
            ],
        )

    def test_letter_to_norway_states_invoice_and_voec_from_sek_0(self):
        for service in ("postnord_export_letter", "postnord_rek"):
            with self.subTest(service=service):
                request = fixture.shipment(
                    "SE", "NO", service, customs=fixture.customs("merchandise")
                )

                self.assertListEqual(
                    fixture.messages(postnord.se_no_digital_invoice, request, CONTEXT),
                    [
                        dict(
                            code="nordic_postnord_se_no_digital_invoice",
                            level="warning",
                            message=f"{NO_DIGITAL_INVOICE_LEAD} {NO_LETTER_SEK_0} {NOT_TRANSMITTED}",
                            details=dict(
                                plugin="nordic_conventions",
                                lane="SE-NO",
                                sources=[
                                    *NO_DIGITAL_INVOICE_SOURCES,
                                    sources.PN_SE_SV_PAGE_NORWAY_LETTERS.to_dict(),
                                ],
                            ),
                        )
                    ],
                )

    def test_letter_not_named_by_the_swedish_page_omits_the_sek_0_statement(self):
        for service in ("postnord_varubrev_first_class", "postnord_tracked_letter"):
            with self.subTest(service=service):
                request = fixture.shipment(
                    "SE", "NO", service, customs=fixture.customs("merchandise")
                )

                self.assertListEqual(
                    fixture.messages(postnord.se_no_digital_invoice, request, CONTEXT),
                    [
                        dict(
                            code="nordic_postnord_se_no_digital_invoice",
                            level="warning",
                            message=f"{NO_DIGITAL_INVOICE_LEAD} {NOT_TRANSMITTED}",
                            details=dict(
                                plugin="nordic_conventions",
                                lane="SE-NO",
                                sources=NO_DIGITAL_INVOICE_SOURCES,
                            ),
                        )
                    ],
                )

    def test_commercial_postpaket_utrikes_to_norway_receives_no_digital_invoice_advisory(self):
        request = fixture.shipment(
            "SE",
            "NO",
            "postnord_postpaket_utrikes",
            customs=fixture.customs(commercial_invoice=True),
        )

        self.assertListEqual(
            fixture.messages(postnord.se_no_digital_invoice, request, CONTEXT), []
        )

    def test_non_commercial_postpaket_utrikes_to_norway_is_a_warning(self):
        request = fixture.shipment(
            "SE",
            "NO",
            "postnord_postpaket_utrikes",
            customs=fixture.customs("gift", False),
        )

        self.assertListEqual(
            fixture.messages(postnord.se_no_digital_invoice, request, CONTEXT),
            [
                dict(
                    code="nordic_postnord_se_no_digital_invoice",
                    level="warning",
                    message=f"{NO_DIGITAL_INVOICE_LEAD} {NOT_TRANSMITTED}",
                    details=dict(
                        plugin="nordic_conventions",
                        lane="SE-NO",
                        sources=NO_DIGITAL_INVOICE_SOURCES,
                    ),
                )
            ],
        )


if __name__ == "__main__":
    unittest.main()
