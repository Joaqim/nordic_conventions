# Tasks

## 1. Procedures core

- [x] 1.1 Add `karrio/plugins/nordic_conventions/procedures.py` with the `Procedure` enum of the five members whose values are the option-key suffixes, and verify a new `tests/nordic_conventions/test_procedures.py` case asserting the five members and their option-key spellings passes
- [x] 1.2 Add the lane-aware answering map over all ten `AdvisoryClassification` members with the two empty entries, and verify a completeness test asserting the map covers every classification exactly passes
- [x] 1.3 Add `expected_procedures(request, context)` deriving its result from the unwrapped rules, and verify test cases for a PostNord SE parcel to a non-Norway destination, a PostNord SE postpaket to Norway, and an intra-EU shipment pass
- [x] 1.4 Export `Procedure` and `expected_procedures` from the package `__init__` when the hook is available, and verify an import test `from karrio.plugins.nordic_conventions import expected_procedures` passes

## 2. Attestation resolver

- [x] 2.1 Add `karrio/plugins/nordic_conventions/attestations.py` with `parse(request)` counting only boolean `true` as a claim and ignoring unknown `nordic_conventions_` keys, and verify tests covering boolean true, boolean false, the string `"false"`, and an unknown key pass
- [x] 2.2 Add the contradiction table with the single PostNord Sweden-to-Norway predicate for `commercial_invoice_paper_copy`, and verify tests pass for a contradicting Norway lane, a non-contradicting Sweden lane, and a Finland-to-Norway lane that does not contradict
- [x] 2.3 Add `with_attestations(rule)` dropping a message only on full coverage by effective attestations, and verify tests pass for full coverage dropping the advisory, partial coverage keeping it unchanged, and a contradicted attestation keeping it
- [x] 2.4 Add the `attestation_conflicts` advisor emitting one warning per contradicted claim with the convention's sources in `details`, and verify tests pass asserting the code, the level, the named procedure, and silence when nothing contradicts

## 3. Composition and code

- [x] 3.1 Add `attestation_conflict` to `AdvisoryClassification` following the namespace rule, and verify the codes enumeration test covers eleven classifications
- [x] 3.2 Recompose `ADVISORS` as wrapped rules plus the conflict advisor in `__init__.py`, and verify `test_plugin.py` end-to-end cases pass: an attested option removes the answered advisory through `run_advisors`, a contradicted attestation yields the original advisory plus the conflict, and a request with no `nordic_conventions_*` options yields byte-identical output to the unwrapped rules

## 4. Documentation and release

- [ ] 4.1 Update `README.md` with the attestation options table, the `nordic_conventions_attestation_conflict` row in the code table, a utilities section showing the `expected_procedures` import, and the reworded non-goal line, and verify every key, code, and symbol in the README matches the implementation
- [ ] 4.2 Bump the package version and verify `python -m unittest discover -v -f tests` is green and `openspec validate attest-expected-procedures --strict` passes
