# Design

## Copy and check

`DHL_TERRITORY_PARENTS` in `lanes.py` copies the connector's `TERRITORY_PARENTS`, built as the connector builds it: the numeric-postcode territories of `territories.NUMERIC_POSTAL_TERRITORY_PARENTS` (`AX`, `FO`, `GL`, `IC`, `EA`) plus `JE`, `GG`, `IM`, and `XI` under `GB`.
A test in `test_lanes.py` compares it with `units.TERRITORY_PARENTS` and is skipped when the connector is not importable, as the other cross-checks are; it runs in the parity suite with `PYTHONPATH` naming the connector.

## Where the mapping applies

The connector replaces a party's territory code by its parent before every check (`shipment/create.py` `shipment_request`), so the plugin maps once, in `lane_of`, before the scope and EU VAT area checks, and only for `dhl_freight_sweden`.
Every DHL Freight Sweden rule reads the mapped `Lane.shipper_country` and `Lane.recipient_country`: the product-lane check, the Great Britain reminder fee and agreement, the Switzerland and Norway destinations, and the Åland test.
Messages and the `details` lane name the mapped country, as the connector's `ProductLaneError` does.
`dhl_lane_served` maps the codes it receives as well, so a caller passing a raw territory code gets the connector's answer.
PostNord shipments are not mapped, because the PostNord connector sends the codes as given.

## EU VAT area

`territories.py` and its parity-bound tables do not change; the mapping only changes which country code they are asked about.
After mapping, `XI` with a `BT` postcode is `GB` `BT…`, inside the area for goods, so the shipment is out of scope, as the connector drops its customs data; `XI` with another postcode is outside.
`AX` 22100 becomes `FI` 22100 and stays outside through the `FI` 22000-22999 range; `IC`, `EA`, `FO`, and `GL` stay outside through their parent's ranges and the Faroese three-digit rule.
An `AX`, `IC`, `EA`, `FO`, or `GL` address whose postcode falls in none of those ranges becomes inside, matching the connector; before this change the plugin treated these codes as outside whatever the postcode.

## Åland

The connector's rule (`_check_aland_customs_services`, `units.in_aland`): when the shipper or the recipient, after mapping, is `FI` with a normalised postcode in 22000-22999, customs handling standard and full service are refused before the booking request; the own declaration, the joint declaration, and no customs service pass, and DHL booked 109 to FI 22100 with customs data and no customs service.
The customs-mode advisory keeps its trigger and level; for an Åland recipient its message drops standard and full service and names the alternatives the connector accepts.
Because the plugin advises only Swedish shippers, only the recipient can be in Åland.

## Specification ordering

The delta modifies "DHL Freight Sweden products are not booked on lanes they do not serve", the name the unarchived change `dhl-product-lanes-not-served` gives that requirement, so `dhl-product-lanes-not-served` must be archived first.
