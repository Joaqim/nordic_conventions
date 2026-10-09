# Proposal

## Why

DHL Freight Sweden publishes country-specific requirements for the lanes this plugin's users book: Cyprus demands documents (commercial invoice and packing list for Union status, T2L where applicable, recipient ID copies for private individuals), Greece demands sender and recipient VAT numbers, Poland SENT, Romania UIT, Hungary EKAER, and Spain a safety data sheet plus dangerous goods declaration.
The connector enforces or default-declares the reference-number rows but has no footprint at all for Cyprus or Spain, and the advisor — whose purpose is to warn the booker before booking — is barred by its own spec from advising on any intra-EU lane, so a Swedish shipper sending to Cyprus, Greece, Poland, Romania, Spain, or Hungary receives no advice today.

## What Changes

- Six new DHL Freight Sweden advisories, all non-blocking (`info`/`warning` only, as the SDK permits), each citing its source:
  - `dhl_freight_sweden_cyprus_documents` (`warning`): invoice and packing list for Union status, T2L where applicable, and recipient ID copies when the recipient appears to be a private individual.
  - `dhl_freight_sweden_greek_tax_ids` (`warning`): sender and recipient VAT numbers on Greek lanes for the products the connector enforces, naming the `EL000000000` fallback for private individuals.
  - `dhl_freight_sweden_sent_information` (`info`): SENT data may be required on Polish lanes; the connector validates consistency and defaults to declaring SENT free.
  - `dhl_freight_sweden_uit_information` (`warning` at or above the weight criterion, `info` below): Romanian UIT code or UIT FREE, naming the weight, value, and high-risk criteria.
  - `dhl_freight_sweden_ekaer_information` (`warning` at or above the weight criterion, `info` below): Hungarian EKAER number or EKAER FREE, naming the weight, value, and risky-goods criteria.
  - `dhl_freight_sweden_spain_dg_documents` (`warning`): safety data sheet and dangerous goods declaration for dangerous goods on Spanish lanes.
- The spec's shipper-scope requirement is modified: the categorical intra-EU exclusion is removed and destination scope becomes a property of each advisory's own requirement, all existing ones of which remain outside-EU.
- The README Destinations vocabulary (and the `AGENTS.md` rule that fixes it) gains the six named countries: Cyprus, Greece, Poland, Romania, Spain, Hungary.
- The README claim that EU destinations "need nothing" is corrected to name the six countries and link their advisories.
- A new `Source` constant cites the DHL Freight "Country-specific shipping requirements (English)" PDF at the dhl.com European road and rail help center, accessed 2026-10-09.
- A recorded decision keeps the customs row (row 7 of the table) covered by the existing EU VAT area and territory machinery rather than adding a verbatim country/postcode list.
- The connector repository is unchanged.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `plugins/advisor-nordic-conventions`: the shipper-scope requirement admits intra-EU destinations, six advisory requirements are added (one per country row above), and the Purpose paragraph no longer restricts the plugin to shipments leaving the EU VAT area.

## Impact

- Code: `karrio/plugins/advisor_nordic_conventions/rules/` (new rule module for the six rules), `lanes.py` (an EU-admitting lane gate alongside the existing outside-EU gate, which existing rules keep), `codes.py` (+6 codes), `sources.py` (+1 document constant), `procedures.py` only if a rule needs an attestation (none planned).
- Documentation: `README.md` (six Advisory reference rows, Destinations vocabulary, corrected EU sentence) and `AGENTS.md` (Destinations enum extension).
- Tests: a new test module with per-rule cases, fixture addresses for CY, GR-mainland, PL, RO, HU, and mainland ES, and connector-parity tests for the copied product sets (skipped when the connector is not importable).
- The karrio SDK needs no change: levels remain `info`/`warning`, and every payload fact the rules read (party tax ids, parcel weights, `dangerous_good` option, product code) is already on `ShipmentRequest`.
- The connector repo `karrio-dhl-freight-sweden` is untouched; its tables are consumed read-only through the existing importlib parity pattern.
