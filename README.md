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

## Requirements at a glance

What the carriers ask for goods sent from Sweden, Denmark, or Finland to outside the EU VAT area; each cell links to its advisory.

| Shipment | Norway | Other non-EU (incl. GB) |
|---|---|---|
| PostNord SE parcel | [Invoice sent digitally](#nordic_conventions_postnord_se_no_digital_invoice) (reminder with customs data) | [3× English invoice in pocket on parcel 1](#nordic_conventions_postnord_se_export_paper_invoice) |
| PostNord SE 91, commercial | [CN23 + digital invoice](#nordic_conventions_postnord_se_postpaket_commercial_invoice) (supply yourself) | [CN23 + 3× invoice with parcel](#nordic_conventions_postnord_se_postpaket_commercial_invoice) (supply yourself) |
| PostNord SE 91, non-commercial | [Invoice sent digitally](#nordic_conventions_postnord_se_no_digital_invoice) | — |
| PostNord SE letter | [Invoice sent digitally; export, REK letters + VOEC](#nordic_conventions_postnord_se_no_digital_invoice) | — |
| PostNord FI parcel | [E-invoice before shipping](#nordic_conventions_postnord_fi_export_invoice) | [3× signed English invoice](#nordic_conventions_postnord_fi_export_invoice) |
| PostNord DK parcel | [2× invoice in visible pocket](#nordic_conventions_postnord_dk_export_documents) | [CH, LI 3×, GB 2× invoice; else CN23 + 2× invoice](#nordic_conventions_postnord_dk_export_documents) |
| PostNord FI or DK 91, letter | — | — |
| DHL Freight SE, any | [Customs mode](#nordic_conventions_dhl_freight_sweden_customs_mode_missing) + [invoice copy](#nordic_conventions_dhl_freight_sweden_invoice_copy) + [VOEC on label if booked](#nordic_conventions_dhl_freight_sweden_voec_marking) | [Customs mode](#nordic_conventions_dhl_freight_sweden_customs_mode_missing) + [invoice copy](#nordic_conventions_dhl_freight_sweden_invoice_copy) |
| DHL Parcel Connect (109) | [+ 2 document copies outside package](#nordic_conventions_dhl_freight_sweden_attached_documents) | [+ 2 document copies outside package](#nordic_conventions_dhl_freight_sweden_attached_documents); [Switzerland not served](#nordic_conventions_dhl_freight_sweden_parcel_connect_not_served); [Great Britain by agreement only](#nordic_conventions_dhl_freight_sweden_parcel_connect_gb_agreement) |
| DHL Parcel Connect Plus (112) | — | [Switzerland not served](#nordic_conventions_dhl_freight_sweden_parcel_connect_not_served); [Great Britain by agreement only](#nordic_conventions_dhl_freight_sweden_parcel_connect_gb_agreement) |
| DHL Parcel Return Connect (107) | — | [Switzerland and Great Britain not served](#nordic_conventions_dhl_freight_sweden_parcel_connect_not_served) |

Both carriers: goods sold need a commercial invoice, not a proforma ([Invoice type mismatch](#nordic_conventions_invoice_type_content_mismatch)), every line needs a customs value above 0 ([Zero-value line](#nordic_conventions_zero_value_line)), a discounted or free line to Switzerland shows its discount on the invoice ([Discount to Switzerland](#nordic_conventions_ch_discount_on_invoice), reminder), and an attested paper invoice on PostNord SE to Norway is flagged ([Attestation conflict](#nordic_conventions_attestation_conflict)).
EU destinations, Northern Ireland included, need nothing; Great Britain, Åland, the Canary Islands, and the other special territories are non-EU ([specification](openspec/specs/plugins/nordic-conventions/spec.md)).
"(reminder)" marks an `info` advisory; — means no advice, not that nothing is required; goods-value thresholds are not checked.

## When the plugin advises

The plugin advises only at shipment creation, never at rating.
It advises on `postnord` shipments from Sweden, Denmark, or Finland and on `dhl_freight_sweden` shipments from Sweden, when the shipper is inside and the recipient outside the EU VAT area; for return shipments the returning party is the shipper, because the SDK swaps shipper and recipient before advisors run.
The EU VAT area follows Tullverket's list of EU customs and fiscal territories for goods movements rather than karrio's `EUCountry`; Northern Ireland is inside for goods, while Åland, the Canary Islands, and the other special territories are outside.
A shipment is commercial when it carries customs data and either `commercial_invoice` is true or its content is sale-like — a `content_type` that is omitted or none of gift, sample, documents, or return merchandise.
The full territory table and the determinations above are specified in the [specification](openspec/specs/plugins/nordic-conventions/spec.md).

## Advisory reference

Each advisory is a message with level `warning` or `info`, a stable code (public contract; renaming one is breaking), English text, and `details` with the lane and its `sources`, each tagged `S`, `W`, or `I`.
Where sources disagree the message states the stricter requirement.
DHL Freight Sweden customs options count only under their unified names: `dhl_freight_sweden_customs_handling_standard`, `dhl_freight_sweden_customs_handling_full_service`, `dhl_freight_sweden_customs_own_declaration`, `dhl_freight_sweden_customs_joint_declaration`.
Footnotes are named after their constants in `karrio/plugins/nordic_conventions/sources.py`; the [specification](openspec/specs/plugins/nordic-conventions/spec.md) has the section and line references.
Non-EU means outside the EU VAT area.

### PostNord from Sweden

| Advisory | Level | Destinations | Trigger | Sources |
|---|---|---|---|---|
| <a id="nordic_conventions_postnord_se_no_digital_invoice"></a>Digital invoice to Norway | `info` for a parcel with customs data, else `warning` | Norway | Any service to Norway unless [Postpaket Utrikes invoice](#nordic_conventions_postnord_se_postpaket_commercial_invoice) applies; `postnord_export_letter` and `postnord_rek` add the SEK 0 invoice and VOEC statement | Service Point terms §4[^pn-se-service-point-terms], Swedish customs page[^pn-se-sv-page], PostNord connector spec[^pns] |
| <a id="nordic_conventions_postnord_se_postpaket_commercial_invoice"></a>Postpaket Utrikes invoice | `warning` | all non-EU | Commercial `postnord_postpaket_utrikes` (91); Norway gets digital routes instead of paper copies | Postpaket Utrikes terms §2[^pn-se-postpaket-terms], English customs page[^pn-se-en-page], Swedish customs page[^pn-se-sv-page], PostNord connector spec[^pns] |
| <a id="nordic_conventions_postnord_se_export_paper_invoice"></a>Paper invoice | `warning` | non-EU except Norway | Parcel product | English customs page[^pn-se-en-page], Swedish customs page[^pn-se-sv-page], Service Point terms §4[^pn-se-service-point-terms] |

### PostNord from Finland

| Advisory | Level | Destinations | Trigger | Sources |
|---|---|---|---|---|
| <a id="nordic_conventions_postnord_fi_export_invoice"></a>Export invoice | `warning` | all non-EU | Parcel product | postnord.fi customs page[^pn-fi-page], PostNord FI parcel terms[^pn-fi-terms] |

### PostNord from Denmark

| Advisory | Level | Destinations | Trigger | Sources |
|---|---|---|---|---|
| <a id="nordic_conventions_postnord_dk_export_documents"></a>Export documents | `warning` | all non-EU | Parcel product | postnord.dk export page[^pn-dk-page] |

### DHL Freight Sweden from Sweden

| Advisory | Level | Destinations | Trigger | Sources |
|---|---|---|---|---|
| <a id="nordic_conventions_dhl_freight_sweden_customs_mode_missing"></a>Customs mode missing | `warning` | all non-EU | No customs service option set by unified name | DHL product manual[^dhl-man], DHL price list[^dhl-prl], DHL connector spec[^dfs] |
| <a id="nordic_conventions_dhl_freight_sweden_invoice_copy"></a>Invoice copy | `warning` | all non-EU | Any service | DHL product manual[^dhl-man], DHL export customs information[^dhl-cie], DHL price list[^dhl-prl] |
| <a id="nordic_conventions_dhl_freight_sweden_attached_documents"></a>Documents outside package | `warning` | all non-EU | Parcel Connect (`dhl_freight_sweden_parcel_connect_b2c`, 109) | DHL product manual[^dhl-man] |
| <a id="nordic_conventions_dhl_freight_sweden_voec_marking"></a>VOEC marking | `warning` | Norway | `customs.options.voec_number` set | DHL product manual[^dhl-man], DHL connector spec[^dfs] |
| <a id="nordic_conventions_dhl_freight_sweden_parcel_connect_not_served"></a>Parcel Connect not served | `warning` | Switzerland and Great Britain | Parcel Connect (`dhl_freight_sweden_parcel_connect_b2c`, 109), Parcel Connect Plus (`dhl_freight_sweden_parcel_connect_plus`, 112), or Parcel Return Connect (`dhl_freight_sweden_parcel_return_connect_c2b`, 107) to Switzerland; Parcel Return Connect to Great Britain | DHL product manual[^dhl-man] |
| <a id="nordic_conventions_dhl_freight_sweden_parcel_connect_gb_agreement"></a>Parcel Connect to Great Britain | `warning` | Great Britain | Parcel Connect (`dhl_freight_sweden_parcel_connect_b2c`, 109) or Parcel Connect Plus (`dhl_freight_sweden_parcel_connect_plus`, 112), which serve Great Britain only by separate agreement | DHL product manual[^dhl-man] |

### Across carriers

| Advisory | Level | Destinations | Trigger | Sources |
|---|---|---|---|---|
| <a id="nordic_conventions_invoice_type_content_mismatch"></a>Invoice type mismatch | `warning` for proforma with sale-like content, `info` for commercial with gift or sample | all non-EU | PostNord parcel product or any DHL Freight Sweden service, with customs data | Bring customs page[^bring], DHL export customs information[^dhl-cie], Postpaket Utrikes terms §2[^pn-se-postpaket-terms], PostNord connector spec[^pns], DHL connector spec[^dfs] |
| <a id="nordic_conventions_attestation_conflict"></a>Attestation conflict | `warning` | Norway | An attestation the lane contradicts; in this version a paper invoice on PostNord from Sweden to Norway | Service Point terms §4[^pn-se-service-point-terms], Swedish customs page[^pn-se-sv-page], PostNord connector spec[^pns] |
| <a id="nordic_conventions_ch_discount_on_invoice"></a>Discount to Switzerland | `info` | Switzerland | A commodity with `metadata.discount_percentage` set or a value of 0 or none | BAZG R-69-03 §5.5.3[^bazg-rabatte] |
| <a id="nordic_conventions_zero_value_line"></a>Zero-value line | `warning` | all non-EU | A commodity with a value of 0 or none | PostNord Norway parcels page[^pn-se-no-page], Tullverket export documents page[^tv-export-documents], DHL Express customs guidelines[^dhl-express-customs] |

### Codes

- Digital invoice to Norway: `nordic_conventions_postnord_se_no_digital_invoice`
- Postpaket Utrikes invoice: `nordic_conventions_postnord_se_postpaket_commercial_invoice`
- Paper invoice: `nordic_conventions_postnord_se_export_paper_invoice`
- Export invoice: `nordic_conventions_postnord_fi_export_invoice`
- Export documents: `nordic_conventions_postnord_dk_export_documents`
- Customs mode missing: `nordic_conventions_dhl_freight_sweden_customs_mode_missing`
- Invoice copy: `nordic_conventions_dhl_freight_sweden_invoice_copy`
- Documents outside package: `nordic_conventions_dhl_freight_sweden_attached_documents`
- VOEC marking: `nordic_conventions_dhl_freight_sweden_voec_marking`
- Parcel Connect not served: `nordic_conventions_dhl_freight_sweden_parcel_connect_not_served`
- Parcel Connect to Great Britain: `nordic_conventions_dhl_freight_sweden_parcel_connect_gb_agreement`
- Invoice type mismatch: `nordic_conventions_invoice_type_content_mismatch`
- Attestation conflict: `nordic_conventions_attestation_conflict`
- Discount to Switzerland: `nordic_conventions_ch_discount_on_invoice`
- Zero-value line: `nordic_conventions_zero_value_line`

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
No advisory on splitting goods sold as one unit into separately packed consignments to Norway to stay under the VOEC value limit, which the [Skatteetaten VOEC guidelines](https://www.skatteetaten.no/globalassets/bedrift-og-organisasjon/voec/voec-guidelines-mars-2024.pdf) (March 2024) prohibit: an advisor sees one shipment request, with no record of the sale or of other consignments, so a split cannot be detected reliably.
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

[^pn-se-service-point-terms]: PostNord SE Service Point special terms, valid 2026-01-01: <https://www.avropa.se/globalassets/bilagor/1.-aktuella-rao/postformedlingstjanster-2021/paketformedlingstjanster--1-lev-postnord/sarskilda-villkor-service-point-2026.pdf> (`PN_SE_SERVICE_POINT_TERMS_URL`).
[^pn-se-sv-page]: PostNord SE Swedish customs documents page, Wayback 2026-02-08: <https://www.postnord.se/foretag/import-export-tull/tulldokument-och-frakthandlingar-for-foretag/> (`PN_SE_SV_PAGE`).
[^pn-se-en-page]: PostNord SE English customs documents page, Wayback 2026-01-16: <https://web.archive.org/web/20260116090151/https://www.postnord.se/en/business/import-export-customs/customs-documents-and-shipping-documents/> (`PN_SE_EN_PAGE`).
[^pn-se-postpaket-terms]: PostNord SE Postpaket Utrikes terms, valid 2025-05-02: <https://api2.postnord.com/rest/customer/v2/ptm/file/download/5341.28764?disposition=inline> (`PN_SE_POSTPAKET_TERMS_URL`).
[^pn-fi-page]: postnord.fi customs information, read 2026-09-25: <https://www.postnord.fi/en/sending/online-tools/customs-information/> (`PN_FI_PAGE_URL`).
[^pn-fi-terms]: PostNord FI special terms for parcels, valid 2026-05-01, Wayback 2026-06-10; no URL is recorded (`PN_FI_TERMS`).
[^pn-dk-page]: postnord.dk export page, Wayback 2026-03-10: <https://www.postnord.dk/erhverv/eksport/> (`PN_DK_PAGE_URL`).
[^dhl-man]: DHL Freight Sweden product manual v5.26, updated 2026-10-01, valid from 2026-11-01, sha256 050660c37ba93d1ae9514c50dfa42c2010bc87763ccaff51a740b2526af11b73, listed at <https://dhlpaket.se/dashboard/specifications/products/> (`DHL_MAN_URL`).
[^dhl-cie]: DHL Freight Sweden customs information export, 2025-02-03: <https://www.dhl.com/content/dam/dhl/local/se/dhl-freight/documents/pdf/se-freight-customs-information-export-en.pdf> (`DHL_CIE_URL`).
[^dhl-prl]: DHL Freight Sweden price list for additional services, valid 2026-05-01: <https://www.dhl.com/content/dam/dhl/local/se/dhl-freight/documents/pdf/se-freight-price-list-additional-services-sv.pdf> (`DHL_PRL_URL`).
[^bring]: Bring customs documents page: <https://www.bring.se/tjanster/tull/tulldokument> (`BRING_URL`).
[^pns]: karrio fork `openspec/specs/postnord/customs-declaration/spec.md` on branch `docs-openspec` at commit 60312fe2e (`PNS`).
[^dfs]: karrio fork `openspec/specs/dhl-freight-sweden/customs/spec.md` on branch `docs-openspec` at commit 60312fe2e (`DFS`).
[^bazg-rabatte]: BAZG Richtlinie R-69-03, valid 2025-01-01: <https://www.bazg.admin.ch/dam/de/sd-web/mIvoM5CF7ydH/steuerbemessungsgrundlage-de.pdf> (`BAZG_R_69_03_URL`).
[^pn-se-no-page]: PostNord SE page on sending parcels to Norway, read 2026-10-02: <https://www.postnord.se/privat/skicka/skicka-brev-och-paket-utomlands/skicka-paket-till-norge/> (`PN_SE_NO_PAGE_URL`).
[^tv-export-documents]: Tullverket supporting documents for export, updated 2026-06-12, read 2026-10-02: <https://www.tullverket.se/sv/foretag/exporteravaror/deklareravarorvidexport/styrkandehandlingarvidexport.4.78aa922815794d801e25e3.html> (`TV_EXPORT_DOCUMENTS_URL`).
[^dhl-express-customs]: DHL Express global customs customer guidelines: <https://mydhl.express.dhl/content/dam/downloads/global/en/customs-guide/express_global_customs_customer_guidelines.pdf.coredownload.pdf> (`DHL_EXPRESS_CUSTOMS_URL`).
