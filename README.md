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

This section states in plain language what the carriers' terms and web pages, as cited by the plugin, ask of a shipper sending goods from Sweden, Denmark, or Finland to a destination outside the EU VAT area.
Each requirement links to the advisory the plugin returns for it (the advisory code is only needed when reading shipment responses) and footnotes its main source; the advisory lists every source.
A requirement marked *reminder* is returned at level `info`; every other requirement is returned at level `warning`.
The plugin does not evaluate goods value, so requirements that start at a value threshold (SEK 2 000, EUR 1 000, DKK 7 500) are not covered, and a cell reading *not covered* means the plugin gives no advice there, not that nothing is required.

### Which destinations count

Shipments to Sweden, Denmark, Finland, or any other EU member state need none of the paperwork below, because they stay inside the EU VAT area.
The EU VAT area for goods follows Tullverket rather than the political map of the EU.
Northern Ireland (UK postcodes beginning `BT`) is inside, while the rest of the United Kingdom is outside.
Åland, the Canary Islands, Ceuta, Melilla, Büsingen, Heligoland, Mount Athos, Livigno, Campione d'Italia, and the French overseas departments are outside, although they belong to member states; Monaco is inside.
A shipper on Åland is therefore also outside, and receives no advice.
Norway is outside and is where the carriers differ most: PostNord Sweden and PostNord Finland want the invoice digitally rather than on paper, PostNord Denmark still wants paper invoices, and DHL Freight Sweden wants a booked VOEC number printed on the package.
Great Britain also has its own figures: two invoices from PostNord Denmark, and a higher DHL Freight Sweden reminder fee.

### PostNord from Sweden

| Service | To Norway | To other destinations outside the EU VAT area |
|---|---|---|
| Parcel products, such as `postnord_parcel` | Commercial invoice sent digitally, not on paper with the parcel; *reminder* when the booking carries customs data, because the booking then sends the invoice data ([advisory](#nordic_conventions_postnord_se_no_digital_invoice))[^pn-se-service-point-terms] | Commercial invoice in English, three copies, in a plastic pocket on parcel no. 1; the customs data in the booking prevails over the paper ([advisory](#nordic_conventions_postnord_se_export_paper_invoice))[^pn-se-en-page] |
| International Parcel (Postpaket Utrikes, 91), commercial | CN23 export declaration, and the commercial invoice sent digitally, not with the parcel; the booking sends neither, so supply both yourself ([advisory](#nordic_conventions_postnord_se_postpaket_commercial_invoice))[^pn-se-sv-page] | CN23 export declaration and a commercial invoice in three copies with the parcel; the booking sends neither, so supply both yourself ([advisory](#nordic_conventions_postnord_se_postpaket_commercial_invoice))[^pn-se-postpaket-terms] |
| International Parcel (91), not commercial | Commercial invoice sent digitally ([advisory](#nordic_conventions_postnord_se_no_digital_invoice))[^pn-se-sv-page] | Not covered |
| Letters | Commercial invoice sent digitally; for export letters (`postnord_export_letter`) and registered letters (`postnord_rek`) a commercial invoice and a VOEC number from SEK 0 ([advisory](#nordic_conventions_postnord_se_no_digital_invoice))[^pn-se-sv-page] | Not covered |

The digital routes to Norway are the booking itself where it sends the invoice data, PostNord Skicka Direkt Business, email to foravisering.export@postnord.com, or upload in PostNord MyCustoms.
The sources disagree on the number of paper copies, between two and three, and the plugin states the stricter three.

### PostNord from Finland

| Service | To Norway | To other destinations outside the EU VAT area |
|---|---|---|
| Parcel products | Invoice sent electronically, reaching PostNord before the shipment ([advisory](#nordic_conventions_postnord_fi_export_invoice))[^pn-fi-page] | Signed commercial invoice in English, three copies, with the parcel ([advisory](#nordic_conventions_postnord_fi_export_invoice))[^pn-fi-terms] |
| International Parcel and letters | Not covered | Not covered |

A copy of the invoice can be emailed to tullaus.fi@postnord.com on every destination.
The signed triplicate comes from PostNord Finland's special terms for parcels; its web page is laxer, and which of the two governs is unresolved.

### PostNord from Denmark

| Service | To Norway | To other destinations outside the EU VAT area |
|---|---|---|
| Parcel products | Two commercial invoices in a plastic pocket visible on the parcel ([advisory](#nordic_conventions_postnord_dk_export_documents))[^pn-dk-page] | In a plastic pocket visible on the parcel: three commercial invoices to Switzerland or Liechtenstein, two to Great Britain, and elsewhere one CN23 and two commercial invoices, the invoice recommended rather than required ([advisory](#nordic_conventions_postnord_dk_export_documents))[^pn-dk-page] |
| International Parcel and letters | Not covered | Not covered |

On every destination, a lodged export declaration is copied to eksport@postnord.com.

### DHL Freight Sweden from Sweden

| Applies to | To Norway | To other destinations outside the EU VAT area |
|---|---|---|
| Every service | Select a customs mode in the booking options: customs handling standard or full service, or your own declaration; each carries a DHL fee, and none is fee-free ([advisory](#nordic_conventions_dhl_freight_sweden_customs_mode_missing))[^dhl-man] | Same as Norway ([advisory](#nordic_conventions_dhl_freight_sweden_customs_mode_missing))[^dhl-man] |
| Every service | A copy of the invoice emailed to dhlfreight.int.se@dhl.com shortly after booking or uploaded in myDHL Freight, even when the booking carries full customs data; missing documents stop the shipment with a 390 kr reminder fee ([advisory](#nordic_conventions_dhl_freight_sweden_invoice_copy))[^dhl-cie] | Same as Norway, with a 650 kr reminder fee for Great Britain ([advisory](#nordic_conventions_dhl_freight_sweden_invoice_copy))[^dhl-cie] |
| Parcel Connect (109) | Two copies of the customs documents attached on the outside of the package ([advisory](#nordic_conventions_dhl_freight_sweden_attached_documents))[^dhl-man] | Same as Norway ([advisory](#nordic_conventions_dhl_freight_sweden_attached_documents))[^dhl-man] |
| A booked VOEC number | The VOEC ID printed on the package or the label ([advisory](#nordic_conventions_dhl_freight_sweden_voec_marking))[^dhl-man] | Does not apply |

Whether Parcel Connect Plus (112) and road-freight products also need the copies on the outside is unconfirmed, and they receive no advice on it.

### Across carriers

On PostNord parcel products and every DHL Freight Sweden service booked with customs data, the invoice type must match what is shipped.
Goods sold need a commercial invoice, because a proforma invoice is for gifts and samples the recipient does not pay for; the booking declares a proforma invoice whenever `customs.commercial_invoice` is not true ([advisory](#nordic_conventions_invoice_type_content_mismatch))[^bring].
A commercial invoice declared for a gift or sample is only a *reminder*, since a proforma invoice is the usual document there.
A consumer that attests a procedure the lane's conventions reject, in this version a paper invoice on a PostNord shipment from Sweden to Norway, is told that the attestation does not hold ([advisory](#nordic_conventions_attestation_conflict))[^pn-se-service-point-terms].

## When the plugin advises

The plugin advises only at shipment creation, never at rating.
It advises on `postnord` shipments from Sweden, Denmark, or Finland and on `dhl_freight_sweden` shipments from Sweden, when the shipper is inside and the recipient outside the EU VAT area; for return shipments the returning party is the shipper, because the SDK swaps shipper and recipient before advisors run.
The EU VAT area follows Tullverket's list of EU customs and fiscal territories for goods movements rather than karrio's `EUCountry`, as summarised in [Which destinations count](#which-destinations-count).
A shipment is commercial when it carries customs data and either `commercial_invoice` is true or its content is sale-like — a `content_type` that is omitted or none of gift, sample, documents, or return merchandise.
The full territory table and the determinations above are specified in the [specification](openspec/specs/plugins/nordic-conventions/spec.md).

## Advisory reference

Every message has level `warning` or `info`, a stable code starting with `nordic_conventions_`, an English message text, and `details` holding the lane and the `sources` behind the claim, each with its evidence tag and the statement it makes.
Where sources disagree the message states the stricter requirement and lists every disagreeing source.
Several advisories may apply to one shipment, and each is returned once.
The codes are public contract; renaming one is a breaking change.

The DHL Freight Sweden customs service options are recognised by their unified names only (`dhl_freight_sweden_customs_handling_standard`, `dhl_freight_sweden_customs_handling_full_service`, `dhl_freight_sweden_customs_own_declaration`, `dhl_freight_sweden_customs_joint_declaration`), exactly as the connector parses them.
The footnotes cite each document once, named after its constant in `karrio/plugins/nordic_conventions/sources.py`; that module and the [specification](openspec/specs/plugins/nordic-conventions/spec.md) add the section, page, and facts-note line numbers behind each claim.

The advisories are grouped by carrier and origin like [Requirements at a glance](#requirements-at-a-glance); the group heading names the carrier and origin each trigger assumes.

### PostNord from Sweden advisories

| Advisory | Level | Destinations | Trigger | Sources |
|---|---|---|---|---|
| <a id="nordic_conventions_postnord_se_no_digital_invoice"></a>`nordic_conventions_postnord_se_no_digital_invoice` | `info` for a parcel product with customs data, else `warning` | Norway only | Any service to Norway, unless the [Postpaket Utrikes advisory](#nordic_conventions_postnord_se_postpaket_commercial_invoice) applies; adds the SEK 0 invoice and VOEC statement for `postnord_export_letter` and `postnord_rek` | Service Point terms §4[^pn-se-service-point-terms], Swedish customs page[^pn-se-sv-page], PostNord connector spec[^pns] |
| <a id="nordic_conventions_postnord_se_postpaket_commercial_invoice"></a>`nordic_conventions_postnord_se_postpaket_commercial_invoice` | `warning` | all destinations outside the EU VAT area | Commercial `postnord_postpaket_utrikes` (91); Norway receives the digital invoice routes instead of paper copies | Postpaket Utrikes terms §2[^pn-se-postpaket-terms], English customs page[^pn-se-en-page], Swedish customs page[^pn-se-sv-page], PostNord connector spec[^pns] |
| <a id="nordic_conventions_postnord_se_export_paper_invoice"></a>`nordic_conventions_postnord_se_export_paper_invoice` | `warning` | outside the EU VAT area except Norway | Parcel product to a destination other than Norway | English customs page[^pn-se-en-page], Swedish customs page[^pn-se-sv-page], Service Point terms §4[^pn-se-service-point-terms] |

### PostNord from Finland advisories

| Advisory | Level | Destinations | Trigger | Sources |
|---|---|---|---|---|
| <a id="nordic_conventions_postnord_fi_export_invoice"></a>`nordic_conventions_postnord_fi_export_invoice` | `warning` | all destinations outside the EU VAT area | Parcel product | postnord.fi customs page[^pn-fi-page], PostNord FI parcel terms[^pn-fi-terms] |

### PostNord from Denmark advisories

| Advisory | Level | Destinations | Trigger | Sources |
|---|---|---|---|---|
| <a id="nordic_conventions_postnord_dk_export_documents"></a>`nordic_conventions_postnord_dk_export_documents` | `warning` | all destinations outside the EU VAT area | Parcel product | postnord.dk export page[^pn-dk-page] |

### DHL Freight Sweden from Sweden advisories

| Advisory | Level | Destinations | Trigger | Sources |
|---|---|---|---|---|
| <a id="nordic_conventions_dhl_freight_sweden_customs_mode_missing"></a>`nordic_conventions_dhl_freight_sweden_customs_mode_missing` | `warning` | all destinations outside the EU VAT area | None of the customs service options set by unified name | DHL product manual[^dhl-man], DHL price list[^dhl-prl], DHL connector spec[^dfs] |
| <a id="nordic_conventions_dhl_freight_sweden_invoice_copy"></a>`nordic_conventions_dhl_freight_sweden_invoice_copy` | `warning` | all destinations outside the EU VAT area | Any service | DHL product manual[^dhl-man], DHL export customs information[^dhl-cie], DHL price list[^dhl-prl] |
| <a id="nordic_conventions_dhl_freight_sweden_attached_documents"></a>`nordic_conventions_dhl_freight_sweden_attached_documents` | `warning` | all destinations outside the EU VAT area | Parcel Connect (`dhl_freight_sweden_parcel_connect_b2c`, 109) | DHL product manual[^dhl-man] |
| <a id="nordic_conventions_dhl_freight_sweden_voec_marking"></a>`nordic_conventions_dhl_freight_sweden_voec_marking` | `warning` | Norway only | Norway with `customs.options.voec_number` | DHL product manual[^dhl-man], DHL connector spec[^dfs] |

### Advisories across carriers

| Advisory | Level | Destinations | Trigger | Sources |
|---|---|---|---|---|
| <a id="nordic_conventions_invoice_type_content_mismatch"></a>`nordic_conventions_invoice_type_content_mismatch` | `warning` for proforma with sale-like content, `info` for commercial with gift or sample | all destinations outside the EU VAT area | PostNord parcel product or any DHL Freight Sweden service, booked with customs data | Bring customs page[^bring], DHL export customs information[^dhl-cie], Postpaket Utrikes terms §2[^pn-se-postpaket-terms], PostNord connector spec[^pns], DHL connector spec[^dfs] |
| <a id="nordic_conventions_attestation_conflict"></a>`nordic_conventions_attestation_conflict` | `warning` | Norway only | An attested procedure the lane's conventions contradict; in this version `nordic_conventions_commercial_invoice_paper_copy` on PostNord from Sweden to Norway | Service Point terms §4[^pn-se-service-point-terms], Swedish customs page[^pn-se-sv-page], PostNord connector spec[^pns] |

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

[^pn-se-service-point-terms]: PostNord SE Service Point special terms, valid 2026-01-01: <https://www.avropa.se/globalassets/bilagor/1.-aktuella-rao/postformedlingstjanster-2021/paketformedlingstjanster--1-lev-postnord/sarskilda-villkor-service-point-2026.pdf> (`PN_SE_SERVICE_POINT_TERMS_URL`).
[^pn-se-sv-page]: PostNord SE Swedish customs documents page, Wayback 2026-02-08: <https://www.postnord.se/foretag/import-export-tull/tulldokument-och-frakthandlingar-for-foretag/> (`PN_SE_SV_PAGE`).
[^pn-se-en-page]: PostNord SE English customs documents page, Wayback 2026-01-16: <https://web.archive.org/web/20260116090151/https://www.postnord.se/en/business/import-export-customs/customs-documents-and-shipping-documents/> (`PN_SE_EN_PAGE`).
[^pn-se-postpaket-terms]: PostNord SE Postpaket Utrikes terms, valid 2025-05-02: <https://api2.postnord.com/rest/customer/v2/ptm/file/download/5341.28764?disposition=inline> (`PN_SE_POSTPAKET_TERMS_URL`).
[^pn-fi-page]: postnord.fi customs information, read 2026-09-25: <https://www.postnord.fi/en/sending/online-tools/customs-information/> (`PN_FI_PAGE_URL`).
[^pn-fi-terms]: PostNord FI special terms for parcels, valid 2026-05-01, Wayback 2026-06-10; no URL is recorded (`PN_FI_TERMS`).
[^pn-dk-page]: postnord.dk export page, Wayback 2026-03-10: <https://www.postnord.dk/erhverv/eksport/> (`PN_DK_PAGE_URL`).
[^dhl-man]: DHL Freight Sweden product manual v5.23, valid 2025-04-14: <https://dhlpaket.se/dashboard/wp-content/uploads/sites/2/2025/04/DHL-FREIGHT-SWEDEN-PRODUCT-MANUAL-v5.23.pdf> (`DHL_MAN_URL`).
[^dhl-cie]: DHL Freight Sweden customs information export, 2025-02-03: <https://www.dhl.com/content/dam/dhl/local/se/dhl-freight/documents/pdf/se-freight-customs-information-export-en.pdf> (`DHL_CIE_URL`).
[^dhl-prl]: DHL Freight Sweden price list for additional services, valid 2026-05-01: <https://www.dhl.com/content/dam/dhl/local/se/dhl-freight/documents/pdf/se-freight-price-list-additional-services-sv.pdf> (`DHL_PRL_URL`).
[^bring]: Bring customs documents page: <https://www.bring.se/tjanster/tull/tulldokument> (`BRING_URL`).
[^pns]: karrio fork `openspec/specs/postnord/customs-declaration/spec.md` on branch `docs-openspec` at commit 60312fe2e (`PNS`).
[^dfs]: karrio fork `openspec/specs/dhl-freight-sweden/customs/spec.md` on branch `docs-openspec` at commit 60312fe2e (`DFS`).
