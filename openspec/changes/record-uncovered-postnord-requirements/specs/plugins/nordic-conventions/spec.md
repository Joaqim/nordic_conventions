# Spec Delta

## MODIFIED Requirements

### Requirement: PostNord Sweden commercial Postpaket Utrikes carries a commercial invoice

For a commercial PostNord shipment from Sweden to a destination outside the EU VAT area booked as International Parcel (`postnord_postpaket_utrikes`, `91`, "Z91 Postpaket Utrikes" in the connector's vendored general descriptions, FN:165, S; marketed in Denmark as EMS), the plugin SHALL return code `nordic_conventions_postnord_se_postpaket_commercial_invoice` at level `warning`.
For destinations other than Norway the message SHALL state that the parcel needs the CN23 export declaration and a commercial invoice in three copies with the parcel.
Three copies is the stricter reading of conflicting sources and satisfies both at every value: the Postpaket Utrikes terms §2 require the CN23 in two copies and the commercial invoice in two copies when the value exceeds SEK 2 000 or the goods are sent for commercial purposes (FN:103, FN:111, W), while the EN and SV web pages require a commercial or proforma invoice in triplicate when the value exceeds SEK 2 000, on value only (FN:102, FN:107, FN:109, W); the plugin does not evaluate goods value, and two copies would fall short of the web pages above SEK 2 000.
`details` SHALL list both the terms and the web pages with the copy count and trigger each states.
For Norway the Norway-specific digital-only rule overrides the general copy count: the message SHALL state that the CN23 is required and that the invoice is sent digitally and not attached to the parcel, naming PostNord's Norway routes (the Booking API, PostNord Skicka Direkt Business, foravisering.export@postnord.com, and MyCustoms upload), and `details` SHALL cite the terms, the web pages, and the Norway rule (FN:142, FN:147, W).
The message SHALL state that the connector currently sends CN22 declaration data and no invoice for International Parcel (PNS lines 10 and 13-16, S), so the consumer must supply the CN23 and the invoice.
Non-commercial Postpaket Utrikes above SEK 2 000 is deferred with the other value thresholds, and letter services receive no such advisory because the letter rule depends on goods value only and the EN and SV pages conflict on CN22 versus CN23 above SEK 2 000 (FN:98, FN:105-110, W and I).
Recorded gap, not addressed: PostNord requires the CN23 for International Parcel at every value, including non-commercial content such as gifts, samples, documents, and returned goods (FN:101, FN:111, W), while the connector sends CN22 declaration data for it (PNS lines 10 and 13-16, S).
For non-commercial International Parcel the plugin returns no advisory for destinations other than Norway, and for Norway returns only `nordic_conventions_postnord_se_no_digital_invoice`, whose message does not mention the CN23.
Sources: FN:101-103 and FN:105-112 (W, verbatim web page and terms rules), FN:165-167 (S and W, code 91 is the contract product).

#### Scenario: Commercial Postpaket Utrikes to the United States

- **WHEN** a PostNord `postnord_postpaket_utrikes` shipment from Sweden to the United States is created with customs data whose `commercial_invoice` is true
- **THEN** the plugin returns code `nordic_conventions_postnord_se_postpaket_commercial_invoice` at level `warning` stating the CN23, a commercial invoice in three copies, and that the connector sends CN22 data, and its details list the terms with two copies and the web pages with triplicate

#### Scenario: Sale-like content triggers the advisory

- **WHEN** a PostNord `postnord_postpaket_utrikes` shipment from Sweden to Switzerland is created with customs data whose `content_type` is `merchandise` and whose `commercial_invoice` is false
- **THEN** the plugin returns code `nordic_conventions_postnord_se_postpaket_commercial_invoice`

#### Scenario: Commercial Postpaket Utrikes to Norway sends the invoice digitally

- **WHEN** a PostNord `postnord_postpaket_utrikes` shipment from Sweden to Norway is created with customs data whose `commercial_invoice` is true
- **THEN** the plugin returns code `nordic_conventions_postnord_se_postpaket_commercial_invoice` stating the CN23 and the invoice sent digitally through the Booking API, Skicka Direkt Business, foravisering.export@postnord.com, or MyCustoms, without paper invoice copies, and its details cite the terms, the web pages, and the Norway rule

#### Scenario: Gift Postpaket Utrikes is not advised

- **WHEN** a PostNord `postnord_postpaket_utrikes` shipment from Sweden to Switzerland is created with customs data whose `content_type` is `gift` and whose `commercial_invoice` is false
- **THEN** the plugin does not return code `nordic_conventions_postnord_se_postpaket_commercial_invoice`, although PostNord requires the CN23 for this shipment at every value (FN:101, FN:111, W), a recorded gap the plugin does not advise

#### Scenario: Letters are not advised

- **WHEN** a commercial PostNord `postnord_export_letter` shipment from Sweden to Switzerland is created
- **THEN** the plugin does not return code `nordic_conventions_postnord_se_postpaket_commercial_invoice`

#### Scenario: Finnish Postpaket Utrikes is not advised

- **WHEN** a commercial PostNord `postnord_postpaket_utrikes` shipment from Finland to Switzerland is created
- **THEN** the plugin does not return code `nordic_conventions_postnord_se_postpaket_commercial_invoice`

### Requirement: PostNord Finland parcels outside the EU VAT area

For a PostNord parcel product from Finland to a destination outside the EU VAT area, the plugin SHALL return code `nordic_conventions_postnord_fi_export_invoice` at level `warning`, stating that a copy of the invoice can be emailed to tullaus.fi@postnord.com and, for destinations other than Norway, that a signed commercial invoice in English in triplicate must accompany the parcel, or, for Norway, that the invoice must reach PostNord electronically before the shipment.
The signed-triplicate statement is the stricter of the conflicting sources: the postnord.fi customs information page says the invoice "can be attached to the shipment or submitted separately" and signed "if necessary" (FN:143, FN:152, W), while the PostNord FI special terms for parcels valid 2026-05-01 require "a signed commercial invoice in English in triplicate" for non-EU parcels and electronic invoices to Norway (FN:143, FN:154, W); which governs is unresolved (FN:155, I; FN:267).
The Norway statement rests on the same page and terms (FN:153-154, W).
Recorded gap, not addressed: this advisory is limited to PostNord parcel products, so International Parcel and letter services from Finland to destinations outside the EU VAT area receive no advisory, and this specification records no PostNord Finland requirement for those services.

#### Scenario: Finnish parcel to Great Britain

- **WHEN** a PostNord `postnord_parcel` shipment from Finland to Great Britain is created
- **THEN** the plugin returns code `nordic_conventions_postnord_fi_export_invoice` at level `warning` naming tullaus.fi@postnord.com and a signed invoice in triplicate, and its details list both the web page and the 2026 special terms with their statements

#### Scenario: Finnish parcel to Norway

- **WHEN** a PostNord `postnord_parcel` shipment from Finland to Norway is created
- **THEN** the plugin returns code `nordic_conventions_postnord_fi_export_invoice` stating that the invoice must reach PostNord electronically before the shipment, without the triplicate statement

### Requirement: PostNord Denmark parcels outside the EU VAT area

For a PostNord parcel product from Denmark to a destination outside the EU VAT area, the plugin SHALL return code `nordic_conventions_postnord_dk_export_documents` at level `warning`, stating that the documents go in a plastic pocket visible on the parcel and the copy count for the destination: 2 invoices for Norway, 3 for Switzerland and Liechtenstein, 2 for Great Britain, and 1 CN23 with 2 invoices for any other destination, where the invoice is described by PostNord as not required but recommended (FN:144, W, postnord.dk/erhverv/eksport via Wayback 2026-03-10, FN:157).
The message SHALL also state, without evaluating any value threshold, that if an export declaration was lodged a copy goes to eksport@postnord.com (FN:144, W); the DKK 7 500 threshold at which PostNord requires the export declaration is deferred.
Recorded gap, not addressed: this advisory is limited to PostNord parcel products, so International Parcel and letter services from Denmark to destinations outside the EU VAT area receive no advisory, and this specification records no PostNord Denmark requirement for those services.

#### Scenario: Danish parcel to Liechtenstein

- **WHEN** a PostNord `postnord_parcel` shipment from Denmark to `LI` is created
- **THEN** the plugin returns code `nordic_conventions_postnord_dk_export_documents` at level `warning` stating 3 copies, a plastic pocket, and that a lodged export declaration is copied to eksport@postnord.com

#### Scenario: Danish parcel to the United States

- **WHEN** a PostNord `postnord_parcel` shipment from Denmark to `US` is created
- **THEN** the plugin returns code `nordic_conventions_postnord_dk_export_documents` stating 1 CN23 and 2 invoices, the invoice being recommended

### Requirement: The invoice type matches the content type

For an in-scope shipment whose booking carries an invoice type, meaning a PostNord parcel product or any DHL Freight Sweden service booked with customs data, the plugin SHALL return code `nordic_conventions_invoice_type_content_mismatch` at level `warning` when `customs.commercial_invoice` is false or omitted while the content is sale-like, and at level `info` when `customs.commercial_invoice` is true while `customs.content_type` is gift or sample.
The warning message SHALL state that the connector declares a proforma invoice from the flag, that a proforma invoice is for gifts and samples for which the recipient makes no payment, and that goods sold need `commercial_invoice` set to true; the info message SHALL state that a commercial invoice is declared for content described as a gift or sample, for which a proforma invoice is the usual document.
The levels differ because the sources restrict the proforma invoice to goods not sold but do not forbid a commercial invoice for gifts or samples.
Recorded gap, not addressed: the Postpaket Utrikes terms §2 permit a proforma invoice only for gifts or samples (FN:111, FN:113, W), but this advisory does not apply to International Parcel, whose booking carries no invoice type.
Recorded gap, not addressed: for International Parcel and letter services the connector sends CN22 declaration data and builds `customs.commercial_invoice`, `customs.invoice`, and `customs.invoice_date` only into the customs invoice of parcel products (PNS lines 10 and 13-16, S; karrio `feat-postnord-customs-invoice` at 1b40eeb7e, `shipment/create.py:608-635` and `shipment/create.py:775`, S), so it drops those fields for these services without a warning.
`nordic_conventions_postnord_se_postpaket_commercial_invoice` tells the consumer to supply the invoice for commercial International Parcel, and no advisory states the drop.
Sources: PNS lines 155-168 and DFS lines 51-64 (S, the connectors apply the flag literally and leave mismatch detection to advisory tooling), FN:56 (W, Bring tulldokument and DHL CIE p.5, a proforma invoice is used for goods not sold), FN:111 and FN:113 (W, Postpaket Utrikes terms §2, "Proformafaktura … får endast användas vid gåva eller varuprov"), FN:30-36 (S, connector mapping of the flag).

#### Scenario: Merchandise declared as proforma

- **WHEN** a DHL Freight Sweden shipment from Sweden to Norway is created with customs data whose `content_type` is `merchandise` and whose `commercial_invoice` is omitted
- **THEN** the plugin returns code `nordic_conventions_invoice_type_content_mismatch` at level `warning`

#### Scenario: Omitted content type declared as proforma

- **WHEN** a PostNord `postnord_parcel` shipment from Sweden to Norway is created with customs data carrying no `content_type` and `commercial_invoice` false
- **THEN** the plugin returns code `nordic_conventions_invoice_type_content_mismatch` at level `warning`

#### Scenario: Gift declared as proforma is consistent

- **WHEN** a PostNord `postnord_parcel` shipment from Sweden to Norway is created with customs data whose `content_type` is `gift` and whose `commercial_invoice` is false
- **THEN** the plugin does not return code `nordic_conventions_invoice_type_content_mismatch`

#### Scenario: Return merchandise declared as proforma is consistent

- **WHEN** a DHL Freight Sweden shipment from Sweden to Norway is created with customs data whose `content_type` is `return_merchandise` and whose `commercial_invoice` is false
- **THEN** the plugin does not return code `nordic_conventions_invoice_type_content_mismatch`

#### Scenario: Sample declared as commercial is informational

- **WHEN** a DHL Freight Sweden shipment from Sweden to Switzerland is created with customs data whose `content_type` is `sample` and whose `commercial_invoice` is true
- **THEN** the plugin returns code `nordic_conventions_invoice_type_content_mismatch` at level `info`

#### Scenario: Letters carry no invoice type

- **WHEN** a PostNord `postnord_export_letter` shipment from Sweden to Norway is created with customs data whose `content_type` is `merchandise` and whose `commercial_invoice` is false
- **THEN** the plugin does not return code `nordic_conventions_invoice_type_content_mismatch`, because the connector sends a CN22 without an invoice type for letters
