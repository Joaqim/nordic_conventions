---
title: "Scope: when the plugin advises"
---

The plugin advises only at shipment creation, never at rating.
It advises on `postnord` shipments from Sweden, Denmark, or Finland and on `dhl_freight_sweden` shipments from Sweden, when the shipper is inside the EU VAT area; for return shipments the returning party is the shipper, because the SDK swaps shipper and recipient before advisors run.
Each advisory covers the destinations its own requirement names: the general advisories a recipient outside the EU VAT area, the country-specific shipping advisories their named countries.
A shipment is commercial when it carries customs data and either `commercial_invoice` is true or its content is sale-like — a `content_type` that is omitted or none of gift, sample, documents, or return merchandise.

The EU VAT area follows Tullverket's list of EU customs and fiscal territories for goods movements rather than karrio's `EUCountry`; Northern Ireland is inside for goods, while Åland, the Canary Islands, and the other special territories are outside ([Territories](territories.md)).
For `dhl_freight_sweden` shipments the plugin reads a territory country code as the DHL Freight Sweden connector books it, under its parent country, before any check, so `XI` with a `BT` postcode is inside the EU VAT area and Jersey, Guernsey, and the Isle of Man receive the Great Britain advice; the mapping is in [DHL territory codes](territories.md#dhl-territory-codes), and PostNord country codes are read as given.
Beyond the outside-EU recipient condition, the six country-specific shipping advisories advise on their countries inside the EU VAT area, and [Territory postal code](advisories.md#advisor_nordic_conventions_dhl_freight_sweden_territory_postal_code_mismatch) is returned for a DHL Freight Sweden recipient territory code whose postal code lies outside the territory even when the parent's mainland is inside the area.

The full territory table and the determinations above are specified in the [specification](../../openspec/specs/plugins/advisor-nordic-conventions/spec.md), which is normative when this page and the code disagree about intended behaviour.

## Compliance

The advisories are reminders, not compliance guarantees.
The consumer owns compliance with carrier terms and customs rules and should verify each advisory against the cited sources, which may change.
An attestation is the consumer's own commitment to perform the procedure; the plugin checks claims against the conventions that govern the lane, not against the consumer's warehouse.

## Non-goals

No advice at rating time, no per-organisation overrides or connection-level attestation defaults, and no advisories for Norwegian shippers.
No goods-value thresholds (SEK 2 000, EUR 1 000, DKK 7 500), CN22 or CN23 selection guidance, invoice-content checks, or CN22 or CN23 advice for PostNord letters.
No advisory on splitting goods sold as one unit into separately packed consignments to Norway to stay under the VOEC value limit, which the [Skatteetaten VOEC guidelines](https://www.skatteetaten.no/globalassets/bedrift-og-organisasjon/voec/voec-guidelines-mars-2024.pdf) (March 2024) prohibit: an advisor sees one shipment request, with no record of the sale or of other consignments, so a split cannot be detected reliably.
Nothing the connectors already enforce, such as field errors for missing customs data or the mapping of `commercial_invoice` to the invoice type.
The plugin never reads connection credentials and makes no network calls.
Known, undecided coverage gaps are recorded inside the requirements they border in the [specification](../../openspec/specs/plugins/advisor-nordic-conventions/spec.md).
