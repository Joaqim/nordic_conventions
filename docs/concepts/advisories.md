---
title: "Advisory reference"
---

Each advisory is a message with level `warning` or `info`, a stable code (public contract; renaming one is breaking), English text, and `details` with the lane and its `sources`, each tagged `S`, `W`, or `I`.
The tags follow the karrio fork's facts note: `S` is repository code or vendored specification, `W` is public carrier or authority documentation, and `I` is inference.
Where sources disagree the message states the stricter requirement.
DHL Freight Sweden customs options count only under their unified names: `dhl_freight_sweden_customs_handling_standard`, `dhl_freight_sweden_customs_handling_full_service`, `dhl_freight_sweden_customs_own_declaration`, `dhl_freight_sweden_customs_joint_declaration`.
Footnotes are named after their constants in `karrio/plugins/advisor_nordic_conventions/sources.py`; the [specification](../../openspec/specs/plugins/advisor-nordic-conventions/spec.md) has the section and line references.
Non-EU means outside the EU VAT area; which recipients count as outside is decided in [Territories](territories.md), and when the plugin advises at all in [Scope](scope.md).

## PostNord from Sweden

| Advisory | Level | Destinations | Trigger | Sources |
|---|---|---|---|---|
| <a id="advisor_nordic_conventions_postnord_se_no_digital_invoice"></a>Digital invoice to Norway | `info` for a parcel with customs data, else `warning` | Norway | Any service to Norway unless [Postpaket Utrikes invoice](#advisor_nordic_conventions_postnord_se_postpaket_commercial_invoice) applies; `postnord_export_letter` and `postnord_rek` add the SEK 0 invoice and VOEC statement | Service Point terms §4[^pn-se-service-point-terms], Swedish customs page[^pn-se-sv-page], PostNord connector spec[^pns] |
| <a id="advisor_nordic_conventions_postnord_se_postpaket_commercial_invoice"></a>Postpaket Utrikes invoice | `warning` | all non-EU | Commercial `postnord_postpaket_utrikes` (91); Norway gets digital routes instead of paper copies | Postpaket Utrikes terms §2[^pn-se-postpaket-terms], English customs page[^pn-se-en-page], Swedish customs page[^pn-se-sv-page], PostNord connector spec[^pns] |
| <a id="advisor_nordic_conventions_postnord_se_export_paper_invoice"></a>Paper invoice | `warning` | non-EU except Norway | Parcel product | English customs page[^pn-se-en-page], Swedish customs page[^pn-se-sv-page], Service Point terms §4[^pn-se-service-point-terms] |

## PostNord from Finland

| Advisory | Level | Destinations | Trigger | Sources |
|---|---|---|---|---|
| <a id="advisor_nordic_conventions_postnord_fi_export_invoice"></a>Export invoice | `warning` | all non-EU | Parcel product | postnord.fi customs page[^pn-fi-page], PostNord FI parcel terms[^pn-fi-terms] |

## PostNord from Denmark

| Advisory | Level | Destinations | Trigger | Sources |
|---|---|---|---|---|
| <a id="advisor_nordic_conventions_postnord_dk_export_documents"></a>Export documents | `warning` | all non-EU | Parcel product | postnord.dk export page[^pn-dk-page] |

## DHL Freight Sweden from Sweden

| Advisory | Level | Destinations | Trigger | Sources |
|---|---|---|---|---|
| <a id="advisor_nordic_conventions_dhl_freight_sweden_customs_mode_missing"></a>Customs mode missing | `warning` | all non-EU | No customs service option set by unified name, except to Åland (FI 22000-22999, also under `AX`), where a booking without one is accepted | DHL product manual[^dhl-man], DHL connector README[^dhl-connector-readme], DHL price list[^dhl-prl], DHL connector spec[^dfs] |
| <a id="advisor_nordic_conventions_dhl_freight_sweden_aland_customs_service_rejected"></a>Åland customs service | `warning` | all non-EU | A recipient in Åland (FI 22000-22999, also under `AX`) with customs handling standard or full service set, which DHL rejects with 24003 and the connector refuses; the message names the own declaration or customs data without a customs service | DHL product manual[^dhl-man], DHL connector destinations page[^dhl-connector-destinations] |
| <a id="advisor_nordic_conventions_dhl_freight_sweden_invoice_copy"></a>Invoice copy | `warning` | all non-EU | Any service | DHL product manual[^dhl-man], DHL export customs information[^dhl-cie], DHL price list[^dhl-prl] |
| <a id="advisor_nordic_conventions_dhl_freight_sweden_attached_documents"></a>Documents outside package | `warning` | all non-EU | Parcel Connect (`dhl_freight_sweden_parcel_connect_b2c`, 109) | DHL product manual[^dhl-man] |
| <a id="advisor_nordic_conventions_dhl_freight_sweden_voec_marking"></a>VOEC marking | `warning` | Norway | `customs.options.voec_number` set | DHL product manual[^dhl-man], DHL connector spec[^dfs] |
| <a id="advisor_nordic_conventions_dhl_freight_sweden_parcel_connect_not_served"></a>Product not served | `warning` | all non-EU | A product, by unified name or carrier code, whose manual "Valid countries" table allows no lane to the recipient's country: Parcel Return Connect (`dhl_freight_sweden_parcel_return_connect_c2b`, 107) to any country, a domestic product abroad, or another product to a country its table leaves out, such as Parcel Connect (109) or Parcel Connect Plus (112) to Switzerland, or a shipper or recipient postal code the product excludes, such as `JE*` and `GY*` under Great Britain for 109 and 112; territory codes are read as their parent country | DHL product manual[^dhl-man], DHL connector destinations page[^dhl-connector-destinations] |
| <a id="advisor_nordic_conventions_dhl_freight_sweden_parcel_connect_gb_agreement"></a>Parcel Connect to Great Britain | `warning` | Great Britain | Parcel Connect (`dhl_freight_sweden_parcel_connect_b2c`, 109) or Parcel Connect Plus (`dhl_freight_sweden_parcel_connect_plus`, 112), which serve Great Britain only by separate agreement, unless the recipient postal code is excluded | DHL product manual[^dhl-man], DHL connector sandbox rejection[^dhl-connector-gb-rejection] |
| <a id="advisor_nordic_conventions_dhl_freight_sweden_territory_postal_code_mismatch"></a>Territory postal code | `warning` | all non-EU | A recipient country code `AX`, `IC`, `EA`, `FO`, or `GL` whose postal code is missing or lies outside the territory, such as `AX` with 00100, which the connector refuses; advised even when the parent country's mainland is inside the EU VAT area | DHL connector territory check[^dhl-connector-territory-check] |
| <a id="advisor_nordic_conventions_dhl_freight_sweden_joint_declaration_destination"></a>Joint declaration destination | `warning` | all non-EU | `dhl_freight_sweden_customs_joint_declaration` set for a recipient country, read as its parent country, other than Norway or Switzerland, which the connector refuses; to Åland the message names the own declaration or no customs service as alternatives | DHL product manual[^dhl-man], DHL connector joint declaration check[^dhl-connector-joint-declaration-check] |
| <a id="advisor_nordic_conventions_dhl_freight_sweden_cyprus_documents"></a>Cyprus documents | `warning` | Cyprus | Any service; a commercial invoice and a packing list are required to prove the Union status of the goods, a T2L document where applicable, and copies of the recipient's ID documents, front and back, when the recipient is residential or names no company; the documents can be uploaded in myDHL Freight | DHL country-specific shipping requirements[^dhl-csr] |
| <a id="advisor_nordic_conventions_dhl_freight_sweden_greek_tax_ids"></a>Greek tax ids | `warning` | Greece | A product in the connector's party tax id set (202, SPI, or 601) with a sender or recipient that has neither `federal_tax_id` nor `state_tax_id`, which the connector refuses; the message requires a VAT number or TIN from the parties whose numbers are missing and states that `EL000000000` can be used for a private individual | DHL country-specific shipping requirements[^dhl-csr], DHL product manual[^dhl-man], DHL connector README[^dhl-connector-readme] |
| <a id="advisor_nordic_conventions_dhl_freight_sweden_sent_information"></a>SENT information | `info` | Poland | A product in the connector's transport declaration set (202, 205, 233, SPI, or 601); a SENT reference number and a Carrier Key Code are required when the goods are subject to the Polish SENT monitoring system, the connector validates the pair's consistency when given and declares the shipment SENT free with no information given, so deciding whether the goods are subject is the booker's responsibility | DHL connector README[^dhl-connector-readme] |
| <a id="advisor_nordic_conventions_dhl_freight_sweden_uit_information"></a>UIT information | `warning` at or above 500 kg total gross weight, `info` below | Romania | A product in the connector's transport declaration set (202, 205, 233, SPI, or 601); a UIT code is required when the goods exceed 500 kg gross weight, 10 000 RON in value, or are high-risk fiscal goods, the Romanian party provides the code, `UIT FREE` is entered when the goods are not subject, and the connector validates the declaration's consistency | DHL connector README[^dhl-connector-readme] |
| <a id="advisor_nordic_conventions_dhl_freight_sweden_ekaer_information"></a>EKAER information | `warning` at or above 500 kg total gross weight, `info` below | Hungary | A product in the connector's transport declaration set (202, 205, 233, SPI, or 601); an EKAER number is required when the goods are subject to the Hungarian EKAER control system (over 500 kg gross weight, over HUF 1 000 000 in value, or risky goods), the Hungarian party provides the number, `EKAER FREE` is entered when the goods are not subject, and the connector validates the declaration's consistency | DHL connector README[^dhl-connector-readme] |
| <a id="advisor_nordic_conventions_dhl_freight_sweden_spain_dg_documents"></a>Spain dangerous goods documents | `warning` | Spain | The `dangerous_good` shipment option set on any product; a dangerous goods declaration and a material safety data sheet must both be attached and can be uploaded in myDHL Freight, and the advisory reaches mainland Spain inside the EU VAT area and the Canary Islands and Ceuta and Melilla outside it | DHL country-specific shipping requirements[^dhl-csr] |

## Across carriers

| Advisory | Level | Destinations | Trigger | Sources |
|---|---|---|---|---|
| <a id="advisor_nordic_conventions_invoice_type_content_mismatch"></a>Invoice type mismatch | `warning` for proforma with sale-like content, `info` for commercial with gift or sample | all non-EU | PostNord parcel product or any DHL Freight Sweden service, with customs data | Bring customs page[^bring], DHL export customs information[^dhl-cie], Postpaket Utrikes terms §2[^pn-se-postpaket-terms], PostNord connector spec[^pns], DHL connector spec[^dfs] |
| <a id="advisor_nordic_conventions_attestation_conflict"></a>Attestation conflict | `warning` | Norway | An attestation the lane contradicts; in this version a paper invoice on PostNord from Sweden to Norway | Service Point terms §4[^pn-se-service-point-terms], Swedish customs page[^pn-se-sv-page], PostNord connector spec[^pns] |
| <a id="advisor_nordic_conventions_ch_discount_on_invoice"></a>Discount to Switzerland | `info` | Switzerland | A commodity with `metadata.discount_percentage` set or a value of 0 or none | BAZG R-69-03 §5.5.3[^bazg-rabatte] |
| <a id="advisor_nordic_conventions_zero_value_line"></a>Zero-value line | `warning` | all non-EU | A commodity with a value of 0 or none | PostNord Norway parcels page[^pn-se-no-page], Tullverket export documents page[^tv-export-documents], DHL Express customs guidelines[^dhl-express-customs] |

## Codes

- Digital invoice to Norway: `advisor_nordic_conventions_postnord_se_no_digital_invoice`
- Postpaket Utrikes invoice: `advisor_nordic_conventions_postnord_se_postpaket_commercial_invoice`
- Paper invoice: `advisor_nordic_conventions_postnord_se_export_paper_invoice`
- Export invoice: `advisor_nordic_conventions_postnord_fi_export_invoice`
- Export documents: `advisor_nordic_conventions_postnord_dk_export_documents`
- Customs mode missing: `advisor_nordic_conventions_dhl_freight_sweden_customs_mode_missing`
- Åland customs service: `advisor_nordic_conventions_dhl_freight_sweden_aland_customs_service_rejected`
- Invoice copy: `advisor_nordic_conventions_dhl_freight_sweden_invoice_copy`
- Documents outside package: `advisor_nordic_conventions_dhl_freight_sweden_attached_documents`
- VOEC marking: `advisor_nordic_conventions_dhl_freight_sweden_voec_marking`
- Product not served: `advisor_nordic_conventions_dhl_freight_sweden_parcel_connect_not_served`
- Parcel Connect to Great Britain: `advisor_nordic_conventions_dhl_freight_sweden_parcel_connect_gb_agreement`
- Territory postal code: `advisor_nordic_conventions_dhl_freight_sweden_territory_postal_code_mismatch`
- Joint declaration destination: `advisor_nordic_conventions_dhl_freight_sweden_joint_declaration_destination`
- Cyprus documents: `advisor_nordic_conventions_dhl_freight_sweden_cyprus_documents`
- Greek tax ids: `advisor_nordic_conventions_dhl_freight_sweden_greek_tax_ids`
- SENT information: `advisor_nordic_conventions_dhl_freight_sweden_sent_information`
- UIT information: `advisor_nordic_conventions_dhl_freight_sweden_uit_information`
- EKAER information: `advisor_nordic_conventions_dhl_freight_sweden_ekaer_information`
- Spain dangerous goods documents: `advisor_nordic_conventions_dhl_freight_sweden_spain_dg_documents`
- Invoice type mismatch: `advisor_nordic_conventions_invoice_type_content_mismatch`
- Attestation conflict: `advisor_nordic_conventions_attestation_conflict`
- Discount to Switzerland: `advisor_nordic_conventions_ch_discount_on_invoice`
- Zero-value line: `advisor_nordic_conventions_zero_value_line`

[^pn-se-service-point-terms]: PostNord SE Service Point special terms, valid 2026-01-01: <https://www.avropa.se/globalassets/bilagor/1.-aktuella-rao/postformedlingstjanster-2021/paketformedlingstjanster--1-lev-postnord/sarskilda-villkor-service-point-2026.pdf> (`PN_SE_SERVICE_POINT_TERMS_URL`).
[^pn-se-sv-page]: PostNord SE Swedish customs documents page, Wayback 2026-02-08: <https://www.postnord.se/foretag/import-export-tull/tulldokument-och-frakthandlingar-for-foretag/> (`PN_SE_SV_PAGE`).
[^pn-se-en-page]: PostNord SE English customs documents page, Wayback 2026-01-16: <https://web.archive.org/web/20260116090151/https://www.postnord.se/en/business/import-export-customs/customs-documents-and-shipping-documents/> (`PN_SE_EN_PAGE`).
[^pn-se-postpaket-terms]: PostNord SE Postpaket Utrikes terms, valid 2025-05-02: <https://api2.postnord.com/rest/customer/v2/ptm/file/download/5341.28764?disposition=inline> (`PN_SE_POSTPAKET_TERMS_URL`).
[^pn-fi-page]: postnord.fi customs information, read 2026-09-25: <https://www.postnord.fi/en/sending/online-tools/customs-information/> (`PN_FI_PAGE_URL`).
[^pn-fi-terms]: PostNord FI special terms for parcels, valid 2026-05-01, Wayback 2026-06-10; no URL is recorded (`PN_FI_TERMS`).
[^pn-dk-page]: postnord.dk export page, Wayback 2026-03-10: <https://www.postnord.dk/erhverv/eksport/> (`PN_DK_PAGE_URL`).
[^dhl-man]: DHL Freight Sweden product manual v5.26, updated 2026-10-01, valid from 2026-11-01, sha256 050660c37ba93d1ae9514c50dfa42c2010bc87763ccaff51a740b2526af11b73, listed at <https://dhlpaket.se/dashboard/specifications/products/> (`DHL_MAN_URL`).
[^dhl-connector-readme]: DHL Freight Sweden connector README at commit 7a2214d, read 2026-10-08: <https://github.com/PrimePack-AB/karrio-dhl-freight-sweden/blob/7a2214d/README.md> (`DHL_CONNECTOR_README_URL`).
[^dhl-connector-destinations]: DHL Freight Sweden connector destinations page at commit 7a2214d, read 2026-10-08: <https://github.com/PrimePack-AB/karrio-dhl-freight-sweden/blob/7a2214d/docs/concepts/destinations.md> (`DHL_CONNECTOR_DESTINATIONS_URL`).
[^dhl-connector-territory-check]: DHL Freight Sweden connector territory check, karrio/providers/dhl_freight_sweden/units.py TERRITORY_POSTAL_CODES and shipment/create.py TerritoryPostalCodeError at commit 142b62d, committed 2026-10-08: <https://github.com/PrimePack-AB/karrio-dhl-freight-sweden/commit/142b62d> (`DHL_CONNECTOR_TERRITORY_CHECK`).
[^dhl-connector-joint-declaration-check]: DHL Freight Sweden connector joint declaration check, karrio/providers/dhl_freight_sweden/units.py JOINT_DECLARATION_COUNTRIES and shipment/create.py JointDeclarationDestinationError at commit f86c8ac, committed 2026-10-08: <https://github.com/PrimePack-AB/karrio-dhl-freight-sweden/commit/f86c8ac> (`DHL_CONNECTOR_JOINT_DECLARATION_CHECK`).
[^dhl-connector-gb-rejection]: DHL Freight Sweden connector sandbox rejection of Parcel Connect Plus (112) from SE to GB, captured 2026-10-06: <https://github.com/PrimePack-AB/karrio-dhl-freight-sweden/blob/28c1ccb/tests/dhl_freight_sweden/fixtures/sandbox/rejection-22005-112-se-gb.json> (`DHL_CONNECTOR_REJECTION_112_GB_URL`).
[^dhl-cie]: DHL Freight Sweden customs information export, 2025-02-03: <https://www.dhl.com/content/dam/dhl/local/se/dhl-freight/documents/pdf/se-freight-customs-information-export-en.pdf> (`DHL_CIE_URL`).
[^dhl-prl]: DHL Freight Sweden price list for additional services, valid 2026-05-01: <https://www.dhl.com/content/dam/dhl/local/se/dhl-freight/documents/pdf/se-freight-price-list-additional-services-sv.pdf> (`DHL_PRL_URL`).
[^dhl-csr]: DHL Freight Sweden Country-specific shipping requirements (English), accessed 2026-10-09: <https://www.dhl.com/se-en/home/freight/help-center-for-european-road-and-rail/useful-information-and-downloads.html> (`DHL_CSR_URL`).
[^bring]: Bring customs documents page: <https://www.bring.se/tjanster/tull/tulldokument> (`BRING_URL`).
[^pns]: karrio fork `openspec/specs/postnord/customs-declaration/spec.md` on branch `docs-openspec` at commit 60312fe2e (`PNS`).
[^dfs]: karrio fork `openspec/specs/dhl-freight-sweden/customs/spec.md` on branch `docs-openspec` at commit 60312fe2e (`DFS`).
[^bazg-rabatte]: BAZG Richtlinie R-69-03, valid 2025-01-01: <https://www.bazg.admin.ch/dam/de/sd-web/mIvoM5CF7ydH/steuerbemessungsgrundlage-de.pdf> (`BAZG_R_69_03_URL`).
[^pn-se-no-page]: PostNord SE page on sending parcels to Norway, read 2026-10-02: <https://www.postnord.se/privat/skicka/skicka-brev-och-paket-utomlands/skicka-paket-till-norge/> (`PN_SE_NO_PAGE_URL`).
[^tv-export-documents]: Tullverket supporting documents for export, updated 2026-06-12, read 2026-10-02: <https://www.tullverket.se/sv/foretag/exporteravaror/deklareravarorvidexport/styrkandehandlingarvidexport.4.78aa922815794d801e25e3.html> (`TV_EXPORT_DOCUMENTS_URL`).
[^dhl-express-customs]: DHL Express global customs customer guidelines: <https://mydhl.express.dhl/content/dam/downloads/global/en/customs-guide/express_global_customs_customer_guidelines.pdf.coredownload.pdf> (`DHL_EXPRESS_CUSTOMS_URL`).
