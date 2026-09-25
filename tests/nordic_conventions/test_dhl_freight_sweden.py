import unittest

import karrio.plugins.nordic_conventions.sources as sources
import karrio.plugins.nordic_conventions.rules.dhl_freight_sweden as dhl_freight_sweden
from . import fixture

CONTEXT = fixture.context("dhl_freight_sweden")
PARCEL_CONNECT = "dhl_freight_sweden_parcel_connect_b2c"
CUSTOMS_OPTIONS = {
    "dhl_freight_sweden_customs_handling_standard": "customsHandlingStandard",
    "dhl_freight_sweden_customs_handling_full_service": "customsHandlingFullService",
    "dhl_freight_sweden_customs_own_declaration": "customsCustomersOwnDeclaration",
    "dhl_freight_sweden_customs_joint_declaration": "customsJointDeclaration",
}


def _advise(advisor, recipient="NO", service=PARCEL_CONNECT, **kwargs) -> list:
    request = fixture.shipment("SE", recipient, service, **kwargs)
    return fixture.messages(advisor, request, CONTEXT)


class TestNordicConventionsDHLFreightSwedenCustomsModeMissing(unittest.TestCase):
    def test_no_customs_option_to_norway(self):
        self.assertListEqual(
            _advise(dhl_freight_sweden.customs_mode_missing),
            [
                dict(
                    code="nordic_dhl_freight_sweden_customs_mode_missing",
                    level="warning",
                    message=(
                        "DHL Freight Sweden requires customs handling (standard or full service) or an own declaration "
                        "to be selected for destinations outside the EU VAT area, and this booking selects none. "
                        "Set the shipment option dhl_freight_sweden_customs_handling_standard, "
                        "dhl_freight_sweden_customs_handling_full_service, or dhl_freight_sweden_customs_own_declaration; "
                        "the connector selects none implicitly because each carries a DHL fee."
                    ),
                    details=dict(
                        plugin="nordic_conventions",
                        lane="SE-NO",
                        sources=[
                            sources.DFS_CUSTOMS_SERVICES_OPT_IN.to_dict(),
                            sources.DHL_MAN_CUSTOMS_SELECTION.to_dict(),
                            sources.DHL_PRL_NO_FEE_FREE_MODE.to_dict(),
                            sources.DHL_OWN_DECLARATION_FEE_INFERENCE.to_dict(),
                        ],
                        fees="No fee-free customs mode exists for destinations outside the EU VAT area.",
                    ),
                )
            ],
        )

    def test_selected_customs_option_silences_the_advisory(self):
        for option in CUSTOMS_OPTIONS:
            with self.subTest(option=option):
                self.assertListEqual(
                    _advise(
                        dhl_freight_sweden.customs_mode_missing,
                        options={option: True},
                    ),
                    [],
                )

    def test_dhl_keyed_option_does_not_silence_the_advisory(self):
        # The connector's options initializer ignores DHL-keyed options, so it sends no customs service.
        for key in CUSTOMS_OPTIONS.values():
            with self.subTest(key=key):
                self.assertListEqual(
                    [
                        message["code"]
                        for message in _advise(
                            dhl_freight_sweden.customs_mode_missing,
                            options={key: True},
                        )
                    ],
                    ["nordic_dhl_freight_sweden_customs_mode_missing"],
                )

    def test_string_true_is_parsed_as_selected(self):
        self.assertListEqual(
            _advise(
                dhl_freight_sweden.customs_mode_missing,
                options=dict(dhl_freight_sweden_customs_handling_full_service="true"),
            ),
            [],
        )

    def test_string_false_is_parsed_as_selected_like_the_connector(self):
        # Mirrors a known karrio bool option parsing quirk (state = value is not False, recorded as an
        # upstream candidate), under which the connector also sends the service; not fixed here.
        self.assertListEqual(
            _advise(
                dhl_freight_sweden.customs_mode_missing,
                options=dict(dhl_freight_sweden_customs_handling_full_service="false"),
            ),
            [],
        )


class TestNordicConventionsDHLFreightSwedenInvoiceCopy(unittest.TestCase):
    def _message(self, recipient: str, fee: str) -> dict:
        return dict(
            code="nordic_dhl_freight_sweden_invoice_copy",
            level="warning",
            message=(
                "DHL Freight Sweden requires a copy of the invoice even when complete customs data is sent with the booking: "
                "email it to dhlfreight.int.se@dhl.com shortly after booking or upload it in myDHL Freight, "
                "one document per shipment with a clear reference, because the DHL API has no document upload. "
                f"Missing documents stop the shipment with a reminder fee of {fee}."
            ),
            details=dict(
                plugin="nordic_conventions",
                lane=f"SE-{recipient}",
                sources=[
                    sources.DHL_MAN_INVOICE_COPY.to_dict(),
                    sources.DHL_CIE_INVOICE_ROUTES.to_dict(),
                    sources.DHL_CIE_REMINDER_FEES.to_dict(),
                    sources.DHL_API_NO_UPLOAD.to_dict(),
                ],
            ),
        )

    def test_invoice_copy_advisory_to_norway(self):
        self.assertListEqual(
            _advise(dhl_freight_sweden.invoice_copy), [self._message("NO", "390 kr")]
        )

    def test_invoice_copy_advisory_to_great_britain_states_the_higher_fee(self):
        self.assertListEqual(
            _advise(
                dhl_freight_sweden.invoice_copy,
                recipient="GB",
                service="dhl_freight_sweden_road_freight_standard",
            ),
            [self._message("GB", "650 kr")],
        )


if __name__ == "__main__":
    unittest.main()
