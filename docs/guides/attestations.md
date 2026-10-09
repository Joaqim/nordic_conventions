---
title: "Attestations"
---

A consumer that has arranged an out-of-booking procedure for a shipment attests it by setting the matching shipment option to the boolean `true`; absent, `false`, and any other value, including the string `"false"`, carry no claim, unlike karrio carrier-option parsing.

| Option | Procedure it attests |
|---|---|
| `advisor_nordic_conventions_commercial_invoice_paper_copy` | a printed commercial invoice travelling with the parcel |
| `advisor_nordic_conventions_customs_declaration_paper_copy` | a printed customs declaration, CN22 or CN23, travelling with the parcel |
| `advisor_nordic_conventions_customs_documents_attached_outside` | copies of the customs documents attached on the outside of the package |
| `advisor_nordic_conventions_commercial_invoice_electronic` | a commercial invoice transmitted electronically outside the booking |
| `advisor_nordic_conventions_voec_marking_printed` | the VOEC ID printed on the package or label |

An advisory is omitted only when every procedure that answers it is covered by an attestation that holds on the lane; partial coverage returns the advisory unchanged, and an attestation contradicted by the lane's conventions covers nothing and yields [Attestation conflict](../concepts/advisories.md#advisor_nordic_conventions_attestation_conflict).
The answering sets are lane-aware where the conventions differ, for example for PostNord destinations in Norway, and the complete mapping is in the [specification](../../openspec/specs/plugins/advisor-nordic-conventions/spec.md).
Advisories whose fix lies inside the booking request — the DHL Freight Sweden customs service options and the `customs.commercial_invoice` flag — are answered by no procedure, so an attestation never replaces correct request data.

## Expected procedures

`expected_procedures` returns the set of procedures the conventions expect for a request before booking, for example to show a pre-booking document checklist:

```python
import karrio.core.advisors as advisors
from karrio.plugins.advisor_nordic_conventions import expected_procedures

procedures = expected_procedures(
    shipment_request,
    advisors.AdvisorContext(carrier_name="postnord", operation="shipping"),
)
```

It returns the empty set outside the plugin's scope — the rating operation, a carrier or lane out of scope, a shipment inside the EU VAT area — and otherwise the union of the answering sets of the advisories that would be returned with no attestations, derived from the same rules that produce the advisories.
