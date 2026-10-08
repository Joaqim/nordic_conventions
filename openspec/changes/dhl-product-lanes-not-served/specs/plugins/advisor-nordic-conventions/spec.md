# Spec Delta

## RENAMED Requirements

- FROM: `### Requirement: DHL Freight Sweden Parcel Connect is not booked where it does not serve`
- TO: `### Requirement: DHL Freight Sweden products are not booked on lanes they do not serve`

## MODIFIED Requirements

### Requirement: DHL Freight Sweden products are not booked on lanes they do not serve

For a DHL Freight Sweden shipment from Sweden booked, by unified name or carrier code, as a product whose "Valid countries" table in the DHL Freight Sweden product manual v5.26 allows no lane from the shipper's country to the recipient's country, the plugin SHALL return code `advisor_nordic_conventions_dhl_freight_sweden_parcel_connect_not_served` at level `warning`.
The lanes SHALL be those of the DHL Freight Sweden connector's `PRODUCT_LANES` table, copied into the plugin and checked against the connector by a test that runs when the connector is importable: the domestic products 102, 103, 104, 118, 209, 210, 211, 212, 401, 402, and 502 within Sweden; Parcel Connect (109) and Parcel Connect Plus (112) from Sweden to their listed countries; Parcel Return Connect (107) from its listed countries to Sweden; and Road Freight Standard (202), Road Freight Direct (205), Road Freight Priority (233), Standard Pallet International (SPI), and Home Delivery International B2C (601) from Sweden to their listed countries and from them to Sweden.
Country codes SHALL be compared as given.
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
