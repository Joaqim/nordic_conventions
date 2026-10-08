# Tasks

## 1. Territory codes

- [x] 1.1 Copy the connector's `TERRITORY_PARENTS` into `lanes.py` as `DHL_TERRITORY_PARENTS`, with a cross-check test against the connector that is skipped when it is not importable, test-first
- [x] 1.2 Map DHL Freight Sweden shipper and recipient country codes in `lane_of` before the scope checks, and in `dhl_lane_served`, test-first: `XI` `BT` out of scope, 109 to `AX` not warned, `JE` reads as `GB` for the reminder fee, the agreement, and 107, PostNord unchanged

## 2. Customs-mode message

- [x] 2.1 Name the joint declaration to Norway or Switzerland in the customs-mode message, test-first
- [x] 2.3 Copy the connector's `JOINT_DECLARATION_COUNTRIES` into `lanes.py` with a cross-check test and name its countries in the customs-mode message
- [x] 2.2 Give Åland recipients a customs-mode message without standard and full service, citing the connector's Åland evidence, test-first (superseded by 3.1)

## 3. Decisions of 2026-10-08

- [x] 3.1 Return no customs-mode advisory to Åland, and add `advisor_nordic_conventions_dhl_freight_sweden_aland_customs_service_rejected` for standard or full service to Åland, without the joint declaration, test-first
- [x] 3.2 Copy the connector's excluded postal codes into `exclusions.py` with a cross-check test, warn excluded postcodes as not served, and skip the Great Britain agreement for them, test-first
- [x] 3.3 Update the README rows, Codes list, matrix, and footnotes for 3.1 and 3.2

- [x] 3.4 Copy the connector's `TERRITORY_POSTAL_CODES` into `lanes.py` with a cross-check test, add `advisor_nordic_conventions_dhl_freight_sweden_territory_postal_code_mismatch` for a recipient territory code outside its territory, and update the README, test-first

## 4. Documentation

- [x] 4.1 Update the README advisory rows, the Requirements at a glance matrix, the scope text, and the footnotes for the new sources

## 5. Verification

- [ ] 5.1 Run `python -m unittest discover -s tests`, the parity suite with `PYTHONPATH=../karrio-dhl-freight-sweden`, the `AGENTS.md` verification commands, and `openspec validate connector-territory-alignment --strict`
- [ ] 5.2 Run the connector's offline tests and `pyright` to confirm the connector is unchanged
