# karrio.nordic_conventions

Advisor-only extension for the [karrio](https://pypi.org/project/karrio) shipping SDK.
It adds non-blocking trade-document advisories to PostNord and DHL Freight Sweden shipment responses for shippers in Sweden, Denmark, and Finland sending outside the EU VAT area, each advisory stating what the consumer still owns and citing the carrier or authority source it rests on.
The plugin declares shipment advisors only: no carrier mapper, proxy, settings, or address validator, and no shipment is blocked or altered.

> **Status: pending an unmerged karrio feature.**
> The advisories need a karrio SDK with the shipment advisors hook, which only the [karrio fork](https://github.com/Joaqim/karrio) branch `feat-shipment-advisors` provides.
> With released karrio the plugin installs and loads but registers no advisors, so it changes nothing.
> Until the feature merges and ships in a karrio release, a working setup requires a local checkout of the fork; see [Development](#development).

## Installation

```bash
pip install "git+https://github.com/Joaqim/nordic_conventions.git"
```

The plugin registers through the `karrio.plugins` entry point group under the id `nordic_conventions` and is reported with the plugin type `advisor`.
Installing it adds messages to shipment responses; uninstalling it removes them.

## When the plugin advises

The plugin advises only at shipment creation, never at rating.
It advises on `postnord` shipments from Sweden, Denmark, or Finland and on `dhl_freight_sweden` shipments from Sweden, when the shipper is inside and the recipient outside the EU VAT area; for return shipments the returning party is the shipper, because the SDK swaps shipper and recipient before advisors run.
The EU VAT area follows Tullverket's list of EU customs and fiscal territories for goods movements rather than karrio's `EUCountry`: Northern Ireland is inside for goods, while Åland, the Canary Islands, and the other special territories are outside.
A shipment is commercial when it carries customs data and either `commercial_invoice` is true or its content is sale-like — a `content_type` that is omitted or none of gift, sample, documents, or return merchandise.
The full territory table and the determinations above are specified in the [specification](openspec/specs/plugins/nordic-conventions/spec.md).

## Advisories

Every message has level `warning` or `info`, a stable code starting with `nordic_conventions_`, an English message text, and `details` holding the lane and the `sources` behind the claim, each with its evidence tag and the statement it makes.
Where sources disagree the message states the stricter requirement and lists every disagreeing source.
Several advisories may apply to one shipment, and each is returned once.
The codes are public contract; renaming one is a breaking change.

The DHL Freight Sweden customs service options are recognised by their unified names only (`dhl_freight_sweden_customs_handling_standard`, `dhl_freight_sweden_customs_handling_full_service`, `dhl_freight_sweden_customs_own_declaration`, `dhl_freight_sweden_customs_joint_declaration`), exactly as the connector parses them.
Full source references, with URLs and facts-note line numbers, live in `karrio/plugins/nordic_conventions/sources.py` and the [specification](openspec/specs/plugins/nordic-conventions/spec.md).

Each advisory below lists its level, the trigger that raises it, and the sources behind it.

### `nordic_conventions_postnord_se_no_digital_invoice`

Level: `info` for a parcel product with customs data, else `warning`.

Trigger: PostNord, Sweden to Norway, unless `nordic_conventions_postnord_se_postpaket_commercial_invoice` applies; adds the SEK 0 invoice and VOEC statement for `postnord_export_letter` and `postnord_rek`.

Sources:

- PostNord Service Point special terms §4 (valid 2026-01-01)
- PostNord SE Swedish customs documents page (Wayback 2026-02-08)
- connector spec

### `nordic_conventions_postnord_se_postpaket_commercial_invoice`

Level: `warning`.

Trigger: PostNord, Sweden, commercial `postnord_postpaket_utrikes` (91); Norway receives the digital invoice routes instead of paper copies.

Sources:

- Postpaket Utrikes terms §2 (valid 2025-05-02)
- PostNord SE English page (Wayback 2026-01-16)
- PostNord SE Swedish page (Wayback 2026-02-08)
- connector spec

### `nordic_conventions_postnord_se_export_paper_invoice`

Level: `warning`.

Trigger: PostNord, Sweden, parcel product, destination other than Norway.

Sources:

- PostNord SE English page (Wayback 2026-01-16)
- PostNord SE Swedish page (Wayback 2026-02-08)
- PostNord Service Point special terms §4 (valid 2026-01-01)

### `nordic_conventions_postnord_fi_export_invoice`

Level: `warning`.

Trigger: PostNord, Finland, parcel product.

Sources:

- postnord.fi customs information (read 2026-09-25)
- PostNord FI special terms for parcels (valid 2026-05-01)

### `nordic_conventions_postnord_dk_export_documents`

Level: `warning`.

Trigger: PostNord, Denmark, parcel product.

Sources:

- postnord.dk export page (Wayback 2026-03-10)

### `nordic_conventions_dhl_freight_sweden_customs_mode_missing`

Level: `warning`.

Trigger: DHL Freight Sweden with none of the customs service options set by unified name.

Sources:

- DHL Freight Sweden product manual v5.23 (valid 2025-04-14)
- DHL Freight Sweden price list for customs services (valid 2026-05-01)
- connector spec

### `nordic_conventions_dhl_freight_sweden_invoice_copy`

Level: `warning`.

Trigger: DHL Freight Sweden, any service.

Sources:

- DHL Freight Sweden product manual v5.23 (valid 2025-04-14)
- DHL Freight Sweden customs information export (2025-02-03)
- DHL Freight Sweden price list (valid 2026-05-01)

### `nordic_conventions_dhl_freight_sweden_attached_documents`

Level: `warning`.

Trigger: DHL Freight Sweden Parcel Connect (`dhl_freight_sweden_parcel_connect_b2c`, 109).

Sources:

- DHL Freight Sweden product manual v5.23 (valid 2025-04-14)

### `nordic_conventions_dhl_freight_sweden_voec_marking`

Level: `warning`.

Trigger: DHL Freight Sweden to Norway with `customs.options.voec_number`.

Sources:

- DHL Freight Sweden product manual v5.23 (valid 2025-04-14)
- connector spec

### `nordic_conventions_invoice_type_content_mismatch`

Level: `warning` for proforma with sale-like content, `info` for commercial with gift or sample.

Trigger: PostNord parcel product or any DHL Freight Sweden service booked with customs data.

Sources:

- Bring customs documents page
- DHL Freight Sweden customs information export (2025-02-03)
- Postpaket Utrikes terms §2 (valid 2025-05-02)
- connector specs

### `nordic_conventions_attestation_conflict`

Level: `warning`.

Trigger: an attested procedure contradicted by the conventions of the lane; in this version `nordic_conventions_commercial_invoice_paper_copy` from Sweden to Norway with PostNord.

Sources:

- PostNord Service Point special terms §4 (valid 2026-01-01)
- PostNord SE Swedish customs documents page (Wayback 2026-02-08)
- connector spec

## Attestations

A consumer that has arranged an out-of-booking procedure for a shipment attests it by setting the matching shipment option to the boolean `true`; absent, `false`, and any other value, including the string `"false"`, carry no claim, unlike karrio carrier-option parsing.

| Option | Procedure it attests |
|---|---|
| `nordic_conventions_commercial_invoice_paper_copy` | a printed commercial invoice travelling with the parcel |
| `nordic_conventions_customs_declaration_paper_copy` | a printed customs declaration, CN22 or CN23, travelling with the parcel |
| `nordic_conventions_customs_documents_attached_outside` | copies of the customs documents attached on the outside of the package |
| `nordic_conventions_commercial_invoice_electronic` | a commercial invoice transmitted electronically outside the booking |
| `nordic_conventions_voec_marking_printed` | the VOEC ID printed on the package or label |

An advisory is omitted only when every procedure that answers it is covered by an attestation that holds on the lane; partial coverage returns the advisory unchanged, and an attestation contradicted by the lane's conventions covers nothing and yields `nordic_conventions_attestation_conflict`.
The answering sets are lane-aware where the conventions differ, for example for PostNord destinations in Norway, and the complete mapping is in the [specification](openspec/specs/plugins/nordic-conventions/spec.md).
Advisories whose fix lies inside the booking request — the DHL Freight Sweden customs service options and the `customs.commercial_invoice` flag — are answered by no procedure, so an attestation never replaces correct request data.

## Utilities

`expected_procedures` returns the set of procedures the conventions expect for a request before booking, for example to show a pre-booking document checklist:

```python
import karrio.core.advisors as advisors
from karrio.plugins.nordic_conventions import expected_procedures

procedures = expected_procedures(
    shipment_request,
    advisors.AdvisorContext(carrier_name="postnord", operation="shipping"),
)
```

It returns the empty set outside the plugin's scope — the rating operation, a carrier or lane out of scope, a shipment inside the EU VAT area — and otherwise the union of the answering sets of the advisories that would be returned with no attestations, derived from the same rules that produce the advisories.

## Compliance

The advisories are reminders, not compliance guarantees.
The consumer owns compliance with carrier terms and customs rules and should verify each advisory against the cited sources, which may change.
An attestation is the consumer's own commitment to perform the procedure; the plugin checks claims against the conventions that govern the lane, not against the consumer's warehouse.

## Non-goals

No advice at rating time, no per-organisation overrides or connection-level attestation defaults, and no advisories for Norwegian shippers.
No goods-value thresholds (SEK 2 000, EUR 1 000, DKK 7 500), CN22 or CN23 selection guidance, invoice-content checks, or CN22 or CN23 advice for PostNord letters.
Nothing the connectors already enforce, such as field errors for missing customs data or the mapping of `commercial_invoice` to the invoice type.
The plugin never reads connection credentials and makes no network calls.
Known, undecided coverage gaps are recorded inside the requirements they border in the [specification](openspec/specs/plugins/nordic-conventions/spec.md).

## Development

Tests use `unittest` and run from the repository root with an interpreter that can import a karrio SDK providing the advisors hook:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -v -f tests
```

Create a virtual environment and install the forked SDK and the plugin with `pip install -r requirements-dev.txt -e .`.
`requirements-dev.txt` installs the SDK editable from a local checkout of the fork's `feat-shipment-advisors` branch; a `git+https` install cannot replace this, because pip recursively fetches the monorepo's private `karrioapi` submodules that `modules/sdk` does not need.
The connector cross-check tests run when the PostNord and DHL Freight Sweden connectors are importable, as in the karrio fork's `develop` dev shell (`nix develop 'git+file:///home/joaqim/projects/karrio?ref=dev-nix-flake#upstream'`, entered from the karrio checkout), and are skipped otherwise.
