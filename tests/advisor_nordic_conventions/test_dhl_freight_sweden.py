import importlib
import unittest

import karrio.plugins.advisor_nordic_conventions.lanes as lanes
import karrio.plugins.advisor_nordic_conventions.sources as sources
import karrio.plugins.advisor_nordic_conventions.rules.dhl_freight_sweden as dhl_freight_sweden
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
                    code="advisor_nordic_conventions_dhl_freight_sweden_customs_mode_missing",
                    level="warning",
                    message=(
                        "DHL Freight Sweden requires customs handling (standard or full service), an own declaration, "
                        "or a joint declaration to Norway or Switzerland "
                        "to be selected for destinations outside the EU VAT area, and this booking selects none. "
                        "Set the shipment option dhl_freight_sweden_customs_handling_standard, "
                        "dhl_freight_sweden_customs_handling_full_service, dhl_freight_sweden_customs_own_declaration, "
                        "or dhl_freight_sweden_customs_joint_declaration; "
                        "the connector selects none implicitly because each carries a DHL fee."
                    ),
                    details=dict(
                        plugin="advisor_nordic_conventions",
                        lane="SE-NO",
                        sources=[
                            sources.DFS_CUSTOMS_SERVICES_OPT_IN.to_dict(),
                            sources.DHL_MAN_CUSTOMS_SELECTION.to_dict(),
                            sources.DHL_MAN_JOINT_DECLARATION.to_dict(),
                            sources.DHL_CONNECTOR_JOINT_DECLARATION_DESTINATIONS.to_dict(),
                            sources.DHL_PRL_NO_FEE_FREE_MODE.to_dict(),
                            sources.DHL_OWN_DECLARATION_FEE_INFERENCE.to_dict(),
                        ],
                        fees="No fee-free customs mode exists for destinations outside the EU VAT area.",
                    ),
                )
            ],
        )

    def test_joint_declaration_countries_match_connector(self):
        self.assertTupleEqual(lanes.DHL_JOINT_DECLARATION_COUNTRIES, ("NO", "CH"))
        try:
            units = importlib.import_module("karrio.providers.dhl_freight_sweden.units")
        except ImportError:
            self.skipTest("dhl_freight_sweden connector is not importable")

        self.assertTupleEqual(lanes.DHL_JOINT_DECLARATION_COUNTRIES, tuple(units.JOINT_DECLARATION_COUNTRIES))

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
                    ["advisor_nordic_conventions_dhl_freight_sweden_customs_mode_missing"],
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


class TestNordicConventionsDHLFreightSwedenAlandCustomsMode(unittest.TestCase):
    ALAND_CODE = "advisor_nordic_conventions_dhl_freight_sweden_aland_customs_service_rejected"

    def _expected(self, services: str) -> list:
        return [
            dict(
                code=self.ALAND_CODE,
                level="warning",
                message=(
                    f"DHL Freight Sweden rejects {services} to Åland (FI 22000-22999) with error 24003, "
                    "and the connector refuses the selection before booking. "
                    "Book Åland with an own declaration (dhl_freight_sweden_customs_own_declaration) "
                    "or with customs data and no customs service, which DHL accepted for Parcel Connect (109) "
                    "without showing how it clears customs."
                ),
                details=dict(
                    plugin="advisor_nordic_conventions",
                    lane="SE-FI",
                    sources=[
                        sources.DHL_MAN_CUSTOMS_SELECTION.to_dict(),
                        sources.DHL_CONNECTOR_ALAND_CUSTOMS.to_dict(),
                    ],
                ),
            )
        ]

    def test_no_customs_option_to_aland_is_bookable(self):
        for recipient in ("AX", "AX_PREFIXED"):
            for advisor in (dhl_freight_sweden.customs_mode_missing, dhl_freight_sweden.aland_customs_service_rejected):
                with self.subTest(recipient=recipient, advisor=advisor.__name__):
                    self.assertListEqual(
                        _advise(advisor, recipient=recipient, customs=fixture.customs("merchandise", True)),
                        [],
                    )

    def test_standard_or_full_service_to_aland(self):
        standard = "customs handling standard (dhl_freight_sweden_customs_handling_standard)"
        full_service = "customs handling full service (dhl_freight_sweden_customs_handling_full_service)"
        for recipient, options, services in (
            ("AX", dict(dhl_freight_sweden_customs_handling_standard=True), standard),
            ("AX_PREFIXED", dict(dhl_freight_sweden_customs_handling_full_service="true"), full_service),
            (
                "AX",
                dict(dhl_freight_sweden_customs_handling_standard=True, dhl_freight_sweden_customs_handling_full_service=True),
                f"{full_service} and {standard}",
            ),
        ):
            with self.subTest(recipient=recipient, options=options):
                self.assertListEqual(
                    _advise(dhl_freight_sweden.aland_customs_service_rejected, recipient=recipient, options=options),
                    self._expected(services),
                )

    def test_aland_message_omits_the_joint_declaration(self):
        message = _advise(
            dhl_freight_sweden.aland_customs_service_rejected,
            recipient="AX",
            options=dict(dhl_freight_sweden_customs_handling_standard=True),
        )[0]["message"]

        self.assertNotIn("joint", message)

    def test_accepted_services_to_aland_and_refused_services_elsewhere_are_not_advised(self):
        for recipient, option in (
            ("AX", "dhl_freight_sweden_customs_own_declaration"),
            ("AX", "dhl_freight_sweden_customs_joint_declaration"),
            ("NO", "dhl_freight_sweden_customs_handling_full_service"),
            ("FI", "dhl_freight_sweden_customs_handling_standard"),
        ):
            with self.subTest(recipient=recipient, option=option):
                self.assertListEqual(
                    _advise(dhl_freight_sweden.aland_customs_service_rejected, recipient=recipient, options={option: True}),
                    [],
                )

    def test_aland_postal_range_matches_connector(self):
        try:
            units = importlib.import_module("karrio.providers.dhl_freight_sweden.units")
        except ImportError:
            self.skipTest("dhl_freight_sweden connector is not importable")

        self.assertTupleEqual(lanes.DHL_ALAND_POSTAL_RANGE, units.ALAND_POSTAL_RANGE)
        self.assertSetEqual(
            set(units.ALAND_REJECTED_CUSTOMS_SERVICES),
            set(dhl_freight_sweden.ALAND_REJECTED_CUSTOMS_OPTIONS),
        )

    def test_mainland_finland_is_not_aland(self):
        self.assertListEqual(
            [
                lanes.dhl_in_aland(country, postal_code)
                for country, postal_code in (("FI", "00100"), ("FI", "FI-22100"), ("FI", "22 999"), ("SE", "22100"), ("FI", None))
            ],
            [False, True, True, False, False],
        )


class TestNordicConventionsDHLFreightSwedenTerritoryPostalCode(unittest.TestCase):
    CODE = "advisor_nordic_conventions_dhl_freight_sweden_territory_postal_code_mismatch"

    def test_territory_code_outside_its_territory(self):
        for recipient, lane, text in (
            (
                "AX_MAINLAND",
                "SE-FI",
                "DHL Freight Sweden books country code AX (Åland) as FI, and the connector refuses the booking "
                "unless the recipient has an FI postal code in 22000-22999; this recipient has postal code '00100'. "
                "Use the country code FI for an address outside Åland.",
            ),
            (
                "AX_NO_POSTAL_CODE",
                "SE-FI",
                "DHL Freight Sweden books country code AX (Åland) as FI, and the connector refuses the booking "
                "unless the recipient has an FI postal code in 22000-22999; this recipient has no postal code. "
                "Use the country code FI for an address outside Åland.",
            ),
            (
                "IC_MAINLAND",
                "SE-ES",
                "DHL Freight Sweden books country code IC (Canary Islands) as ES, and the connector refuses the booking "
                "unless the recipient has an ES postal code in 35000-35999 or 38000-38999; "
                "this recipient has postal code '28001'. Use the country code ES for an address outside Canary Islands.",
            ),
            (
                "GL_FAROESE",
                "SE-DK",
                "DHL Freight Sweden books country code GL (Greenland) as DK, and the connector refuses the booking "
                "unless the recipient has a DK postal code in 3800-3999; this recipient has postal code '100'. "
                "Use the country code DK for an address outside Greenland.",
            ),
        ):
            with self.subTest(recipient=recipient):
                self.assertListEqual(
                    _advise(dhl_freight_sweden.territory_postal_code_mismatch, recipient=recipient),
                    [
                        dict(
                            code=self.CODE,
                            level="warning",
                            message=text,
                            details=dict(
                                plugin="advisor_nordic_conventions",
                                lane=lane,
                                sources=[sources.DHL_CONNECTOR_TERRITORY_POSTAL_CODES.to_dict()],
                            ),
                        )
                    ],
                )

    def test_territory_code_inside_its_territory_or_unchecked(self):
        for recipient in ("AX_CODE", "AX_PREFIXED", "IC_CODE", "FO", "JE", "XI_NON_BT", "AX", "NO"):
            with self.subTest(recipient=recipient):
                self.assertListEqual(
                    _advise(dhl_freight_sweden.territory_postal_code_mismatch, recipient=recipient),
                    [],
                )

    def test_postnord_and_rating_are_not_advised(self):
        request = fixture.shipment("SE", "AX_MAINLAND", "postnord_parcel")
        self.assertListEqual(
            fixture.messages(dhl_freight_sweden.territory_postal_code_mismatch, request, fixture.context("postnord")),
            [],
        )
        self.assertListEqual(
            fixture.messages(
                dhl_freight_sweden.territory_postal_code_mismatch,
                fixture.shipment("SE", "AX_MAINLAND", PARCEL_CONNECT),
                fixture.context("dhl_freight_sweden", operation="rating"),
            ),
            [],
        )

    def test_territory_postal_codes_match_connector(self):
        try:
            units = importlib.import_module("karrio.providers.dhl_freight_sweden.units")
        except ImportError:
            self.skipTest("dhl_freight_sweden connector is not importable")

        self.assertDictEqual(
            {code: tuple(territory) for code, territory in lanes.DHL_TERRITORY_POSTAL_CODES.items()},
            {code: tuple(territory) for code, territory in units.TERRITORY_POSTAL_CODES.items()},
        )


class TestNordicConventionsDHLFreightSwedenJointDeclarationDestination(unittest.TestCase):
    CODE = "advisor_nordic_conventions_dhl_freight_sweden_joint_declaration_destination"
    JOINT = dict(dhl_freight_sweden_customs_joint_declaration=True)

    def _expected(self, lane: str, country: str, alternatives: str) -> list:
        return [
            dict(
                code=self.CODE,
                level="warning",
                message=(
                    "DHL Freight Sweden's customs joint declaration (dhl_freight_sweden_customs_joint_declaration) "
                    f"is valid only to Norway or Switzerland, and the connector refuses it to {country}. "
                    f"Select {alternatives} instead."
                ),
                details=dict(
                    plugin="advisor_nordic_conventions",
                    lane=lane,
                    sources=[
                        sources.DHL_MAN_JOINT_DECLARATION.to_dict(),
                        sources.DHL_CONNECTOR_JOINT_DECLARATION_DESTINATION.to_dict(),
                    ],
                ),
            )
        ]

    def test_joint_declaration_outside_norway_and_switzerland(self):
        handling = (
            "customs handling (dhl_freight_sweden_customs_handling_standard or "
            "dhl_freight_sweden_customs_handling_full_service) or an own declaration "
            "(dhl_freight_sweden_customs_own_declaration)"
        )
        aland = (
            "an own declaration (dhl_freight_sweden_customs_own_declaration) "
            "or customs data with no customs service"
        )
        for recipient, service, lane, country, alternatives in (
            ("GB", "dhl_freight_sweden_road_freight_standard", "SE-GB", "GB", handling),
            ("JE", "dhl_freight_sweden_road_freight_priority", "SE-GB", "GB", handling),
            ("US", PARCEL_CONNECT, "SE-US", "US", handling),
            ("AX_CODE", PARCEL_CONNECT, "SE-FI", "FI", aland),
        ):
            with self.subTest(recipient=recipient):
                self.assertListEqual(
                    _advise(
                        dhl_freight_sweden.joint_declaration_destination,
                        recipient=recipient,
                        service=service,
                        options=self.JOINT,
                    ),
                    self._expected(lane, country, alternatives),
                )

    def test_joint_declaration_to_norway_or_switzerland(self):
        for recipient, service in (("NO", PARCEL_CONNECT), ("CH", "dhl_freight_sweden_road_freight_standard")):
            with self.subTest(recipient=recipient):
                self.assertListEqual(
                    _advise(
                        dhl_freight_sweden.joint_declaration_destination,
                        recipient=recipient,
                        service=service,
                        options=self.JOINT,
                    ),
                    [],
                )

    def test_inside_the_eu_vat_area_is_not_advised(self):
        for recipient in ("DE", "XI"):
            with self.subTest(recipient=recipient):
                self.assertListEqual(
                    _advise(
                        dhl_freight_sweden.joint_declaration_destination,
                        recipient=recipient,
                        service="dhl_freight_sweden_road_freight_standard",
                        options=self.JOINT,
                    ),
                    [],
                )

    def test_without_the_joint_declaration_is_not_advised(self):
        self.assertListEqual(
            _advise(
                dhl_freight_sweden.joint_declaration_destination,
                recipient="GB",
                service="dhl_freight_sweden_road_freight_standard",
                options=dict(dhl_freight_sweden_customs_own_declaration=True),
            ),
            [],
        )


class TestNordicConventionsDHLFreightSwedenInvoiceCopy(unittest.TestCase):
    def _message(self, recipient: str, fee: str) -> dict:
        return dict(
            code="advisor_nordic_conventions_dhl_freight_sweden_invoice_copy",
            level="warning",
            message=(
                "DHL Freight Sweden requires a copy of the invoice even when complete customs data is sent with the booking: "
                "email it to dhlfreight.int.se@dhl.com shortly after booking or upload it in myDHL Freight, "
                "one document per shipment with a clear reference, because the DHL API has no document upload. "
                f"Missing documents stop the shipment with a reminder fee of {fee}."
            ),
            details=dict(
                plugin="advisor_nordic_conventions",
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

    def test_invoice_copy_advisory_to_jersey_states_the_great_britain_fee(self):
        self.assertListEqual(
            _advise(
                dhl_freight_sweden.invoice_copy,
                recipient="JE",
                service="dhl_freight_sweden_road_freight_priority",
            ),
            [self._message("GB", "650 kr")],
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


class TestNordicConventionsDHLFreightSwedenAttachedDocuments(unittest.TestCase):
    def test_parcel_connect_to_norway(self):
        for service in (PARCEL_CONNECT, "109"):
            with self.subTest(service=service):
                self.assertListEqual(
                    _advise(dhl_freight_sweden.attached_documents, service=service),
                    [
                        dict(
                            code="advisor_nordic_conventions_dhl_freight_sweden_attached_documents",
                            level="warning",
                            message=(
                                "DHL Freight Sweden requires two copies of the customs documents attached on the outside of the package "
                                "for Parcel Connect (109) to destinations outside the EU VAT area."
                            ),
                            details=dict(
                                plugin="advisor_nordic_conventions",
                                lane="SE-NO",
                                sources=[
                                    sources.DHL_MAN_OUTSIDE_COPIES.to_dict(),
                                    sources.DHL_OUTSIDE_COPIES_UNCONFIRMED.to_dict(),
                                ],
                                unconfirmed=(
                                    "The requirement is unconfirmed for Parcel Connect Plus (112) and road-freight products, "
                                    "which receive no such advisory."
                                ),
                            ),
                        )
                    ],
                )

    def test_parcel_connect_matches_connector(self):
        try:
            units = importlib.import_module("karrio.providers.dhl_freight_sweden.units")
        except ImportError:
            self.skipTest("dhl_freight_sweden connector is not importable")

        service = units.ShippingService.dhl_freight_sweden_parcel_connect_b2c
        self.assertSetEqual(
            set(dhl_freight_sweden.PARCEL_CONNECT_SERVICES), {service.name, service.value}
        )

    def test_parcel_connect_plus_is_not_advised(self):
        self.assertListEqual(
            _advise(
                dhl_freight_sweden.attached_documents,
                service="dhl_freight_sweden_parcel_connect_plus",
            ),
            [],
        )


class TestNordicConventionsDHLFreightSwedenVOECMarking(unittest.TestCase):
    def test_voec_number_to_norway(self):
        self.assertListEqual(
            _advise(
                dhl_freight_sweden.voec_marking,
                customs=fixture.customs("merchandise", True, voec_number="VOEC2024001"),
            ),
            [
                dict(
                    code="advisor_nordic_conventions_dhl_freight_sweden_voec_marking",
                    level="warning",
                    message=(
                        "The connector sends the VOEC number to DHL Freight Sweden as the VOEC service, "
                        "and DHL also requires the VOEC ID printed on the package or the label for Norway."
                    ),
                    details=dict(
                        plugin="advisor_nordic_conventions",
                        lane="SE-NO",
                        sources=[
                            sources.DFS_VOEC_SERVICE.to_dict(),
                            sources.DHL_MAN_VOEC_MARKING.to_dict(),
                            sources.DHL_MAN_VOEC_PARCEL_CONNECT.to_dict(),
                        ],
                    ),
                )
            ],
        )

    def test_no_voec_number(self):
        self.assertListEqual(
            _advise(
                dhl_freight_sweden.voec_marking,
                customs=fixture.customs("merchandise", True),
            ),
            [],
        )

    def test_voec_number_to_switzerland_is_not_advised(self):
        self.assertListEqual(
            _advise(
                dhl_freight_sweden.voec_marking,
                recipient="CH",
                service="dhl_freight_sweden_road_freight_standard",
                customs=fixture.customs("merchandise", True, voec_number="VOEC2024001"),
            ),
            [],
        )


if __name__ == "__main__":
    unittest.main()
