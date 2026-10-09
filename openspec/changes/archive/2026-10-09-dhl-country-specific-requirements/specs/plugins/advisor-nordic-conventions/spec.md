# Spec Delta

## MODIFIED Requirements

### Requirement: Advice is limited to Nordic shippers at shipment creation

The plugin SHALL return no message unless all of the following hold: the advisor context operation is `shipping`; the context carrier name is `postnord` with a shipper country of `SE`, `DK`, or `FI`, or `dhl_freight_sweden` with a shipper country of `SE`; and the shipper address is inside the EU VAT area.
The destination each advisory covers is defined by that advisory's own requirement; every advisory outside the country-specific shipping requirements scopes its advice to recipients outside the EU VAT area, while the country-specific shipping requirements name their destination countries themselves.
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
- **THEN** the plugin returns no message, because Germany triggers no country-specific shipping requirement

#### Scenario: Intra-EU shipments with a country-specific requirement receive that advice

- **WHEN** a DHL Freight Sweden shipment from Sweden to Greece is created for product 202 without sender or recipient tax identification numbers
- **THEN** the plugin returns code `advisor_nordic_conventions_dhl_freight_sweden_greek_tax_ids` at level `warning`

#### Scenario: Return from Norway receives no advice

- **WHEN** a PostNord return shipment is created whose original shipper is in Sweden and original recipient is in Norway
- **THEN** the request passed to the advisor has a Norwegian shipper and the plugin returns no message

#### Scenario: Åland shipper receives no advice

- **WHEN** a PostNord shipment is created from `FI` with postal code 22100 to Norway
- **THEN** the plugin returns no message, because the shipper is outside the EU VAT area

## ADDED Requirements

### Requirement: DHL Freight Sweden Cyprus shipments carry Union-status and recipient documents

For a DHL Freight Sweden shipment from Sweden to a recipient in Cyprus, the plugin SHALL return code `advisor_nordic_conventions_dhl_freight_sweden_cyprus_documents` at level `warning`, stating that a commercial invoice and packing list are required to prove the Union status of the goods, that a T2L document is required where applicable, that documents can be uploaded in myDHL Freight, and, when the recipient is a private individual, that copies of the recipient's ID documents, front and back, must be provided.
The recipient SHALL be read as a private individual when the recipient address sets the residential flag or names no company.
The advice applies to every product, because the requirement names shipments to Cyprus without product restriction (W, CSR).

#### Scenario: Business recipient to Cyprus

- **WHEN** a DHL Freight Sweden shipment from Sweden to Cyprus is created whose recipient names a company and does not set the residential flag
- **THEN** the plugin returns code `advisor_nordic_conventions_dhl_freight_sweden_cyprus_documents` at level `warning`, stating the invoice, packing list, and T2L requirements and not mentioning recipient ID documents

#### Scenario: Private recipient to Cyprus

- **WHEN** a DHL Freight Sweden shipment from Sweden to Cyprus is created whose recipient sets the residential flag or names no company
- **THEN** the plugin returns code `advisor_nordic_conventions_dhl_freight_sweden_cyprus_documents` at level `warning`, additionally stating that copies of the recipient's ID documents, front and back, must be provided

#### Scenario: Other destinations receive no Cyprus advice

- **WHEN** a DHL Freight Sweden shipment from Sweden to Greece is created
- **THEN** the plugin does not return code `advisor_nordic_conventions_dhl_freight_sweden_cyprus_documents`

### Requirement: DHL Freight Sweden Greek lanes carry sender and recipient VAT numbers

For a DHL Freight Sweden shipment from Sweden to a recipient in Greece on a product in the connector's party tax id product set (202, SPI, and 601), when the shipper or the recipient has neither a federal nor a state tax identification number, the plugin SHALL return code `advisor_nordic_conventions_dhl_freight_sweden_greek_tax_ids` at level `warning`, naming the parties whose numbers are missing, stating that `EL000000000` can be used for a private individual, and naming the connector fields the numbers are read from.
The product set SHALL be the connector's `PARTY_TAX_ID_PRODUCTS`, copied into the plugin and checked against the connector by a test that runs when the connector is importable (S, karrio-dhl-freight-sweden `units.py`), because the manual requires the numbers per product (W, MAN v5.26 §5.4 p.22, §5.11 p.51, §5.19 p.81) and the connector refuses the booking without them.

#### Scenario: Greek lane without tax identification numbers

- **WHEN** a DHL Freight Sweden shipment from Sweden to Greece is created for product 202 with no tax identification numbers on either party
- **THEN** the plugin returns code `advisor_nordic_conventions_dhl_freight_sweden_greek_tax_ids` at level `warning`, naming both parties and the `EL000000000` fallback

#### Scenario: Both parties identified silences the advisory

- **WHEN** the same shipment is created with a federal tax identification number on each party
- **THEN** the plugin does not return code `advisor_nordic_conventions_dhl_freight_sweden_greek_tax_ids`

#### Scenario: Product outside the set receives no advice

- **WHEN** a DHL Freight Sweden shipment from Sweden to Greece is created for product 205
- **THEN** the plugin does not return code `advisor_nordic_conventions_dhl_freight_sweden_greek_tax_ids`, because 205 is outside the connector's party tax id product set

### Requirement: DHL Freight Sweden Polish lanes state SENT information

For a DHL Freight Sweden shipment from Sweden to a recipient in Poland on a product in the connector's transport declaration product set (202, 205, 233, SPI, and 601), the plugin SHALL return code `advisor_nordic_conventions_dhl_freight_sweden_sent_information` at level `info`, stating that a SENT reference number and Carrier Key Code are required when the goods are subject to the Polish SENT monitoring system, that the connector validates the pair's consistency when given, and that with no information given the connector declares SENT free, so deciding whether the goods are subject is the booker's responsibility.
The product set SHALL be the connector's transport declaration product set, copied into the plugin and checked against the connector by a test that runs when the connector is importable (S, karrio-dhl-freight-sweden `units.py`).

#### Scenario: Polish lane receives the SENT reminder

- **WHEN** a DHL Freight Sweden shipment from Sweden to Poland is created for product 202 with parcels weighing 500 kg
- **THEN** the plugin returns code `advisor_nordic_conventions_dhl_freight_sweden_sent_information` at level `info`

#### Scenario: SENT data given still receives the reminder

- **WHEN** the same shipment is created with a SENT reference number and Carrier Key Code provided
- **THEN** the plugin still returns code `advisor_nordic_conventions_dhl_freight_sweden_sent_information` at level `info`, because the reminder is informational

#### Scenario: Product outside the set receives no SENT advice

- **WHEN** a DHL Freight Sweden shipment from Sweden to Poland is created for a product outside the transport declaration product set
- **THEN** the plugin does not return code `advisor_nordic_conventions_dhl_freight_sweden_sent_information`

### Requirement: DHL Freight Sweden Romanian lanes state UIT information

For a DHL Freight Sweden shipment from Sweden to a recipient in Romania on a product in the connector's transport declaration product set (202, 205, 233, SPI, and 601), the plugin SHALL return code `advisor_nordic_conventions_dhl_freight_sweden_uit_information`, at level `warning` when the shipment's total gross weight is 500 kg or more and at level `info` below that, stating that a UIT code is required when the goods exceed 500 kg gross weight, 10 000 RON in value, or are high-risk fiscal goods, that the code is provided by the Romanian party, that `UIT FREE` is entered when the goods are not subject, and that the connector validates the declaration's consistency.
The weight SHALL be the sum of the parcel weights read from the request, compared against the connector's transport declaration free weight limit, copied into the plugin and checked against the connector by a test that runs when the connector is importable (S, karrio-dhl-freight-sweden `units.py`).

#### Scenario: Romanian lane at 500 kg warns

- **WHEN** a DHL Freight Sweden shipment from Sweden to Romania is created for product 202 with parcels totalling 500 kg
- **THEN** the plugin returns code `advisor_nordic_conventions_dhl_freight_sweden_uit_information` at level `warning`

#### Scenario: Romanian lane below the weight criterion informs

- **WHEN** a DHL Freight Sweden shipment from Sweden to Romania is created for product 202 with parcels totalling 100 kg
- **THEN** the plugin returns code `advisor_nordic_conventions_dhl_freight_sweden_uit_information` at level `info`, because the value and high-risk criteria may still apply

#### Scenario: Product outside the set receives no UIT advice

- **WHEN** a DHL Freight Sweden shipment from Sweden to Romania is created for a product outside the transport declaration product set
- **THEN** the plugin does not return code `advisor_nordic_conventions_dhl_freight_sweden_uit_information`

### Requirement: DHL Freight Sweden Hungarian lanes state EKAER information

For a DHL Freight Sweden shipment from Sweden to a recipient in Hungary on a product in the connector's transport declaration product set (202, 205, 233, SPI, and 601), the plugin SHALL return code `advisor_nordic_conventions_dhl_freight_sweden_ekaer_information`, at level `warning` when the shipment's total gross weight is 500 kg or more and at level `info` below that, stating that an EKAER number is required when the goods are subject to the Hungarian EKAER control system, that the number is obtained from the Hungarian party, that `EKAER FREE` is entered when the goods are not subject, and that the connector validates the declaration's consistency.
The weight SHALL be the sum of the parcel weights read from the request, compared against the connector's transport declaration free weight limit, copied into the plugin and checked against the connector by a test that runs when the connector is importable (S, karrio-dhl-freight-sweden `units.py`).

#### Scenario: Hungarian lane at 500 kg warns

- **WHEN** a DHL Freight Sweden shipment from Sweden to Hungary is created for product 202 with parcels totalling 500 kg
- **THEN** the plugin returns code `advisor_nordic_conventions_dhl_freight_sweden_ekaer_information` at level `warning`

#### Scenario: Hungarian lane below the weight criterion informs

- **WHEN** a DHL Freight Sweden shipment from Sweden to Hungary is created for product 202 with parcels totalling 100 kg
- **THEN** the plugin returns code `advisor_nordic_conventions_dhl_freight_sweden_ekaer_information` at level `info`, because the value and risky-goods criteria may still apply

#### Scenario: Product outside the set receives no EKAER advice

- **WHEN** a DHL Freight Sweden shipment from Sweden to Hungary is created for a product outside the transport declaration product set
- **THEN** the plugin does not return code `advisor_nordic_conventions_dhl_freight_sweden_ekaer_information`

### Requirement: DHL Freight Sweden Spanish dangerous goods carry a safety data sheet

For a DHL Freight Sweden shipment from Sweden to a recipient in Spain on which the shipment option `dangerous_good` is set, the plugin SHALL return code `advisor_nordic_conventions_dhl_freight_sweden_spain_dg_documents` at level `warning`, stating that both a dangerous goods declaration and a material safety data sheet must be attached and that the documents can be uploaded in myDHL Freight.
The manual's to-and-from Spain wording reaches this plugin as the to-Spain direction only, because the connector serves Swedish shippers, so the plugin sees no lane from Spain.
The advice applies to every product, because the requirement names dangerous-goods shipments to and from Spain without product restriction (W, CSR).

#### Scenario: Dangerous goods to Spain

- **WHEN** a DHL Freight Sweden shipment from Sweden to Spain is created with the `dangerous_good` shipment option set
- **THEN** the plugin returns code `advisor_nordic_conventions_dhl_freight_sweden_spain_dg_documents` at level `warning`

#### Scenario: Ordinary goods to Spain receive no advice

- **WHEN** a DHL Freight Sweden shipment from Sweden to Spain is created without the `dangerous_good` shipment option
- **THEN** the plugin does not return code `advisor_nordic_conventions_dhl_freight_sweden_spain_dg_documents`

#### Scenario: Dangerous goods elsewhere receive no advice

- **WHEN** a DHL Freight Sweden shipment from Sweden to Germany is created with the `dangerous_good` shipment option set
- **THEN** the plugin does not return code `advisor_nordic_conventions_dhl_freight_sweden_spain_dg_documents`
