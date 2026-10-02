# Proposal

## Why

A consumer shipping DAP merchandise from Sweden to Norway, Switzerland, and the United Kingdom declares a free promotional item as a 100%-discounted line of the sale and relies on this plugin as the convention authority for merchandise sent outside the EU VAT area.
Research on 2026-10-02 verified carrier and authority sources on declared values that no advisory relays today: the Swiss treatment of discounts and add-ons (BAZG Richtlinie R-69-03 §5.5.3), the rule that an invoice value is never 0 (PostNord's page on parcels to Norway, Tullverket's page on supporting documents for export, DHL Express's customs guidelines), and the countries DHL Freight Sweden's Parcel Connect family serves, Great Britain only by separate agreement (product manual v5.23).

## What Changes

- Adds `nordic_conventions_ch_discount_on_invoice` at level `info`: a discounted or zero-valued commodity on a shipment to Switzerland, reminding that the invoice shows the discount and ties the item to the sale.
- Adds `nordic_conventions_zero_value_line` at level `warning`: a commodity with a customs value of 0 or none on any shipment the plugin advises on.
- Adds `nordic_conventions_dhl_freight_sweden_parcel_connect_not_served` at level `warning`: Parcel Connect (109), Parcel Connect Plus (112), or Parcel Return Connect (107) booked to Switzerland, or Parcel Return Connect booked to Great Britain, which these products do not serve.
- Adds `nordic_conventions_dhl_freight_sweden_parcel_connect_gb_agreement` at level `warning`: Parcel Connect (109) or Parcel Connect Plus (112) booked to Great Britain, which they serve only by separate agreement with DHL.
- Maps the four codes to the empty answering set, since their remedy lies in the invoice content, the declared values, or the booked product.
- Records in the README that splitting goods sold as one unit into separately packed consignments to Norway under VOEC is prohibited, and why the plugin cannot advise it.
- Corrects the citation of the PostNord customs invoice behaviour: PNS at 60312fe2e is the specification text, and the connector code entered the karrio fork's develop as face88f37 through merge 52d21fbfb.

Out of scope: goods-value thresholds (a recorded non-goal), attestations answering the new advisories, and connector changes.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `plugins/nordic-conventions`: four advisory requirements are added, and the answering-procedures requirement maps the new codes to the empty set.

## Impact

`codes.py`, `sources.py`, `rules/customs_values.py` (new), `rules/dhl_freight_sweden.py`, `procedures.py`, tests, `README.md`, `AGENTS.md`, and the main specification.
Advisory codes are public API: four are added and none is renamed.
