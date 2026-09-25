import unittest

import karrio.plugins.nordic_conventions.sources as sources
import karrio.plugins.nordic_conventions.rules.invoice_type as invoice_type
from . import fixture

PROFORMA_FOR_GOODS_SOLD = (
    "The connector declares a proforma invoice because customs.commercial_invoice is not true, "
    "but the content is described as goods for sale. "
    "A proforma invoice is for gifts and samples for which the recipient makes no payment; "
    "set commercial_invoice to true for goods sold."
)
COMMERCIAL_FOR_GIFT_OR_SAMPLE = (
    "A commercial invoice is declared for content described as a gift or sample, "
    "for which a proforma invoice is the usual document."
)
POSTNORD_SOURCES = [
    sources.PNS_COMMERCIAL_FLAG.to_dict(),
    sources.PROFORMA_FOR_GOODS_NOT_SOLD.to_dict(),
    sources.PN_POSTPAKET_TERMS_PROFORMA.to_dict(),
    sources.CONNECTOR_FLAG_MAPPING.to_dict(),
]
DHL_FREIGHT_SWEDEN_SOURCES = [
    sources.DFS_COMMERCIAL_FLAG.to_dict(),
    sources.PROFORMA_FOR_GOODS_NOT_SOLD.to_dict(),
    sources.CONNECTOR_FLAG_MAPPING.to_dict(),
]


def _advise(carrier, service, customs, recipient="NO") -> list:
    return fixture.messages(
        invoice_type.invoice_type_content_mismatch,
        fixture.shipment("SE", recipient, service, customs=customs),
        fixture.context(carrier),
    )


def _message(level, text, lane, cited) -> dict:
    return dict(
        code="nordic_invoice_type_content_mismatch",
        level=level,
        message=text,
        details=dict(plugin="nordic_conventions", lane=lane, sources=cited),
    )


class TestNordicConventionsInvoiceTypeContentMismatch(unittest.TestCase):
    def test_merchandise_declared_as_proforma(self):
        self.assertListEqual(
            _advise(
                "dhl_freight_sweden",
                "dhl_freight_sweden_parcel_connect_b2c",
                fixture.customs("merchandise"),
            ),
            [
                _message(
                    "warning",
                    PROFORMA_FOR_GOODS_SOLD,
                    "SE-NO",
                    DHL_FREIGHT_SWEDEN_SOURCES,
                )
            ],
        )

    def test_omitted_content_type_declared_as_proforma(self):
        self.assertListEqual(
            _advise("postnord", "postnord_parcel", fixture.customs(commercial_invoice=False)),
            [_message("warning", PROFORMA_FOR_GOODS_SOLD, "SE-NO", POSTNORD_SOURCES)],
        )

    def test_upper_case_merchandise_declared_as_proforma(self):
        self.assertListEqual(
            _advise("postnord", "postnord_parcel", fixture.customs("MERCHANDISE", False)),
            [_message("warning", PROFORMA_FOR_GOODS_SOLD, "SE-NO", POSTNORD_SOURCES)],
        )

    def test_gift_declared_as_proforma_is_consistent(self):
        self.assertListEqual(
            _advise("postnord", "postnord_parcel", fixture.customs("gift", False)), []
        )

    def test_documents_declared_as_proforma_is_consistent(self):
        self.assertListEqual(
            _advise("postnord", "postnord_parcel", fixture.customs("documents", False)),
            [],
        )

    def test_return_merchandise_declared_as_proforma_is_consistent(self):
        self.assertListEqual(
            _advise(
                "dhl_freight_sweden",
                "dhl_freight_sweden_parcel_connect_b2c",
                fixture.customs("return_merchandise", False),
            ),
            [],
        )

    def test_sample_declared_as_commercial_is_informational(self):
        self.assertListEqual(
            _advise(
                "dhl_freight_sweden",
                "dhl_freight_sweden_road_freight_standard",
                fixture.customs("sample", True),
                recipient="CH",
            ),
            [
                _message(
                    "info",
                    COMMERCIAL_FOR_GIFT_OR_SAMPLE,
                    "SE-CH",
                    DHL_FREIGHT_SWEDEN_SOURCES,
                )
            ],
        )

    def test_letters_carry_no_invoice_type(self):
        self.assertListEqual(
            _advise(
                "postnord", "postnord_export_letter", fixture.customs("merchandise", False)
            ),
            [],
        )


if __name__ == "__main__":
    unittest.main()
