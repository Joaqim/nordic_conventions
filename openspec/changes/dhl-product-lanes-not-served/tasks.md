# Tasks

## 1. Product lanes

- [x] 1.1 Copy the connector's product lanes, citations, and unified names into `lanes.py`, with a cross-check test against the connector that is skipped when it is not importable, test-first
- [ ] 1.2 Widen `parcel_connect_not_served` to every product and lane outside the copied table, with the new message and manual source, test-first
- [ ] 1.3 Update the README advisory row, Codes list, and Requirements at a glance matrix

## 2. Verification

- [ ] 2.1 Run `python -m unittest discover -s tests`, the parity suite with `PYTHONPATH=../karrio-dhl-freight-sweden`, the `AGENTS.md` verification commands, and `openspec validate dhl-product-lanes-not-served --strict`
