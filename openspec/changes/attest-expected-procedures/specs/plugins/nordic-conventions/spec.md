# Spec Delta

## ADDED Requirements

### Requirement: Per-shipment procedure attestations
The plugin SHALL accept five shipment options in the request options dictionary, each naming one out-of-booking procedure: `nordic_conventions_commercial_invoice_paper_copy`, `nordic_conventions_customs_declaration_paper_copy`, `nordic_conventions_customs_documents_attached_outside`, `nordic_conventions_commercial_invoice_electronic`, and `nordic_conventions_voec_marking_printed`.
An option SHALL count as an attestation only when its value is the boolean `true`; absent, `false`, or any other value, including the string `"false"`, SHALL count as no claim.
An option in the `nordic_conventions_` namespace that the plugin does not define SHALL be ignored, with no message and no change to any advisory.
The procedures SHALL mean: a printed commercial invoice travelling with the parcel; a printed customs declaration, CN22 or CN23, travelling with the parcel; copies of the customs documents attached on the outside of the package; a commercial invoice transmitted electronically outside the booking; and the VOEC ID printed on the package or label.

#### Scenario: Boolean true attests
- **WHEN** an attestation option's value is the boolean `true`
- **THEN** the shipment carries the claim to perform that procedure

#### Scenario: String false is no claim
- **WHEN** an attestation option's value is the string `"false"`
- **THEN** the shipment carries no claim, unlike karrio carrier-option parsing where a string `"false"` counts as set

#### Scenario: Unknown namespaced option is ignored
- **WHEN** the options carry a `nordic_conventions_` key the plugin does not define
- **THEN** the key is ignored and every advisory is returned exactly as without it

### Requirement: Advisory answering procedures
The plugin SHALL hold, for every advisory classification, the set of procedures whose performance answers it; the set is empty when no out-of-booking procedure answers it, and the plugin SHALL keep the mapping complete over all classifications.
`nordic_conventions_dhl_freight_sweden_customs_mode_missing` and `nordic_conventions_invoice_type_content_mismatch` SHALL map to the empty set, because their remedy lies inside the booking request, in the connector's customs service options and the `customs.commercial_invoice` flag.
The answering sets SHALL be lane-aware as follows.
`nordic_conventions_postnord_se_no_digital_invoice` is answered by `commercial_invoice_electronic`.
`nordic_conventions_postnord_se_postpaket_commercial_invoice` is answered, for Norway, by `customs_declaration_paper_copy` and `commercial_invoice_electronic`, and for other destinations by `customs_declaration_paper_copy` and `commercial_invoice_paper_copy`, resting on the terms' CN23 in two copies and invoice copies with the parcel (FN:103, FN:111, W).
`nordic_conventions_postnord_se_export_paper_invoice` is answered by `commercial_invoice_paper_copy`.
`nordic_conventions_postnord_fi_export_invoice` is answered, for Norway, by `commercial_invoice_electronic`, and for other destinations by `commercial_invoice_paper_copy`.
`nordic_conventions_postnord_dk_export_documents` is answered, for Norway, Switzerland, and Liechtenstein, and Great Britain, by `commercial_invoice_paper_copy`, and for any other destination by `customs_declaration_paper_copy` and `commercial_invoice_paper_copy`, resting on the 1 CN23 and 2 invoices default (FN:144, W).
`nordic_conventions_dhl_freight_sweden_invoice_copy` is answered by `commercial_invoice_electronic`.
`nordic_conventions_dhl_freight_sweden_attached_documents` is answered by `customs_documents_attached_outside`.
`nordic_conventions_dhl_freight_sweden_voec_marking` is answered by `voec_marking_printed`.

#### Scenario: Mapping is complete
- **WHEN** the plugin adds an advisory classification
- **THEN** its answering set is defined, and an omitted entry is a test failure

#### Scenario: Finland to Norway answers electronically
- **WHEN** `nordic_conventions_postnord_fi_export_invoice` applies to a Norway destination
- **THEN** its answering set is `commercial_invoice_electronic` alone

#### Scenario: Denmark default destination needs both paper procedures
- **WHEN** `nordic_conventions_postnord_dk_export_documents` applies to a destination other than Norway, Switzerland, Liechtenstein, and Great Britain
- **THEN** its answering set is `customs_declaration_paper_copy` and `commercial_invoice_paper_copy`

### Requirement: Answered advisories are omitted
This requirement qualifies every requirement stating that an advisory SHALL be returned.
An advisory SHALL be omitted when its answering set is non-empty and every procedure in the set is covered by an attestation that holds on the lane.
An attestation contradicted on the lane SHALL cover nothing, and partial coverage SHALL omit nothing.

#### Scenario: Full coverage omits the advisory
- **WHEN** every procedure in an advisory's answering set is attested and no attestation is contradicted
- **THEN** the advisory is not returned

#### Scenario: Partial coverage omits nothing
- **WHEN** only some procedures in an advisory's answering set are attested
- **THEN** the advisory is returned, unchanged in level and text

#### Scenario: Contradicted attestation covers nothing
- **WHEN** an attestation covering an answering procedure is contradicted on the lane
- **THEN** the advisory is returned and the conflict advisory is also returned

### Requirement: Contradicted attestations are reported
When an attested procedure is contradicted by the conventions that govern the lane, the plugin SHALL return code `nordic_conventions_attestation_conflict` at level `warning`, once per contradicted attestation, naming the attested procedure and the contradicting convention, with the convention's sources in `details`.
In this change the only contradiction is `nordic_conventions_commercial_invoice_paper_copy` on a PostNord lane from Sweden to Norway, whose sources require the commercial invoice digitally and not on paper with the parcel (FN:118, FN:142, W; PNS lines 28-31, S).

#### Scenario: Paper invoice attested on the Sweden-to-Norway lane
- **WHEN** `nordic_conventions_commercial_invoice_paper_copy` is attested on a PostNord shipment from Sweden to Norway
- **THEN** the conflict warning is returned, naming the digital-only convention and its sources

#### Scenario: No contradiction, no conflict message
- **WHEN** every attestation holds on the lane
- **THEN** the attestations cover their procedures and no conflict advisory is returned

### Requirement: Pre-booking expected procedures
The plugin SHALL expose a public function `expected_procedures` that takes a shipment request and an advisor context and returns the set of procedures the conventions expect for that request.
It SHALL return the empty set outside the plugin's scope, for the rating operation, a carrier or lane out of scope, or a shipment inside the EU VAT area, and otherwise return the union of the answering sets of the advisories that would be returned with no attestations.
It SHALL derive its result from the same rules that produce the advisories, so the function and the advisories cannot disagree.

#### Scenario: PostNord parcel from Sweden expects the paper invoice
- **WHEN** `expected_procedures` evaluates a PostNord parcel request from Sweden to a destination outside the EU VAT area other than Norway
- **THEN** the result includes `commercial_invoice_paper_copy`

#### Scenario: Out-of-scope request expects nothing
- **WHEN** `expected_procedures` evaluates a shipment inside the EU VAT area
- **THEN** the result is the empty set
