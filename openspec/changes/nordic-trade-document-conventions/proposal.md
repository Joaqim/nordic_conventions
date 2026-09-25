# Proposal

## Why

Shipping goods from Sweden, Denmark, or Finland to destinations outside the EU VAT area with PostNord or DHL Freight Sweden carries trade-document duties that the carrier connectors cannot express: invoice copies that must be emailed or uploaded, paper invoices in a plastic pocket, copies attached outside the package, and customs modes that must be chosen.
These duties differ by carrier, shipper country, destination, and product, and the carriers and customs authorities publish them in scattered and sometimes conflicting documents.
The karrio fork now has a shipment advisors hook (`PluginMetadata.shipment_advisors`, branch `feat-shipment-advisors`), whose own proposal names this Nordic conventions plugin as its first consumer.
The facts it rests on are collated with attribution in the karrio fork's `docs/notes/customs/nordic-trade-documents-facts.md` (branch `docs-openspec`, commit 0d02edf3a), cited below as FN with line numbers.

## What Changes

- Add an advisor-only karrio plugin `nordic_conventions` (package `karrio_nordic_conventions`, directory `plugins/nordic_conventions/`) that declares shipment advisors and no carrier mapper, proxy, settings, or address validator.
- The plugin advises only at shipment creation (`context.operation == "shipping"`), only for the carriers `postnord` and `dhl_freight_sweden`, and only when the shipper is in its Nordic scope: Sweden, Denmark, or Finland for PostNord, and Sweden for DHL Freight Sweden; recipients may be anywhere.
- It decides whether a destination is outside the EU VAT area from its own territory table, including postal-code-based special fiscal territories such as Åland and the Canary Islands, matching the definition the PostNord and DHL Freight Sweden connectors already apply.
- It emits ten advisories, each with its own stable code, as non-blocking `warning` or `info` messages that tell the API consumer what they still own: PostNord Sweden to Norway digital invoice routes; PostNord Sweden commercial letters (Export Letter, Registered, and Varubrev) and International Parcel needing CN23 and a commercial invoice, with the invoice sent digitally instead for Norway; PostNord Finland invoice copy and signed paper invoice; PostNord Sweden paper invoice for parcel products outside the EU VAT area; PostNord Denmark copy counts by destination and the export-declaration copy address; DHL Freight Sweden missing customs handling mode; DHL Freight Sweden invoice copy by email or upload; DHL Freight Sweden Parcel Connect documents attached outside the package; DHL Freight Sweden VOEC ID on the package or label; and a commercial-invoice flag that contradicts the customs content type, in either direction.
- Whether a shipment is commercial is determined once, from `customs.commercial_invoice` and `customs.content_type`, and reused by every advisory that depends on it.
- Every advisory names its sources with their evidence tag in the message details, and where sources conflict the message states the stricter requirement and the details name both sources.
- Wording prefers electronic forwarding and carrier-native, no-cost routes over paper where the sources allow it.
- The plugin imports and loads on karrio versions without the advisors hook, registering no advisors and logging once instead of failing.

Out of scope for this change: advice that depends on goods-value thresholds (SEK 2 000, EUR 1 000, DKK 7 500), CN22 and CN23 selection guidance, an invoice-content checklist, special fiscal territory handling beyond the destination test (the connectors already omit or keep customs accordingly), letter services the PostNord SE customs documents page does not name or that map to no connector code without doubt (Expressbrev, Värde, the Danish letter services, the tracked export letter, and the registered variants `RK` and `RL`), a different treatment of Monaco, Northern Ireland, and Mount Athos (a later change across both connectors and this plugin), Norwegian shippers (PostNord Norway export rules are unknown, FN:129, FN:247), and rating-time advice.
Nothing the connectors already enforce is repeated: field errors for missing customs data, the intra-EU customs omission warning, and the `commercial_invoice` to invoice-type mapping stay in the connectors (karrio fork `openspec/specs/postnord/customs-declaration/spec.md`, `openspec/specs/dhl-freight-sweden/customs/spec.md`).

## Capabilities

### New Capabilities

- `plugins/nordic-conventions`: which shipments the Nordic conventions plugin advises on, the advisories it emits with their codes, levels, triggers, and cited sources, how it treats conflicting sources, and how it degrades on karrio versions without the advisors hook.

### Modified Capabilities

None.

## Impact

- New directory `plugins/nordic_conventions/` with `pyproject.toml` (entry point group `karrio.plugins`, unpinned `karrio` dependency like its siblings), the plugin package, unittest tests under `tests/nordic_conventions/`, and a README stating the required karrio version or branch.
- The repository root README gains an entry under utility plugins.
- No change to karrio itself, to other plugins, or to shared packages under `packages/`.
- API consumers with the plugin installed see additional `warning` and `info` messages on PostNord and DHL Freight Sweden shipment responses for in-scope lanes; no shipment is blocked or altered.
- Requires the shipment advisors hook, currently on the karrio fork branch `feat-shipment-advisors` (commit 92c5d1ec0) and not yet in an upstream karrio release.
