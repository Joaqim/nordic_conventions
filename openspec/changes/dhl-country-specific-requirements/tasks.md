# Tasks

## 1. Spec and vocabulary groundwork

- [x] 1.1 Edit `openspec/specs/plugins/advisor-nordic-conventions/spec.md` directly: rewrite the Purpose paragraph to drop "sending goods outside the EU VAT area" in favor of destination scope living in each advisory's requirement, and add the CSR shorthand (DHL Freight "Country-specific shipping requirements (English)", dhl.com European road and rail help center, accessed 2026-10-09) to the source-reference paragraph; verify `openspec validate dhl-country-specific-requirements --strict` still passes and the paragraphs read correctly.
- [x] 1.2 Extend the Destinations vocabulary sentence in `AGENTS.md` with the six named countries (Cyprus, Greece, Poland, Romania, Spain, Hungary); verify by grepping `AGENTS.md` for the extended list and confirming the README-sync rules still parse as one sentence.

## 2. Codes and sources

- [x] 2.1 Test-first: extend `tests/advisor_nordic_conventions/test_codes.py` to expect the six new codes (`dhl_freight_sweden_cyprus_documents`, `dhl_freight_sweden_greek_tax_ids`, `dhl_freight_sweden_sent_information`, `dhl_freight_sweden_uit_information`, `dhl_freight_sweden_ekaer_information`, `dhl_freight_sweden_spain_dg_documents`), watch it fail, then add them to `karrio/plugins/advisor_nordic_conventions/codes.py`; verify `test_codes.py` passes.
- [x] 2.2 Add `DHL_CSR_URL` to `sources.py` in the `DHL_MAN_URL` annotation style (page URL, document name, accessed 2026-10-09) plus the `Source` objects the six rules cite (CSR for Cyprus and Spain, CSR plus the manual's product tables for Greece, the connector tables for the product sets and threshold); verify `test_sources.py` passes and every new `Source` is cited by a rule or test.

## 3. Lane gate

- [x] 3.1 Test-first: add `test_lanes.py` cases asserting that the country gate yields a lane for SE to each of CY, GR, PL, RO, ES, HU while `lane_of` still returns none for the same addresses, watch them fail, then add the EU-admitting country gate to `karrio/plugins/advisor_nordic_conventions/lanes.py`; verify `test_lanes.py` passes and no existing lane test changes.

## 4. Country requirement rules

- [x] 4.1 Create `karrio/plugins/advisor_nordic_conventions/rules/dhl_country_requirements.py` with the shared helpers (copied product sets, kg weight sum, private-individual test) and the Cyprus rule, registered in the rules aggregation; test-first with the three delta scenarios (business recipient omits the ID sentence, private recipient includes it, Greece receives no Cyprus code) using a new CY fixture address; verify the new test class passes.
- [x] 4.2 Add the Greece rule (party tax id presence on the `PARTY_TAX_ID_PRODUCTS` copy, naming missing parties and the `EL000000000` fallback); test-first with the three delta scenarios, including product 205 outside the set; verify with a GR-mainland fixture.
- [x] 4.3 Add the SENT rule (info reminder on PL lanes for the transport declaration product set copy); test-first with the three delta scenarios, including a SENT-option-set shipment still receiving the reminder; verify with a PL fixture.
- [x] 4.4 Add the UIT rule (warning at or above, info below, the summed-kg threshold); test-first with the three delta scenarios at exactly 500 kg and 100 kg, including a product outside the set; verify with an RO fixture and a multi-parcel LB-weight case proving unit normalization.
- [x] 4.5 Add the EKAER rule mirroring UIT for HU; test-first with the three delta scenarios; verify with an HU fixture.
- [x] 4.6 Add the Spain rule (`dangerous_good` option on ES lanes); test-first with the three delta scenarios, pinning the universal option key; verify with a mainland-ES fixture (the existing ES entries are Canary Islands territory variants).
- [x] 4.7 Add parity tests comparing the copied product sets and the 500 kg limit against the connector's `units.py` via importlib, skipping when the connector is not importable; verify they pass with `PYTHONPATH` pointing at the connector and skip cleanly without it.

## 5. README sync

- [x] 5.1 Add the six Codes list entries, the six Advisory reference rows under the DHL Freight Sweden from Sweden group (Destinations cells naming the country, Level cells stating the conditional UIT/EKAER split briefly, Trigger and Sources cells per the AGENTS.md rules, CSR footnote), and rewrite the "EU destinations, Northern Ireland included, need nothing" sentence to name the six countries and link their advisories; verify the four AGENTS.md diff and `comm` commands produce no output and the test suite still passes.

## 6. Integration verification

- [x] 6.1 Run the full local suite: `.venv/bin/python -m unittest discover -s tests` from the advisor repo root; verify it passes.
- [x] 6.2 Run the parity suite: `PYTHONPATH=../karrio-dhl-freight-sweden .venv/bin/python -m unittest discover -s tests`; verify it passes with the connector importable.
- [x] 6.3 Run `openspec validate dhl-country-specific-requirements --strict` and the AGENTS.md verification commands end to end; verify both are clean.
