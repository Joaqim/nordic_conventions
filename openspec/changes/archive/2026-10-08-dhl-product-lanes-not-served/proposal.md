# Proposal

## Why

The DHL Freight Sweden connector now rates and books each product only on the lanes its "Valid countries" table in product manual v5.26 allows, refusing other bookings with `ProductLaneError` before the booking request (karrio-dhl-freight-sweden branch `products-manual-country-lists`, commit b54fcdb).
This plugin warns about only part of those lanes: Parcel Connect (109), Parcel Connect Plus (112), and Parcel Return Connect (107) to Switzerland, and 107 to Great Britain.
For a Swedish shipper outside the EU VAT area it says nothing about 107 to Norway, although 107 only returns a parcel from abroad to the original sender in Sweden (§5.15 p.65), nor about 109, 112, and the road-freight products to countries their tables leave out, nor about the domestic products, whose only valid country is Sweden.

## What Changes

- Copies the connector's `PRODUCT_LANES` table, its manual citations, and its unified names into `lanes.py` as `DHL_PRODUCT_LANES`, `DHL_PRODUCT_LANE_CITATIONS`, and `DHL_PRODUCT_CODES`, following the existing convention for connector facts such as `DHLCustomsOption`.
- Widens `advisor_nordic_conventions_dhl_freight_sweden_parcel_connect_not_served` to every DHL Freight Sweden product booked, by unified name or carrier code, on a lane outside its valid countries, such as 107 from Sweden to any country and 109, 112, 202, 205, 233, SPI, 601, or a domestic product to a country its table leaves out.
- States the product, its code, and the lane in the message, adds the Switzerland alternatives when the recipient is Switzerland, and adds that 107 returns parcels to Sweden when the product is 107.
- Cites a new manual source naming every "Valid countries" table.
- Adds a cross-check test that fails when the copied table differs from the connector's and is skipped when the connector is not importable, as the existing cross-checks are.

The advisory code keeps its value, because codes are consumer-facing; its README short name becomes "Product not served".
Territory country codes such as `AX`, `JE`, or `IC` are compared as given, because the plugin does not map territory codes to their parent country; the queued territory-code change owns that mapping.

Out of scope: any connector change, the Great Britain agreement advisory, the Åland customs-mode advice, and the joint declaration in the customs-mode message.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `plugins/advisor-nordic-conventions`: the requirement "DHL Freight Sweden Parcel Connect is not booked where it does not serve" becomes "DHL Freight Sweden products are not booked on lanes they do not serve".

## Impact

`lanes.py`, `sources.py`, `rules/dhl_freight_sweden.py`, tests, `README.md`, and the main specification.
The advisory fires on more lanes and its message text changes for Switzerland and Great Britain; no code, level, or attestation changes.
