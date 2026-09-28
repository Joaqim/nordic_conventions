# karrio.nordic_conventions

This package is an advisor-only extension of the [karrio](https://pypi.org/project/karrio) multi carrier shipping SDK.
It adds non-blocking trade-document advisories to PostNord and DHL Freight Sweden shipment responses for shippers in Sweden, Denmark, and Finland sending outside the EU VAT area.
Each advisory tells the API consumer what they still own, such as an invoice copy to email or upload, a paper invoice in a plastic pocket, copies attached outside the package, or a customs mode to select, and cites the carrier or authority source it rests on.
The plugin declares shipment advisors only, and no carrier mapper, proxy, settings, or address validator.

## Requirements

`Python 3.7+` and a karrio SDK that provides the shipment advisors hook (`PluginMetadata.shipment_advisors`).
Until the hook is released in karrio, use the karrio fork branch `feat-shipment-advisors` (commit 92c5d1ec0).
On a karrio SDK without the hook the plugin still loads, registers no advisors, and logs one warning that the hook is unavailable, so shipment responses are unchanged.

## Installation

```bash
pip install "git+https://github.com/Joaqim/nordic_conventions.git"
```

The plugin registers through the `karrio.plugins` entry point group under the id `nordic_conventions` and is reported with the plugin type `advisor`.
Installing it adds messages to shipment responses; uninstalling it removes them.
No shipment is blocked or altered.

## When the plugin advises

The plugin advises only at shipment creation (`context.operation == "shipping"`), never at rating.
It advises on `postnord` shipments from Sweden, Denmark, or Finland and on `dhl_freight_sweden` shipments from Sweden, when the shipper is inside and the recipient outside the EU VAT area.
Norwegian shippers are out of scope because PostNord Norway export rules were not found.
For return shipments the SDK swaps shipper and recipient before advisors run, so the returning party is the shipper.

The EU VAT area follows Tullverket's list of EU customs and fiscal territories as it applies to goods movements, shared with the PostNord and DHL Freight Sweden connectors, rather than karrio's `EUCountry`.
The member states are inside, with Greece as `GR` or `EL`, and Monaco (`MC`) is treated as EU.
Northern Ireland (`GB` with a postal code beginning `BT`) is inside for goods, which is the verdict this plugin gives; it is outside the EU VAT area for services.
Åland (`AX`, or `FI` 22000-22999), the Canary Islands (`IC`, or `ES` 35000-35999 and 38000-38999), Ceuta, Melilla, Büsingen, Heligoland, Livigno, Campione d'Italia, Mount Athos (`GR` 63086), and the French overseas departments are outside.
Postal codes are compared after removing spaces; the exclusion ranges apply only when the code is purely numeric, and the Northern Ireland prefix in any case.

A shipment's content is sale-like when its customs `content_type` is omitted or is none of gift, sample, documents, or return merchandise, compared case-insensitively.
A shipment is commercial when it carries customs data and either `customs.commercial_invoice` is true or its content is sale-like.

## Advisories

Every message has level `warning` or `info`, a stable code starting with `nordic_conventions_`, an English message text, and `details` holding `plugin`, `lane` (for example `SE-NO`), and `sources`.
Each source entry names its evidence `tag` (S for repository code or vendored specification, W for public carrier or authority documentation, I for inference), its `reference`, and the `statement` it makes.
Where sources disagree, the message states the stricter requirement and `details.sources` lists each disagreeing source with its own statement.
Several advisories may apply to one shipment, and each is returned once.

| Code | Level | Trigger | Sources |
|---|---|---|---|
| `nordic_conventions_postnord_se_no_digital_invoice` | `info` for a parcel product with customs data, else `warning` | PostNord, Sweden to Norway, unless `nordic_conventions_postnord_se_postpaket_commercial_invoice` applies; adds the SEK 0 invoice and VOEC statement for `postnord_export_letter` and `postnord_rek` | PostNord Service Point special terms §4 (valid 2026-01-01), PostNord SE Swedish customs documents page (Wayback 2026-02-08), connector spec |
| `nordic_conventions_postnord_se_postpaket_commercial_invoice` | `warning` | PostNord, Sweden, commercial `postnord_postpaket_utrikes` (91); Norway receives the digital invoice routes instead of paper copies | Postpaket Utrikes terms §2 (valid 2025-05-02), PostNord SE English page (Wayback 2026-01-16) and Swedish page (Wayback 2026-02-08), connector spec |
| `nordic_conventions_postnord_se_export_paper_invoice` | `warning` | PostNord, Sweden, parcel product, destination other than Norway | PostNord SE English page (Wayback 2026-01-16) and Swedish page (Wayback 2026-02-08), Service Point special terms §4 (valid 2026-01-01) |
| `nordic_conventions_postnord_fi_export_invoice` | `warning` | PostNord, Finland, parcel product | postnord.fi customs information (read 2026-09-25), PostNord FI special terms for parcels (valid 2026-05-01) |
| `nordic_conventions_postnord_dk_export_documents` | `warning` | PostNord, Denmark, parcel product | postnord.dk export page (Wayback 2026-03-10) |
| `nordic_conventions_dhl_freight_sweden_customs_mode_missing` | `warning` | DHL Freight Sweden with none of the customs service options set by unified name | DHL Freight Sweden product manual v5.23 (valid 2025-04-14), price list for customs services (valid 2026-05-01), connector spec |
| `nordic_conventions_dhl_freight_sweden_invoice_copy` | `warning` | DHL Freight Sweden, any service | DHL Freight Sweden product manual v5.23 (valid 2025-04-14), customs information export (2025-02-03), price list (valid 2026-05-01) |
| `nordic_conventions_dhl_freight_sweden_attached_documents` | `warning` | DHL Freight Sweden Parcel Connect (`dhl_freight_sweden_parcel_connect_b2c`, 109) | DHL Freight Sweden product manual v5.23 (valid 2025-04-14) |
| `nordic_conventions_dhl_freight_sweden_voec_marking` | `warning` | DHL Freight Sweden to Norway with `customs.options.voec_number` | DHL Freight Sweden product manual v5.23 (valid 2025-04-14), connector spec |
| `nordic_conventions_invoice_type_content_mismatch` | `warning` for proforma with sale-like content, `info` for commercial with gift or sample | PostNord parcel product or any DHL Freight Sweden service booked with customs data | Bring customs documents page, DHL Freight Sweden customs information export (2025-02-03), Postpaket Utrikes terms §2 (valid 2025-05-02), connector specs |
| `nordic_conventions_attestation_conflict` | `warning` | an attested procedure contradicted by the conventions of the lane; in this version `nordic_conventions_commercial_invoice_paper_copy` from Sweden to Norway with PostNord | PostNord Service Point special terms §4 (valid 2026-01-01), PostNord SE Swedish customs documents page (Wayback 2026-02-08), connector spec |

The DHL Freight Sweden customs service options are recognised by their unified names only (`dhl_freight_sweden_customs_handling_standard`, `dhl_freight_sweden_customs_handling_full_service`, `dhl_freight_sweden_customs_own_declaration`, `dhl_freight_sweden_customs_joint_declaration`), exactly as the connector parses them.
The codes are part of the plugin's public contract, and renaming one is a breaking change.
The full source references, including URLs and the facts note line numbers, are in `karrio/plugins/nordic_conventions/sources.py`.

## Attestations

A consumer that has arranged an out-of-booking procedure for one shipment attests it by setting the matching shipment option to the boolean `true`.

| Option | Procedure it attests |
|---|---|
| `nordic_conventions_commercial_invoice_paper_copy` | a printed commercial invoice travelling with the parcel |
| `nordic_conventions_customs_declaration_paper_copy` | a printed customs declaration, CN22 or CN23, travelling with the parcel |
| `nordic_conventions_customs_documents_attached_outside` | copies of the customs documents attached on the outside of the package |
| `nordic_conventions_commercial_invoice_electronic` | a commercial invoice transmitted electronically outside the booking |
| `nordic_conventions_voec_marking_printed` | the VOEC ID printed on the package or label |

Only the boolean `true` attests: an absent option, `false`, and any other value, including the string `"false"`, carry no claim, unlike karrio carrier-option parsing.
An option key in the `nordic_conventions_` namespace that the plugin does not define is ignored, with no message and no change to any advisory.
An advisory is omitted only when its answering procedures are non-empty and every one is covered by an attestation that holds on the lane; partial coverage returns the advisory unchanged, and an attestation contradicted by the lane's conventions covers nothing and returns `nordic_conventions_attestation_conflict` naming the claim and the contradicting convention with its sources.
The answering sets are lane-aware for the PostNord Postpaket Utrikes, Finland, and Denmark advisories, whose procedures differ for Norway, and for Denmark's paper-only destinations Norway, Switzerland, Liechtenstein, and Great Britain, from the other destinations.
The advisories whose fix lies inside the booking request — the DHL Freight Sweden customs service options and the `customs.commercial_invoice` flag — are answered by no procedure, so an attestation never replaces correct request data.

## Utilities

`expected_procedures` returns the procedures the conventions expect for a request before any booking, for example to show a pre-booking document checklist:

```python
import karrio.core.advisors as advisors
from karrio.plugins.nordic_conventions import expected_procedures

procedures = expected_procedures(
    shipment_request,
    advisors.AdvisorContext(carrier_name="postnord", operation="shipping"),
)
```

It takes the same request and context pair an advisor receives, returns the empty set outside the plugin's scope — the rating operation, a carrier or lane out of scope, a shipment inside the EU VAT area — and otherwise returns the union of the answering sets of the advisories that would be returned with no attestations.
It derives its result from the same rules that produce the advisories, so the function and the advisories cannot disagree.

## Compliance

The advisories are reminders, not compliance guarantees.
The API consumer owns compliance with carrier terms and customs rules, and should verify each advisory against the cited sources, which may change.
An attestation is the consumer's own commitment to perform the procedure; the plugin checks claims against the conventions that govern the lane, not against the consumer's warehouse.

## Non-goals

The plugin does not advise at rating time, and has no per-organisation overrides or connection-level attestation defaults; attestations are per-shipment claims only.
It does not evaluate goods-value thresholds (SEK 2 000, EUR 1 000, DKK 7 500), give CN22 or CN23 selection guidance, check invoice contents, or advise CN22 or CN23 for PostNord letters.
It does not advise Norwegian shippers.
It repeats nothing the connectors already enforce, such as field errors for missing customs data, the intra-EU customs omission warning, or the mapping of `commercial_invoice` to the invoice type.
It never reads connection credentials and makes no network calls.

## Development

Tests use `unittest` and run from the repository root with an interpreter that can import a karrio SDK providing the advisors hook:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -v -f tests
```

The karrio fork's `develop` dev shell (`nix develop 'git+file:///home/joaqim/projects/karrio?ref=dev-nix-flake#upstream'`, entered from the karrio checkout) provides such an interpreter, with the SDK and the PostNord and DHL Freight Sweden connectors on `PYTHONPATH`.
Inside it, a virtual environment created with `python -m venv --system-site-packages .venv` and the plugin installed with `pip install --no-deps -e .` registers the plugin's entry point.
The connector cross-check tests run when the PostNord and DHL Freight Sweden connectors are importable and are skipped otherwise.
