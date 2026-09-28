# Design

## Context

See proposal.md for motivation and the recorded gaps.
Source references use the main spec's conventions: FN is the karrio fork's `docs/notes/customs/nordic-trade-documents-facts.md` at commit baf8eb3dd with line numbers and evidence tags, and PNS is the karrio fork's `openspec/specs/postnord/customs-declaration/spec.md` at commit 60312fe2e.
The main spec already records deferrals inside the requirement they border, for example "Non-commercial Postpaket Utrikes above SEK 2 000 is deferred with the other value thresholds" in the commercial Postpaket Utrikes requirement and the DKK 7 500 deferral in the PostNord Denmark requirement.

## Goals / Non-Goals

Goals: each gap recorded in the requirement whose scope it borders, with its sources, so a reader of that requirement sees what the requirement does not cover.
Non-goals: any change to a normative SHALL statement, advisory code, level, message text, or scenario outcome; any code or test change.

## Decisions

### Recorded gaps are prose in the bordering requirement

Each gap is a sentence prefixed "Recorded gap, not addressed:" in a MODIFIED requirement, following the existing inline deferral sentences.
Alternative considered: a new requirement listing all gaps; rejected because a requirement must state required behaviour, and these gaps state the absence of behaviour.
Alternative considered: a README non-goals entry; not chosen in this change because the README non-goals describe deliberate scope, while these gaps are undecided.

### The gift scenario states the CN23 duty

The scenario "Gift Postpaket Utrikes is not advised" keeps its outcome and gains a clause stating that PostNord requires the CN23 for that shipment at every value, so the scenario does not read as a statement that no duty exists.

### The maintenance note stays in the proposal

Line-number drift in `sources.py` and `lanes.py` concerns code citations, not behaviour, so it is recorded in proposal.md and not in the spec.

## Risks / Trade-offs

[Recorded gaps read as commitments to fix] → Each sentence says "not addressed", and the proposal states that no fix is designed.
[Connector line citations drift again] → The connector cross-check test guards set membership; the citations carry their commit.
