# Spec Delta

## ADDED Requirements

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

- **WHEN** a DHL Freight Sweden `dhl_freight_sweden_parcel_connect_plus` shipment from Sweden to `JE` with postal code JE2 3AB is created
- **THEN** the plugin returns code `advisor_nordic_conventions_dhl_freight_sweden_parcel_connect_gb_agreement`, and code `advisor_nordic_conventions_dhl_freight_sweden_invoice_copy` with a reminder fee of 650 kr

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
For a recipient in Åland, `FI` with a postal code normalised as in "The EU VAT area follows Tullverket for goods" in 22000-22999 after the territory mapping, the message SHALL instead state that DHL rejects customs handling standard and full service to Åland with 24003 and that the connector refuses both, and SHALL name the own declaration, the joint declaration, or customs data sent without a customs service as the bookings the connector accepts; `details` SHALL add the connector's Åland evidence (S, connector `docs/concepts/destinations.md` "Åland" at 7a2214d, rejections 24003 for 112 with full service and with Standard, and booking 2906762592 of 109 with customs data and no customs service).

#### Scenario: No customs option to Norway

- **WHEN** a DHL Freight Sweden shipment from Sweden to Norway is created without any customs service option
- **THEN** the plugin returns code `advisor_nordic_conventions_dhl_freight_sweden_customs_mode_missing` at level `warning`, naming the joint declaration to Norway or Switzerland and its option `dhl_freight_sweden_customs_joint_declaration`

#### Scenario: Selected customs option silences the advisory

- **WHEN** a DHL Freight Sweden shipment from Sweden to Norway is created with the full-service customs handling option set
- **THEN** the plugin does not return code `advisor_nordic_conventions_dhl_freight_sweden_customs_mode_missing`

#### Scenario: No customs option to Åland

- **WHEN** a DHL Freight Sweden shipment from Sweden to `FI` with postal code 22100, or to `AX` with postal code AX-22100, is created without any customs service option
- **THEN** the plugin returns code `advisor_nordic_conventions_dhl_freight_sweden_customs_mode_missing` at level `warning` whose message does not suggest `dhl_freight_sweden_customs_handling_standard` or `dhl_freight_sweden_customs_handling_full_service`

### Requirement: DHL Freight Sweden products are not booked on lanes they do not serve

For a DHL Freight Sweden shipment from Sweden booked, by unified name or carrier code, as a product whose "Valid countries" table in the DHL Freight Sweden product manual v5.26 allows no lane from the shipper's country to the recipient's country, the plugin SHALL return code `advisor_nordic_conventions_dhl_freight_sweden_parcel_connect_not_served` at level `warning`.
The lanes SHALL be those of the DHL Freight Sweden connector's `PRODUCT_LANES` table, copied into the plugin and checked against the connector by a test that runs when the connector is importable: the domestic products 102, 103, 104, 118, 209, 210, 211, 212, 401, 402, and 502 within Sweden; Parcel Connect (109) and Parcel Connect Plus (112) from Sweden to their listed countries; Parcel Return Connect (107) from its listed countries to Sweden; and Road Freight Standard (202), Road Freight Direct (205), Road Freight Priority (233), Standard Pallet International (SPI), and Home Delivery International B2C (601) from Sweden to their listed countries and from them to Sweden.
Country codes SHALL be compared after the territory mapping of "DHL Freight Sweden territory codes are read as their parent country", in the message as well.
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

#### Scenario: Parcel Return Connect to Jersey reads as Great Britain

- **WHEN** a DHL Freight Sweden `107` shipment from Sweden to `JE` with postal code JE2 3AB is created
- **THEN** the plugin returns code `advisor_nordic_conventions_dhl_freight_sweden_parcel_connect_not_served` at level `warning`, and the message states that 107 does not ship from SE to GB
