# Tasks

## 1. Territory table

- [ ] 1.1 Add `("FR", 97000, 97999)` and `("DK", 3800, 3999)` to `NON_EU_VAT_POSTAL_RANGES`, test-first
- [ ] 1.2 Remove a leading copy of the address's own country code from the postal code in `in_eu_vat_area`, test-first

## 2. DHL product manual v5.26

- [ ] 2.1 Cite manual v5.26 in `sources.py`, move every manual section and page reference to v5.26, restate the Parcel Connect country facts, and update the README footnote in the same commit
- [ ] 2.2 Name the Switzerland alternatives by their v5.26 product names in the `parcel_connect_not_served` message, test-first
- [ ] 2.3 Add the connector's 112 SE to GB rejection evidence as a source of `parcel_connect_gb_agreement`, test-first, with its README Sources cell and footnote

## 3. Verification

- [ ] 3.1 Run `python -m unittest discover -f tests`, the `AGENTS.md` verification commands, and `openspec validate dhl-manual-v5-26-and-territory-gaps --strict`
- [ ] 3.2 Archive this change after the parallel connector change lands, so the parity cross-check sees identical tables
