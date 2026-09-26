# Spec Delta

## Purpose

Defines the Nordic conventions plugin, an advisor-only karrio plugin that adds non-blocking trade-document advisories to PostNord and DHL Freight Sweden shipment responses for Swedish, Danish, and Finnish shippers sending goods outside the EU VAT area, each advisory citing the carrier or authority source it rests on.

Source references in this spec use FN for the karrio fork's `docs/notes/customs/nordic-trade-documents-facts.md` (branch `docs-openspec`, commit baf8eb3dd) with line numbers, and keep the note's evidence tags: S is repository code or vendored specification, W is public carrier or authority documentation, and I is inference.
Connector behaviour cited as S refers to the karrio fork's main specs `openspec/specs/postnord/customs-declaration/spec.md` (PNS) and `openspec/specs/dhl-freight-sweden/customs/spec.md` (DFS), both on branch `docs-openspec` at commit 60312fe2e.
PostNord parcel products are the PostNord services that are neither letter services nor International Parcel (`postnord_postpaket_utrikes`), as defined by PNS lines 10-11.
PostNord letter services are `postnord_tracked` (`04`), `postnord_tracked_letter` (`34`), `postnord_export_letter` (`UX`), `postnord_varubrev_first_class` (`86`), `postnord_expressbrev` (`LX`), `postnord_rek` (`RR`), `postnord_rek_retur` (`RK`), `postnord_rek_extra` (`RL`), `postnord_rekommanderet_brev` (`RE`), `postnord_rekommanderet_quickbrev` (`RQ`), `postnord_varde` (`VV`), and `postnord_afleveringsattest` (`AF`), the letter set of the PostNord connector (karrio `develop` at 7a56ffa5b, `modules/connectors/postnord/karrio/providers/postnord/units.py:269-284`, S).
Norway-named letter services are the letter services named in the letters table of the PostNord SE Swedish customs documents page (Brev utrikes, PostNord Untracked letter, Spårbart brev utrikes, Rek utrikes; W, Wayback 2026-02-08, FN:108) that map to a connector code with clear evidence: `postnord_export_letter` (`UX`, connector label "Export Letter Sweden", live-verified as an SE export letter in the karrio fork's `docs/notes/postnord/customs-declaration-live-verification.md:5`, S) and `postnord_rek` (`RR`, connector label "registered mail", S).
Spårbart brev utrikes (tracked) has no connector code identified with clear evidence and Varubrev is not named in that table, so neither is a Norway-named letter service.

## ADDED Requirements

### Requirement: The plugin is an advisor-only plugin

The plugin SHALL register through the `karrio.plugins` entry point group under the id `nordic_conventions`, SHALL declare shipment advisors and no carrier mapper, proxy, settings, or address validator, and SHALL be reported by karrio with the plugin type `advisor`.

#### Scenario: Installed plugin is collected as an advisor

- **WHEN** the plugin is installed alongside a karrio SDK that provides the shipment advisors hook
- **THEN** karrio lists a plugin `nordic_conventions` of type `advisor` and collects its advisors

### Requirement: The plugin degrades without the advisors hook

On a karrio SDK whose plugin metadata has no `shipment_advisors` field, importing and loading the plugin SHALL NOT raise; the plugin SHALL register no advisors and SHALL log once that the hook is unavailable.

#### Scenario: Older karrio loads the plugin without advisors

- **WHEN** the plugin is loaded by a karrio SDK without the shipment advisors hook
- **THEN** plugin discovery succeeds, no advisor is registered, one log record states that the hook is unavailable, and shipment responses are unchanged

### Requirement: Advice is limited to Nordic shippers at shipment creation

The plugin SHALL return no message unless all of the following hold: the advisor context operation is `shipping`; the context carrier name is `postnord` with a shipper country of `SE`, `DK`, or `FI`, or `dhl_freight_sweden` with a shipper country of `SE`; the shipper address is inside the EU VAT area; and the recipient address is outside the EU VAT area.
Shipper and recipient SHALL be read from the request as passed to the advisor, so for return shipments, whose shipper and recipient the SDK swaps before advisors run, the returning party is the shipper.
Norwegian shippers are out of scope because PostNord Norway export rules were not found (FN:145, FN:263, W).

#### Scenario: Rating receives no advice

- **WHEN** rates are fetched from PostNord for a Swedish shipper and a Norwegian recipient
- **THEN** the plugin returns no message

#### Scenario: Other carriers receive no advice

- **WHEN** a shipment from Sweden to Norway is created with a carrier other than `postnord` or `dhl_freight_sweden`
- **THEN** the plugin returns no message

#### Scenario: Norwegian shippers receive no advice

- **WHEN** a PostNord shipment from Norway to Sweden is created
- **THEN** the plugin returns no message

#### Scenario: Danish shippers receive no DHL Freight Sweden advice

- **WHEN** a DHL Freight Sweden shipment from Denmark to Norway is created
- **THEN** the plugin returns no message

#### Scenario: Intra-EU shipments receive no advice

- **WHEN** a PostNord or DHL Freight Sweden shipment from Sweden to Germany is created
- **THEN** the plugin returns no message

#### Scenario: Return from Norway receives no advice

- **WHEN** a PostNord return shipment is created whose original shipper is in Sweden and original recipient is in Norway
- **THEN** the request passed to the advisor has a Norwegian shipper and the plugin returns no message

#### Scenario: Åland shipper receives no advice

- **WHEN** a PostNord shipment is created from `FI` with postal code 22100 to Norway
- **THEN** the plugin returns no message, because the shipper is outside the EU VAT area

### Requirement: The EU VAT area follows the connectors' definition

The plugin SHALL decide EU VAT area membership from its own territory table, independent of karrio's `EUCountry`, which lists Greece as `EL` and lacks `AX` and `XI` (FN:235, FN:276, S).
The table SHALL match the definition applied by the PostNord and DHL Freight Sweden connectors (PNS line 188, DFS line 114, S), itself taken from Tullverket's list of EU customs and fiscal territories (FN:58-65, W): the EU member states with Greece as `GR` are inside, and Åland (`AX`, or `FI` 22000-22999), the Canary Islands (`IC`, or `ES` 35000-35999 and 38000-38999), Ceuta (`ES` 51000-51999), Melilla (`ES` 52000-52999), Büsingen (`DE` 78266), Heligoland (`DE` 27498), Livigno (`IT` 23041), Campione d'Italia (`IT` 22061), and the French overseas departments (`GP`, `GF`, `MQ`, `RE`, `YT`) are outside.
Monaco, Northern Ireland, and Mount Athos, which Tullverket lists with a different status (FN:58-65, W), SHALL follow the connectors' country-level treatment; changing them is deferred to a change covering both connectors and this plugin.
Postal codes SHALL be compared after removing spaces, and a postal code that is not purely numeric SHALL leave the country-level decision unchanged.

#### Scenario: Åland by postal code is outside

- **WHEN** a PostNord shipment is created from Sweden to `FI` with postal code 22100
- **THEN** the recipient is treated as outside the EU VAT area and the Swedish PostNord advisories for destinations outside the EU VAT area apply

#### Scenario: Greece is inside

- **WHEN** a DHL Freight Sweden shipment is created from Sweden to `GR`
- **THEN** the plugin returns no message

#### Scenario: Canary Islands by postal code are outside

- **WHEN** a DHL Freight Sweden shipment is created from Sweden to `ES` with postal code 35 001
- **THEN** the recipient is treated as outside the EU VAT area

### Requirement: Advisories are non-blocking, coded, and attributed

Every message the plugin returns SHALL have level `warning` or `info`, a code from this specification that starts with `nordic_` and does not contain `SHIPPING_SDK_`, a message text in English, and `details` holding a `sources` list in which each entry names its evidence tag (`S`, `W`, or `I`) and its reference.
Where the cited sources disagree, the message text SHALL state the stricter requirement and `details` SHALL list every disagreeing source with the statement each makes.
Message texts SHALL name electronic and carrier-native, no-cost routes before paper where the sources allow them.
Several advisories MAY apply to one shipment, and the plugin SHALL return each applicable advisory once.

#### Scenario: Conflicting sources are both attributed

- **WHEN** an advisory whose sources state different invoice copy counts is returned
- **THEN** its message states the larger count and its details list each source with the count that source states

#### Scenario: Several advisories on one shipment

- **WHEN** a DHL Freight Sweden Parcel Connect (`109`) shipment from Sweden to Norway is created without customs data and without a customs handling option
- **THEN** the response carries exactly one message each with codes `nordic_dhl_freight_sweden_customs_mode_missing`, `nordic_dhl_freight_sweden_invoice_copy`, and `nordic_dhl_freight_sweden_attached_documents`

### Requirement: Commercial content is determined once

The plugin SHALL use one determination of sale-like content and of commercial shipments for every advisory that depends on them.
A shipment's content is sale-like when its customs data carries a `content_type` that, compared case-insensitively against karrio's customs content type names and values, is neither gift nor sample nor documents nor return merchandise, or carries no `content_type`.
A shipment is commercial when it carries customs data and either `customs.commercial_invoice` is true or its content is sale-like.
A shipment without customs data is neither sale-like nor commercial.

#### Scenario: Merchandise is sale-like

- **WHEN** customs data carries `content_type` `MERCHANDISE` and `commercial_invoice` false
- **THEN** the content is sale-like and the shipment is commercial

#### Scenario: Omitted content type is sale-like

- **WHEN** customs data carries no `content_type`
- **THEN** the content is sale-like

#### Scenario: Gift with commercial flag is commercial but not sale-like

- **WHEN** customs data carries `content_type` `gift` and `commercial_invoice` true
- **THEN** the content is not sale-like and the shipment is commercial

#### Scenario: Return merchandise without commercial flag is not commercial

- **WHEN** customs data carries `content_type` `return_merchandise` and `commercial_invoice` false
- **THEN** the content is not sale-like and the shipment is not commercial

### Requirement: PostNord Sweden to Norway invoices go digitally

For a PostNord shipment from Sweden to Norway to which `nordic_postnord_se_postpaket_commercial_invoice` does not apply, the plugin SHALL return code `nordic_postnord_se_no_digital_invoice`, stating that PostNord requires the commercial invoice for Norway digitally rather than on paper with the parcel, and naming the routes: the booking itself (the connector transmits a customs invoice for parcel products booked with customs data, PNS lines 28-31, S), PostNord Skicka Direkt Business, the email address foravisering.export@postnord.com, and upload in PostNord MyCustoms.
For a Norway-named letter service the message SHALL also state that a commercial invoice and a VOEC number are required for letters to Norway from SEK 0, the invoice sent digitally through the same routes (FN:99, FN:108, W, SV page only); other letter services receive this advisory without that statement.
When `nordic_postnord_se_postpaket_commercial_invoice` applies to a shipment, it carries the Norway invoice routes itself and this advisory SHALL NOT be returned, so each shipment receives the invoice routes once.
The level SHALL be `info` when the booking is a parcel product carrying customs data, because the connector already transmits the invoice data, and `warning` otherwise, because the invoice then reaches PostNord only through a route the consumer owns.
Sources: FN:118 (W, Service Point special terms §4, "To Norway the commercial invoice and shipment list shall be sent digitally"), FN:142 and FN:147 (W, PostNord SE customs documents pages, Norway channels and MyCustoms), FN:149 (W, the separate channels are stated for Norway only), FN:108 (W, SV page, "Vid export till Norge behöver Handelsfaktura och VOEC* anges från 0 kr.").

#### Scenario: Parcel booking with customs data is informational

- **WHEN** a PostNord `postnord_parcel` shipment from Sweden to Norway is created with customs data
- **THEN** the plugin returns code `nordic_postnord_se_no_digital_invoice` at level `info`, naming Skicka Direkt Business, foravisering.export@postnord.com, and MyCustoms

#### Scenario: Letter to Norway states invoice and VOEC from SEK 0

- **WHEN** a PostNord `postnord_export_letter` shipment from Sweden to Norway is created with customs data whose `content_type` is `merchandise`
- **THEN** the plugin returns code `nordic_postnord_se_no_digital_invoice` at level `warning`, stating that a commercial invoice and a VOEC number are required from SEK 0 and that the invoice is sent digitally, and citing the SV page

#### Scenario: Letter not named by the Swedish page omits the SEK 0 statement

- **WHEN** a PostNord `postnord_varubrev_first_class` shipment from Sweden to Norway is created with customs data whose `content_type` is `merchandise`
- **THEN** the plugin returns code `nordic_postnord_se_no_digital_invoice` at level `warning` naming the Norway invoice routes, without the commercial invoice and VOEC from SEK 0 statement

#### Scenario: Commercial Postpaket Utrikes to Norway receives the invoice routes once

- **WHEN** a PostNord `postnord_postpaket_utrikes` shipment from Sweden to Norway is created with customs data whose `commercial_invoice` is true
- **THEN** the plugin returns code `nordic_postnord_se_postpaket_commercial_invoice` naming the Norway invoice routes and does not return code `nordic_postnord_se_no_digital_invoice`

#### Scenario: Non-commercial Postpaket Utrikes to Norway is a warning

- **WHEN** a PostNord `postnord_postpaket_utrikes` shipment from Sweden to Norway is created with customs data whose `content_type` is `gift` and whose `commercial_invoice` is false
- **THEN** the plugin returns code `nordic_postnord_se_no_digital_invoice` at level `warning` and not code `nordic_postnord_se_postpaket_commercial_invoice`

### Requirement: PostNord Sweden parcels outside the EU VAT area carry a paper invoice

For a PostNord parcel product from Sweden to a destination outside the EU VAT area other than Norway, the plugin SHALL return code `nordic_postnord_se_export_paper_invoice` at level `warning`, stating that a commercial invoice in English in triplicate must accompany the shipment in a plastic pocket on parcel no. 1, and that the digital data sent with the booking prevails over paper on discrepancy.
The copy count is the stricter of the conflicting sources: the PostNord SE English customs documents page states triplicate (FN:100, FN:142, W), the Swedish page states two copies (FN:142, FN:264, W), and the Service Point special terms §4 state "at least two copies" in a plastic pocket on parcel no. 1 with digital data prevailing (FN:118-119, W); the plastic-pocket wording comes only from the Service Point terms (FN:148, I).
International Parcel is covered by `nordic_postnord_se_postpaket_commercial_invoice`, and letter services are excluded because their invoice duty depends on the SEK 2 000 value threshold (FN:98, FN:105, FN:108, W), which this change defers.

#### Scenario: Parcel to Switzerland gets the paper invoice advisory

- **WHEN** a PostNord `postnord_mypack_home` shipment from Sweden to Switzerland is created
- **THEN** the plugin returns code `nordic_postnord_se_export_paper_invoice` at level `warning` stating triplicate and parcel no. 1, and its details list the English page, the Swedish page, and the Service Point terms with their copy counts

#### Scenario: Norway is excluded

- **WHEN** a PostNord `postnord_parcel` shipment from Sweden to Norway is created
- **THEN** the plugin does not return code `nordic_postnord_se_export_paper_invoice`

#### Scenario: International Parcel is excluded

- **WHEN** a PostNord `postnord_postpaket_utrikes` shipment from Sweden to Switzerland is created
- **THEN** the plugin does not return code `nordic_postnord_se_export_paper_invoice`

### Requirement: PostNord Sweden commercial Postpaket Utrikes carries a commercial invoice

For a commercial PostNord shipment from Sweden to a destination outside the EU VAT area booked as International Parcel (`postnord_postpaket_utrikes`, `91`, "Z91 Postpaket Utrikes" in the connector's vendored general descriptions, FN:165, S; marketed in Denmark as EMS), the plugin SHALL return code `nordic_postnord_se_postpaket_commercial_invoice` at level `warning`.
For destinations other than Norway the message SHALL state that the parcel needs the CN23 export declaration and a commercial invoice in three copies with the parcel.
Three copies is the stricter reading of conflicting sources and satisfies both at every value: the Postpaket Utrikes terms §2 require the CN23 in two copies and the commercial invoice in two copies when the value exceeds SEK 2 000 or the goods are sent for commercial purposes (FN:103, FN:111, W), while the EN and SV web pages require a commercial or proforma invoice in triplicate when the value exceeds SEK 2 000, on value only (FN:102, FN:107, FN:109, W); the plugin does not evaluate goods value, and two copies would fall short of the web pages above SEK 2 000.
`details` SHALL list both the terms and the web pages with the copy count and trigger each states.
For Norway the Norway-specific digital-only rule overrides the general copy count: the message SHALL state that the CN23 is required and that the invoice is sent digitally and not attached to the parcel, naming PostNord's Norway routes (the Booking API, PostNord Skicka Direkt Business, foravisering.export@postnord.com, and MyCustoms upload), and `details` SHALL cite the terms, the web pages, and the Norway rule (FN:142, FN:147, W).
The message SHALL state that the connector currently sends CN22 declaration data and no invoice for International Parcel (PNS lines 10 and 13-16, S), so the consumer must supply the CN23 and the invoice.
Non-commercial Postpaket Utrikes above SEK 2 000 is deferred with the other value thresholds, and letter services receive no such advisory because the letter rule depends on goods value only and the EN and SV pages conflict on CN22 versus CN23 above SEK 2 000 (FN:98, FN:105-110, W and I).
Sources: FN:101-103 and FN:105-112 (W, verbatim web page and terms rules), FN:165-167 (S and W, code 91 is the contract product).

#### Scenario: Commercial Postpaket Utrikes to the United States

- **WHEN** a PostNord `postnord_postpaket_utrikes` shipment from Sweden to the United States is created with customs data whose `commercial_invoice` is true
- **THEN** the plugin returns code `nordic_postnord_se_postpaket_commercial_invoice` at level `warning` stating the CN23, a commercial invoice in three copies, and that the connector sends CN22 data, and its details list the terms with two copies and the web pages with triplicate

#### Scenario: Sale-like content triggers the advisory

- **WHEN** a PostNord `postnord_postpaket_utrikes` shipment from Sweden to Switzerland is created with customs data whose `content_type` is `merchandise` and whose `commercial_invoice` is false
- **THEN** the plugin returns code `nordic_postnord_se_postpaket_commercial_invoice`

#### Scenario: Commercial Postpaket Utrikes to Norway sends the invoice digitally

- **WHEN** a PostNord `postnord_postpaket_utrikes` shipment from Sweden to Norway is created with customs data whose `commercial_invoice` is true
- **THEN** the plugin returns code `nordic_postnord_se_postpaket_commercial_invoice` stating the CN23 and the invoice sent digitally through the Booking API, Skicka Direkt Business, foravisering.export@postnord.com, or MyCustoms, without paper invoice copies, and its details cite the terms, the web pages, and the Norway rule

#### Scenario: Gift Postpaket Utrikes is not advised

- **WHEN** a PostNord `postnord_postpaket_utrikes` shipment from Sweden to Switzerland is created with customs data whose `content_type` is `gift` and whose `commercial_invoice` is false
- **THEN** the plugin does not return code `nordic_postnord_se_postpaket_commercial_invoice`

#### Scenario: Letters are not advised

- **WHEN** a commercial PostNord `postnord_export_letter` shipment from Sweden to Switzerland is created
- **THEN** the plugin does not return code `nordic_postnord_se_postpaket_commercial_invoice`

#### Scenario: Finnish Postpaket Utrikes is not advised

- **WHEN** a commercial PostNord `postnord_postpaket_utrikes` shipment from Finland to Switzerland is created
- **THEN** the plugin does not return code `nordic_postnord_se_postpaket_commercial_invoice`

### Requirement: PostNord Finland parcels outside the EU VAT area

For a PostNord parcel product from Finland to a destination outside the EU VAT area, the plugin SHALL return code `nordic_postnord_fi_export_invoice` at level `warning`, stating that a copy of the invoice can be emailed to tullaus.fi@postnord.com and, for destinations other than Norway, that a signed commercial invoice in English in triplicate must accompany the parcel, or, for Norway, that the invoice must reach PostNord electronically before the shipment.
The signed-triplicate statement is the stricter of the conflicting sources: the postnord.fi customs information page says the invoice "can be attached to the shipment or submitted separately" and signed "if necessary" (FN:143, FN:152, W), while the PostNord FI special terms for parcels valid 2026-05-01 require "a signed commercial invoice in English in triplicate" for non-EU parcels and electronic invoices to Norway (FN:143, FN:154, W); which governs is unresolved (FN:155, I; FN:267).
The Norway statement rests on the same page and terms (FN:153-154, W).

#### Scenario: Finnish parcel to Great Britain

- **WHEN** a PostNord `postnord_parcel` shipment from Finland to Great Britain is created
- **THEN** the plugin returns code `nordic_postnord_fi_export_invoice` at level `warning` naming tullaus.fi@postnord.com and a signed invoice in triplicate, and its details list both the web page and the 2026 special terms with their statements

#### Scenario: Finnish parcel to Norway

- **WHEN** a PostNord `postnord_parcel` shipment from Finland to Norway is created
- **THEN** the plugin returns code `nordic_postnord_fi_export_invoice` stating that the invoice must reach PostNord electronically before the shipment, without the triplicate statement

### Requirement: PostNord Denmark parcels outside the EU VAT area

For a PostNord parcel product from Denmark to a destination outside the EU VAT area, the plugin SHALL return code `nordic_postnord_dk_export_documents` at level `warning`, stating that the documents go in a plastic pocket visible on the parcel and the copy count for the destination: 2 invoices for Norway, 3 for Switzerland and Liechtenstein, 2 for Great Britain, and 1 CN23 with 2 invoices for any other destination, where the invoice is described by PostNord as not required but recommended (FN:144, W, postnord.dk/erhverv/eksport via Wayback 2026-03-10, FN:157).
The message SHALL also state, without evaluating any value threshold, that if an export declaration was lodged a copy goes to eksport@postnord.com (FN:144, W); the DKK 7 500 threshold at which PostNord requires the export declaration is deferred.

#### Scenario: Danish parcel to Liechtenstein

- **WHEN** a PostNord `postnord_parcel` shipment from Denmark to `LI` is created
- **THEN** the plugin returns code `nordic_postnord_dk_export_documents` at level `warning` stating 3 copies, a plastic pocket, and that a lodged export declaration is copied to eksport@postnord.com

#### Scenario: Danish parcel to the United States

- **WHEN** a PostNord `postnord_parcel` shipment from Denmark to `US` is created
- **THEN** the plugin returns code `nordic_postnord_dk_export_documents` stating 1 CN23 and 2 invoices, the invoice being recommended

### Requirement: DHL Freight Sweden needs a customs handling mode

For a DHL Freight Sweden shipment from Sweden to a destination outside the EU VAT area on which none of the connector's customs service options (standard handling, full-service handling, customer's own declaration, joint declaration) is set, the plugin SHALL return code `nordic_dhl_freight_sweden_customs_mode_missing` at level `warning`, stating that DHL requires customs handling (standard or full service) or an own declaration to be selected for such destinations and naming the connector options that select them.
The connector selects no customs service implicitly because each carries a fee (DFS lines 75-83, S); DHL's product manual requires the selection for Switzerland, Great Britain, Norway, Åland, and other non-EU destinations (FN:196, W, MAN §7.6.1 and §6.7), and no fee-free mode exists for non-EU destinations (FN:208, W and I), which the details SHALL state.

#### Scenario: No customs option to Norway

- **WHEN** a DHL Freight Sweden shipment from Sweden to Norway is created without any customs service option
- **THEN** the plugin returns code `nordic_dhl_freight_sweden_customs_mode_missing` at level `warning`

#### Scenario: Selected customs option silences the advisory

- **WHEN** a DHL Freight Sweden shipment from Sweden to Norway is created with the full-service customs handling option set
- **THEN** the plugin does not return code `nordic_dhl_freight_sweden_customs_mode_missing`

### Requirement: DHL Freight Sweden invoice copy is sent separately

For a DHL Freight Sweden shipment from Sweden to a destination outside the EU VAT area, the plugin SHALL return code `nordic_dhl_freight_sweden_invoice_copy` at level `warning`, stating that a copy of the invoice must be emailed to dhlfreight.int.se@dhl.com shortly after booking or uploaded in myDHL Freight, one document per shipment with a clear reference, even when complete customs data is sent with the booking, and that missing documents stop the shipment with a reminder fee of 390 kr, or 650 kr for Great Britain.
Sources: FN:213 (W, MAN §7.6.2, "A copy of the invoice must still be sent"), FN:214 (W, CIE p.9, email and upload routes), FN:216 (W, CIE p.12 and PRL, reminder fees), FN:179 (S, the DHL API has no attachment or upload endpoint).

#### Scenario: Invoice copy advisory to Great Britain states the higher fee

- **WHEN** a DHL Freight Sweden shipment from Sweden to Great Britain is created
- **THEN** the plugin returns code `nordic_dhl_freight_sweden_invoice_copy` at level `warning` naming dhlfreight.int.se@dhl.com, myDHL Freight, and a reminder fee of 650 kr

### Requirement: DHL Freight Sweden Parcel Connect documents are attached outside the package

For a DHL Freight Sweden Parcel Connect shipment (service `dhl_freight_sweden_parcel_connect_b2c`, DHL product 109) from Sweden to a destination outside the EU VAT area, the plugin SHALL return code `nordic_dhl_freight_sweden_attached_documents` at level `warning`, stating that two copies of the customs documents must be attached on the outside of the package.
The details SHALL state that the requirement is unconfirmed for Parcel Connect Plus (112) and road-freight products, which receive no such advisory.
Sources: FN:215 (W, MAN p.66, "Two copies of customs documents must also be attached on the outside of the package"), FN:268 (open question for 112 and road freight).

#### Scenario: Parcel Connect to Norway

- **WHEN** a DHL Freight Sweden `dhl_freight_sweden_parcel_connect_b2c` shipment from Sweden to Norway is created
- **THEN** the plugin returns code `nordic_dhl_freight_sweden_attached_documents` at level `warning`, and its details state that 112 and road freight are unconfirmed

#### Scenario: Parcel Connect Plus is not advised

- **WHEN** a DHL Freight Sweden `dhl_freight_sweden_parcel_connect_plus` shipment from Sweden to Norway is created
- **THEN** the plugin does not return code `nordic_dhl_freight_sweden_attached_documents`

### Requirement: DHL Freight Sweden VOEC ID is marked on the package

For a DHL Freight Sweden shipment from Sweden to Norway whose customs data carries `options.voec_number`, which the connector sends as DHL's VOEC supply VAT service (DFS lines 66-73, S), the plugin SHALL return code `nordic_dhl_freight_sweden_voec_marking` at level `warning`, stating that the VOEC ID must be printed on the package or the label.
Sources: FN:217 (W, MAN pp.97 and 99), FN:206 (W, VOEC with Parcel Connect to Norway).

#### Scenario: VOEC number to Norway

- **WHEN** a DHL Freight Sweden shipment from Sweden to Norway is created with customs data carrying a VOEC number
- **THEN** the plugin returns code `nordic_dhl_freight_sweden_voec_marking` at level `warning`

#### Scenario: No VOEC number

- **WHEN** a DHL Freight Sweden shipment from Sweden to Norway is created with customs data carrying no VOEC number
- **THEN** the plugin does not return code `nordic_dhl_freight_sweden_voec_marking`

### Requirement: The invoice type matches the content type

For an in-scope shipment whose booking carries an invoice type, meaning a PostNord parcel product or any DHL Freight Sweden service booked with customs data, the plugin SHALL return code `nordic_invoice_type_content_mismatch` at level `warning` when `customs.commercial_invoice` is false or omitted while the content is sale-like, and at level `info` when `customs.commercial_invoice` is true while `customs.content_type` is gift or sample.
The warning message SHALL state that the connector declares a proforma invoice from the flag, that a proforma invoice is for gifts and samples for which the recipient makes no payment, and that goods sold need `commercial_invoice` set to true; the info message SHALL state that a commercial invoice is declared for content described as a gift or sample, for which a proforma invoice is the usual document.
The levels differ because the sources restrict the proforma invoice to goods not sold but do not forbid a commercial invoice for gifts or samples.
Sources: PNS lines 155-168 and DFS lines 51-64 (S, the connectors apply the flag literally and leave mismatch detection to advisory tooling), FN:56 (W, Bring tulldokument and DHL CIE p.5, a proforma invoice is used for goods not sold), FN:111 and FN:113 (W, Postpaket Utrikes terms §2, "Proformafaktura … får endast användas vid gåva eller varuprov"), FN:30-36 (S, connector mapping of the flag).

#### Scenario: Merchandise declared as proforma

- **WHEN** a DHL Freight Sweden shipment from Sweden to Norway is created with customs data whose `content_type` is `merchandise` and whose `commercial_invoice` is omitted
- **THEN** the plugin returns code `nordic_invoice_type_content_mismatch` at level `warning`

#### Scenario: Omitted content type declared as proforma

- **WHEN** a PostNord `postnord_parcel` shipment from Sweden to Norway is created with customs data carrying no `content_type` and `commercial_invoice` false
- **THEN** the plugin returns code `nordic_invoice_type_content_mismatch` at level `warning`

#### Scenario: Gift declared as proforma is consistent

- **WHEN** a PostNord `postnord_parcel` shipment from Sweden to Norway is created with customs data whose `content_type` is `gift` and whose `commercial_invoice` is false
- **THEN** the plugin does not return code `nordic_invoice_type_content_mismatch`

#### Scenario: Return merchandise declared as proforma is consistent

- **WHEN** a DHL Freight Sweden shipment from Sweden to Norway is created with customs data whose `content_type` is `return_merchandise` and whose `commercial_invoice` is false
- **THEN** the plugin does not return code `nordic_invoice_type_content_mismatch`

#### Scenario: Sample declared as commercial is informational

- **WHEN** a DHL Freight Sweden shipment from Sweden to Switzerland is created with customs data whose `content_type` is `sample` and whose `commercial_invoice` is true
- **THEN** the plugin returns code `nordic_invoice_type_content_mismatch` at level `info`

#### Scenario: Letters carry no invoice type

- **WHEN** a PostNord `postnord_export_letter` shipment from Sweden to Norway is created with customs data whose `content_type` is `merchandise` and whose `commercial_invoice` is false
- **THEN** the plugin does not return code `nordic_invoice_type_content_mismatch`, because the connector sends a CN22 without an invoice type for letters
