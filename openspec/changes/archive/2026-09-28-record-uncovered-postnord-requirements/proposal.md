# Proposal

## Why

A read-only survey on 2026-09-28 of the plugin at 146ce7e, the karrio PostNord connector on branch `feat-postnord-customs-invoice` (1b40eeb7e), and the karrio fork's facts note `docs/notes/customs/nordic-trade-documents-facts.md` ("Requirements by product (shipper in Sweden)") found PostNord requirements that the connector does not transmit, that the plugin does not advise, and that this specification does not record.
The plugin owner decided on 2026-09-28 to record these as known, unaddressed gaps before deciding whether and how to address them.
Recording them in the requirements they border keeps the specification from reading as complete coverage of those lanes.

## What Changes

This change records gaps and changes no code, advisory code, level, message text, or scenario outcome.

- Records that PostNord requires a CN23 for International Parcel (`postnord_postpaket_utrikes`, `91`) at every value, including non-commercial content (gift, sample, documents, returned goods) (FN:101, FN:111, W), that the connector sends CN22 declaration data for it (PNS lines 10 and 13-16, S), and that the plugin returns no advisory for non-commercial International Parcel outside Norway and only `nordic_conventions_postnord_se_no_digital_invoice`, without a CN23 statement, to Norway.
- Records that the Postpaket Utrikes terms §2 permit a proforma invoice only for gifts or samples (FN:111, FN:113, W), while `nordic_conventions_invoice_type_content_mismatch` applies only to PostNord parcel products and DHL Freight Sweden (`rules/invoice_type.py:32-40`), not to International Parcel.
- Records that the PostNord Finland and PostNord Denmark advisories apply only to PostNord parcel products (`rules/postnord.py:190`, `rules/postnord.py:237`), so International Parcel and letter services from Finnish and Danish shippers receive no advisory.
- Records that the connector builds `customs.commercial_invoice`, `customs.invoice`, and `customs.invoice_date` into the booking only in the customs invoice sent for parcel products (karrio `feat-postnord-customs-invoice` `shipment/create.py:608-635` and `shipment/create.py:775`, `units.py:377-385`, S), so for International Parcel and letter services it drops them without a warning; the commercial International Parcel advisory partly relays this by telling the consumer to supply the invoice, and no message or requirement records the drop.

Out of scope for this change: any fix to the connector or the plugin, any new advisory code or message text, and the goods-value thresholds (SEK 2 000, EUR 1 000, DKK 7 500), which remain recorded non-goals.
Post-shipment customs processes (printing, attaching, signing, electronic submission) remain consumer-owned, and the plugin relays duties as post-booking warnings.

## Maintenance note

`sources.py` and `lanes.py` cite PostNord connector line numbers pinned to older karrio commits, and those lines have moved.
`lanes.py:24-26` cites `units.py:264-285` at karrio `develop` 7a56ffa5b; on `feat-postnord-customs-invoice` (1b40eeb7e) `LETTER_SERVICES` and `INTERNATIONAL_PARCEL_SERVICE` are at `units.py:277-293`.
`sources.py:121` (`PN_POSTPAKET_CODE_91`) cites `units.py:146` for `postnord_postpaket_utrikes = "91"`, which is at `units.py:154` on that branch.
The main specification's purpose section cites the letter set at `units.py:269-284` on 7a56ffa5b.
Membership of the letter set and the International Parcel service remains guarded by the connector cross-check test (`tests/nordic_conventions/test_lanes.py:192-199`), so the moved line numbers affect citations only.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `plugins/nordic-conventions`: the requirements for commercial Postpaket Utrikes, PostNord Finland parcels, PostNord Denmark parcels, and the invoice type gain sentences recording the gaps above; no normative statement changes.

## Impact

- `openspec/specs/plugins/nordic-conventions/spec.md` after sync: recorded-gap sentences in four requirements and a clarified THEN clause in the scenario "Gift Postpaket Utrikes is not advised".
- No code, test, README, or consumer-facing change.
