# Proposal

## Why

Tullverket lists the Faroe Islands and Greenland outside both the EU customs union and the EU VAT area (FN:63, W), and the territory table already treats `FO` and `GL` country codes and `DK` 3800-3999 as outside.
An address under `DK` whose postal code carries an `FO` or `GL` territory prefix, such as `FO-100`, normalises to a code outside 3800-3999 and stays inside today, and so does a bare Faroese three-digit code such as `100`.
The archived change `dhl-manual-v5-26-and-territory-gaps` left this as an open question for the operator, who decided that both cases are outside.

## What Changes

- Under `DK`, an address is outside the EU VAT area when the leading prefix code removed from its postal code is `FO` or `GL`, whatever number follows, as in `FO-100`, `fo 100`, `FO100`, or `GL 3900`.
- Under `DK`, an address is outside the EU VAT area when its normalised postal code is exactly three digits, the Faroese format.
- Adds two tables to `territories.py` for these rules, `NON_EU_VAT_POSTAL_TERRITORY_PREFIXES` and `NON_EU_VAT_POSTAL_CODE_LENGTHS`; the existing tables keep their names and contents.

Bare four-digit `DK` codes outside 3800-3999 stay inside, and the `FO` and `GL` country codes stay outside.

Out of scope: any change to the connectors, which mirror the territory tables in a parallel change.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `plugins/nordic-conventions`: the EU VAT area requirement treats `FO`- and `GL`-prefixed and three-digit postal codes under `DK` as outside.

## Impact

`territories.py`, its tests, and the main specification.
No advisory code, level, trigger, message, or attestation changes; verdicts change only for `DK` addresses with an `FO` or `GL` postal prefix or a three-digit postal code.
