import unittest

import karrio.plugins.advisor_nordic_conventions.sources as sources
import karrio.plugins.advisor_nordic_conventions.rules.dhl_country_requirements as dhl_country_requirements
from . import fixture

CONTEXT = fixture.context("dhl_freight_sweden")
ROAD_FREIGHT_STANDARD = "dhl_freight_sweden_road_freight_standard"
ROAD_FREIGHT_DIRECT = "dhl_freight_sweden_road_freight_direct"
PARCEL_CONNECT = "dhl_freight_sweden_parcel_connect_b2c"


def _advise(advisor, shipper="SE", recipient="NO", service=ROAD_FREIGHT_STANDARD, **kwargs) -> list:
    request = fixture.shipment(shipper, recipient, service, **kwargs)
    return fixture.messages(advisor, request, CONTEXT)


class TestNordicConventionsDHLCountryRequirementsCyprusDocuments(unittest.TestCase):
    CODE = "advisor_nordic_conventions_dhl_freight_sweden_cyprus_documents"

    def _expected(self, private: bool) -> list:
        return [
            dict(
                code=self.CODE,
                level="warning",
                message=(
                    "DHL Freight Sweden requires a commercial invoice and a packing list on shipments to Cyprus "
                    "to prove the Union status of the goods, and a T2L document where applicable; "
                    "the documents can be uploaded in myDHL Freight."
                    + (
                        " The recipient appears to be a private individual, "
                        "so copies of the recipient's ID documents, front and back, must also be provided."
                        if private
                        else ""
                    )
                ),
                details=dict(
                    plugin="advisor_nordic_conventions",
                    lane="SE-CY",
                    sources=[sources.DHL_CSR_CYPRUS_DOCUMENTS.to_dict()],
                ),
            )
        ]

    def test_business_recipient_to_cyprus(self):
        for service in (ROAD_FREIGHT_STANDARD, ROAD_FREIGHT_DIRECT):
            with self.subTest(service=service):
                self.assertListEqual(
                    _advise(
                        dhl_country_requirements.cyprus_documents,
                        recipient="CY_BUSINESS",
                        service=service,
                    ),
                    self._expected(private=False),
                )

    def test_private_recipient_to_cyprus(self):
        for recipient in ("CY", "CY_RESIDENTIAL"):
            with self.subTest(recipient=recipient):
                self.assertListEqual(
                    _advise(
                        dhl_country_requirements.cyprus_documents,
                        recipient=recipient,
                    ),
                    self._expected(private=True),
                )

    def test_other_destinations_receive_no_cyprus_advice(self):
        self.assertListEqual(
            _advise(dhl_country_requirements.cyprus_documents, recipient="GR"),
            [],
        )


class TestNordicConventionsDHLCountryRequirementsGreekTaxIds(unittest.TestCase):
    CODE = "advisor_nordic_conventions_dhl_freight_sweden_greek_tax_ids"

    def _expected(self, parties: str) -> list:
        return [
            dict(
                code=self.CODE,
                level="warning",
                message=(
                    "DHL Freight Sweden requires a VAT number or TIN "
                    f"from {parties} on shipments to Greece on this product, "
                    f"and this booking provides none for {parties}. "
                    "The connector reads each party's number from federal_tax_id or state_tax_id "
                    "and refuses the booking without one; "
                    "EL000000000 can be used for a private individual."
                ),
                details=dict(
                    plugin="advisor_nordic_conventions",
                    lane="SE-GR",
                    sources=[
                        sources.DHL_CSR_GREEK_TAX_IDS.to_dict(),
                        sources.DHL_MAN_GREEK_TAX_ID_PRODUCTS.to_dict(),
                        sources.DHL_CONNECTOR_GREEK_TAX_ID_PRODUCTS.to_dict(),
                    ],
                ),
            )
        ]

    def test_greek_lane_without_tax_identification_numbers(self):
        for service in ("202", "SPI", "dhl_freight_sweden_home_delivery_international_b2c"):
            with self.subTest(service=service):
                self.assertListEqual(
                    _advise(dhl_country_requirements.greek_tax_ids, recipient="GR", service=service),
                    self._expected("the sender and the recipient"),
                )

    def test_one_party_missing_names_only_that_party(self):
        for shipper, recipient, parties in (
            ("SE_TAXED", "GR", "the recipient"),
            ("SE", "GR_TAXED", "the sender"),
        ):
            with self.subTest(shipper=shipper, recipient=recipient):
                self.assertListEqual(
                    _advise(
                        dhl_country_requirements.greek_tax_ids,
                        shipper=shipper,
                        recipient=recipient,
                    ),
                    self._expected(parties),
                )

    def test_both_parties_identified_silences_the_advisory(self):
        for shipper, recipient in (
            ("SE_TAXED", "GR_TAXED"),
            ("SE_STATE_TAXED", "GR_TAXED"),
        ):
            with self.subTest(shipper=shipper):
                self.assertListEqual(
                    _advise(
                        dhl_country_requirements.greek_tax_ids,
                        shipper=shipper,
                        recipient=recipient,
                    ),
                    [],
                )

    def test_product_outside_the_set_receives_no_advice(self):
        self.assertListEqual(
            _advise(
                dhl_country_requirements.greek_tax_ids,
                recipient="GR",
                service=ROAD_FREIGHT_DIRECT,
            ),
            [],
        )


class TestNordicConventionsDHLCountryRequirementsSentInformation(unittest.TestCase):
    CODE = "advisor_nordic_conventions_dhl_freight_sweden_sent_information"
    FIVE_HUNDRED_KG = [dict(weight=500.0, weight_unit="KG")]

    def _expected(self) -> list:
        return [
            dict(
                code=self.CODE,
                level="info",
                message=(
                    "DHL Freight Sweden requires a SENT reference number and a Carrier Key Code "
                    "on a shipment to Poland on this product when the goods are subject "
                    "to the Polish SENT monitoring system. "
                    "The connector validates the pair's consistency when given and declares the shipment "
                    "SENT free with no information given, so deciding whether the goods are subject "
                    "is the booker's responsibility."
                ),
                details=dict(
                    plugin="advisor_nordic_conventions",
                    lane="SE-PL",
                    sources=[
                        sources.DHL_CONNECTOR_TRANSPORT_DECLARATION_PRODUCTS.to_dict(),
                        sources.DHL_CONNECTOR_TRANSPORT_DECLARATION_DEFAULTS.to_dict(),
                    ],
                ),
            )
        ]

    def test_polish_lane_receives_the_sent_reminder(self):
        self.assertListEqual(
            _advise(
                dhl_country_requirements.sent_information,
                recipient="PL",
                parcels=self.FIVE_HUNDRED_KG,
            ),
            self._expected(),
        )

    def test_every_transport_declaration_product_receives_the_reminder(self):
        for service in ("205", "233", "SPI", "dhl_freight_sweden_home_delivery_international_b2c"):
            with self.subTest(service=service):
                self.assertListEqual(
                    _advise(
                        dhl_country_requirements.sent_information,
                        recipient="PL",
                        service=service,
                    ),
                    self._expected(),
                )

    def test_sent_data_given_still_receives_the_reminder(self):
        self.assertListEqual(
            _advise(
                dhl_country_requirements.sent_information,
                recipient="PL",
                options=dict(
                    dhl_freight_sweden_sent_ref="SENT1234567890",
                    dhl_freight_sweden_sent_carkey="CARKEY123456",
                ),
            ),
            self._expected(),
        )

    def test_product_outside_the_set_receives_no_sent_advice(self):
        self.assertListEqual(
            _advise(
                dhl_country_requirements.sent_information,
                recipient="PL",
                service=PARCEL_CONNECT,
            ),
            [],
        )


class TestNordicConventionsDHLCountryRequirementsUitInformation(unittest.TestCase):
    CODE = "advisor_nordic_conventions_dhl_freight_sweden_uit_information"

    def _expected(self, level: str) -> list:
        return [
            dict(
                code=self.CODE,
                level=level,
                message=(
                    "DHL Freight Sweden requires a UIT code on a shipment to Romania on this product "
                    "when the goods exceed 500 kg gross weight, exceed 10 000 RON in value, "
                    "or are high-risk fiscal goods. "
                    "The code is provided by the Romanian party, UIT FREE is entered when the goods "
                    "are not subject, and the connector validates the declaration's consistency."
                ),
                details=dict(
                    plugin="advisor_nordic_conventions",
                    lane="SE-RO",
                    sources=[
                        sources.DHL_CONNECTOR_TRANSPORT_DECLARATION_PRODUCTS.to_dict(),
                        sources.DHL_CONNECTOR_TRANSPORT_DECLARATION_DEFAULTS.to_dict(),
                    ],
                ),
            )
        ]

    def test_romanian_lane_at_500_kg_warns(self):
        self.assertListEqual(
            _advise(
                dhl_country_requirements.uit_information,
                recipient="RO",
                parcels=[dict(weight=250.0, weight_unit="KG"), dict(weight=250.0, weight_unit="KG")],
            ),
            self._expected("warning"),
        )

    def test_romanian_lane_below_the_weight_criterion_informs(self):
        self.assertListEqual(
            _advise(
                dhl_country_requirements.uit_information,
                recipient="RO",
                parcels=[dict(weight=100.0, weight_unit="KG")],
            ),
            self._expected("info"),
        )

    def test_pound_parcel_weights_normalize_to_kilograms(self):
        for parcels, level in (
            (
                [dict(weight=1102.31, weight_unit="LB"), dict(weight=2.5, weight_unit="KG")],
                "warning",
            ),
            ([dict(weight=1102.31, weight_unit="LB")], "info"),
        ):
            with self.subTest(parcels=parcels):
                self.assertListEqual(
                    _advise(
                        dhl_country_requirements.uit_information,
                        recipient="RO",
                        parcels=parcels,
                    ),
                    self._expected(level),
                )

    def test_product_outside_the_set_receives_no_uit_advice(self):
        self.assertListEqual(
            _advise(
                dhl_country_requirements.uit_information,
                recipient="RO",
                service=PARCEL_CONNECT,
            ),
            [],
        )


class TestNordicConventionsDHLCountryRequirementsEkaerInformation(unittest.TestCase):
    CODE = "advisor_nordic_conventions_dhl_freight_sweden_ekaer_information"

    def _expected(self, level: str) -> list:
        return [
            dict(
                code=self.CODE,
                level=level,
                message=(
                    "DHL Freight Sweden requires an EKAER number on a shipment to Hungary on this product "
                    "when the goods are subject to the Hungarian EKAER control system: "
                    "over 500 kg gross weight, over HUF 1 000 000 in value, or risky goods. "
                    "The number is obtained from the Hungarian party, EKAER FREE is entered when the goods "
                    "are not subject, and the connector validates the declaration's consistency."
                ),
                details=dict(
                    plugin="advisor_nordic_conventions",
                    lane="SE-HU",
                    sources=[
                        sources.DHL_CONNECTOR_TRANSPORT_DECLARATION_PRODUCTS.to_dict(),
                        sources.DHL_CONNECTOR_TRANSPORT_DECLARATION_DEFAULTS.to_dict(),
                    ],
                ),
            )
        ]

    def test_hungarian_lane_at_500_kg_warns(self):
        self.assertListEqual(
            _advise(
                dhl_country_requirements.ekaer_information,
                recipient="HU",
                parcels=[dict(weight=250.0, weight_unit="KG"), dict(weight=250.0, weight_unit="KG")],
            ),
            self._expected("warning"),
        )

    def test_hungarian_lane_below_the_weight_criterion_informs(self):
        self.assertListEqual(
            _advise(
                dhl_country_requirements.ekaer_information,
                recipient="HU",
                parcels=[dict(weight=100.0, weight_unit="KG")],
            ),
            self._expected("info"),
        )

    def test_product_outside_the_set_receives_no_ekaer_advice(self):
        self.assertListEqual(
            _advise(
                dhl_country_requirements.ekaer_information,
                recipient="HU",
                service=PARCEL_CONNECT,
            ),
            [],
        )


if __name__ == "__main__":
    unittest.main()
