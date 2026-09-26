# Tasks

Karrio-fork tasks live in `/home/joaqim/projects/karrio`; plugin tasks live in this repository.
Follow the design's landing order: groups 1 and 2 land in the fork first, then group 3 merges here.

## 1. Facts note (karrio `docs-openspec`)

- [x] 1.1 Append the Skatteverket quotation ("Nordirland räknas som ett EU-land vid varuhandel med andra EU-länder …") and GOV.UK VAT Notice 725 as corroboration of the Northern Ireland row in the territories section of `docs/notes/customs/nordic-trade-documents-facts.md`, keeping numbering append-only, and verify with `rg -n "Nordirland" docs/notes/customs/nordic-trade-documents-facts.md` that the existing FN:58-65 lines are unchanged and the new lines follow the last existing line

## 2. Connectors (karrio feature branch `fix-eu-vat-area-territories`)

- [x] 2.1 Branch `fix-postnord-eu-vat-territories` from `feat-postnord-customs-invoice` per `docs/notes/workflow/develop-assembly.md` and update the PostNord connector's `units.py`: append `"MC"` beside `"GR"` in `EU_VAT_AREA_COUNTRIES`, add `("GR", 63086, 63086)` to `NON_EU_VAT_POSTAL_RANGES`, add `EU_VAT_POSTAL_PREFIXES` with `("GB", "BT")`, and extend `in_eu_vat_area` with the upper-cased prefix disjunct, and verify the connector's unit tests pass together with new cases: `MC` inside, `GR` `630 86` outside, `GB` `BT1 1AA` inside, `GB` `EC1A 1BB` outside
- [x] 2.2 Branch `fix-dhl-freight-se-eu-vat-territories` from `feat-dhl-freight-se-customs` and apply the same four changes to the DHL Freight Sweden connector's `units.py`, and verify its unit tests pass with the same four cases
- [x] 2.3 Update the PNS requirement ("Customs is omitted within the EU VAT area", `openspec/specs/postnord/customs-declaration/spec.md`) and the DFS requirement ("Customs information is omitted within the EU VAT area", `openspec/specs/dhl-freight-sweden/customs/spec.md`) on `docs-openspec` to state the three territories and cite the new FN lines, and verify with `openspec validate` in the karrio repository
- [x] 2.4 Register both branches in `BRANCHES` in `assemble-develop.sh` on `docs-openspec` and regenerate `develop` with `rebuild-develop.sh`, and verify the regenerated `develop` contains both connector changes and its test suite passes

## 3. Plugin territory table (this repository, branch `tullverket-vat-territory-alignment`)

- [x] 3.1 Update `karrio/plugins/nordic_conventions/territories.py`: add `"MC"` to `EU_VAT_AREA_COUNTRIES`, add `("GR", 63086, 63086)` to `NON_EU_VAT_POSTAL_RANGES`, add `EU_VAT_POSTAL_PREFIXES` with `("GB", "BT")`, extend `in_eu_vat_area` with the prefix disjunct on the space-stripped upper-cased postal code, and state the Northern Ireland goods-movement caveat in the module docstring, and verify `python -m unittest tests.nordic_conventions.test_territories -v` passes with the existing cases before the new tests land
- [ ] 3.2 Extend `tests/nordic_conventions/test_territories.py` with the spec's scenarios (Mount Athos `630 86` outside, `MC` inside, `FR` `98000` inside, `GB` `BT1 1AA` inside, `GB` `EC1A 1BB` outside) and extend `test_matches_connector_tables` to assert tuple equality of `EU_VAT_POSTAL_PREFIXES`, and verify `python -m unittest discover -v -f tests` from the repository root inside the karrio `develop` dev shell
- [ ] 3.3 Update the README: drop the non-goal sentence that Monaco, Northern Ireland, and Mount Athos follow the connectors' treatment and state the Tullverket goods-movement alignment instead, and verify the sentence against the modified requirement in `specs/plugins/nordic-conventions/spec.md`

## 4. Integration checks

- [ ] 4.1 Run the full plugin suite against the regenerated karrio `develop` (both connectors importable) and verify every test passes with no cross-check skips, confirming all three territory tables are equal
- [ ] 4.2 Verify `openspec validate tullverket-vat-territory-alignment --strict` passes and the change is ready for review
