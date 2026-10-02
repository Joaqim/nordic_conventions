# Tasks

## 1. Advisories

- [ ] 1.1 Add the four codes, the sources, `rules/customs_values.py`, the two Parcel Connect rules, and their registration with empty answering sets, test-first
- [ ] 1.2 Correct the `PNS_PARCEL_CUSTOMS_INVOICE` citation and state the implementation commit in `sources.py` and the main specification's purpose

## 2. Documentation

- [ ] 2.1 Update the README matrix, reference rows, codes list, footnotes, and the VOEC note, and allow `Switzerland` as a Destinations value in `AGENTS.md`; run the AGENTS.md verification commands

## 3. Verification and archive

- [ ] 3.1 Run `python -m unittest discover -f tests`, validate this change with `openspec validate add-customs-value-advisories --strict`, and archive it
