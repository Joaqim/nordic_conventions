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
An `AX`, `IC`, `EA`, `FO`, or `GL` address whose postcode falls in none of those ranges becomes inside, so the lane advisories stop; the connector refuses such a booking (142b62d), and the territory postal code advisory below warns about it.
Before this change the plugin treated these codes as outside whatever the postcode.

## Åland

The connector's rule (`_check_aland_customs_services`, `units.in_aland`): when the shipper or the recipient, after mapping, is `FI` with a normalised postcode in 22000-22999, customs handling standard and full service are refused before the booking request; the own declaration, the joint declaration, and no customs service pass, and DHL booked 109 to FI 22100 with customs data and no customs service.
The customs-mode advisory is not returned for an Åland recipient, because a booking without a customs service is accepted there.
A separate code, `advisor_nordic_conventions_dhl_freight_sweden_aland_customs_service_rejected`, fires only when standard or full service is selected, read through `lane.dhl_customs_options`, which parses the unified option names with karrio's option helper as the connector's initializer does.
A new code rather than the customs-mode code is used because the shipment has selected a customs mode; a consumer keying on `customs_mode_missing` would otherwise read a selected mode as a missing one.
Its message names the own declaration and customs data without a customs service, and not the joint declaration, which the connector refuses outside Norway and Switzerland.
`DHL_ALAND_POSTAL_RANGE` copies the connector's `ALAND_POSTAL_RANGE`, and a test checks the connector's `ALAND_REJECTED_CUSTOMS_SERVICES` against the two services the message names.
Because the plugin advises only Swedish shippers, only the recipient can be in Åland.

## Excluded postal codes

`exclusions.py` copies the connector's `POSTAL_CODE_FORMATS`, `POSTAL_CODE_EXCLUSIONS`, and `POSTAL_CODE_PATTERN_EXCLUSIONS` as named tuples with the connector's fields, product codes as strings, so the cross-check compares them as plain tuples.
`POSTAL_CODE_PATTERN_EXCLUSIONS` is copied with `POSTAL_CODE_EXCLUSIONS` because the `JE*` and `GY*` exclusions of 109 and 112 live there.
The verdicts follow the connector: a numeric range compares the digits the country's format keys on, and a code outside the format has no verdict; a Danish range marked for the territories also excludes a code led by `FO` or `GL` or of three digits; a pattern is matched with `fnmatchcase` against the normalised code.
The connector refuses a booking whose postal code has no verdict ("requires a postal code"); the plugin warns only on an excluded verdict, leaving malformed and missing codes to the connector's error.
The check runs on the mapped country codes, as the connector's does, and in the not-served rule after the lane check, so a lane outside the product's countries keeps the lane message; the Great Britain agreement rule skips an excluded recipient postcode.

## Territory postal codes

The connector refuses a territory code `AX`, `IC`, `EA`, `FO`, or `GL` whose postal code is missing or outside the territory before mapping it (`TERRITORY_POSTAL_CODES`, `TerritoryPostalCodeError`, 142b62d).
Mapped, such a recipient is usually the parent's mainland and inside the EU VAT area, where `lane_of` returns no lane, so the advisory reads the lane through `shipper_lane_of`, which applies every scope condition of `lane_of` except the recipient's EU VAT area.
`DHLTerritoryPostalCodes` copies the connector's named tuple with its `describe` and `matches`, and the cross-check compares the table as plain tuples.
Only the recipient is checked, because a shipper with a territory code is never in Sweden after mapping and is out of scope.

## Specification ordering

The delta modifies "DHL Freight Sweden products are not booked on lanes they do not serve", the name the unarchived change `dhl-product-lanes-not-served` gives that requirement, so `dhl-product-lanes-not-served` must be archived first.
