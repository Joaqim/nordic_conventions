import unittest

import karrio.plugins.advisor_nordic_conventions.sources as sources
import karrio.plugins.advisor_nordic_conventions.rules.dhl_country_requirements as dhl_country_requirements
from . import fixture

CONTEXT = fixture.context("dhl_freight_sweden")
ROAD_FREIGHT_STANDARD = "dhl_freight_sweden_road_freight_standard"
ROAD_FREIGHT_DIRECT = "dhl_freight_sweden_road_freight_direct"
PARCEL_CONNECT = "dhl_freight_sweden_parcel_connect_b2c"


def _advise(advisor, recipient="NO", service=ROAD_FREIGHT_STANDARD, **kwargs) -> list:
    request = fixture.shipment("SE", recipient, service, **kwargs)
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


if __name__ == "__main__":
    unittest.main()
