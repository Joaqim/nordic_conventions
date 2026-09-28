import importlib
import logging
import unittest
from unittest import mock

import attr
import karrio.core.advisors as advisors
import karrio.core.metadata as metadata
import karrio.core.settings as settings
import karrio.references as references

import karrio.plugins.nordic_conventions as nordic_conventions
import karrio.plugins.nordic_conventions.procedures as procedures
from . import fixture


@attr.s(auto_attribs=True)
class ConnectionSettings(settings.Settings):
    name: str = None

    @property
    def carrier_name(self):
        return self.name


def _connection(carrier_name: str) -> ConnectionSettings:
    return ConnectionSettings(name=carrier_name, carrier_id=f"{carrier_name}_se")


def _plugin_messages(messages) -> list:
    return [
        message
        for message in messages
        if (message.details or {}).get("plugin") == "nordic_conventions"
    ]


def _advise_all(request, context) -> list:
    return [
        message
        for advisor in nordic_conventions.ADVISORS
        for message in fixture.messages(advisor, request, context)
    ]


@attr.s(auto_attribs=True)
class PluginMetadataWithoutAdvisors:
    id: str
    label: str
    description: str = ""
    status: str = "beta"


class TestNordicConventionsPlugin(unittest.TestCase):
    def tearDown(self):
        references.import_extensions()

    def test_installed_plugin_is_collected_as_an_advisor(self):
        references.import_extensions()

        plugin = references.collect_references(plugin_registry={})["plugins"][
            "nordic_conventions"
        ]

        self.assertEqual(plugin["type"], "advisor")
        self.assertListEqual(
            [
                advisor
                for plugin_id, advisor in references.get_advisors()
                if plugin_id == "nordic_conventions"
            ],
            nordic_conventions.ADVISORS,
        )
        self.assertEqual(len(nordic_conventions.ADVISORS), 11)

    def test_messages_reach_the_sdk_runner(self):
        references.import_extensions()
        request = fixture.shipment("SE", "CH", "postnord_mypack_home")

        self.assertListEqual(
            [
                (message.carrier_name, message.carrier_id, message.code)
                for message in _plugin_messages(
                    advisors.run_advisors(request, _connection("postnord"), "shipping")
                )
            ],
            [
                (
                    "postnord",
                    "postnord_se",
                    "nordic_conventions_postnord_se_export_paper_invoice",
                )
            ],
        )

    def test_several_advisories_on_one_shipment(self):
        references.import_extensions()
        request = fixture.shipment("SE", "NO", "109")

        self.assertListEqual(
            sorted(
                message.code
                for message in _plugin_messages(
                    advisors.run_advisors(
                        request, _connection("dhl_freight_sweden"), "shipping"
                    )
                )
            ),
            [
                "nordic_conventions_dhl_freight_sweden_attached_documents",
                "nordic_conventions_dhl_freight_sweden_customs_mode_missing",
                "nordic_conventions_dhl_freight_sweden_invoice_copy",
            ],
        )

    def test_rating_through_the_sdk_runner_receives_no_advice(self):
        references.import_extensions()
        request = fixture.shipment("SE", "NO", "postnord_parcel")

        self.assertListEqual(
            _plugin_messages(
                advisors.run_advisors(request, _connection("postnord"), "rating")
            ),
            [],
        )


class TestNordicConventionsMessages(unittest.TestCase):
    def test_every_message_is_coded_levelled_and_attributed(self):
        cases = [
            ("postnord", "SE", "NO", "postnord_parcel", fixture.customs()),
            ("postnord", "SE", "NO", "postnord_export_letter", fixture.customs()),
            ("postnord", "SE", "US", "postnord_postpaket_utrikes", fixture.customs()),
            ("postnord", "SE", "CH", "postnord_mypack_home", None),
            ("postnord", "FI", "GB", "postnord_parcel", None),
            ("postnord", "DK", "US", "postnord_parcel", None),
            (
                "dhl_freight_sweden",
                "SE",
                "NO",
                "109",
                fixture.customs("sample", True, voec_number="VOEC2024001"),
            ),
        ]
        messages = [
            message
            for carrier, shipper, recipient, service, customs in cases
            for message in _advise_all(
                fixture.shipment(shipper, recipient, service, customs=customs),
                fixture.context(carrier),
            )
        ]

        self.assertEqual(
            len({message["code"] for message in messages}),
            10,
        )
        self.assertListEqual(
            [
                message
                for message in messages
                if not message["code"].startswith("nordic_conventions_")
                or "SHIPPING_SDK_" in message["code"]
                or message["level"] not in advisors.ADVISORY_LEVELS
                or not message["message"]
                or not message["details"]["sources"]
                or any(
                    source["tag"] not in ("S", "W", "I") or not source["reference"]
                    for source in message["details"]["sources"]
                )
            ],
            [],
        )

    def test_out_of_scope_shipments_receive_no_advice(self):
        cases = [
            ("postnord", "shipping", "NO", "SE", "postnord_parcel"),
            ("bring", "shipping", "SE", "NO", "bring_business_parcel"),
            ("dhl_freight_sweden", "shipping", "DK", "NO", "109"),
            ("postnord", "shipping", "SE", "DE", "postnord_parcel"),
            ("dhl_freight_sweden", "shipping", "SE", "DE", "109"),
            ("dhl_freight_sweden", "shipping", "SE", "GR", "202"),
            ("postnord", "shipping", "AX", "NO", "postnord_parcel"),
            ("postnord", "rating", "SE", "NO", "postnord_parcel"),
        ]

        self.assertListEqual(
            [
                case
                for case in cases
                if _advise_all(
                    fixture.shipment(
                        case[2], case[3], case[4], customs=fixture.customs()
                    ),
                    fixture.context(case[0], operation=case[1]),
                )
            ],
            [],
        )

    def test_return_from_norway_receives_no_advice(self):
        request = fixture.shipment(
            "NO", "SE", "postnord_parcel", customs=fixture.customs(), is_return=True
        )

        self.assertListEqual(_advise_all(request, fixture.context("postnord")), [])


class TestNordicConventionsAttestations(unittest.TestCase):
    def tearDown(self):
        references.import_extensions()

    def test_attested_option_removes_the_answered_advisory(self):
        references.import_extensions()
        request = fixture.shipment(
            "SE",
            "CH",
            "postnord_mypack_home",
            options={"nordic_conventions_commercial_invoice_paper_copy": True},
        )

        self.assertListEqual(
            _plugin_messages(
                advisors.run_advisors(request, _connection("postnord"), "shipping")
            ),
            [],
        )

    def test_contradicted_attestation_keeps_the_advisory_and_adds_the_conflict(self):
        references.import_extensions()
        request = fixture.shipment(
            "SE",
            "NO",
            "postnord_parcel",
            customs=fixture.customs("merchandise", True),
            options={"nordic_conventions_commercial_invoice_paper_copy": True},
        )

        self.assertListEqual(
            sorted(
                (message.code, message.level)
                for message in _plugin_messages(
                    advisors.run_advisors(request, _connection("postnord"), "shipping")
                )
            ),
            [
                ("nordic_conventions_attestation_conflict", "warning"),
                ("nordic_conventions_postnord_se_no_digital_invoice", "info"),
            ],
        )

    def test_no_attestation_options_match_the_unwrapped_rules(self):
        cases = [
            ("postnord", "SE", "NO", "postnord_parcel", fixture.customs("merchandise", True)),
            (
                "postnord",
                "SE",
                "NO",
                "postnord_postpaket_utrikes",
                fixture.customs(commercial_invoice=True),
            ),
            (
                "postnord",
                "SE",
                "US",
                "postnord_postpaket_utrikes",
                fixture.customs(commercial_invoice=True),
            ),
            ("postnord", "SE", "CH", "postnord_mypack_home", None),
            ("postnord", "FI", "GB", "postnord_parcel", None),
            ("postnord", "DK", "US", "postnord_parcel", None),
            (
                "dhl_freight_sweden",
                "SE",
                "NO",
                "109",
                fixture.customs("sample", True, voec_number="VOEC2024001"),
            ),
        ]

        for carrier, shipper, recipient, service, customs in cases:
            with self.subTest(lane=f"{shipper}-{recipient}", service=service):
                request = fixture.shipment(shipper, recipient, service, customs=customs)
                context = fixture.context(carrier)

                self.assertListEqual(
                    _advise_all(request, context),
                    [
                        message
                        for rule in procedures.RULES
                        for message in fixture.messages(rule, request, context)
                    ],
                )


class TestNordicConventionsHookGuard(unittest.TestCase):
    def tearDown(self):
        importlib.reload(nordic_conventions)

    def test_older_karrio_loads_the_plugin_without_advisors(self):
        with mock.patch.object(
            metadata, "PluginMetadata", PluginMetadataWithoutAdvisors
        ), self.assertLogs(nordic_conventions.__name__, logging.WARNING) as logs:
            module = importlib.reload(nordic_conventions)

        self.assertFalse(module.HOOK_AVAILABLE)
        self.assertIsInstance(module.METADATA, PluginMetadataWithoutAdvisors)
        self.assertFalse(hasattr(module.METADATA, "shipment_advisors"))
        self.assertEqual(len(logs.records), 1)
        self.assertIn("hook unavailable", logs.records[0].getMessage())


if __name__ == "__main__":
    unittest.main()
