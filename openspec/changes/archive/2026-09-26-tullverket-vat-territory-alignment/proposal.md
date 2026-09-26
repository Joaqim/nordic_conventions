# Proposal

## Why

Tullverket's list of EU customs and fiscal territories (FN:58-65, W) treats Monaco and Northern Ireland as EU and Mount Athos as inside the customs union but outside the VAT area, while the plugin and both connectors follow the connectors' country-level treatment: Monaco (`MC`) and the whole United Kingdom, including Northern Ireland, sit outside the EU VAT area, and Mount Athos (`GR` 63086) sits inside it with Greece.
A Swedish shipment to Northern Ireland therefore receives export-document advisories although Northern Ireland is inside the EU VAT area for goods (FN:64, W), a shipment to Monaco receives advisories although Monaco is treated as EU, and a shipment to Mount Athos receives none although customs formalities are due from Sweden.
The nordic-trade-document-conventions change deferred exactly this divergence to a later change covering both connectors and this plugin, and post-Brexit goods volume to Northern Ireland makes that deferral live now.

## What Changes

- The EU VAT area test stops mirroring the connectors' country-level shortcut and follows Tullverket for goods movements: Northern Ireland, identified as `GB` with a postal code beginning `BT`, is inside, Monaco (`MC`) is inside, and Mount Athos (`GR` 63086) joins Åland and the Canary Islands as a postal-code exclusion inside a member state.
- The territory table gains an inclusion mechanism next to the existing exclusion ranges: a `(country, postal prefix)` tuple set that admits Northern Ireland's alphanumeric `BT` postcodes, which the purely numeric range comparison cannot express.
- Monaco's French-style postal codes (`FR` 98000-98999) keep their current inside verdict through the `FR` country code, so only the `MC` country code changes verdict.
- Both karrio connectors, PostNord and DHL Freight Sweden, receive the same three changes in the karrio fork together with their specs (PNS, DFS) and the facts note, so the plugin's cross-check test against the connectors' tables remains an equality check rather than a divergence record.
- The README drops its non-goal sentence that Monaco, Northern Ireland, and Mount Athos follow the connectors' treatment.
- The helper name `in_eu_vat_area` stays; its documentation states that the Northern Ireland verdict is the goods-movement verdict, which is the only verdict this plugin and the connectors need, because they decide customs handling for goods shipments.

Out of scope for this change: territory semantics for services VAT, where Northern Ireland is outside the EU VAT area and the plugin never advises; San Marino, the Faroe Islands, Greenland, Andorra, the Vatican, and the Channel Islands, whose country-level outside verdict already matches Tullverket; changes to karrio's `EUCountry`, which lacks `AX`, `XI`, and `MC` and to which the connectors already append `GR` and will append `MC` the same way; and everything the nordic-trade-document-conventions change already deferred for other reasons (value thresholds, CN22/CN23 selection, invoice-content checks).

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `plugins/nordic-conventions`: the EU VAT area requirement stops deferring Monaco, Northern Ireland, and Mount Athos to the connectors' country-level treatment and states their Tullverket-aligned verdicts for goods movements, with new scenarios for each of the three territories and for Great Britain outside Northern Ireland.

## Impact

- This repository: `karrio/plugins/nordic_conventions/territories.py` gains `MC`, the Mount Athos range, and the inclusion prefix tuple; `tests/nordic_conventions/test_territories.py` gains the new territory cases and extends the connector cross-check to the prefix tuple; the README territory sentences change.
- The karrio fork (Joaqim/karrio): both connectors' `units.py` territory tables and `in_eu_vat_area` helpers, their connector unit tests, the PNS and DFS spec deltas, and facts-note additions live on a feature branch with the spec and note work on `docs-openspec`; `develop` is regenerated after merge, never committed to directly.
- Consumers: shipments from the Nordic scope to Northern Ireland or Monaco stop receiving export-document advisories, and the connectors stop omitting customs for them on the inside verdict; shipments to `GR` 63086 start receiving advisories; no advisory codes, levels, or message contracts change.
- Advisory messages are non-blocking, so the changed verdicts alter advice, never bookings.
