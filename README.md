# karrio.advisor_nordic_conventions

Advisor-only extension for the [karrio](https://pypi.org/project/karrio) shipping SDK.
It adds non-blocking trade-document advisories to PostNord and DHL Freight Sweden shipment responses for shippers in Sweden, Denmark, and Finland sending outside the EU VAT area, each advisory stating what the consumer still owns and citing the carrier or authority source it rests on.
The plugin declares shipment advisors only: no carrier mapper, proxy, settings, or address validator, and no shipment is blocked or altered.
The reference pages behind this guide are published at <https://primepack-ab.github.io/karrio-advisor-nordic-conventions/>.

> **Status: pending an unmerged karrio feature.**
> The advisories need a karrio SDK with the shipment advisors hook, which only the [karrio fork](https://github.com/Joaqim/karrio) branch `feat-shipment-advisors` provides.
> With released karrio the plugin installs and loads but registers no advisors, so it changes nothing.
> Until the feature merges and ships in a karrio release, a working setup requires a local checkout of the fork; see [Development](#development).

## Installation

```bash
pip install "git+https://github.com/PrimePack-AB/karrio-advisor-nordic-conventions.git"
```

The plugin registers through the `karrio.plugins` entry point group under the id `advisor_nordic_conventions` and is reported with the plugin type `advisor`.
Installing it adds messages to shipment responses; uninstalling it removes them.
The advisories need a karrio SDK with the shipment advisors hook; the fork requirement and how to install against it are in the [installation guide](docs/guides/installation.md).

## Requirements at a glance

What the carriers ask for goods sent from Sweden, Denmark, or Finland to outside the EU VAT area; each cell links to its advisory.

| Shipment | Norway | Other non-EU (incl. GB) |
|---|---|---|
| PostNord SE parcel | [Invoice sent digitally](docs/concepts/advisories.md#advisor_nordic_conventions_postnord_se_no_digital_invoice) (reminder with customs data) | [3× English invoice in pocket on parcel 1](docs/concepts/advisories.md#advisor_nordic_conventions_postnord_se_export_paper_invoice) |
| PostNord SE 91, commercial | [CN23 + digital invoice](docs/concepts/advisories.md#advisor_nordic_conventions_postnord_se_postpaket_commercial_invoice) (supply yourself) | [CN23 + 3× invoice with parcel](docs/concepts/advisories.md#advisor_nordic_conventions_postnord_se_postpaket_commercial_invoice) (supply yourself) |
| PostNord SE 91, non-commercial | [Invoice sent digitally](docs/concepts/advisories.md#advisor_nordic_conventions_postnord_se_no_digital_invoice) | — |
| PostNord SE letter | [Invoice sent digitally; export, REK letters + VOEC](docs/concepts/advisories.md#advisor_nordic_conventions_postnord_se_no_digital_invoice) | — |
| PostNord FI parcel | [E-invoice before shipping](docs/concepts/advisories.md#advisor_nordic_conventions_postnord_fi_export_invoice) | [3× signed English invoice](docs/concepts/advisories.md#advisor_nordic_conventions_postnord_fi_export_invoice) |
| PostNord DK parcel | [2× invoice in visible pocket](docs/concepts/advisories.md#advisor_nordic_conventions_postnord_dk_export_documents) | [CH, LI 3×, GB 2× invoice; else CN23 + 2× invoice](docs/concepts/advisories.md#advisor_nordic_conventions_postnord_dk_export_documents) |
| PostNord FI or DK 91, letter | — | — |
| DHL Freight SE, any | [Customs mode](docs/concepts/advisories.md#advisor_nordic_conventions_dhl_freight_sweden_customs_mode_missing) + [invoice copy](docs/concepts/advisories.md#advisor_nordic_conventions_dhl_freight_sweden_invoice_copy) + [VOEC on label if booked](docs/concepts/advisories.md#advisor_nordic_conventions_dhl_freight_sweden_voec_marking) | [Customs mode](docs/concepts/advisories.md#advisor_nordic_conventions_dhl_freight_sweden_customs_mode_missing) + [invoice copy](docs/concepts/advisories.md#advisor_nordic_conventions_dhl_freight_sweden_invoice_copy); [Åland: no standard or full service](docs/concepts/advisories.md#advisor_nordic_conventions_dhl_freight_sweden_aland_customs_service_rejected); [territory code needs a territory postcode](docs/concepts/advisories.md#advisor_nordic_conventions_dhl_freight_sweden_territory_postal_code_mismatch); [joint declaration only to NO or CH](docs/concepts/advisories.md#advisor_nordic_conventions_dhl_freight_sweden_joint_declaration_destination) |
| DHL Parcel Connect (109) | [+ 2 document copies outside package](docs/concepts/advisories.md#advisor_nordic_conventions_dhl_freight_sweden_attached_documents); [not served to Svalbard or Jan Mayen](docs/concepts/advisories.md#advisor_nordic_conventions_dhl_freight_sweden_parcel_connect_not_served) | [+ 2 document copies outside package](docs/concepts/advisories.md#advisor_nordic_conventions_dhl_freight_sweden_attached_documents); [not served outside its countries or postal codes, e.g. CH, JE](docs/concepts/advisories.md#advisor_nordic_conventions_dhl_freight_sweden_parcel_connect_not_served); [Great Britain by agreement only](docs/concepts/advisories.md#advisor_nordic_conventions_dhl_freight_sweden_parcel_connect_gb_agreement) |
| DHL Parcel Connect Plus (112) | [Not served to Svalbard or Jan Mayen](docs/concepts/advisories.md#advisor_nordic_conventions_dhl_freight_sweden_parcel_connect_not_served) | [Not served outside its countries or postal codes, e.g. CH, JE](docs/concepts/advisories.md#advisor_nordic_conventions_dhl_freight_sweden_parcel_connect_not_served); [Great Britain by agreement only](docs/concepts/advisories.md#advisor_nordic_conventions_dhl_freight_sweden_parcel_connect_gb_agreement) |
| DHL Parcel Return Connect (107) | [Not served from Sweden](docs/concepts/advisories.md#advisor_nordic_conventions_dhl_freight_sweden_parcel_connect_not_served) | [Not served from Sweden](docs/concepts/advisories.md#advisor_nordic_conventions_dhl_freight_sweden_parcel_connect_not_served) |
| DHL road freight (202, 205, 233, SPI) or 601 | [202, 233, 601 not served to Svalbard or Jan Mayen](docs/concepts/advisories.md#advisor_nordic_conventions_dhl_freight_sweden_parcel_connect_not_served) | [Not served outside its countries or postal codes](docs/concepts/advisories.md#advisor_nordic_conventions_dhl_freight_sweden_parcel_connect_not_served) |
| DHL domestic (102-104, 118, 209-212, 401, 402, 502) | [Not served abroad](docs/concepts/advisories.md#advisor_nordic_conventions_dhl_freight_sweden_parcel_connect_not_served) | [Not served abroad](docs/concepts/advisories.md#advisor_nordic_conventions_dhl_freight_sweden_parcel_connect_not_served) |

Both carriers: goods sold need a commercial invoice, not a proforma ([Invoice type mismatch](docs/concepts/advisories.md#advisor_nordic_conventions_invoice_type_content_mismatch)), every line needs a customs value above 0 ([Zero-value line](docs/concepts/advisories.md#advisor_nordic_conventions_zero_value_line)), a discounted or free line to Switzerland shows its discount on the invoice ([Discount to Switzerland](docs/concepts/advisories.md#advisor_nordic_conventions_ch_discount_on_invoice), reminder), and an attested paper invoice on PostNord SE to Norway is flagged ([Attestation conflict](docs/concepts/advisories.md#advisor_nordic_conventions_attestation_conflict)).
EU destinations, Northern Ireland included, need nothing, except that DHL Freight Sweden from Sweden carries country-specific advisories to [Cyprus](docs/concepts/advisories.md#advisor_nordic_conventions_dhl_freight_sweden_cyprus_documents), [Greece](docs/concepts/advisories.md#advisor_nordic_conventions_dhl_freight_sweden_greek_tax_ids), [Poland](docs/concepts/advisories.md#advisor_nordic_conventions_dhl_freight_sweden_sent_information), [Romania](docs/concepts/advisories.md#advisor_nordic_conventions_dhl_freight_sweden_uit_information), [Hungary](docs/concepts/advisories.md#advisor_nordic_conventions_dhl_freight_sweden_ekaer_information), and [Spain](docs/concepts/advisories.md#advisor_nordic_conventions_dhl_freight_sweden_spain_dg_documents); Great Britain, Åland, the Canary Islands, and the other special territories are non-EU ([specification](openspec/specs/plugins/advisor-nordic-conventions/spec.md)).
"(reminder)" marks an `info` advisory; — means no advice, not that nothing is required; goods-value thresholds are not checked.

## When the plugin advises

The plugin advises only at shipment creation, never at rating, on `postnord` shipments from Sweden, Denmark, or Finland and on `dhl_freight_sweden` shipments from Sweden, when the shipper is inside the EU VAT area.
Each advisory covers the destinations its own requirement names, and the EU VAT area follows Tullverket's list for goods movements, so Northern Ireland is inside while Åland, the Canary Islands, and the other special territories are outside.
When each advisory fires, how territory codes are read, the compliance stance, and the non-goals are documented in [Scope](docs/concepts/scope.md) and [Territories](docs/concepts/territories.md); the determinations are specified in the [specification](openspec/specs/plugins/advisor-nordic-conventions/spec.md).

## Advisory reference

Each advisory is a message with level `warning` or `info`, a stable code (public contract; renaming one is breaking), English text, and `details` with the lane and its `sources`, each tagged `S` (repository code or vendored specification), `W` (public carrier or authority documentation), or `I` (inference); where sources disagree the message states the stricter requirement.
The full per-carrier reference, with every advisory's level, destinations, trigger, and cited sources, the stable codes, and the source footnotes, is published in the [advisory reference](docs/concepts/advisories.md):

- [PostNord from Sweden](docs/concepts/advisories.md#postnord-from-sweden): digital invoice to Norway, Postpaket Utrikes invoice, paper invoice.
- [PostNord from Finland](docs/concepts/advisories.md#postnord-from-finland): export invoice.
- [PostNord from Denmark](docs/concepts/advisories.md#postnord-from-denmark): export documents.
- [DHL Freight Sweden from Sweden](docs/concepts/advisories.md#dhl-freight-sweden-from-sweden): customs mode, Åland customs service, invoice copy, Parcel Connect documents, VOEC marking, product lanes, territory postal codes, joint declaration, and the country-specific requirements for Cyprus, Greece, Poland, Romania, Hungary, and Spain.
- [Across carriers](docs/concepts/advisories.md#across-carriers): invoice type mismatch, attestation conflict, discount to Switzerland, zero-value line.

## Attestations

A consumer that has arranged an out-of-booking procedure for a shipment attests it by setting the matching shipment option to the boolean `true`; absent, `false`, and any other value, including the string `"false"`, carry no claim, unlike karrio carrier-option parsing.
An advisory is omitted only when every procedure that answers it is covered by an attestation that holds on the lane, and an attestation contradicted by the lane's conventions covers nothing and yields [Attestation conflict](docs/concepts/advisories.md#advisor_nordic_conventions_attestation_conflict).
The attestation options, the conflict behaviour, and how the answering sets differ per lane are in the [attestations guide](docs/guides/attestations.md).

## Utilities

`expected_procedures` returns the set of procedures the conventions expect for a request before booking, for example to show a pre-booking document checklist; it returns the empty set outside the plugin's scope.
The usage example is in the [attestations guide](docs/guides/attestations.md#expected-procedures).

## Compliance

The advisories are reminders, not compliance guarantees; the consumer owns compliance with carrier terms and customs rules and should verify each advisory against its cited sources.
The full stance is in [Scope](docs/concepts/scope.md#compliance).

## Non-goals

No advice at rating time, no per-organisation overrides, no advisories for Norwegian shippers, no goods-value thresholds, no CN22 or CN23 selection guidance, nothing the connectors already enforce, and no network calls.
The complete list, with the reason for each gap, is in [Scope](docs/concepts/scope.md#non-goals).

## Development

Tests use `unittest` and run from the repository root with an interpreter that can import a karrio SDK providing the advisors hook:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -v -f tests
```

Setup against the karrio fork, the connector cross-check tests, and the documentation-site preview are documented in [Development](docs/development/index.md).
