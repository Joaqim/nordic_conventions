# plugins/advisor-nordic-conventions Specification

## Purpose
Defines the Nordic conventions plugin, an advisor-only karrio plugin that adds non-blocking trade-document advisories to PostNord and DHL Freight Sweden shipment responses for Swedish, Danish, and Finnish shippers sending goods outside the EU VAT area, each advisory citing the carrier or authority source it rests on.

Source references in this spec use FN for the karrio fork's `docs/notes/customs/nordic-trade-documents-facts.md` (branch `docs-openspec`, commit baf8eb3dd) with line numbers, and keep the note's evidence tags: S is repository code or vendored specification, W is public carrier or authority documentation, and I is inference.
Connector behaviour cited as S refers to the karrio fork's main specs `openspec/specs/postnord/customs-declaration/spec.md` (PNS) and `openspec/specs/dhl-freight-sweden/customs/spec.md` (DFS), both on branch `docs-openspec` at commit 60312fe2e.
The parcel customs invoice PNS specifies entered the PostNord connector on the fork branch `feat-postnord-customs-invoice` (tip face88f37), merged into the fork's develop by 52d21fbfb.
PostNord parcel products are the PostNord services that are neither letter services nor International Parcel (`postnord_postpaket_utrikes`), as defined by PNS lines 10-11.
PostNord letter services are `postnord_tracked` (`04`), `postnord_tracked_letter` (`34`), `postnord_export_letter` (`UX`), `postnord_varubrev_first_class` (`86`), `postnord_expressbrev` (`LX`), `postnord_rek` (`RR`), `postnord_rek_retur` (`RK`), `postnord_rek_extra` (`RL`), `postnord_rekommanderet_brev` (`RE`), `postnord_rekommanderet_quickbrev` (`RQ`), `postnord_varde` (`VV`), and `postnord_afleveringsattest` (`AF`), the letter set of the PostNord connector (karrio `develop` at 7a56ffa5b, `modules/connectors/postnord/karrio/providers/postnord/units.py:269-284`, S).
Norway-named letter services are the letter services named in the letters table of the PostNord SE Swedish customs documents page (Brev utrikes, PostNord Untracked letter, Spårbart brev utrikes, Rek utrikes; W, Wayback 2026-02-08, FN:108) that map to a connector code with clear evidence: `postnord_export_letter` (`UX`, connector label "Export Letter Sweden", live-verified as an SE export letter in the karrio fork's `docs/notes/postnord/customs-declaration-live-verification.md:5`, S) and `postnord_rek` (`RR`, connector label "registered mail", S).
Spårbart brev utrikes (tracked) has no connector code identified with clear evidence and Varubrev is not named in that table, so neither is a Norway-named letter service.

## Requirements

### Requirement: The plugin is an advisor-only plugin

The plugin SHALL register through the `karrio.plugins` entry point group under the id `advisor_nordic_conventions`, SHALL declare shipment advisors and no carrier mapper, proxy, settings, or address validator, and SHALL be reported by karrio with the plugin type `advisor`.

#### Scenario: Installed plugin is collected as an advisor

- **WHEN** the plugin is installed alongside a karrio SDK that provides the shipment advisors hook
- **THEN** karrio lists a plugin `advisor_nordic_conventions` of type `advisor` and collects its advisors

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

### Requirement: The EU VAT area follows Tullverket for goods

The plugin SHALL decide EU VAT area membership from its own territory table, independent of karrio's `EUCountry`, which lists Greece as `EL` and lacks `AX` and `XI` (FN:235, FN:276, S).
The table SHALL match Tullverket's list of EU customs and fiscal territories as it applies to goods movements (FN:58-65, W): the EU member states with Greece as `GR` are inside; Monaco is inside (FN:64, W); Northern Ireland is inside, identified as `GB` with a postal code beginning `BT` (FN:64, W); and Åland (`AX`, or `FI` 22000-22999), the Canary Islands (`IC`, or `ES` 35000-35999 and 38000-38999), Ceuta (`ES` 51000-51999), Melilla (`ES` 52000-52999), Büsingen (`DE` 78266), Heligoland (`DE` 27498), Livigno (`IT` 23041), Campione d'Italia (`IT` 22061), the French overseas departments (`GP`, `GF`, `MQ`, `RE`, `YT`, or `FR` 97000-97999), Wallis and Futuna, French Polynesia, and New Caledonia addressed under `FR` (`FR` 98600-98899), the Faroe Islands and Greenland addressed under `DK` (`DK` 3800-3999), and Mount Athos (`GR` or `EL` 63086) are outside.
The `DK` range is the one DHL Freight Sweden's product manual v5.26 gives for "Greenland & The Faroe Islands" (W, MAN v5.26 §5.3 p.18, §5.14 p.63, §5.15 p.66); the two `FR` ranges are the operator's, inside the manual's delivery exclusion 97100-99999, which also covers Monaco's 98000 and is therefore not adopted.
Great Britain other than Northern Ireland is outside (FN:65, W).
Northern Ireland's inside verdict is the goods-movement verdict: Northern Ireland is inside the EU VAT area for goods and outside it for services, and the plugin decides customs-document advice for goods shipments, so the territory table carries no services verdict.
Monaco's French-style postal codes 98000-98099 keep their inside verdict through the `FR` country code, so only the `MC` country code changes verdict.
A postal code SHALL be upper-cased and trimmed, SHALL lose a leading prefix code together with the hyphen and whitespace after it, and SHALL then be compared after removing spaces.
A prefix code is the address's own country code, or a territory code with numeric postcodes whose parent is that country (`AX` under `FI`, `FO` and `GL` under `DK`, `IC` and `EA` under `ES`), followed by a hyphen, whitespace, or a digit; `GB` is a prefix code only when a hyphen or whitespace follows it, and `JE`, `GY`, `IM`, and `BT` are never prefix codes.
The DHL Freight Sweden connector applies the same normalisation.
Under `DK`, an address SHALL be outside when the prefix code removed from its postal code is `FO` or `GL`, whatever number follows, or when its normalised postal code is exactly three digits, the Faroese format, because the Faroe Islands and Greenland are outside the EU VAT area (FN:63, W); a four-digit `DK` postal code outside 3800-3999 stays inside.
A postal code that is not purely numeric after this normalisation SHALL leave the country-level decision unchanged, except that the Northern Ireland prefix comparison SHALL apply to a normalised postal code beginning `BT` whether or not it is purely numeric.

#### Scenario: Åland by postal code is outside

- **WHEN** a PostNord shipment is created from Sweden to `FI` with postal code 22100
- **THEN** the recipient is treated as outside the EU VAT area and the Swedish PostNord advisories for destinations outside the EU VAT area apply

#### Scenario: Åland by country-prefixed postal code is outside

- **WHEN** a DHL Freight Sweden shipment is created from Sweden to `FI` with postal code `FI-22100`, `fi 22100`, `FI22100`, or `FI 22 100`
- **THEN** the recipient is treated as outside the EU VAT area

#### Scenario: Åland by territory-prefixed postal code is outside

- **WHEN** a PostNord shipment is created from Sweden to `FI` with postal code `AX-22100`
- **THEN** the recipient is treated as outside the EU VAT area, because `AX` is a territory code whose parent is `FI`

#### Scenario: Letters that begin a postal code are kept

- **WHEN** a PostNord shipment is created from Sweden to `MT` with postal code `MTF 1234`
- **THEN** the recipient is treated as inside the EU VAT area

#### Scenario: Greece is inside

- **WHEN** a DHL Freight Sweden shipment is created from Sweden to `GR`
- **THEN** the plugin returns no message

#### Scenario: Canary Islands by postal code are outside

- **WHEN** a DHL Freight Sweden shipment is created from Sweden to `ES` with postal code 35 001
- **THEN** the recipient is treated as outside the EU VAT area

#### Scenario: French overseas department by postal code is outside

- **WHEN** a DHL Freight Sweden shipment is created from Sweden to `FR` with postal code 97400
- **THEN** the recipient is treated as outside the EU VAT area

#### Scenario: French Pacific collectivity by postal code is outside

- **WHEN** a DHL Freight Sweden shipment is created from Sweden to `FR` with postal code 98713
- **THEN** the recipient is treated as outside the EU VAT area

#### Scenario: Faroe Islands and Greenland by Danish postal code are outside

- **WHEN** a PostNord shipment is created from Sweden to `DK` with postal code `DK 3800` or `DK-3900`
- **THEN** the recipient is treated as outside the EU VAT area and the Swedish PostNord advisories for destinations outside the EU VAT area apply

#### Scenario: Faroe Islands and Greenland by territory-prefixed Danish postal code are outside

- **WHEN** a PostNord shipment is created from Sweden to `DK` with postal code `FO-100`, `fo 100`, `FO100`, or `GL 3900`
- **THEN** the recipient is treated as outside the EU VAT area

#### Scenario: Faroese three-digit postal code under Denmark is outside

- **WHEN** a DHL Freight Sweden shipment is created from Sweden to `DK` with postal code 100 or `DK-100`
- **THEN** the recipient is treated as outside the EU VAT area

#### Scenario: Danish four-digit postal code outside the Faroe and Greenland range is inside

- **WHEN** a PostNord shipment is created from Sweden to `DK` with postal code 1000 or `DK-2100`
- **THEN** the recipient is treated as inside the EU VAT area

#### Scenario: Mount Athos by postal code is outside

- **WHEN** a PostNord shipment is created from Sweden to `GR` or `EL` with postal code 630 86
- **THEN** the recipient is treated as outside the EU VAT area and the Swedish PostNord advisories for destinations outside the EU VAT area apply

#### Scenario: Monaco by country code is inside

- **WHEN** a DHL Freight Sweden shipment is created from Sweden to `MC` with postal code 98000
- **THEN** the plugin returns no message

#### Scenario: Monaco by French postal code is inside

- **WHEN** a PostNord shipment is created from Sweden to `FR` with postal code 98000
- **THEN** the plugin returns no message

#### Scenario: Northern Ireland is inside for goods

- **WHEN** a PostNord shipment is created from Sweden to `GB` with postal code BT1 1AA or `GB-BT1 1AA`
- **THEN** the plugin returns no message

#### Scenario: Channel Islands and Isle of Man postcodes are not prefixes

- **WHEN** a PostNord shipment is created from Sweden to `GB` with postal code JE2 3AB, GY1 1AA, or IM1 1AA
- **THEN** the recipient is treated as outside the EU VAT area

#### Scenario: Great Britain outside Northern Ireland is outside

- **WHEN** a PostNord shipment is created from Sweden to `GB` with postal code EC1A 1BB
- **THEN** the recipient is treated as outside the EU VAT area and the Swedish PostNord advisories for destinations outside the EU VAT area apply

### Requirement: Advisories are non-blocking, coded, and attributed

Every message the plugin returns SHALL have level `warning` or `info`, a code from this specification that starts with `advisor_nordic_conventions_` and does not contain `SHIPPING_SDK_`, a message text in English, and `details` holding a `sources` list in which each entry names its evidence tag (`S`, `W`, or `I`) and its reference.
Where the cited sources disagree, the message text SHALL state the stricter requirement and `details` SHALL list every disagreeing source with the statement each makes.
Message texts SHALL name electronic and carrier-native, no-cost routes before paper where the sources allow them.
Several advisories MAY apply to one shipment, and the plugin SHALL return each applicable advisory once.

#### Scenario: Conflicting sources are both attributed

- **WHEN** an advisory whose sources state different invoice copy counts is returned
- **THEN** its message states the larger count and its details list each source with the count that source states

#### Scenario: Several advisories on one shipment

- **WHEN** a DHL Freight Sweden Parcel Connect (`109`) shipment from Sweden to Norway is created without customs data and without a customs handling option
- **THEN** the response carries exactly one message each with codes `advisor_nordic_conventions_dhl_freight_sweden_customs_mode_missing`, `advisor_nordic_conventions_dhl_freight_sweden_invoice_copy`, and `advisor_nordic_conventions_dhl_freight_sweden_attached_documents`

### Requirement: Advisory codes carry the plugin namespace

Every advisory code value SHALL be the plugin identity `advisor_nordic_conventions_`, matching the `karrio.plugins` entry-point id, the package name, and the plugin's `PLUGIN_ID`, followed by the scope segment and the topic segment, all lower_snake_case.
The prefix SHALL remain fixed at `advisor_nordic_conventions_`, and the codes are consumer-facing API surface, so renaming one is a breaking change.

#### Scenario: Every code starts with the plugin identity

- **WHEN** any advisory is returned
- **THEN** its code starts with `advisor_nordic_conventions_` followed by lower_snake_case scope and topic segments

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

For a PostNord shipment from Sweden to Norway to which `advisor_nordic_conventions_postnord_se_postpaket_commercial_invoice` does not apply, the plugin SHALL return code `advisor_nordic_conventions_postnord_se_no_digital_invoice`, stating that PostNord requires the commercial invoice for Norway digitally rather than on paper with the parcel, and naming the routes: the booking itself (the connector transmits a customs invoice for parcel products booked with customs data, PNS lines 28-31, S), PostNord Skicka Direkt Business, the email address foravisering.export@postnord.com, and upload in PostNord MyCustoms.
For a Norway-named letter service the message SHALL also state that a commercial invoice and a VOEC number are required for letters to Norway from SEK 0, the invoice sent digitally through the same routes (FN:99, FN:108, W, SV page only); other letter services receive this advisory without that statement.
When `advisor_nordic_conventions_postnord_se_postpaket_commercial_invoice` applies to a shipment, it carries the Norway invoice routes itself and this advisory SHALL NOT be returned, so each shipment receives the invoice routes once.
The level SHALL be `info` when the booking is a parcel product carrying customs data, because the connector already transmits the invoice data, and `warning` otherwise, because the invoice then reaches PostNord only through a route the consumer owns.
Sources: FN:118 (W, Service Point special terms §4, "To Norway the commercial invoice and shipment list shall be sent digitally"), FN:142 and FN:147 (W, PostNord SE customs documents pages, Norway channels and MyCustoms), FN:149 (W, the separate channels are stated for Norway only), FN:108 (W, SV page, "Vid export till Norge behöver Handelsfaktura och VOEC* anges från 0 kr.").

#### Scenario: Parcel booking with customs data is informational

- **WHEN** a PostNord `postnord_parcel` shipment from Sweden to Norway is created with customs data
- **THEN** the plugin returns code `advisor_nordic_conventions_postnord_se_no_digital_invoice` at level `info`, naming Skicka Direkt Business, foravisering.export@postnord.com, and MyCustoms

#### Scenario: Letter to Norway states invoice and VOEC from SEK 0

- **WHEN** a PostNord `postnord_export_letter` shipment from Sweden to Norway is created with customs data whose `content_type` is `merchandise`
- **THEN** the plugin returns code `advisor_nordic_conventions_postnord_se_no_digital_invoice` at level `warning`, stating that a commercial invoice and a VOEC number are required from SEK 0 and that the invoice is sent digitally, and citing the SV page

#### Scenario: Letter not named by the Swedish page omits the SEK 0 statement

- **WHEN** a PostNord `postnord_varubrev_first_class` shipment from Sweden to Norway is created with customs data whose `content_type` is `merchandise`
- **THEN** the plugin returns code `advisor_nordic_conventions_postnord_se_no_digital_invoice` at level `warning` naming the Norway invoice routes, without the commercial invoice and VOEC from SEK 0 statement

#### Scenario: Commercial Postpaket Utrikes to Norway receives the invoice routes once

- **WHEN** a PostNord `postnord_postpaket_utrikes` shipment from Sweden to Norway is created with customs data whose `commercial_invoice` is true
- **THEN** the plugin returns code `advisor_nordic_conventions_postnord_se_postpaket_commercial_invoice` naming the Norway invoice routes and does not return code `advisor_nordic_conventions_postnord_se_no_digital_invoice`

#### Scenario: Non-commercial Postpaket Utrikes to Norway is a warning

- **WHEN** a PostNord `postnord_postpaket_utrikes` shipment from Sweden to Norway is created with customs data whose `content_type` is `gift` and whose `commercial_invoice` is false
- **THEN** the plugin returns code `advisor_nordic_conventions_postnord_se_no_digital_invoice` at level `warning` and not code `advisor_nordic_conventions_postnord_se_postpaket_commercial_invoice`

### Requirement: PostNord Sweden parcels outside the EU VAT area carry a paper invoice

For a PostNord parcel product from Sweden to a destination outside the EU VAT area other than Norway, the plugin SHALL return code `advisor_nordic_conventions_postnord_se_export_paper_invoice` at level `warning`, stating that a commercial invoice in English in triplicate must accompany the shipment in a plastic pocket on parcel no. 1, and that the digital data sent with the booking prevails over paper on discrepancy.
The copy count is the stricter of the conflicting sources: the PostNord SE English customs documents page states triplicate (FN:100, FN:142, W), the Swedish page states two copies (FN:142, FN:264, W), and the Service Point special terms §4 state "at least two copies" in a plastic pocket on parcel no. 1 with digital data prevailing (FN:118-119, W); the plastic-pocket wording comes only from the Service Point terms (FN:148, I).
International Parcel is covered by `advisor_nordic_conventions_postnord_se_postpaket_commercial_invoice`, and letter services are excluded because their invoice duty depends on the SEK 2 000 value threshold (FN:98, FN:105, FN:108, W), which this change defers.

#### Scenario: Parcel to Switzerland gets the paper invoice advisory

- **WHEN** a PostNord `postnord_mypack_home` shipment from Sweden to Switzerland is created
- **THEN** the plugin returns code `advisor_nordic_conventions_postnord_se_export_paper_invoice` at level `warning` stating triplicate and parcel no. 1, and its details list the English page, the Swedish page, and the Service Point terms with their copy counts

#### Scenario: Norway is excluded

- **WHEN** a PostNord `postnord_parcel` shipment from Sweden to Norway is created
- **THEN** the plugin does not return code `advisor_nordic_conventions_postnord_se_export_paper_invoice`

#### Scenario: International Parcel is excluded

- **WHEN** a PostNord `postnord_postpaket_utrikes` shipment from Sweden to Switzerland is created
- **THEN** the plugin does not return code `advisor_nordic_conventions_postnord_se_export_paper_invoice`

### Requirement: PostNord Sweden commercial Postpaket Utrikes carries a commercial invoice

For a commercial PostNord shipment from Sweden to a destination outside the EU VAT area booked as International Parcel (`postnord_postpaket_utrikes`, `91`, "Z91 Postpaket Utrikes" in the connector's vendored general descriptions, FN:165, S; marketed in Denmark as EMS), the plugin SHALL return code `advisor_nordic_conventions_postnord_se_postpaket_commercial_invoice` at level `warning`.
For destinations other than Norway the message SHALL state that the parcel needs the CN23 export declaration and a commercial invoice in three copies with the parcel.
Three copies is the stricter reading of conflicting sources and satisfies both at every value: the Postpaket Utrikes terms §2 require the CN23 in two copies and the commercial invoice in two copies when the value exceeds SEK 2 000 or the goods are sent for commercial purposes (FN:103, FN:111, W), while the EN and SV web pages require a commercial or proforma invoice in triplicate when the value exceeds SEK 2 000, on value only (FN:102, FN:107, FN:109, W); the plugin does not evaluate goods value, and two copies would fall short of the web pages above SEK 2 000.
`details` SHALL list both the terms and the web pages with the copy count and trigger each states.
For Norway the Norway-specific digital-only rule overrides the general copy count: the message SHALL state that the CN23 is required and that the invoice is sent digitally and not attached to the parcel, naming PostNord's Norway routes (the Booking API, PostNord Skicka Direkt Business, foravisering.export@postnord.com, and MyCustoms upload), and `details` SHALL cite the terms, the web pages, and the Norway rule (FN:142, FN:147, W).
The message SHALL state that the connector currently sends CN22 declaration data and no invoice for International Parcel (PNS lines 10 and 13-16, S), so the consumer must supply the CN23 and the invoice.
Non-commercial Postpaket Utrikes above SEK 2 000 is deferred with the other value thresholds, and letter services receive no such advisory because the letter rule depends on goods value only and the EN and SV pages conflict on CN22 versus CN23 above SEK 2 000 (FN:98, FN:105-110, W and I).
Recorded gap, not addressed: PostNord requires the CN23 for International Parcel at every value, including non-commercial content such as gifts, samples, documents, and returned goods (FN:101, FN:111, W), while the connector sends CN22 declaration data for it (PNS lines 10 and 13-16, S).
For non-commercial International Parcel the plugin returns no advisory for destinations other than Norway, and for Norway returns only `advisor_nordic_conventions_postnord_se_no_digital_invoice`, whose message does not mention the CN23.
Sources: FN:101-103 and FN:105-112 (W, verbatim web page and terms rules), FN:165-167 (S and W, code 91 is the contract product).

#### Scenario: Commercial Postpaket Utrikes to the United States

- **WHEN** a PostNord `postnord_postpaket_utrikes` shipment from Sweden to the United States is created with customs data whose `commercial_invoice` is true
- **THEN** the plugin returns code `advisor_nordic_conventions_postnord_se_postpaket_commercial_invoice` at level `warning` stating the CN23, a commercial invoice in three copies, and that the connector sends CN22 data, and its details list the terms with two copies and the web pages with triplicate

#### Scenario: Sale-like content triggers the advisory

- **WHEN** a PostNord `postnord_postpaket_utrikes` shipment from Sweden to Switzerland is created with customs data whose `content_type` is `merchandise` and whose `commercial_invoice` is false
- **THEN** the plugin returns code `advisor_nordic_conventions_postnord_se_postpaket_commercial_invoice`

#### Scenario: Commercial Postpaket Utrikes to Norway sends the invoice digitally

- **WHEN** a PostNord `postnord_postpaket_utrikes` shipment from Sweden to Norway is created with customs data whose `commercial_invoice` is true
- **THEN** the plugin returns code `advisor_nordic_conventions_postnord_se_postpaket_commercial_invoice` stating the CN23 and the invoice sent digitally through the Booking API, Skicka Direkt Business, foravisering.export@postnord.com, or MyCustoms, without paper invoice copies, and its details cite the terms, the web pages, and the Norway rule

#### Scenario: Gift Postpaket Utrikes is not advised

- **WHEN** a PostNord `postnord_postpaket_utrikes` shipment from Sweden to Switzerland is created with customs data whose `content_type` is `gift` and whose `commercial_invoice` is false
- **THEN** the plugin does not return code `advisor_nordic_conventions_postnord_se_postpaket_commercial_invoice`, although PostNord requires the CN23 for this shipment at every value (FN:101, FN:111, W), a recorded gap the plugin does not advise

#### Scenario: Letters are not advised

- **WHEN** a commercial PostNord `postnord_export_letter` shipment from Sweden to Switzerland is created
- **THEN** the plugin does not return code `advisor_nordic_conventions_postnord_se_postpaket_commercial_invoice`

#### Scenario: Finnish Postpaket Utrikes is not advised

- **WHEN** a commercial PostNord `postnord_postpaket_utrikes` shipment from Finland to Switzerland is created
- **THEN** the plugin does not return code `advisor_nordic_conventions_postnord_se_postpaket_commercial_invoice`

### Requirement: PostNord Finland parcels outside the EU VAT area

For a PostNord parcel product from Finland to a destination outside the EU VAT area, the plugin SHALL return code `advisor_nordic_conventions_postnord_fi_export_invoice` at level `warning`, stating that a copy of the invoice can be emailed to tullaus.fi@postnord.com and, for destinations other than Norway, that a signed commercial invoice in English in triplicate must accompany the parcel, or, for Norway, that the invoice must reach PostNord electronically before the shipment.
The signed-triplicate statement is the stricter of the conflicting sources: the postnord.fi customs information page says the invoice "can be attached to the shipment or submitted separately" and signed "if necessary" (FN:143, FN:152, W), while the PostNord FI special terms for parcels valid 2026-05-01 require "a signed commercial invoice in English in triplicate" for non-EU parcels and electronic invoices to Norway (FN:143, FN:154, W); which governs is unresolved (FN:155, I; FN:267).
The Norway statement rests on the same page and terms (FN:153-154, W).
Recorded gap, not addressed: this advisory is limited to PostNord parcel products, so International Parcel and letter services from Finland to destinations outside the EU VAT area receive no advisory, and this specification records no PostNord Finland requirement for those services.

#### Scenario: Finnish parcel to Great Britain

- **WHEN** a PostNord `postnord_parcel` shipment from Finland to Great Britain is created
- **THEN** the plugin returns code `advisor_nordic_conventions_postnord_fi_export_invoice` at level `warning` naming tullaus.fi@postnord.com and a signed invoice in triplicate, and its details list both the web page and the 2026 special terms with their statements

#### Scenario: Finnish parcel to Norway

- **WHEN** a PostNord `postnord_parcel` shipment from Finland to Norway is created
- **THEN** the plugin returns code `advisor_nordic_conventions_postnord_fi_export_invoice` stating that the invoice must reach PostNord electronically before the shipment, without the triplicate statement

### Requirement: PostNord Denmark parcels outside the EU VAT area

For a PostNord parcel product from Denmark to a destination outside the EU VAT area, the plugin SHALL return code `advisor_nordic_conventions_postnord_dk_export_documents` at level `warning`, stating that the documents go in a plastic pocket visible on the parcel and the copy count for the destination: 2 invoices for Norway, 3 for Switzerland and Liechtenstein, 2 for Great Britain, and 1 CN23 with 2 invoices for any other destination, where the invoice is described by PostNord as not required but recommended (FN:144, W, postnord.dk/erhverv/eksport via Wayback 2026-03-10, FN:157).
The message SHALL also state, without evaluating any value threshold, that if an export declaration was lodged a copy goes to eksport@postnord.com (FN:144, W); the DKK 7 500 threshold at which PostNord requires the export declaration is deferred.
Recorded gap, not addressed: this advisory is limited to PostNord parcel products, so International Parcel and letter services from Denmark to destinations outside the EU VAT area receive no advisory, and this specification records no PostNord Denmark requirement for those services.

#### Scenario: Danish parcel to Liechtenstein

- **WHEN** a PostNord `postnord_parcel` shipment from Denmark to `LI` is created
- **THEN** the plugin returns code `advisor_nordic_conventions_postnord_dk_export_documents` at level `warning` stating 3 copies, a plastic pocket, and that a lodged export declaration is copied to eksport@postnord.com

#### Scenario: Danish parcel to the United States

- **WHEN** a PostNord `postnord_parcel` shipment from Denmark to `US` is created
- **THEN** the plugin returns code `advisor_nordic_conventions_postnord_dk_export_documents` stating 1 CN23 and 2 invoices, the invoice being recommended

### Requirement: DHL Freight Sweden needs a customs handling mode

For a DHL Freight Sweden shipment from Sweden to a destination outside the EU VAT area on which none of the connector's customs service options (standard handling, full-service handling, customer's own declaration, joint declaration) is set, the plugin SHALL return code `advisor_nordic_conventions_dhl_freight_sweden_customs_mode_missing` at level `warning`, stating that DHL requires customs handling (standard or full service), an own declaration, or a joint declaration to Norway or Switzerland to be selected for such destinations and naming the connector options that select them.
The joint declaration's destinations SHALL be the connector's `JOINT_DECLARATION_COUNTRIES`, Norway and Switzerland, outside which the connector refuses the joint declaration across the EU VAT area border (karrio-dhl-freight-sweden f86c8ac), copied into the plugin and checked against the connector by a test that runs when the connector is importable; the manual names Norway only (W, MAN v5.26 §6.8 p.98; S, connector README at 7a2214d, citing product matches to NO and CH).
The connector selects no customs service implicitly because each carries a fee (DFS lines 75-83, S); DHL's product manual requires the selection for Switzerland, Great Britain, Norway, Åland, and other non-EU destinations (FN:196, W, MAN v5.26 §7.6.1 p.163 and §6.7 p.96), and no fee-free mode exists for non-EU destinations (FN:208, W and I), which the details SHALL state.
For a recipient in Åland, as "DHL Freight Sweden customs handling is not selected to Åland" defines it, the plugin SHALL NOT return this code, because the connector accepts an Åland booking without a customs service, and DHL booked 109 to FI 22100 with customs data and no customs service (S, connector `docs/concepts/destinations.md` "Åland" at 7a2214d).

#### Scenario: No customs option to Norway

- **WHEN** a DHL Freight Sweden shipment from Sweden to Norway is created without any customs service option
- **THEN** the plugin returns code `advisor_nordic_conventions_dhl_freight_sweden_customs_mode_missing` at level `warning`, naming the joint declaration to Norway or Switzerland and its option `dhl_freight_sweden_customs_joint_declaration`

#### Scenario: Selected customs option silences the advisory

- **WHEN** a DHL Freight Sweden shipment from Sweden to Norway is created with the full-service customs handling option set
- **THEN** the plugin does not return code `advisor_nordic_conventions_dhl_freight_sweden_customs_mode_missing`

#### Scenario: No customs option to Åland

- **WHEN** a DHL Freight Sweden shipment from Sweden to `FI` with postal code 22100, or to `AX` with postal code AX-22100, is created with customs data and without any customs service option
- **THEN** the plugin returns no customs-mode or Åland customs service code

### Requirement: DHL Freight Sweden invoice copy is sent separately

For a DHL Freight Sweden shipment from Sweden to a destination outside the EU VAT area, the plugin SHALL return code `advisor_nordic_conventions_dhl_freight_sweden_invoice_copy` at level `warning`, stating that a copy of the invoice must be emailed to dhlfreight.int.se@dhl.com shortly after booking or uploaded in myDHL Freight, one document per shipment with a clear reference, even when complete customs data is sent with the booking, and that missing documents stop the shipment with a reminder fee of 390 kr, or 650 kr for Great Britain.
Sources: FN:213 (W, MAN v5.26 §7.6.2 p.163, "A copy of the invoice must still be sent"), FN:214 (W, CIE p.9, email and upload routes), FN:216 (W, CIE p.12 and PRL, reminder fees), FN:179 (S, the DHL API has no attachment or upload endpoint).

#### Scenario: Invoice copy advisory to Great Britain states the higher fee

- **WHEN** a DHL Freight Sweden shipment from Sweden to Great Britain is created
- **THEN** the plugin returns code `advisor_nordic_conventions_dhl_freight_sweden_invoice_copy` at level `warning` naming dhlfreight.int.se@dhl.com, myDHL Freight, and a reminder fee of 650 kr

### Requirement: DHL Freight Sweden Parcel Connect documents are attached outside the package

For a DHL Freight Sweden Parcel Connect shipment (service `dhl_freight_sweden_parcel_connect_b2c`, DHL product 109) from Sweden to a destination outside the EU VAT area, the plugin SHALL return code `advisor_nordic_conventions_dhl_freight_sweden_attached_documents` at level `warning`, stating that two copies of the customs documents must be attached on the outside of the package.
The details SHALL state that the requirement is unconfirmed for Parcel Connect Plus (112) and road-freight products, which receive no such advisory.
Sources: FN:215 (W, MAN v5.26 §5.14 p.62, "Two copies of customs documents must also be attached on the outside of the package"), FN:268 (open question for 112 and road freight; MAN v5.26 §5.3 p.18 asks for 112 only that documents are sent by e-mail).

#### Scenario: Parcel Connect to Norway

- **WHEN** a DHL Freight Sweden `dhl_freight_sweden_parcel_connect_b2c` shipment from Sweden to Norway is created
- **THEN** the plugin returns code `advisor_nordic_conventions_dhl_freight_sweden_attached_documents` at level `warning`, and its details state that 112 and road freight are unconfirmed

#### Scenario: Parcel Connect Plus is not advised

- **WHEN** a DHL Freight Sweden `dhl_freight_sweden_parcel_connect_plus` shipment from Sweden to Norway is created
- **THEN** the plugin does not return code `advisor_nordic_conventions_dhl_freight_sweden_attached_documents`

### Requirement: DHL Freight Sweden VOEC ID is marked on the package

For a DHL Freight Sweden shipment from Sweden to Norway whose customs data carries `options.voec_number`, which the connector sends as DHL's VOEC supply VAT service (DFS lines 66-73, S), the plugin SHALL return code `advisor_nordic_conventions_dhl_freight_sweden_voec_marking` at level `warning`, stating that the VOEC ID must be printed on the package or the label.
Sources: FN:217 (W, MAN v5.26 §6.5 p.92, §6.6 p.94, and §9.4.2 p.168), FN:206 (W, VOEC with Parcel Connect to Norway, sent in the API as `additionalServices.voecSupplyVAT.vatId` per MAN v5.26 §6.5 p.92 and §6.6 p.94).

#### Scenario: VOEC number to Norway

- **WHEN** a DHL Freight Sweden shipment from Sweden to Norway is created with customs data carrying a VOEC number
- **THEN** the plugin returns code `advisor_nordic_conventions_dhl_freight_sweden_voec_marking` at level `warning`

#### Scenario: No VOEC number

- **WHEN** a DHL Freight Sweden shipment from Sweden to Norway is created with customs data carrying no VOEC number
- **THEN** the plugin does not return code `advisor_nordic_conventions_dhl_freight_sweden_voec_marking`

### Requirement: The invoice type matches the content type

For an in-scope shipment whose booking carries an invoice type, meaning a PostNord parcel product or any DHL Freight Sweden service booked with customs data, the plugin SHALL return code `advisor_nordic_conventions_invoice_type_content_mismatch` at level `warning` when `customs.commercial_invoice` is false or omitted while the content is sale-like, and at level `info` when `customs.commercial_invoice` is true while `customs.content_type` is gift or sample.
The warning message SHALL state that the connector declares a proforma invoice from the flag, that a proforma invoice is for gifts and samples for which the recipient makes no payment, and that goods sold need `commercial_invoice` set to true; the info message SHALL state that a commercial invoice is declared for content described as a gift or sample, for which a proforma invoice is the usual document.
The levels differ because the sources restrict the proforma invoice to goods not sold but do not forbid a commercial invoice for gifts or samples.
Recorded gap, not addressed: the Postpaket Utrikes terms §2 permit a proforma invoice only for gifts or samples (FN:111, FN:113, W), but this advisory does not apply to International Parcel, whose booking carries no invoice type.
Recorded gap, not addressed: for International Parcel and letter services the connector sends CN22 declaration data and builds `customs.commercial_invoice`, `customs.invoice`, and `customs.invoice_date` only into the customs invoice of parcel products (PNS lines 10 and 13-16, S; karrio `feat-postnord-customs-invoice` at 1b40eeb7e, `shipment/create.py:608-635` and `shipment/create.py:775`, S), so it drops those fields for these services without a warning.
`advisor_nordic_conventions_postnord_se_postpaket_commercial_invoice` tells the consumer to supply the invoice for commercial International Parcel, and no advisory states the drop.
Sources: PNS lines 155-168 and DFS lines 51-64 (S, the connectors apply the flag literally and leave mismatch detection to advisory tooling), FN:56 (W, Bring tulldokument and DHL CIE p.5, a proforma invoice is used for goods not sold), FN:111 and FN:113 (W, Postpaket Utrikes terms §2, "Proformafaktura … får endast användas vid gåva eller varuprov"), FN:30-36 (S, connector mapping of the flag).

#### Scenario: Merchandise declared as proforma

- **WHEN** a DHL Freight Sweden shipment from Sweden to Norway is created with customs data whose `content_type` is `merchandise` and whose `commercial_invoice` is omitted
- **THEN** the plugin returns code `advisor_nordic_conventions_invoice_type_content_mismatch` at level `warning`

#### Scenario: Omitted content type declared as proforma

- **WHEN** a PostNord `postnord_parcel` shipment from Sweden to Norway is created with customs data carrying no `content_type` and `commercial_invoice` false
- **THEN** the plugin returns code `advisor_nordic_conventions_invoice_type_content_mismatch` at level `warning`

#### Scenario: Gift declared as proforma is consistent

- **WHEN** a PostNord `postnord_parcel` shipment from Sweden to Norway is created with customs data whose `content_type` is `gift` and whose `commercial_invoice` is false
- **THEN** the plugin does not return code `advisor_nordic_conventions_invoice_type_content_mismatch`

#### Scenario: Return merchandise declared as proforma is consistent

- **WHEN** a DHL Freight Sweden shipment from Sweden to Norway is created with customs data whose `content_type` is `return_merchandise` and whose `commercial_invoice` is false
- **THEN** the plugin does not return code `advisor_nordic_conventions_invoice_type_content_mismatch`

#### Scenario: Sample declared as commercial is informational

- **WHEN** a DHL Freight Sweden shipment from Sweden to Switzerland is created with customs data whose `content_type` is `sample` and whose `commercial_invoice` is true
- **THEN** the plugin returns code `advisor_nordic_conventions_invoice_type_content_mismatch` at level `info`

#### Scenario: Letters carry no invoice type

- **WHEN** a PostNord `postnord_export_letter` shipment from Sweden to Norway is created with customs data whose `content_type` is `merchandise` and whose `commercial_invoice` is false
- **THEN** the plugin does not return code `advisor_nordic_conventions_invoice_type_content_mismatch`, because the connector sends a CN22 without an invoice type for letters

### Requirement: Per-shipment procedure attestations

The plugin SHALL accept five shipment options in the request options dictionary, each naming one out-of-booking procedure: `advisor_nordic_conventions_commercial_invoice_paper_copy`, `advisor_nordic_conventions_customs_declaration_paper_copy`, `advisor_nordic_conventions_customs_documents_attached_outside`, `advisor_nordic_conventions_commercial_invoice_electronic`, and `advisor_nordic_conventions_voec_marking_printed`.
An option SHALL count as an attestation only when its value is the boolean `true`; absent, `false`, or any other value, including the string `"false"`, SHALL count as no claim.
An option in the `advisor_nordic_conventions_` namespace that the plugin does not define SHALL be ignored, with no message and no change to any advisory.
The procedures SHALL mean: a printed commercial invoice travelling with the parcel; a printed customs declaration, CN22 or CN23, travelling with the parcel; copies of the customs documents attached on the outside of the package; a commercial invoice transmitted electronically outside the booking; and the VOEC ID printed on the package or label.

#### Scenario: Boolean true attests

- **WHEN** an attestation option's value is the boolean `true`
- **THEN** the shipment carries the claim to perform that procedure

#### Scenario: String false is no claim

- **WHEN** an attestation option's value is the string `"false"`
- **THEN** the shipment carries no claim, unlike karrio carrier-option parsing where a string `"false"` counts as set

#### Scenario: Unknown namespaced option is ignored

- **WHEN** the options carry a `advisor_nordic_conventions_` key the plugin does not define
- **THEN** the key is ignored and every advisory is returned exactly as without it

### Requirement: Advisory answering procedures

The plugin SHALL hold, for every advisory classification, the set of procedures whose performance answers it; the set is empty when no out-of-booking procedure answers it, and the plugin SHALL keep the mapping complete over all classifications.
`advisor_nordic_conventions_dhl_freight_sweden_customs_mode_missing`, `advisor_nordic_conventions_dhl_freight_sweden_aland_customs_service_rejected`, `advisor_nordic_conventions_dhl_freight_sweden_joint_declaration_destination`, and `advisor_nordic_conventions_invoice_type_content_mismatch` SHALL map to the empty set, because their remedy lies inside the booking request, in the connector's customs service options and the `customs.commercial_invoice` flag.
The answering sets SHALL be lane-aware as follows.
`advisor_nordic_conventions_postnord_se_no_digital_invoice` is answered by `commercial_invoice_electronic`.
`advisor_nordic_conventions_postnord_se_postpaket_commercial_invoice` is answered, for Norway, by `customs_declaration_paper_copy` and `commercial_invoice_electronic`, and for other destinations by `customs_declaration_paper_copy` and `commercial_invoice_paper_copy`, resting on the terms' CN23 in two copies and invoice copies with the parcel (FN:103, FN:111, W).
`advisor_nordic_conventions_postnord_se_export_paper_invoice` is answered by `commercial_invoice_paper_copy`.
`advisor_nordic_conventions_postnord_fi_export_invoice` is answered, for Norway, by `commercial_invoice_electronic`, and for other destinations by `commercial_invoice_paper_copy`.
`advisor_nordic_conventions_postnord_dk_export_documents` is answered, for Norway, Switzerland, and Liechtenstein, and Great Britain, by `commercial_invoice_paper_copy`, and for any other destination by `customs_declaration_paper_copy` and `commercial_invoice_paper_copy`, resting on the 1 CN23 and 2 invoices default (FN:144, W).
`advisor_nordic_conventions_dhl_freight_sweden_invoice_copy` is answered by `commercial_invoice_electronic`.
`advisor_nordic_conventions_dhl_freight_sweden_attached_documents` is answered by `customs_documents_attached_outside`.
`advisor_nordic_conventions_dhl_freight_sweden_voec_marking` is answered by `voec_marking_printed`.
`advisor_nordic_conventions_ch_discount_on_invoice`, `advisor_nordic_conventions_zero_value_line`, `advisor_nordic_conventions_dhl_freight_sweden_parcel_connect_not_served`, `advisor_nordic_conventions_dhl_freight_sweden_parcel_connect_gb_agreement`, and `advisor_nordic_conventions_dhl_freight_sweden_territory_postal_code_mismatch` SHALL map to the empty set, because their remedy lies in the invoice content, the declared values, the booked product, or the address.

#### Scenario: Mapping is complete

- **WHEN** the plugin adds an advisory classification
- **THEN** its answering set is defined, and an omitted entry is a test failure

#### Scenario: Finland to Norway answers electronically

- **WHEN** `advisor_nordic_conventions_postnord_fi_export_invoice` applies to a Norway destination
- **THEN** its answering set is `commercial_invoice_electronic` alone

#### Scenario: Denmark default destination needs both paper procedures

- **WHEN** `advisor_nordic_conventions_postnord_dk_export_documents` applies to a destination other than Norway, Switzerland, Liechtenstein, and Great Britain
- **THEN** its answering set is `customs_declaration_paper_copy` and `commercial_invoice_paper_copy`

### Requirement: Answered advisories are omitted

This requirement qualifies every requirement stating that an advisory SHALL be returned.
An advisory SHALL be omitted when its answering set is non-empty and every procedure in the set is covered by an attestation that holds on the lane.
An attestation contradicted on the lane SHALL cover nothing, and partial coverage SHALL omit nothing.

#### Scenario: Full coverage omits the advisory

- **WHEN** every procedure in an advisory's answering set is attested and no attestation is contradicted
- **THEN** the advisory is not returned

#### Scenario: Partial coverage omits nothing

- **WHEN** only some procedures in an advisory's answering set are attested
- **THEN** the advisory is returned, unchanged in level and text

#### Scenario: Contradicted attestation covers nothing

- **WHEN** an attestation covering an answering procedure is contradicted on the lane
- **THEN** the advisory is returned and the conflict advisory is also returned

### Requirement: Contradicted attestations are reported

When an attested procedure is contradicted by the conventions that govern the lane, the plugin SHALL return code `advisor_nordic_conventions_attestation_conflict` at level `warning`, once per contradicted attestation, naming the attested procedure and the contradicting convention, with the convention's sources in `details`.
In this change the only contradiction is `advisor_nordic_conventions_commercial_invoice_paper_copy` on a PostNord lane from Sweden to Norway, whose sources require the commercial invoice digitally and not on paper with the parcel (FN:118, FN:142, W; PNS lines 28-31, S).

#### Scenario: Paper invoice attested on the Sweden-to-Norway lane

- **WHEN** `advisor_nordic_conventions_commercial_invoice_paper_copy` is attested on a PostNord shipment from Sweden to Norway
- **THEN** the conflict warning is returned, naming the digital-only convention and its sources

#### Scenario: No contradiction, no conflict message

- **WHEN** every attestation holds on the lane
- **THEN** the attestations cover their procedures and no conflict advisory is returned

### Requirement: Pre-booking expected procedures

The plugin SHALL expose a public function `expected_procedures` that takes a shipment request and an advisor context and returns the set of procedures the conventions expect for that request.
It SHALL return the empty set outside the plugin's scope, for the rating operation, a carrier or lane out of scope, or a shipment inside the EU VAT area, and otherwise return the union of the answering sets of the advisories that would be returned with no attestations.
It SHALL derive its result from the same rules that produce the advisories, so the function and the advisories cannot disagree.

#### Scenario: PostNord parcel from Sweden expects the paper invoice

- **WHEN** `expected_procedures` evaluates a PostNord parcel request from Sweden to a destination outside the EU VAT area other than Norway
- **THEN** the result includes `commercial_invoice_paper_copy`

#### Scenario: Out-of-scope request expects nothing

- **WHEN** `expected_procedures` evaluates a shipment inside the EU VAT area
- **THEN** the result is the empty set

### Requirement: Discounted lines to Switzerland are shown on the invoice

For a PostNord or DHL Freight Sweden shipment within the plugin's scope to Switzerland whose customs data contains a commodity with `metadata.discount_percentage` set or with a `value_amount` of 0 or none, the plugin SHALL return code `advisor_nordic_conventions_ch_discount_on_invoice` at level `info`.
The message SHALL state that Switzerland does not tax a discount, or an item handed over with a sold item as a discount in kind or add-on, as part of the import consideration, provided the item is directly connected to the sale, and that the commercial invoice shows the discount and ties the discounted or free item to that sale.
`details` SHALL list the zero-based indexes of the triggering commodities under `lines`, cite BAZG Richtlinie R-69-03 §5.5.3 (W), and state under `unconfirmed` that R-69-03 does not address an add-on shipped in a separate parcel from the sale it belongs to.

#### Scenario: Free line in a sale to Switzerland

- **WHEN** a PostNord `postnord_parcel` shipment from Sweden to Switzerland is created with customs data whose second commodity carries `metadata.discount_percentage` 100
- **THEN** the plugin returns code `advisor_nordic_conventions_ch_discount_on_invoice` at level `info` with `lines` [1]

#### Scenario: Zero-valued line to Switzerland

- **WHEN** a DHL Freight Sweden shipment from Sweden to Switzerland is created with customs data whose first commodity has a `value_amount` of 0
- **THEN** the plugin returns code `advisor_nordic_conventions_ch_discount_on_invoice` with `lines` [0]

#### Scenario: Discounted line to Norway

- **WHEN** a PostNord `postnord_parcel` shipment from Sweden to Norway is created with a commodity carrying `metadata.discount_percentage` 100
- **THEN** the plugin does not return code `advisor_nordic_conventions_ch_discount_on_invoice`

#### Scenario: Fully valued lines

- **WHEN** a PostNord `postnord_parcel` shipment from Sweden to Switzerland is created with commodities that all carry a positive value and no discount
- **THEN** the plugin does not return code `advisor_nordic_conventions_ch_discount_on_invoice`

### Requirement: Zero-value commodity lines are flagged

For a shipment within the plugin's scope whose customs data contains a commodity with a `value_amount` of 0 or none, the plugin SHALL return code `advisor_nordic_conventions_zero_value_line` at level `warning`.
The message SHALL state that a commercial or pro forma invoice may never carry a value of 0, even for gifts or samples, and that each line needs its customs value.
`details` SHALL list the zero-based indexes of the triggering commodities under `lines` and cite PostNord's page on parcels to Norway, Tullverket's page on supporting documents for export, and DHL Express's customs guidelines (all W).

#### Scenario: Zero-valued line to Norway

- **WHEN** a PostNord `postnord_parcel` shipment from Sweden to Norway is created with customs data whose second commodity has a `value_amount` of 0
- **THEN** the plugin returns code `advisor_nordic_conventions_zero_value_line` at level `warning` with `lines` [1]

#### Scenario: Line without a value

- **WHEN** a DHL Freight Sweden shipment from Sweden to the United Kingdom is created with a commodity that has no `value_amount`
- **THEN** the plugin returns code `advisor_nordic_conventions_zero_value_line`

#### Scenario: Inside the EU VAT area

- **WHEN** a PostNord `postnord_parcel` shipment from Sweden to Germany is created with a zero-valued commodity
- **THEN** the plugin returns no advisory

### Requirement: DHL Freight Sweden products are not booked on lanes they do not serve

For a DHL Freight Sweden shipment from Sweden booked, by unified name or carrier code, as a product whose "Valid countries" table in the DHL Freight Sweden product manual v5.26 allows no lane from the shipper's country to the recipient's country, the plugin SHALL return code `advisor_nordic_conventions_dhl_freight_sweden_parcel_connect_not_served` at level `warning`.
The lanes SHALL be those of the DHL Freight Sweden connector's `PRODUCT_LANES` table, copied into the plugin and checked against the connector by a test that runs when the connector is importable: the domestic products 102, 103, 104, 118, 209, 210, 211, 212, 401, 402, and 502 within Sweden; Parcel Connect (109) and Parcel Connect Plus (112) from Sweden to their listed countries; Parcel Return Connect (107) from its listed countries to Sweden; and Road Freight Standard (202), Road Freight Direct (205), Road Freight Priority (233), Standard Pallet International (SPI), and Home Delivery International B2C (601) from Sweden to their listed countries and from them to Sweden.
Country codes SHALL be compared after the territory mapping of "DHL Freight Sweden territory codes are read as their parent country", in the message as well.
On a lane the product serves, the plugin SHALL also return the code when the shipper's or the recipient's postal code is excluded for the product, as the connector's `POSTAL_CODE_EXCLUSIONS` (the manual's numeric "Excluded regions/areas") and `POSTAL_CODE_PATTERN_EXCLUSIONS` (the manual's areas without ranges, such as `JE*`, `GY*`, and `BT*` under `GB` for 109 and 112, and the Product API catalog's `postalCodeExcludes` for 202, 233, and 601) decide it after the territory mapping: a numeric range compared in the country's postal code format, a Danish range also excluding a code led by `FO` or `GL` or of three digits where the connector marks it so, and a pattern matched against the whole normalised code.
These tables SHALL be copied into the plugin and checked against the connector by a test that runs when the connector is importable.
A postal code that is missing or does not match the country's format SHALL NOT be advised as excluded.
The message for an excluded postal code SHALL name the product, its code, the country, the excluded codes, and the region, and `details` SHALL cite the manual's excluded areas (W, §5.3 p.18, §5.4 p.23, §5.9 p.43, §5.11 p.52, §5.14 p.63, §5.15 p.66) and the connector's destinations page for the catalog patterns (S, 7a2214d).
A service that names no DHL Freight Sweden product SHALL return no message.
The message SHALL name the product and its code and state that it does not ship from the shipper's country to the recipient's country.
For Parcel Return Connect (107) the message SHALL add that it only returns a parcel from abroad to its original sender in Sweden.
For a recipient in Switzerland the message SHALL add products that serve it: Home Delivery International B2C (601), Road Freight Standard (202), Road Freight Direct (205), and Road Freight Priority (233).
`details` SHALL cite the DHL Freight Sweden product manual v5.26 overview and "Valid countries" tables (W, §5.1 p.13, §5.2 p.15 to §5.19 p.82, §5.15 p.65).

#### Scenario: Parcel Connect to Switzerland

- **WHEN** a DHL Freight Sweden `dhl_freight_sweden_parcel_connect_b2c` shipment from Sweden to Switzerland is created
- **THEN** the plugin returns code `advisor_nordic_conventions_dhl_freight_sweden_parcel_connect_not_served` at level `warning`, and the message names the products that serve Switzerland

#### Scenario: Parcel Return Connect to Great Britain

- **WHEN** a DHL Freight Sweden `dhl_freight_sweden_parcel_return_connect_c2b` shipment from Sweden to Great Britain is created
- **THEN** the plugin returns code `advisor_nordic_conventions_dhl_freight_sweden_parcel_connect_not_served` at level `warning`

#### Scenario: Parcel Return Connect from Sweden

- **WHEN** a DHL Freight Sweden `dhl_freight_sweden_parcel_return_connect_c2b` or `107` shipment from Sweden to Norway, Great Britain, or Switzerland is created
- **THEN** the plugin returns code `advisor_nordic_conventions_dhl_freight_sweden_parcel_connect_not_served` at level `warning`, and the message states that 107 only returns a parcel to its original sender in Sweden

#### Scenario: Domestic product abroad

- **WHEN** a DHL Freight Sweden `dhl_freight_sweden_paket` shipment from Sweden to Norway is created
- **THEN** the plugin returns code `advisor_nordic_conventions_dhl_freight_sweden_parcel_connect_not_served` at level `warning`

#### Scenario: Road freight to an unlisted country

- **WHEN** a DHL Freight Sweden `233` shipment from Sweden to Ukraine, or a `dhl_freight_sweden_road_freight_standard` shipment from Sweden to the United States, is created
- **THEN** the plugin returns code `advisor_nordic_conventions_dhl_freight_sweden_parcel_connect_not_served` at level `warning`

#### Scenario: Home Delivery International to Switzerland

- **WHEN** a DHL Freight Sweden `dhl_freight_sweden_home_delivery_international_b2c` shipment from Sweden to Switzerland is created
- **THEN** the plugin does not return code `advisor_nordic_conventions_dhl_freight_sweden_parcel_connect_not_served`

#### Scenario: Parcel Connect to Norway

- **WHEN** a DHL Freight Sweden `dhl_freight_sweden_parcel_connect_b2c` shipment from Sweden to Norway is created
- **THEN** the plugin does not return code `advisor_nordic_conventions_dhl_freight_sweden_parcel_connect_not_served`

#### Scenario: Parcel Connect to Great Britain is an agreement case

- **WHEN** a DHL Freight Sweden `dhl_freight_sweden_parcel_connect_plus` shipment from Sweden to Great Britain is created
- **THEN** the plugin does not return code `advisor_nordic_conventions_dhl_freight_sweden_parcel_connect_not_served`

#### Scenario: Unknown service

- **WHEN** a DHL Freight Sweden shipment from Sweden to Norway is created with a service that names no DHL Freight Sweden product
- **THEN** the plugin does not return code `advisor_nordic_conventions_dhl_freight_sweden_parcel_connect_not_served`

#### Scenario: Parcel Connect to Åland by territory code

- **WHEN** a DHL Freight Sweden `dhl_freight_sweden_parcel_connect_b2c` shipment from Sweden to `AX` with postal code 22100 is created
- **THEN** the plugin does not return code `advisor_nordic_conventions_dhl_freight_sweden_parcel_connect_not_served`, because 109 serves `FI`

#### Scenario: Parcel Connect Plus to a Jersey postcode

- **WHEN** a DHL Freight Sweden `dhl_freight_sweden_parcel_connect_plus` shipment from Sweden to `GB` or `JE` with postal code JE2 3AB is created
- **THEN** the plugin returns code `advisor_nordic_conventions_dhl_freight_sweden_parcel_connect_not_served` at level `warning`, and the message names the GB postal codes `JE*`, `GY*`, `BT*`

#### Scenario: Parcel Connect to the Canary Islands by territory code

- **WHEN** a DHL Freight Sweden `109` shipment from Sweden to `IC` with postal code 35001 is created
- **THEN** the plugin returns code `advisor_nordic_conventions_dhl_freight_sweden_parcel_connect_not_served`, because 109 excludes `ES` 35000-35999

#### Scenario: Parcel Return Connect to Jersey reads as Great Britain

- **WHEN** a DHL Freight Sweden `107` shipment from Sweden to `JE` with postal code JE2 3AB is created
- **THEN** the plugin returns code `advisor_nordic_conventions_dhl_freight_sweden_parcel_connect_not_served` at level `warning`, and the message states that 107 does not ship from SE to GB

### Requirement: DHL Freight Sweden Parcel Connect serves Great Britain only by separate agreement

For a DHL Freight Sweden shipment from Sweden to Great Britain booked, by unified name or carrier code, as Parcel Connect (`dhl_freight_sweden_parcel_connect_b2c`, `109`) or Parcel Connect Plus (`dhl_freight_sweden_parcel_connect_plus`, `112`), the plugin SHALL return code `advisor_nordic_conventions_dhl_freight_sweden_parcel_connect_gb_agreement` at level `warning`, unless the recipient's postal code is excluded for the product as "DHL Freight Sweden products are not booked on lanes they do not serve" defines it, in which case that requirement's code is returned instead.
The message SHALL state that these products serve Great Britain only by separate agreement with DHL.
`details` SHALL cite the DHL Freight Sweden product manual v5.26 (W, §5.3 p.18, §5.14 p.63) and the DHL Freight Sweden connector's committed sandbox evidence that a 112 booking from Sweden to Great Britain without the agreement was rejected with 22005 and 22026 (S, `tests/dhl_freight_sweden/fixtures/sandbox/rejection-22005-112-se-gb.json` at 28c1ccb).

#### Scenario: Parcel Connect to Great Britain

- **WHEN** a DHL Freight Sweden `dhl_freight_sweden_parcel_connect_b2c` shipment from Sweden to Great Britain is created
- **THEN** the plugin returns code `advisor_nordic_conventions_dhl_freight_sweden_parcel_connect_gb_agreement` at level `warning`, and not code `advisor_nordic_conventions_dhl_freight_sweden_parcel_connect_not_served`

#### Scenario: Parcel Connect to Switzerland is not an agreement case

- **WHEN** a DHL Freight Sweden `dhl_freight_sweden_parcel_connect_b2c` shipment from Sweden to Switzerland is created
- **THEN** the plugin does not return code `advisor_nordic_conventions_dhl_freight_sweden_parcel_connect_gb_agreement`

#### Scenario: Parcel Connect to a Jersey postcode is not an agreement case

- **WHEN** a DHL Freight Sweden `dhl_freight_sweden_parcel_connect_plus` shipment from Sweden to `GB` or `JE` with postal code JE2 3AB is created
- **THEN** the plugin does not return code `advisor_nordic_conventions_dhl_freight_sweden_parcel_connect_gb_agreement`

### Requirement: DHL Freight Sweden customs handling is not selected to Åland

For a DHL Freight Sweden shipment from Sweden to a recipient in Åland, `FI` with a postal code normalised as in "The EU VAT area follows Tullverket for goods" in 22000-22999 after the territory mapping, on which customs handling standard (`dhl_freight_sweden_customs_handling_standard`) or full service (`dhl_freight_sweden_customs_handling_full_service`) is set, read as the plugin reads every DHL Freight Sweden customs service option, the plugin SHALL return code `advisor_nordic_conventions_dhl_freight_sweden_aland_customs_service_rejected` at level `warning`.
The message SHALL name the selected services, state that DHL rejects them to Åland with 24003 and that the connector refuses them before booking, and name the own declaration or customs data sent without a customs service as the bookings the connector accepts, adding that DHL's acceptance of customs data without a customs service does not show how it clears customs.
The joint declaration SHALL NOT be named, because the connector refuses it to destinations other than Norway and Switzerland.
The Åland range and the refused services SHALL be the connector's `ALAND_POSTAL_RANGE` and `ALAND_REJECTED_CUSTOMS_SERVICES`, checked against the connector by a test that runs when the connector is importable.
`details` SHALL cite the connector's Åland evidence (S, connector `docs/concepts/destinations.md` "Åland" at 7a2214d: rejections 24003 for 112 with full service and with Standard, and booking 2906762592 of 109 with customs data and no customs service) and the manual's customs selection (W, MAN v5.26 §7.6.1 p.163, §6.7 p.96).
The answering set of the code SHALL be empty, because its remedy lies in the booking's customs service options.

#### Scenario: Standard customs handling to Åland

- **WHEN** a DHL Freight Sweden shipment from Sweden to `FI` with postal code 22100, or to `AX` with postal code AX-22100, is created with `dhl_freight_sweden_customs_handling_standard` set
- **THEN** the plugin returns code `advisor_nordic_conventions_dhl_freight_sweden_aland_customs_service_rejected` at level `warning`, and its message does not name the joint declaration

#### Scenario: Own declaration to Åland

- **WHEN** a DHL Freight Sweden shipment from Sweden to `FI` with postal code 22100 is created with `dhl_freight_sweden_customs_own_declaration` set
- **THEN** the plugin does not return code `advisor_nordic_conventions_dhl_freight_sweden_aland_customs_service_rejected`

#### Scenario: Full service to Norway

- **WHEN** a DHL Freight Sweden shipment from Sweden to Norway is created with `dhl_freight_sweden_customs_handling_full_service` set
- **THEN** the plugin does not return code `advisor_nordic_conventions_dhl_freight_sweden_aland_customs_service_rejected`

### Requirement: DHL Freight Sweden territory codes carry a postal code of the territory

For a DHL Freight Sweden shipment from Sweden whose recipient carries the country code `AX`, `IC`, `EA`, `FO`, or `GL` with a postal code that is missing or, normalised under the parent country as in "The EU VAT area follows Tullverket for goods", lies outside the territory (`FI` 22000-22999 for `AX`; `ES` 35000-35999 or 38000-38999 for `IC`; `ES` 51000-51999 or 52000-52999 for `EA`; `DK` 3800-3999 or a three-digit code for `FO`; `DK` 3800-3999 for `GL`), the plugin SHALL return code `advisor_nordic_conventions_dhl_freight_sweden_territory_postal_code_mismatch` at level `warning`.
This requirement qualifies "Advice is limited to Nordic shippers at shipment creation": the advisory SHALL be returned whether or not the recipient, read under its parent country, lies outside the EU VAT area, because such a code is otherwise booked as the parent's mainland.
The message SHALL name the territory code, the territory, the parent country, the postal codes the connector requires, and the recipient's postal code or its absence, state that the connector refuses the booking, and advise the parent country code for an address outside the territory.
The territories and their postal codes SHALL be the connector's `TERRITORY_POSTAL_CODES`, copied into the plugin and checked against the connector by a test that runs when the connector is importable; `JE`, `GG`, `IM`, and `XI` have no range and SHALL NOT be checked.
`details` SHALL cite the connector's `TerritoryPostalCodeError` (S, karrio-dhl-freight-sweden branch `products-manual-country-lists` at 142b62d).
The answering set of the code SHALL be empty, because its remedy lies in the booking's address.

#### Scenario: Åland code with a mainland postal code

- **WHEN** a DHL Freight Sweden shipment from Sweden to `AX` with postal code 00100, or with no postal code, is created
- **THEN** the plugin returns code `advisor_nordic_conventions_dhl_freight_sweden_territory_postal_code_mismatch` at level `warning`

#### Scenario: Territory code inside its territory

- **WHEN** a DHL Freight Sweden shipment from Sweden to `AX` with postal code AX-22100, `IC` with postal code 35001, or `FO` with postal code FO-100 is created
- **THEN** the plugin does not return code `advisor_nordic_conventions_dhl_freight_sweden_territory_postal_code_mismatch`

#### Scenario: Jersey is not checked

- **WHEN** a DHL Freight Sweden shipment from Sweden to `JE` with postal code JE2 3AB is created
- **THEN** the plugin does not return code `advisor_nordic_conventions_dhl_freight_sweden_territory_postal_code_mismatch`

### Requirement: DHL Freight Sweden joint declaration is selected only to Norway or Switzerland

For a DHL Freight Sweden shipment from Sweden to a destination outside the EU VAT area on which `dhl_freight_sweden_customs_joint_declaration` is set, read as the plugin reads every DHL Freight Sweden customs service option, and whose recipient country after the territory mapping is not in the connector's `JOINT_DECLARATION_COUNTRIES` (`NO`, `CH`), the plugin SHALL return code `advisor_nordic_conventions_dhl_freight_sweden_joint_declaration_destination` at level `warning`.
The scope matches the connector's `JointDeclarationDestinationError` (S, karrio-dhl-freight-sweden branch `products-manual-country-lists` at f86c8ac), applied only across the EU VAT area border; inside the area the connector drops customs services with a warning instead, and the plugin, which advises only recipients outside the area, SHALL return no message there.
The message SHALL name the option, state that the joint declaration is valid only to Norway or Switzerland and that the connector refuses it to the recipient country, and name customs handling (standard or full service) or an own declaration as alternatives, or, for a recipient in Åland as "DHL Freight Sweden customs handling is not selected to Åland" defines it, an own declaration or customs data with no customs service.
`details` SHALL cite the manual's joint declaration (W, MAN v5.26 §6.8 p.98) and the connector's refusal.
The answering set of the code SHALL be empty, because its remedy lies in the booking's customs service options.

#### Scenario: Joint declaration to Great Britain

- **WHEN** a DHL Freight Sweden shipment from Sweden to Great Britain, or to `JE`, is created with `dhl_freight_sweden_customs_joint_declaration` set
- **THEN** the plugin returns code `advisor_nordic_conventions_dhl_freight_sweden_joint_declaration_destination` at level `warning`

#### Scenario: Joint declaration to Åland

- **WHEN** a DHL Freight Sweden shipment from Sweden to `AX` with postal code 22100 is created with `dhl_freight_sweden_customs_joint_declaration` set
- **THEN** the plugin returns code `advisor_nordic_conventions_dhl_freight_sweden_joint_declaration_destination`, and the message does not suggest customs handling standard or full service

#### Scenario: Joint declaration to Norway or Switzerland

- **WHEN** a DHL Freight Sweden shipment from Sweden to Norway or Switzerland is created with `dhl_freight_sweden_customs_joint_declaration` set
- **THEN** the plugin does not return code `advisor_nordic_conventions_dhl_freight_sweden_joint_declaration_destination`

#### Scenario: Joint declaration inside the EU VAT area

- **WHEN** a DHL Freight Sweden shipment from Sweden to Germany, or to `XI` with postal code BT1 1AA, is created with `dhl_freight_sweden_customs_joint_declaration` set
- **THEN** the plugin returns no message

### Requirement: DHL Freight Sweden territory codes are read as their parent country

For a `dhl_freight_sweden` advisor context, the plugin SHALL read the shipper's and the recipient's country codes as the DHL Freight Sweden connector books them, replacing a territory code by its parent country: `AX` by `FI`, `FO` and `GL` by `DK`, `IC` and `EA` by `ES`, and `JE`, `GG`, `IM`, and `XI` by `GB`, before the scope and EU VAT area checks of "Advice is limited to Nordic shippers at shipment creation" and in every DHL Freight Sweden advisory that reads a country.
The mapping SHALL be the connector's `TERRITORY_PARENTS` table, copied into the plugin and checked against the connector by a test that runs when the connector is importable (S, karrio-dhl-freight-sweden `units.py` and `docs/concepts/destinations.md` "Special territories" at 7a2214d).
The postal code SHALL be used as given, and the EU VAT area table SHALL be unchanged; only the country code it is asked about changes.
For other carriers the plugin SHALL read the country codes as given.

#### Scenario: Northern Ireland by territory code is inside for goods

- **WHEN** a DHL Freight Sweden shipment from Sweden to `XI` with postal code BT1 1AA is created
- **THEN** the plugin returns no message, because `GB` `BT1 1AA` is inside the EU VAT area for goods

#### Scenario: Northern Ireland by territory code without a BT postcode is outside

- **WHEN** a DHL Freight Sweden shipment from Sweden to `XI` with postal code EC1A 1BB is created
- **THEN** the recipient is treated as `GB` outside the EU VAT area

#### Scenario: Jersey reads as Great Britain

- **WHEN** a DHL Freight Sweden `233` shipment from Sweden to `JE` with postal code JE2 3AB is created
- **THEN** the plugin returns code `advisor_nordic_conventions_dhl_freight_sweden_invoice_copy` with a reminder fee of 650 kr

#### Scenario: Isle of Man reads as Great Britain

- **WHEN** a DHL Freight Sweden `dhl_freight_sweden_parcel_connect_plus` shipment from Sweden to `IM` with postal code IM1 1AA is created
- **THEN** the plugin returns code `advisor_nordic_conventions_dhl_freight_sweden_parcel_connect_gb_agreement`

#### Scenario: Parcel Return Connect from Jersey reads as from Great Britain

- **WHEN** the plugin decides whether Parcel Return Connect (107) ships from `JE` to `SE`
- **THEN** it decides as for `GB` to `SE`, which 107 does not serve

#### Scenario: PostNord keeps territory codes

- **WHEN** a PostNord shipment from Sweden to `XI` with postal code BT1 1AA is created
- **THEN** the recipient country is `XI`, outside the EU VAT area
