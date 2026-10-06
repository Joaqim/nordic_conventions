# Design

## Context

`in_eu_vat_area` normalises a postal code by upper-casing and trimming it, removing one leading prefix code from `postal_prefix_codes(country)`, and removing spaces.
For `DK` the prefix codes are `DK`, `FO`, and `GL`, so `FO-100` normalises to `100`, which is outside `DK` 3800-3999, and the address stays inside.
The archived change `dhl-manual-v5-26-and-territory-gaps` recorded this as an open question.

## Decision

The operator decided that under `DK` an address is outside the EU VAT area when its postal code carried an `FO` or `GL` prefix, regardless of the number that follows, or when the normalised postal code is exactly three digits.
The basis is Tullverket's list, which places the Faroe Islands and Greenland outside both the customs union and the VAT area (FN:63, W), the same basis the archived change gave for `DK` 3800-3999 alongside DHL's range.
Faroese postal codes have three digits, and Danish ones have four, so a three-digit code under `DK` addresses the Faroe Islands.

Two tables carry the rules, shaped like `EU_VAT_POSTAL_PREFIXES` so the connectors can mirror them:

| Table | Content | Meaning |
| --- | --- | --- |
| `NON_EU_VAT_POSTAL_TERRITORY_PREFIXES` | `("DK", "FO")`, `("DK", "GL")` | A removed prefix code that places the address outside. |
| `NON_EU_VAT_POSTAL_CODE_LENGTHS` | `("DK", 3)` | A purely numeric normalised postal code of this many digits places the address outside. |

`AX`, `IC`, and `EA` stay prefix codes that only normalise, because the operator's decision covers `FO` and `GL` only.

## Open questions

- Whether the connector parity test should also compare the two new tables once the PostNord and DHL Freight Sweden connectors carry them.
