# Spec Delta

## ADDED Requirements

### Requirement: Discounted lines to Switzerland are shown on the invoice

For a PostNord or DHL Freight Sweden shipment within the plugin's scope to Switzerland whose customs data contains a commodity with `metadata.discount_percentage` set or with a `value_amount` of 0 or none, the plugin SHALL return code `nordic_conventions_ch_discount_on_invoice` at level `info`.
The message SHALL state that Switzerland does not tax a discount, or an item handed over with a sold item as a discount in kind or add-on, as part of the import consideration, provided the item is directly connected to the sale, and that the commercial invoice shows the discount and ties the discounted or free item to that sale.
`details` SHALL list the zero-based indexes of the triggering commodities under `lines`, cite BAZG Richtlinie R-69-03 §5.5.3 (W), and state under `unconfirmed` that R-69-03 does not address an add-on shipped in a separate parcel from the sale it belongs to.

#### Scenario: Free line in a sale to Switzerland

- **WHEN** a PostNord `postnord_parcel` shipment from Sweden to Switzerland is created with customs data whose second commodity carries `metadata.discount_percentage` 100
- **THEN** the plugin returns code `nordic_conventions_ch_discount_on_invoice` at level `info` with `lines` [1]

#### Scenario: Zero-valued line to Switzerland

- **WHEN** a DHL Freight Sweden shipment from Sweden to Switzerland is created with customs data whose first commodity has a `value_amount` of 0
- **THEN** the plugin returns code `nordic_conventions_ch_discount_on_invoice` with `lines` [0]

#### Scenario: Discounted line to Norway

- **WHEN** a PostNord `postnord_parcel` shipment from Sweden to Norway is created with a commodity carrying `metadata.discount_percentage` 100
- **THEN** the plugin does not return code `nordic_conventions_ch_discount_on_invoice`

#### Scenario: Fully valued lines

- **WHEN** a PostNord `postnord_parcel` shipment from Sweden to Switzerland is created with commodities that all carry a positive value and no discount
- **THEN** the plugin does not return code `nordic_conventions_ch_discount_on_invoice`

### Requirement: Zero-value commodity lines are flagged

For a shipment within the plugin's scope whose customs data contains a commodity with a `value_amount` of 0 or none, the plugin SHALL return code `nordic_conventions_zero_value_line` at level `warning`.
The message SHALL state that a commercial or pro forma invoice may never carry a value of 0, even for gifts or samples, and that each line needs its customs value.
`details` SHALL list the zero-based indexes of the triggering commodities under `lines` and cite PostNord's page on parcels to Norway, Tullverket's page on supporting documents for export, and DHL Express's customs guidelines (all W).

#### Scenario: Zero-valued line to Norway

- **WHEN** a PostNord `postnord_parcel` shipment from Sweden to Norway is created with customs data whose second commodity has a `value_amount` of 0
- **THEN** the plugin returns code `nordic_conventions_zero_value_line` at level `warning` with `lines` [1]

#### Scenario: Line without a value

- **WHEN** a DHL Freight Sweden shipment from Sweden to the United Kingdom is created with a commodity that has no `value_amount`
- **THEN** the plugin returns code `nordic_conventions_zero_value_line`

#### Scenario: Inside the EU VAT area

- **WHEN** a PostNord `postnord_parcel` shipment from Sweden to Germany is created with a zero-valued commodity
- **THEN** the plugin returns no advisory

### Requirement: DHL Freight Sweden Parcel Connect is not booked where it does not serve

For a DHL Freight Sweden shipment from Sweden booked, by unified name or carrier code, as Parcel Connect (`dhl_freight_sweden_parcel_connect_b2c`, `109`), Parcel Connect Plus (`dhl_freight_sweden_parcel_connect_plus`, `112`), or Parcel Return Connect (`dhl_freight_sweden_parcel_return_connect_c2b`, `107`) to Switzerland, or as Parcel Return Connect to Great Britain, the plugin SHALL return code `nordic_conventions_dhl_freight_sweden_parcel_connect_not_served` at level `warning`.
For Switzerland the message SHALL state that these products do not serve Switzerland and name products that serve it: Home Delivery International B2C (601), Euroconnect (202), Euroline (205), and Eurapid (233).
For Great Britain the message SHALL state that Parcel Return Connect (107) does not serve Great Britain.
`details` SHALL cite the DHL Freight Sweden product manual v5.23 (W).

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
`details` SHALL cite the DHL Freight Sweden product manual v5.23 (W).

#### Scenario: Parcel Connect to Great Britain

- **WHEN** a DHL Freight Sweden `dhl_freight_sweden_parcel_connect_b2c` shipment from Sweden to Great Britain is created
- **THEN** the plugin returns code `nordic_conventions_dhl_freight_sweden_parcel_connect_gb_agreement` at level `warning`, and not code `nordic_conventions_dhl_freight_sweden_parcel_connect_not_served`

#### Scenario: Parcel Connect to Switzerland is not an agreement case

- **WHEN** a DHL Freight Sweden `dhl_freight_sweden_parcel_connect_b2c` shipment from Sweden to Switzerland is created
- **THEN** the plugin does not return code `nordic_conventions_dhl_freight_sweden_parcel_connect_gb_agreement`

## MODIFIED Requirements

### Requirement: Advisory answering procedures

The plugin SHALL hold, for every advisory classification, the set of procedures whose performance answers it; the set is empty when no out-of-booking procedure answers it, and the plugin SHALL keep the mapping complete over all classifications.
`nordic_conventions_dhl_freight_sweden_customs_mode_missing` and `nordic_conventions_invoice_type_content_mismatch` SHALL map to the empty set, because their remedy lies inside the booking request, in the connector's customs service options and the `customs.commercial_invoice` flag.
The answering sets SHALL be lane-aware as follows.
`nordic_conventions_postnord_se_no_digital_invoice` is answered by `commercial_invoice_electronic`.
`nordic_conventions_postnord_se_postpaket_commercial_invoice` is answered, for Norway, by `customs_declaration_paper_copy` and `commercial_invoice_electronic`, and for other destinations by `customs_declaration_paper_copy` and `commercial_invoice_paper_copy`, resting on the terms' CN23 in two copies and invoice copies with the parcel (FN:103, FN:111, W).
`nordic_conventions_postnord_se_export_paper_invoice` is answered by `commercial_invoice_paper_copy`.
`nordic_conventions_postnord_fi_export_invoice` is answered, for Norway, by `commercial_invoice_electronic`, and for other destinations by `commercial_invoice_paper_copy`.
`nordic_conventions_postnord_dk_export_documents` is answered, for Norway, Switzerland, and Liechtenstein, and Great Britain, by `commercial_invoice_paper_copy`, and for any other destination by `customs_declaration_paper_copy` and `commercial_invoice_paper_copy`, resting on the 1 CN23 and 2 invoices default (FN:144, W).
`nordic_conventions_dhl_freight_sweden_invoice_copy` is answered by `commercial_invoice_electronic`.
`nordic_conventions_dhl_freight_sweden_attached_documents` is answered by `customs_documents_attached_outside`.
`nordic_conventions_dhl_freight_sweden_voec_marking` is answered by `voec_marking_printed`.
`nordic_conventions_ch_discount_on_invoice`, `nordic_conventions_zero_value_line`, `nordic_conventions_dhl_freight_sweden_parcel_connect_not_served`, and `nordic_conventions_dhl_freight_sweden_parcel_connect_gb_agreement` SHALL map to the empty set, because their remedy lies in the invoice content, the declared values, or the booked product.

#### Scenario: Mapping is complete

- **WHEN** the plugin adds an advisory classification
- **THEN** its answering set is defined, and an omitted entry is a test failure

#### Scenario: Finland to Norway answers electronically

- **WHEN** `nordic_conventions_postnord_fi_export_invoice` applies to a Norway destination
- **THEN** its answering set is `commercial_invoice_electronic` alone

#### Scenario: Denmark default destination needs both paper procedures

- **WHEN** `nordic_conventions_postnord_dk_export_documents` applies to a destination other than Norway, Switzerland, Liechtenstein, and Great Britain
- **THEN** its answering set is `customs_declaration_paper_copy` and `commercial_invoice_paper_copy`
