# Proposal

## Why

DHL Freight Sweden published product manual v5.26 (updated 2026-10-01, valid from 2026-11-01), listed at <https://dhlpaket.se/dashboard/specifications/products/>, and the DHL Freight Sweden connector now follows it, while this plugin's sources and DHL requirements still cite v5.23.
v5.26 changes facts the plugin restates: Parcel Connect Plus (112) now serves France (excluding 97100-99999) and no longer excludes Åland, product 232 and PPI are removed, and products 202, 205, and 233 are renamed Road Freight Standard, Road Freight Direct, and Road Freight Priority.
The connector's sandbox also rejected a 112 booking from Sweden to Great Britain made without the separate agreement (22005 and 22026), which corroborates the agreement advisory.

The territory table misses two groups of special territories that are addressed under a member state's country code: French overseas departments under `FR` (postal codes 97000-97999) and the Faroe Islands and Greenland under `DK` (3800-3999), which Tullverket lists outside the EU VAT area.
A postal code written with its country prefix, such as `FI-22100`, `DK-3900`, or `fi 22100`, is not purely numeric, so the table currently falls back to the member state's inside verdict for it.

## What Changes

- Cites manual v5.26 by its listing page, version, dates, and sha256, and moves every manual section and page reference to v5.26.
- Restates the Parcel Connect country facts from v5.26 and names the Switzerland alternatives by their v5.26 product names in the `nordic_conventions_dhl_freight_sweden_parcel_connect_not_served` message.
- Adds the connector's committed 112 SE to GB rejection evidence as a source of `nordic_conventions_dhl_freight_sweden_parcel_connect_gb_agreement`.
- Adds `("FR", 97000, 97999)` and `("DK", 3800, 3999)` to `NON_EU_VAT_POSTAL_RANGES`.
- Removes a leading copy of the address's own country code, followed by a hyphen, spaces, or a digit, from the postal code before the range and prefix comparisons; Northern Ireland stays inside.
- Records candidate territory advisories and a way to run the connector parity test in the design, for operator decision.

Out of scope: new advisories, codes, or attestations; any change to the connectors, which a parallel change in the DHL Freight Sweden connector mirrors.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `plugins/nordic-conventions`: the EU VAT area requirement gains two postal ranges and country-prefix normalisation; the six DHL Freight Sweden manual-backed requirements cite v5.26.

## Impact

`territories.py`, `sources.py`, `rules/dhl_freight_sweden.py`, tests, `README.md`, and the main specification.
No advisory code, level, trigger, or attestation changes; verdicts change only for `FR` 97000-97999, `DK` 3800-3999, and country-prefixed postal codes.
