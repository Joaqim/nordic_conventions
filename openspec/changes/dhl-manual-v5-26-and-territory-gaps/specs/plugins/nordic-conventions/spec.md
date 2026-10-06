# Spec Delta

## MODIFIED Requirements

### Requirement: The EU VAT area follows Tullverket for goods

The plugin SHALL decide EU VAT area membership from its own territory table, independent of karrio's `EUCountry`, which lists Greece as `EL` and lacks `AX` and `XI` (FN:235, FN:276, S).
The table SHALL match Tullverket's list of EU customs and fiscal territories as it applies to goods movements (FN:58-65, W): the EU member states with Greece as `GR` are inside; Monaco is inside (FN:64, W); Northern Ireland is inside, identified as `GB` with a postal code beginning `BT` (FN:64, W); and Åland (`AX`, or `FI` 22000-22999), the Canary Islands (`IC`, or `ES` 35000-35999 and 38000-38999), Ceuta (`ES` 51000-51999), Melilla (`ES` 52000-52999), Büsingen (`DE` 78266), Heligoland (`DE` 27498), Livigno (`IT` 23041), Campione d'Italia (`IT` 22061), the French overseas departments (`GP`, `GF`, `MQ`, `RE`, `YT`, or `FR` 97000-97999), the Faroe Islands and Greenland addressed under `DK` (`DK` 3800-3999), and Mount Athos (`GR` 63086) are outside.
The `DK` range is the one DHL Freight Sweden's product manual v5.26 gives for "Greenland & The Faroe Islands" (W, MAN v5.26 §5.3 p.18, §5.14 p.63, §5.15 p.66), and the `FR` range is the operator's range for the overseas departments, narrower than the manual's delivery exclusion 97100-99999, which also covers Monaco's 98000.
Great Britain other than Northern Ireland is outside (FN:65, W).
Northern Ireland's inside verdict is the goods-movement verdict: Northern Ireland is inside the EU VAT area for goods and outside it for services, and the plugin decides customs-document advice for goods shipments, so the territory table carries no services verdict.
Monaco's French-style postal codes 98000-98999 keep their inside verdict through the `FR` country code, so only the `MC` country code changes verdict.
A postal code SHALL be upper-cased and trimmed, SHALL lose a leading copy of the address's own country code when a hyphen, whitespace, or a digit follows that code, together with the hyphen and whitespace, and SHALL then be compared after removing spaces.
A postal code that is not purely numeric after this normalisation SHALL leave the country-level decision unchanged, except that the Northern Ireland prefix comparison SHALL apply to a normalised postal code beginning `BT` whether or not it is purely numeric.

#### Scenario: Åland by postal code is outside

- **WHEN** a PostNord shipment is created from Sweden to `FI` with postal code 22100
- **THEN** the recipient is treated as outside the EU VAT area and the Swedish PostNord advisories for destinations outside the EU VAT area apply

#### Scenario: Åland by country-prefixed postal code is outside

- **WHEN** a DHL Freight Sweden shipment is created from Sweden to `FI` with postal code `FI-22100`, `fi 22100`, or `FI22100`
- **THEN** the recipient is treated as outside the EU VAT area

#### Scenario: Another country's prefix leaves the country-level decision

- **WHEN** a PostNord shipment is created from Sweden to `FI` with postal code `AX-22100`
- **THEN** the recipient is treated as inside the EU VAT area, because only the address's own country code is removed

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

#### Scenario: Greenland by Danish postal code is outside

- **WHEN** a PostNord shipment is created from Sweden to `DK` with postal code `DK-3900`
- **THEN** the recipient is treated as outside the EU VAT area and the Swedish PostNord advisories for destinations outside the EU VAT area apply

#### Scenario: Mount Athos by postal code is outside

- **WHEN** a PostNord shipment is created from Sweden to `GR` with postal code 630 86
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

#### Scenario: Great Britain outside Northern Ireland is outside

- **WHEN** a PostNord shipment is created from Sweden to `GB` with postal code EC1A 1BB
- **THEN** the recipient is treated as outside the EU VAT area and the Swedish PostNord advisories for destinations outside the EU VAT area apply

### Requirement: DHL Freight Sweden needs a customs handling mode

For a DHL Freight Sweden shipment from Sweden to a destination outside the EU VAT area on which none of the connector's customs service options (standard handling, full-service handling, customer's own declaration, joint declaration) is set, the plugin SHALL return code `nordic_conventions_dhl_freight_sweden_customs_mode_missing` at level `warning`, stating that DHL requires customs handling (standard or full service) or an own declaration to be selected for such destinations and naming the connector options that select them.
The connector selects no customs service implicitly because each carries a fee (DFS lines 75-83, S); DHL's product manual requires the selection for Switzerland, Great Britain, Norway, Åland, and other non-EU destinations (FN:196, W, MAN v5.26 §7.6.1 p.163 and §6.7 p.96), and no fee-free mode exists for non-EU destinations (FN:208, W and I), which the details SHALL state.

#### Scenario: No customs option to Norway

- **WHEN** a DHL Freight Sweden shipment from Sweden to Norway is created without any customs service option
- **THEN** the plugin returns code `nordic_conventions_dhl_freight_sweden_customs_mode_missing` at level `warning`

#### Scenario: Selected customs option silences the advisory

- **WHEN** a DHL Freight Sweden shipment from Sweden to Norway is created with the full-service customs handling option set
- **THEN** the plugin does not return code `nordic_conventions_dhl_freight_sweden_customs_mode_missing`

### Requirement: DHL Freight Sweden invoice copy is sent separately

For a DHL Freight Sweden shipment from Sweden to a destination outside the EU VAT area, the plugin SHALL return code `nordic_conventions_dhl_freight_sweden_invoice_copy` at level `warning`, stating that a copy of the invoice must be emailed to dhlfreight.int.se@dhl.com shortly after booking or uploaded in myDHL Freight, one document per shipment with a clear reference, even when complete customs data is sent with the booking, and that missing documents stop the shipment with a reminder fee of 390 kr, or 650 kr for Great Britain.
Sources: FN:213 (W, MAN v5.26 §7.6.2 p.163, "A copy of the invoice must still be sent"), FN:214 (W, CIE p.9, email and upload routes), FN:216 (W, CIE p.12 and PRL, reminder fees), FN:179 (S, the DHL API has no attachment or upload endpoint).

#### Scenario: Invoice copy advisory to Great Britain states the higher fee

- **WHEN** a DHL Freight Sweden shipment from Sweden to Great Britain is created
- **THEN** the plugin returns code `nordic_conventions_dhl_freight_sweden_invoice_copy` at level `warning` naming dhlfreight.int.se@dhl.com, myDHL Freight, and a reminder fee of 650 kr

### Requirement: DHL Freight Sweden Parcel Connect documents are attached outside the package

For a DHL Freight Sweden Parcel Connect shipment (service `dhl_freight_sweden_parcel_connect_b2c`, DHL product 109) from Sweden to a destination outside the EU VAT area, the plugin SHALL return code `nordic_conventions_dhl_freight_sweden_attached_documents` at level `warning`, stating that two copies of the customs documents must be attached on the outside of the package.
The details SHALL state that the requirement is unconfirmed for Parcel Connect Plus (112) and road-freight products, which receive no such advisory.
Sources: FN:215 (W, MAN v5.26 §5.14 p.62, "Two copies of customs documents must also be attached on the outside of the package"), FN:268 (open question for 112 and road freight; MAN v5.26 §5.3 p.18 asks for 112 only that documents are sent by e-mail).

#### Scenario: Parcel Connect to Norway

- **WHEN** a DHL Freight Sweden `dhl_freight_sweden_parcel_connect_b2c` shipment from Sweden to Norway is created
- **THEN** the plugin returns code `nordic_conventions_dhl_freight_sweden_attached_documents` at level `warning`, and its details state that 112 and road freight are unconfirmed

#### Scenario: Parcel Connect Plus is not advised

- **WHEN** a DHL Freight Sweden `dhl_freight_sweden_parcel_connect_plus` shipment from Sweden to Norway is created
- **THEN** the plugin does not return code `nordic_conventions_dhl_freight_sweden_attached_documents`

### Requirement: DHL Freight Sweden VOEC ID is marked on the package

For a DHL Freight Sweden shipment from Sweden to Norway whose customs data carries `options.voec_number`, which the connector sends as DHL's VOEC supply VAT service (DFS lines 66-73, S), the plugin SHALL return code `nordic_conventions_dhl_freight_sweden_voec_marking` at level `warning`, stating that the VOEC ID must be printed on the package or the label.
Sources: FN:217 (W, MAN v5.26 §6.5 p.92, §6.6 p.94, and §9.4.2 p.168), FN:206 (W, VOEC with Parcel Connect to Norway, sent in the API as `additionalServices.voecSupplyVAT.vatId` per MAN v5.26 §6.5 p.92 and §6.6 p.94).

#### Scenario: VOEC number to Norway

- **WHEN** a DHL Freight Sweden shipment from Sweden to Norway is created with customs data carrying a VOEC number
- **THEN** the plugin returns code `nordic_conventions_dhl_freight_sweden_voec_marking` at level `warning`

#### Scenario: No VOEC number

- **WHEN** a DHL Freight Sweden shipment from Sweden to Norway is created with customs data carrying no VOEC number
- **THEN** the plugin does not return code `nordic_conventions_dhl_freight_sweden_voec_marking`

### Requirement: DHL Freight Sweden Parcel Connect is not booked where it does not serve

For a DHL Freight Sweden shipment from Sweden booked, by unified name or carrier code, as Parcel Connect (`dhl_freight_sweden_parcel_connect_b2c`, `109`), Parcel Connect Plus (`dhl_freight_sweden_parcel_connect_plus`, `112`), or Parcel Return Connect (`dhl_freight_sweden_parcel_return_connect_c2b`, `107`) to Switzerland, or as Parcel Return Connect to Great Britain, the plugin SHALL return code `nordic_conventions_dhl_freight_sweden_parcel_connect_not_served` at level `warning`.
For Switzerland the message SHALL state that these products do not serve Switzerland and name products that serve it: Home Delivery International B2C (601), Road Freight Standard (202), Road Freight Direct (205), and Road Freight Priority (233).
For Great Britain the message SHALL state that Parcel Return Connect (107) does not serve Great Britain.
`details` SHALL cite the DHL Freight Sweden product manual v5.26 (W, §5.3 p.18, §5.14 p.63, §5.15 p.66).

#### Scenario: Parcel Connect to Switzerland

- **WHEN** a DHL Freight Sweden `dhl_freight_sweden_parcel_connect_b2c` shipment from Sweden to Switzerland is created
- **THEN** the plugin returns code `nordic_conventions_dhl_freight_sweden_parcel_connect_not_served` at level `warning`

#### Scenario: Parcel Return Connect to Great Britain

- **WHEN** a DHL Freight Sweden `dhl_freight_sweden_parcel_return_connect_c2b` shipment from Sweden to Great Britain is created
- **THEN** the plugin returns code `nordic_conventions_dhl_freight_sweden_parcel_connect_not_served` at level `warning`

#### Scenario: Home Delivery International to Switzerland

- **WHEN** a DHL Freight Sweden `dhl_freight_sweden_home_delivery_international_b2c` shipment from Sweden to Switzerland is created
- **THEN** the plugin does not return code `nordic_conventions_dhl_freight_sweden_parcel_connect_not_served`

#### Scenario: Parcel Connect to Norway

- **WHEN** a DHL Freight Sweden `dhl_freight_sweden_parcel_connect_b2c` shipment from Sweden to Norway is created
- **THEN** the plugin does not return code `nordic_conventions_dhl_freight_sweden_parcel_connect_not_served`

### Requirement: DHL Freight Sweden Parcel Connect serves Great Britain only by separate agreement

For a DHL Freight Sweden shipment from Sweden to Great Britain booked, by unified name or carrier code, as Parcel Connect (`dhl_freight_sweden_parcel_connect_b2c`, `109`) or Parcel Connect Plus (`dhl_freight_sweden_parcel_connect_plus`, `112`), the plugin SHALL return code `nordic_conventions_dhl_freight_sweden_parcel_connect_gb_agreement` at level `warning`.
The message SHALL state that these products serve Great Britain only by separate agreement with DHL.
`details` SHALL cite the DHL Freight Sweden product manual v5.26 (W, §5.3 p.18, §5.14 p.63) and the DHL Freight Sweden connector's committed sandbox evidence that a 112 booking from Sweden to Great Britain without the agreement was rejected with 22005 and 22026 (S, `tests/dhl_freight_sweden/fixtures/sandbox/rejection-22005-112-se-gb.json` at 28c1ccb).

#### Scenario: Parcel Connect to Great Britain

- **WHEN** a DHL Freight Sweden `dhl_freight_sweden_parcel_connect_b2c` shipment from Sweden to Great Britain is created
- **THEN** the plugin returns code `nordic_conventions_dhl_freight_sweden_parcel_connect_gb_agreement` at level `warning`, and not code `nordic_conventions_dhl_freight_sweden_parcel_connect_not_served`

#### Scenario: Parcel Connect to Switzerland is not an agreement case

- **WHEN** a DHL Freight Sweden `dhl_freight_sweden_parcel_connect_b2c` shipment from Sweden to Switzerland is created
- **THEN** the plugin does not return code `nordic_conventions_dhl_freight_sweden_parcel_connect_gb_agreement`
