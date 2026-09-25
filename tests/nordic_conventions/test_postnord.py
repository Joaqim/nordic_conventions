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


POSTPAKET_CONNECTOR_NOTE = (
    "The connector currently sends CN22 declaration data and no invoice for International Parcel, "
    "so supply the CN23 and the invoice yourself."
)
POSTPAKET_SOURCES = [
    sources.PN_SE_POSTPAKET_TERMS.to_dict(),
    sources.PN_SE_EN_PAGE_POSTPAKET.to_dict(),
    sources.PN_SE_SV_PAGE_POSTPAKET.to_dict(),
]
POSTPAKET_CODE_SOURCES = [
    sources.PNS_INTERNATIONAL_PARCEL_CN22.to_dict(),
    sources.PN_POSTPAKET_CODE_91.to_dict(),
    sources.PN_POSTPAKET_CODE_95.to_dict(),
]


class TestNordicConventionsPostNordSEPostpaketCommercialInvoice(unittest.TestCase):
    def test_commercial_postpaket_utrikes_to_the_united_states(self):
        request = fixture.shipment(
            "SE",
            "US",
            "postnord_postpaket_utrikes",
            customs=fixture.customs(commercial_invoice=True),
        )

        self.assertListEqual(
            fixture.messages(postnord.se_postpaket_commercial_invoice, request, CONTEXT),
            [
                dict(
                    code="nordic_postnord_se_postpaket_commercial_invoice",
                    level="warning",
                    message=(
                        "Commercial PostNord Postpaket Utrikes (International Parcel, 91) outside the EU VAT area needs the CN23 export declaration "
                        "and a commercial invoice in three copies with the parcel. "
                        "Three copies satisfies both the Postpaket Utrikes terms (two copies above SEK 2 000 or for commercial purposes) "
                        "and the PostNord web pages (triplicate above SEK 2 000). "
                        f"{POSTPAKET_CONNECTOR_NOTE}"
                    ),
                    details=dict(
                        plugin="nordic_conventions",
                        lane="SE-US",
                        sources=[*POSTPAKET_SOURCES, *POSTPAKET_CODE_SOURCES],
                    ),
                )
            ],
        )
        self.assertListEqual(
            [source["reference"].split(";")[0] for source in POSTPAKET_SOURCES],
            ["FN:103, FN:111", "FN:102, FN:107", "FN:102, FN:109"],
        )
        self.assertIn("i 2 exemplar", POSTPAKET_SOURCES[0]["statement"])
        self.assertIn("triplicate", POSTPAKET_SOURCES[1]["statement"])
        self.assertIn("tre exemplar", POSTPAKET_SOURCES[2]["statement"])

    def test_sale_like_content_triggers_the_advisory(self):
        request = fixture.shipment(
            "SE",
            "CH",
            "postnord_postpaket_utrikes",
            customs=fixture.customs("merchandise", False),
        )

        self.assertListEqual(
            [
                message["code"]
                for message in fixture.messages(
                    postnord.se_postpaket_commercial_invoice, request, CONTEXT
                )
            ],
            ["nordic_postnord_se_postpaket_commercial_invoice"],
        )

    def test_commercial_postpaket_utrikes_to_norway_sends_the_invoice_digitally(self):
        request = fixture.shipment(
            "SE",
            "NO",
            "postnord_postpaket_utrikes",
            customs=fixture.customs(commercial_invoice=True),
        )

        self.assertListEqual(
            fixture.messages(postnord.se_postpaket_commercial_invoice, request, CONTEXT),
            [
                dict(
                    code="nordic_postnord_se_postpaket_commercial_invoice",
                    level="warning",
                    message=(
                        "Commercial PostNord Postpaket Utrikes (International Parcel, 91) to Norway needs the CN23 export declaration, "
                        "and PostNord requires the commercial invoice for Norway digitally, not attached to the parcel: "
                        "send it through the Booking API, PostNord Skicka Direkt Business, email to foravisering.export@postnord.com, "
                        "or upload in PostNord MyCustoms. "
                        f"{POSTPAKET_CONNECTOR_NOTE}"
                    ),
                    details=dict(
                        plugin="nordic_conventions",
                        lane="SE-NO",
                        sources=[
                            *POSTPAKET_SOURCES,
                            sources.PN_SE_NORWAY_CHANNELS.to_dict(),
                            *POSTPAKET_CODE_SOURCES,
                        ],
                    ),
                )
            ],
        )
        self.assertListEqual(_codes(request), ["nordic_postnord_se_postpaket_commercial_invoice"])

    def test_gift_postpaket_utrikes_is_not_advised(self):
        request = fixture.shipment(
            "SE",
            "CH",
            "postnord_postpaket_utrikes",
            customs=fixture.customs("gift", False),
        )

        self.assertListEqual(
            fixture.messages(postnord.se_postpaket_commercial_invoice, request, CONTEXT),
            [],
        )

    def test_letters_are_not_advised(self):
        request = fixture.shipment(
            "SE",
            "CH",
            "postnord_export_letter",
            customs=fixture.customs("merchandise", True),
        )

        self.assertListEqual(
            fixture.messages(postnord.se_postpaket_commercial_invoice, request, CONTEXT),
            [],
        )

    def test_finnish_postpaket_utrikes_is_not_advised(self):
        request = fixture.shipment(
            "FI",
            "CH",
            "postnord_postpaket_utrikes",
            customs=fixture.customs("merchandise", True),
        )

        self.assertListEqual(
            fixture.messages(postnord.se_postpaket_commercial_invoice, request, CONTEXT),
            [],
        )

    def test_no_swedish_shipment_to_norway_receives_the_invoice_routes_twice(self):
        requests = [
            fixture.shipment("SE", "NO", service, customs=customs)
            for service in (
                "postnord_parcel",
                "postnord_postpaket_utrikes",
                "91",
                "postnord_export_letter",
                "postnord_varubrev_first_class",
            )
            for customs in (
                None,
                fixture.customs("merchandise", True),
                fixture.customs("gift", False),
                fixture.customs("gift", True),
            )
        ]

        self.assertListEqual(
            [
                codes
                for codes in map(_codes, requests)
                if {
                    "nordic_postnord_se_no_digital_invoice",
                    "nordic_postnord_se_postpaket_commercial_invoice",
                }
                <= set(codes)
            ],
            [],
        )


if __name__ == "__main__":
    unittest.main()
