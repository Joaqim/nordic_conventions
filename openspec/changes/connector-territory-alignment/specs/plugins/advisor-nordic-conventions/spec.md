# Spec Delta

## ADDED Requirements

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

## MODIFIED Requirements

### Requirement: DHL Freight Sweden needs a customs handling mode

For a DHL Freight Sweden shipment from Sweden to a destination outside the EU VAT area on which none of the connector's customs service options (standard handling, full-service handling, customer's own declaration, joint declaration) is set, the plugin SHALL return code `advisor_nordic_conventions_dhl_freight_sweden_customs_mode_missing` at level `warning`, stating that DHL requires customs handling (standard or full service), an own declaration, or a joint declaration to Norway or Switzerland to be selected for such destinations and naming the connector options that select them.
The joint declaration's destinations SHALL be those of the connector README's customs table, Norway and Switzerland, where the manual names Norway only (W, MAN v5.26 §6.8 p.98; S, connector README at 7a2214d, citing product matches to NO and CH).
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

### Requirement: Advisory answering procedures

The plugin SHALL hold, for every advisory classification, the set of procedures whose performance answers it; the set is empty when no out-of-booking procedure answers it, and the plugin SHALL keep the mapping complete over all classifications.
`advisor_nordic_conventions_dhl_freight_sweden_customs_mode_missing`, `advisor_nordic_conventions_dhl_freight_sweden_aland_customs_service_rejected`, and `advisor_nordic_conventions_invoice_type_content_mismatch` SHALL map to the empty set, because their remedy lies inside the booking request, in the connector's customs service options and the `customs.commercial_invoice` flag.
The answering sets SHALL be lane-aware as follows.
`advisor_nordic_conventions_postnord_se_no_digital_invoice` is answered by `commercial_invoice_electronic`.
`advisor_nordic_conventions_postnord_se_postpaket_commercial_invoice` is answered, for Norway, by `customs_declaration_paper_copy` and `commercial_invoice_electronic`, and for other destinations by `customs_declaration_paper_copy` and `commercial_invoice_paper_copy`, resting on the terms' CN23 in two copies and invoice copies with the parcel (FN:103, FN:111, W).
`advisor_nordic_conventions_postnord_se_export_paper_invoice` is answered by `commercial_invoice_paper_copy`.
`advisor_nordic_conventions_postnord_fi_export_invoice` is answered, for Norway, by `commercial_invoice_electronic`, and for other destinations by `commercial_invoice_paper_copy`.
`advisor_nordic_conventions_postnord_dk_export_documents` is answered, for Norway, Switzerland, and Liechtenstein, and Great Britain, by `commercial_invoice_paper_copy`, and for any other destination by `customs_declaration_paper_copy` and `commercial_invoice_paper_copy`, resting on the 1 CN23 and 2 invoices default (FN:144, W).
`advisor_nordic_conventions_dhl_freight_sweden_invoice_copy` is answered by `commercial_invoice_electronic`.
`advisor_nordic_conventions_dhl_freight_sweden_attached_documents` is answered by `customs_documents_attached_outside`.
`advisor_nordic_conventions_dhl_freight_sweden_voec_marking` is answered by `voec_marking_printed`.
`advisor_nordic_conventions_ch_discount_on_invoice`, `advisor_nordic_conventions_zero_value_line`, `advisor_nordic_conventions_dhl_freight_sweden_parcel_connect_not_served`, and `advisor_nordic_conventions_dhl_freight_sweden_parcel_connect_gb_agreement` SHALL map to the empty set, because their remedy lies in the invoice content, the declared values, or the booked product.

#### Scenario: Mapping is complete

- **WHEN** the plugin adds an advisory classification
- **THEN** its answering set is defined, and an omitted entry is a test failure

#### Scenario: Finland to Norway answers electronically

- **WHEN** `advisor_nordic_conventions_postnord_fi_export_invoice` applies to a Norway destination
- **THEN** its answering set is `commercial_invoice_electronic` alone

#### Scenario: Denmark default destination needs both paper procedures

- **WHEN** `advisor_nordic_conventions_postnord_dk_export_documents` applies to a destination other than Norway, Switzerland, Liechtenstein, and Great Britain
- **THEN** its answering set is `customs_declaration_paper_copy` and `commercial_invoice_paper_copy`

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
