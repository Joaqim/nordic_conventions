# Proposal

## Why

The plugin's DHL Freight Sweden advice departs from what the DHL Freight Sweden connector does in three places (karrio-dhl-freight-sweden branch `products-manual-country-lists`, commit 9e2b98f, and `main` at 7a2214d).

The connector books a territory code under its parent country, `AX` as `FI`, `JE`, `GG`, `IM`, and `XI` as `GB`, `FO` and `GL` as `DK`, and `IC` and `EA` as `ES` (`units.TERRITORY_PARENTS`), before its customs-area, lane, and excluded-postal-code checks, while the plugin reads the codes as given.
As a result a shipment to `XI` with a `BT` postcode is advised as leaving the EU VAT area, which the connector treats as inside for goods; `JE` and `GG` miss the Great Britain rules (the 650 kr reminder fee and the Parcel Connect agreement); and the product-lane warning added by `dhl-product-lanes-not-served` warns about lanes the connector books, such as Parcel Connect (109) to `AX`.

The customs-mode advice suggests customs handling standard or full service for every destination outside the EU VAT area, Åland included, although the connector refuses both to or from Åland (FI 22000-22999) with `AlandCustomsServiceError`, because DHL rejected them with 24003.
The same message omits the joint declaration, which the plugin already counts as a selected customs mode.

## What Changes

- Copies the connector's `TERRITORY_PARENTS` into `lanes.py` as `DHL_TERRITORY_PARENTS`, with a cross-check test against the connector that is skipped when the connector is not importable.
- For `dhl_freight_sweden` shipments, reads the shipper and recipient country codes through that mapping before the scope and EU VAT area checks, so the lane, the product-lane check, the Great Britain rules, and the customs rules see the country the connector books; `lanes.dhl_lane_served` maps the codes it is given in the same way.
  PostNord shipments keep their country codes as given.
- The customs-mode message names the joint declaration and its destinations, Norway and Switzerland, as the connector README's customs table does.
- To Åland the customs-mode message no longer suggests customs handling standard or full service; it states that DHL rejects them with 24003 and the connector refuses them, and names the own declaration, the joint declaration, or customs data without a customs service.
- New sources cite the connector's destinations page and README at 7a2214d.

The EU VAT area tables in `territories.py`, which must match the connector's, are not changed.
No advisory code, level, or attestation changes.

Out of scope: any connector change, the connector's excluded postal codes (for example `JE*` and `GY*` for 109 and 112), and PostNord territory handling.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `plugins/advisor-nordic-conventions`: adds "DHL Freight Sweden territory codes are read as their parent country", and modifies "DHL Freight Sweden needs a customs handling mode" and "DHL Freight Sweden products are not booked on lanes they do not serve".

## Impact

`lanes.py`, `sources.py`, `rules/dhl_freight_sweden.py`, tests, `README.md`, and the main specification.
DHL Freight Sweden advice to `XI` with a `BT` postcode disappears; `JE`, `GG`, and `IM` recipients receive the Great Britain advice; territory recipients are no longer warned as not served when the parent country is served; the customs-mode message text changes for every destination, and differs for Åland.
