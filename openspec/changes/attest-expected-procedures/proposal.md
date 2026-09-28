# Proposal

## Why

The advisories remind consumers of post-booking duties — paper copies with the parcel, electronic transmissions, package markings — that the consumer performs outside the booking, so a consumer who has already arranged a duty still receives the warning and must filter it downstream.
Consumers also rewrite the plugin's lane knowledge outside the advisory flow, for example to show a pre-booking document checklist, with no shared source of truth keeping the two in step.
The archived design of 2026-09-26 named configuration as a possible follow-up; per-shipment attestations are that follow-up, shaped so a claim only silences what it genuinely answers.

## What Changes

- Adds five `nordic_conventions_*` shipment options, one per out-of-booking procedure the conventions expect, that a consumer sets to `true` to attest the procedure will be performed for that shipment.
- Adds an attestation resolver: an advisory is omitted only when its required procedures are fully covered by attestations valid on that lane, and an attestation contradicted by the lane's conventions covers nothing.
- Adds advisory code `nordic_conventions_attestation_conflict` at level `warning`, returned once per contradicted attestation, naming the claim and the contradicting convention with its sources.
- Advisories whose fix lies inside the booking request — the DHL Freight Sweden customs service options and the `customs.commercial_invoice` flag — remain un-attestable by design, so an attestation never replaces correct request data.
- Adds a public `expected_procedures` function returning the procedures the conventions expect for a request and advisor context before any booking, derived from the same rules so advisories and utility cannot drift.
- Rewords the README non-goal line "has no configuration or per-organisation overrides": per-shipment attestations exist, per-organisation overrides remain a non-goal.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `plugins/nordic-conventions`: adds requirements for the attestation options and their strict parsing, the answering and contradiction semantics with the new conflict advisory code, completeness of the advisory-to-procedures mapping, and the public `expected_procedures` function.

## Impact

- Plugin package `karrio/plugins/nordic_conventions/`: new modules `procedures.py` and `attestations.py`; new classification in `codes.py`; `ADVISORS` composition in `__init__.py` gains the resolver wrapper and the conflict advisor; the ten rule functions are unchanged.
- Tests: new `tests/nordic_conventions/test_procedures.py` and `test_attestations.py`; end-to-end attestation cases in `test_plugin.py`; existing rule tests unchanged.
- README: options table, conflict code row, utilities section, reworded non-goals.
- Consumers: additive only — new option keys, one new advisory code, one new importable function; no existing code, level, or text changes.
- No karrio fork changes: the mechanism uses only the existing advisor contract (`request.options` and `AdvisorContext`).
