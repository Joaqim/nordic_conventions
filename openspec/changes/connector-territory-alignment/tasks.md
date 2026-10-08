# Tasks

## 1. Territory codes

- [ ] 1.1 Copy the connector's `TERRITORY_PARENTS` into `lanes.py` as `DHL_TERRITORY_PARENTS`, with a cross-check test against the connector that is skipped when it is not importable, test-first
- [ ] 1.2 Map DHL Freight Sweden shipper and recipient country codes in `lane_of` before the scope checks, and in `dhl_lane_served`, test-first: `XI` `BT` out of scope, 109 to `AX` not warned, `JE` reads as `GB` for the reminder fee, the agreement, and 107, PostNord unchanged

## 2. Customs-mode message

- [ ] 2.1 Name the joint declaration to Norway or Switzerland in the customs-mode message, test-first
- [ ] 2.2 Give Åland recipients a customs-mode message without standard and full service, citing the connector's Åland evidence, test-first

## 3. Documentation

- [ ] 3.1 Update the README advisory rows, the Requirements at a glance matrix, the scope text, and the footnotes for the new sources

## 4. Verification

- [ ] 4.1 Run `python -m unittest discover -s tests`, the parity suite with `PYTHONPATH=../karrio-dhl-freight-sweden`, the `AGENTS.md` verification commands, and `openspec validate connector-territory-alignment --strict`
- [ ] 4.2 Run the connector's offline tests and `pyright` to confirm the connector is unchanged
