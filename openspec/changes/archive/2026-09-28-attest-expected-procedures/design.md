# Design

## Context

The plugin registers ten advisor functions through `PluginMetadata.shipment_advisors`; karrio's `run_advisors` calls each advisor independently with its own deep copy of the request and an `AdvisorContext`, and concatenates the results (`karrio/references.py`, `karrio/core/advisors.py` in the fork).
The advisor contract therefore offers no plugin-side aggregation point: no advisor can see another advisor's messages, so answering and conflict logic must live inside individual advisor entries.
The request carries no per-request `config` field; the per-request dictionaries that reach an advisor are `options` and `metadata`, and `AdvisorContext.config` is the carrier connection's config, which is per-connection rather than per-shipment.
Every rule funnels through `lanes.lane_of(request, context)` as the single scope gate and emits messages through the `advisory()` factory in `rules/__init__.py`, with `codes.AdvisoryClassification` as the consumer-facing code enum.
The Postpaket Utrikes terms settle the CN23 question before this design: the CN23 travels with the parcel in two copies alongside the invoice copies (FN:103, FN:111, W), so a paper customs-declaration procedure answers it.

## Goals / Non-Goals

**Goals:**

- Let a consumer silence exactly the advisories its own out-of-booking procedures genuinely answer, per shipment, with claims the plugin checks against the conventions that govern the lane.
- Expose the conventions' expected procedures as a pure function consumers can call before booking, derived from the same rules as the advisories.
- Keep the ten rule functions byte-identical and all existing tests passing unchanged.

**Non-Goals:**

- Per-organisation or connection-level attestation defaults; claims are per-shipment only.
- Suppression by advisory-code list; a claim maps to procedures, never to codes.
- Contradiction detection beyond what sources state explicitly; inference-based conflicts are out of scope.
- Changing any advisory's level or text when an attestation partially covers it; partial coverage omits nothing.
- Advising at rating time, including for attestations and expected procedures.

## Decisions

### Attestations ride flat boolean shipment options
One option key per procedure, `nordic_conventions_<procedure>`, value `true`.
This is the only per-shipment channel the advisor contract provides, and flat boolean keys are the karrio-idiomatic options form.
Alternative rejected: `AdvisorContext.config` is per-connection, which conflicts with per-shipment scope; a single list-valued option key is un-idiomatic for karrio shipment options and gives per-key typos no visible failure.

### Parsing is strict boolean identity, not karrio option enums
A claim exists only when `value is True`.
`lib.to_shipping_options` and `OptionEnum` treat the string `"false"` as set, a quirk the DHL customs-option tests already document; reusing that machinery would turn a mistyped JSON string into a compliance claim.
The parser is a total function: any value shape yields a claim or no claim, never an exception, because the advisor contract turns exceptions into `shipment_advisor_failed` warnings.

### A resolver wrapper plus a dedicated conflict advisor, rules untouched
`__init__.py` composes `ADVISORS = [with_attestations(rule) for rule in RAW_RULES] + [attestation_conflicts]`.
`with_attestations` wraps one rule: it runs the rule unchanged, then keeps each emitted message unless the message's answering set is non-empty and fully covered by effective attestations, where effective means attested minus contradicted on the lane.
`attestation_conflicts` is a separate advisor that emits one `nordic_conventions_attestation_conflict` warning per contradicted claim; separation guarantees the conflict is emitted exactly once, which per-rule emission could not.
Alternative rejected: parsing attestations into `Lane` and consulting them inside each rule distributes the answering and conflict logic across ten rules, touches every rule file and test, and duplicates the invalid-answers-nothing invariant; a cross-advisor post-pass is impossible under the contract, as noted in Context.

### One lane-aware answering map, completeness-tested
`procedures.py` defines `Procedure` and a mapping from `AdvisoryClassification` to its answering set, lane-aware for the three advisories whose remedy differs by destination, exactly as the spec delta states.
Every classification has an entry, empty for the two un-attestable ones, and a test fails if a classification lacks one, so a future advisory cannot ship without deciding its attestation story.
The map lives centrally rather than beside each rule because the conflict advisor and `expected_procedures` read the same map; one location keeps the three consumers in step.

### Contradictions are source-explicit only
The contradiction table maps a procedure to lane predicates; in this change it holds exactly one entry: `commercial_invoice_paper_copy` on a PostNord Sweden-to-Norway lane, where the sources state the invoice is required digitally and not on paper with the parcel (FN:118, FN:142, W).
PostNord Finland's Norway rule requires the invoice electronically before the shipment but does not state that paper is rejected, so it is not a contradiction; a paper attestation there simply covers nothing.
This keeps every emitted conflict traceable to a cited source, mirroring the plugin's evidence discipline.

### `expected_procedures` runs the raw rules
`procedures.expected_procedures(request, context)` gates on `lanes.lane_of`, calls the ten unwrapped rule functions, and unions the answering sets of the messages they emit.
The function therefore cannot disagree with the advisories, because it is the advisories: no lane predicate is duplicated.
It accepts the same `(request, context)` pair an advisor receives, so a pre-booking consumer constructs a `models.ShipmentRequest` and an `advisors.AdvisorContext` with `operation="shipping"` and its carrier identity.
The symbol is exported from the package root alongside `ADVISORS` and `METADATA`.

### The conflict code joins the classification enum
`nordic_conventions_attestation_conflict` is added to `AdvisoryClassification` and follows the namespace rule; codes are public contract and the addition is non-breaking.
Its `details` carry the attested procedure, the lane, and the contradicting convention's `sources`, matching the advisory shape requirement.

## Risks / Trade-offs

- [Risk] A consumer attests a procedure and then fails to perform it, losing the reminder the advisory would have given.
  → Mitigation: the README compliance section states that attestations are the consumer's own commitment and the plugin checks claims against conventions, not against the consumer's warehouse; the conflict advisory covers the cases the conventions themselves reject.
- [Risk] The answering map drifts from the advisory texts as either evolves.
  → Mitigation: the completeness test pins every classification, and scenario tests tie the destination-aware entries to fixture lanes, so a text or trigger change that breaks an entry fails tests.
- [Risk] A mistyped `nordic_conventions_` option key silently fails to attest, leaving an advisory the consumer expected gone.
  → Mitigation: conservative by design, the advisory stays; the README documents the exact keys and the ignore rule.
- [Risk] Wrapping every rule recomputes `lane_of` and the attestation parse per rule under `run_advisors`, adding per-booking cost.
  → Mitigation: each rule already computes `lane_of` today and the parse is five dictionary lookups; the cost is negligible against ten rules' existing work.

## Migration Plan

Ship as an additive minor version bump.
No data or API migration: no existing option key, code, level, or text changes; consumers who set no `nordic_conventions_*` options see byte-identical advisory output.
Rollback is pinning or uninstalling the previous version; attestations leave no persisted state beyond ordinary shipment options.

## Open Questions

None.
The CN23 remedy is resolved from the terms (FN:103, FN:111, W) and the contradiction scope is a recorded decision, not a deferral.
