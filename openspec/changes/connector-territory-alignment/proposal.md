# Proposal

## Why

The plugin's DHL Freight Sweden advice departs from what the DHL Freight Sweden connector does in three places (karrio-dhl-freight-sweden branch `products-manual-country-lists`, commit 9e2b98f, and `main` at 7a2214d).

The connector books a territory code under its parent country, `AX` as `FI`, `JE`, `GG`, `IM`, and `XI` as `GB`, `FO` and `GL` as `DK`, and `IC` and `EA` as `ES` (`units.TERRITORY_PARENTS`), before its customs-area, lane, and excluded-postal-code checks, while the plugin reads the codes as given.
As a result a shipment to `XI` with a `BT` postcode is advised as leaving the EU VAT area, which the connector treats as inside for goods; `JE` and `GG` miss the Great Britain rules (the 650 kr reminder fee and the Parcel Connect agreement); and the product-lane warning added by `dhl-product-lanes-not-served` warns about lanes the connector books, such as Parcel Connect (109) to `AX`.

The customs-mode advice suggests customs handling standard or full service for every destination outside the EU VAT area, Åland included, although the connector refuses both to or from Åland (FI 22000-22999) with `AlandCustomsServiceError`, because DHL rejected them with 24003.
The same message omits the joint declaration, which the plugin already counts as a selected customs mode.

The plugin also does not know the postal codes the connector excludes per product (`POSTAL_CODE_EXCLUSIONS` and `POSTAL_CODE_PATTERN_EXCLUSIONS`), so Parcel Connect (109) or Parcel Connect Plus (112) to a Jersey or Guernsey postcode receives the Great Britain agreement warning although the connector refuses the booking with `ExcludedDestinationError`.

## What Changes

- Copies the connector's `TERRITORY_PARENTS` into `lanes.py` as `DHL_TERRITORY_PARENTS`, with a cross-check test against the connector that is skipped when the connector is not importable.
- For `dhl_freight_sweden` shipments, reads the shipper and recipient country codes through that mapping before the scope and EU VAT area checks, so the lane, the product-lane check, the Great Britain rules, and the customs rules see the country the connector books; `lanes.dhl_lane_served` maps the codes it is given in the same way.
  PostNord shipments keep their country codes as given.
- The customs-mode message names the joint declaration and its destinations, Norway and Switzerland, as the connector README's customs table does.
- To Åland the customs-mode advisory is not returned, because a booking with customs data and no customs service is accepted.
- A new advisory, `advisor_nordic_conventions_dhl_freight_sweden_aland_customs_service_rejected` (warning), fires to Åland only when customs handling standard or full service is selected, which DHL rejects with 24003 and the connector refuses; it names the own declaration or customs data without a customs service, not the joint declaration, which the connector refuses outside Norway and Switzerland.
- Copies the connector's `TERRITORY_POSTAL_CODES` into `lanes.py` with a cross-check test, and adds `advisor_nordic_conventions_dhl_freight_sweden_territory_postal_code_mismatch` (warning) for a recipient territory code `AX`, `IC`, `EA`, `FO`, or `GL` whose postal code is missing or outside the territory, which the connector refuses with `TerritoryPostalCodeError` (karrio-dhl-freight-sweden 142b62d); it fires whether or not the recipient read under its parent is outside the EU VAT area.
- Copies the connector's `JOINT_DECLARATION_COUNTRIES` (f86c8ac) into `lanes.py` with a cross-check test and names its countries in the customs-mode message.
- Adds `advisor_nordic_conventions_dhl_freight_sweden_joint_declaration_destination` (warning) when the joint declaration is selected across the EU VAT area border for a recipient country, after the territory mapping, other than Norway or Switzerland, which the connector refuses with `JointDeclarationDestinationError` (f86c8ac); inside the area the connector only drops customs services, so the plugin says nothing.
- Copies the connector's excluded postal codes, `POSTAL_CODE_EXCLUSIONS` with the postal code formats and `POSTAL_CODE_PATTERN_EXCLUSIONS`, into a new `exclusions.py`, with a cross-check test against the connector, and returns the not-served warning for an excluded postal code after the territory mapping; the Great Britain agreement warning is not returned for an excluded postcode, so 109 and 112 to `JE*` and `GY*` are warned as not served.
- New sources cite the connector's destinations page and README at 7a2214d.

The EU VAT area tables in `territories.py`, which must match the connector's, are not changed.
Three advisory codes are added; no existing code, level, or attestation changes.

Out of scope: any connector change and PostNord territory handling.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `plugins/advisor-nordic-conventions`: adds "DHL Freight Sweden territory codes are read as their parent country", "DHL Freight Sweden territory codes carry a postal code of the territory", "DHL Freight Sweden joint declaration is selected only to Norway or Switzerland", and "DHL Freight Sweden customs handling is not selected to Åland", and modifies "DHL Freight Sweden needs a customs handling mode", "Advisory answering procedures", "DHL Freight Sweden Parcel Connect serves Great Britain only by separate agreement", and "DHL Freight Sweden products are not booked on lanes they do not serve".

## Impact

`lanes.py`, the new `exclusions.py`, `territories.py` (a public postal code normaliser), `codes.py`, `procedures.py`, `sources.py`, `rules/dhl_freight_sweden.py`, tests, `README.md`, and the main specification.
DHL Freight Sweden advice to `XI` with a `BT` postcode disappears; `JE`, `GG`, and `IM` recipients receive the Great Britain advice; territory recipients are no longer warned as not served when the parent country is served; the customs-mode message text changes for every destination and is not returned for Åland; excluded postcodes are warned as not served.
