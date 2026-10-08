# Design

## Copy and check

The plugin does not depend on the DHL Freight Sweden connector at runtime: connector facts it needs are copied into its own modules, and cross-check tests compare them with the connector when it is importable (`DHLCustomsOption`, the territory tables).
The product lanes follow the same convention, chosen by the operator over a runtime import of the connector's `units` module.
`lanes.py` holds the copy, because it already holds the connector's customs option names and PostNord service tables.

The copy keeps the connector's shape: per product code, a tuple of lanes, each a pair of frozen sets of shipper and recipient countries, built by the same helpers (`_from_sweden`, `_to_sweden`, `_to_and_from_sweden`) over country lists named as the connector names them.
The cross-check compares the lanes, the citations, and the unified-name-to-code pairs with `PRODUCT_LANES`, `PRODUCT_LANE_CITATIONS`, and `ShippingService`.

## Scope

The plugin advises only Swedish DHL Freight Sweden shippers sending outside the EU VAT area, so the advisory fires for every such lane outside a product's table: always for 107 and the domestic products, and for the export products when the recipient country is not in their list.
A service that names no known product is not advised.

## Territory codes

The connector books a territory code under its parent country (`AX` as `FI`, `JE`, `GG`, `IM`, and `XI` as `GB`, `FO` and `GL` as `DK`, `IC` and `EA` as `ES`).
The plugin compares the recipient country as given, so a shipment addressed to `AX` on 109 is warned although the connector books it as `FI`.
The queued territory-code change, which aligns the plugin with the connector's territory mapping, removes these warnings; this change does not add the mapping.
