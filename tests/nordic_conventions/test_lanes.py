import importlib
import unittest

import karrio.plugins.nordic_conventions.lanes as lanes
from . import fixture


def _connector_units(carrier_name: str):
    try:
        return importlib.import_module(f"karrio.providers.{carrier_name}.units")
    except ImportError:
        return None


def _lane(shipper, recipient, service="postnord_parcel", carrier="postnord", **kwargs):
    return lanes.lane_of(
        fixture.shipment(shipper, recipient, service, **kwargs),
        fixture.context(carrier),
    )


class TestNordicConventionsCommercialContent(unittest.TestCase):
    def _determination(self, **customs):
        request = fixture.shipment(
            "SE", "NO", "postnord_parcel", customs=fixture.customs(**customs)
        )
        return lanes.sale_like(request.customs), lanes.commercial(request.customs)

    def test_merchandise_is_sale_like(self):
        self.assertTupleEqual(
            self._determination(content_type="MERCHANDISE", commercial_invoice=False),
            (True, True),
        )

    def test_omitted_content_type_is_sale_like(self):
        self.assertTupleEqual(self._determination(), (True, True))

    def test_gift_with_commercial_flag_is_commercial_but_not_sale_like(self):
        self.assertTupleEqual(
            self._determination(content_type="gift", commercial_invoice=True),
            (False, True),
        )

    def test_return_merchandise_without_commercial_flag_is_not_commercial(self):
        self.assertTupleEqual(
            self._determination(
                content_type="return_merchandise", commercial_invoice=False
            ),
            (False, False),
        )

    def test_shipment_without_customs_is_neither(self):
        request = fixture.shipment("SE", "NO", "postnord_parcel")
        self.assertTupleEqual(
            (lanes.sale_like(request.customs), lanes.commercial(request.customs)),
            (False, False),
        )


class TestNordicConventionsScope(unittest.TestCase):
    def test_rating_receives_no_advice(self):
        self.assertIsNone(
            lanes.lane_of(
                fixture.shipment("SE", "NO", "postnord_parcel"),
                fixture.context("postnord", operation="rating"),
            )
        )

    def test_other_carriers_receive_no_advice(self):
        self.assertIsNone(_lane("SE", "NO", "bring_business_parcel", carrier="bring"))

    def test_norwegian_shippers_receive_no_advice(self):
        self.assertIsNone(_lane("NO", "SE"))

    def test_danish_shippers_receive_no_dhl_freight_sweden_advice(self):
        self.assertIsNone(
            _lane(
                "DK",
                "NO",
                "dhl_freight_sweden_parcel_connect_b2c",
                carrier="dhl_freight_sweden",
            )
        )

    def test_intra_eu_shipments_receive_no_advice(self):
        self.assertListEqual(
            [
                _lane("SE", "DE"),
                _lane(
                    "SE",
                    "DE",
                    "dhl_freight_sweden_parcel_connect_b2c",
                    carrier="dhl_freight_sweden",
                ),
            ],
            [None, None],
        )

    def test_return_from_norway_receives_no_advice(self):
        request = fixture.shipment("NO", "SE", "postnord_parcel", is_return=True)

        self.assertEqual(request.shipper.country_code, "NO")
        self.assertIsNone(lanes.lane_of(request, fixture.context("postnord")))

    def test_aland_shipper_receives_no_advice(self):
        self.assertIsNone(_lane("AX", "NO"))

    def test_aland_recipient_by_postal_code_is_in_scope(self):
        self.assertEqual(_lane("SE", "AX").recipient_country, "FI")

    def test_greece_recipient_is_out_of_scope(self):
        self.assertIsNone(
            _lane(
                "SE",
                "GR",
                "dhl_freight_sweden_road_freight_standard",
                carrier="dhl_freight_sweden",
            )
        )

    def test_canary_islands_recipient_by_postal_code_is_in_scope(self):
        self.assertIsNotNone(
            _lane(
                "SE",
                "IC",
                "dhl_freight_sweden_road_freight_standard",
                carrier="dhl_freight_sweden",
            )
        )

    def test_lane_of_swedish_postnord_shipment_to_norway(self):
        lane = _lane(
            "SE",
            "NO",
            "postnord_parcel",
            customs=fixture.customs("GIFT", voec_number="NO123"),
            options=dict(dhl_freight_sweden_customs_handling_standard=True),
        )

        self.assertEqual(
            lane,
            lanes.Lane(
                carrier_name="postnord",
                shipper_country="SE",
                recipient_country="NO",
                to_norway=True,
                service="postnord_parcel",
                postnord_product_group=lanes.PARCEL,
                has_customs=True,
                commercial_invoice=False,
                content_type="gift",
                voec_number="NO123",
                dhl_customs_options=frozenset(
                    {"dhl_freight_sweden_customs_handling_standard"}
                ),
                sale_like=False,
                commercial=False,
            ),
        )


class TestNordicConventionsProductGroups(unittest.TestCase):
    def test_postnord_product_groups_by_name_and_code(self):
        self.assertDictEqual(
            {
                service: lanes.postnord_product_group(service)
                for service in (
                    "postnord_parcel",
                    "18",
                    "postnord_export_letter",
                    "UX",
                    "postnord_postpaket_utrikes",
                    "91",
                )
            },
            {
                "postnord_parcel": lanes.PARCEL,
                "18": lanes.PARCEL,
                "postnord_export_letter": lanes.LETTER,
                "UX": lanes.LETTER,
                "postnord_postpaket_utrikes": lanes.INTERNATIONAL_PARCEL,
                "91": lanes.INTERNATIONAL_PARCEL,
            },
        )

    def test_postnord_services_match_connector(self):
        units = _connector_units("postnord")
        if units is None:
            self.skipTest("postnord connector is not importable")

        self.assertDictEqual(
            lanes.POSTNORD_LETTER_SERVICES,
            {service.name: service.value for service in units.LETTER_SERVICES},
        )
        self.assertTupleEqual(
            lanes.POSTNORD_INTERNATIONAL_PARCEL,
            (
                units.INTERNATIONAL_PARCEL_SERVICE.name,
                units.INTERNATIONAL_PARCEL_SERVICE.value,
            ),
        )

    def test_dhl_customs_options_match_connector(self):
        units = _connector_units("dhl_freight_sweden")
        if units is None:
            self.skipTest("dhl_freight_sweden connector is not importable")

        self.assertDictEqual(
            {option.name: option.value.code for option in lanes.DHLCustomsOption},
            {
                option.name: units.ShippingOption[option.name].value.code
                for option in lanes.DHLCustomsOption
            },
        )


if __name__ == "__main__":
    unittest.main()
