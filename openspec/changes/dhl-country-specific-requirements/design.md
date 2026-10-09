# Design

## Context

All plugin advice today passes through `lanes.lane_of`, which yields no lane when the recipient is inside the EU VAT area; the only EU-admitting exception is the territory rule's `shipper_lane_of` (`lanes.py:360`).
Every existing rule's requirement text scopes it to recipients outside the EU VAT area, and the rules rely on `lane_of`'s exclusion to honor that, so widening `lane_of` would silently change existing trigger surfaces.
The six country rows all become SE-to-X lanes because the connector serves Swedish shippers only, collapsing the manual's to-and-from phrasing to the to-X direction.
The SDK enforces advisory levels `info` and `warning` only (`core/advisors.py` coerces anything else), and advisory messages carry `details` with plugin, lane, and sources, set by the shared `advisory()` factory in `rules/__init__.py`.
The payload facts the rules need are all on `ShipmentRequest`: party `federal_tax_id`/`state_tax_id`, `parcels` weight and weight unit, the universal `dangerous_good` option, and the service code mapped through `lanes.dhl_product_code`.
The connector already encodes the product sets and threshold this design copies: `PARTY_TAX_ID_PRODUCTS` (202, SPI, 601), the transport declaration product set (202, 205, 233, SPI, 601), and `TRANSPORT_DECLARATION_FREE_WEIGHT_LIMIT_KG = 500.0` compared with `>=` (`create.py:1319`).

## Goals / Non-Goals

**Goals:**

- Six new advisories exactly as the delta specifies, with parity tests against the connector's copied tables.
- Existing advisories keep byte-identical trigger behavior; the spec's scope change is invisible on every lane that already worked.
- README and `AGENTS.md` vocabulary changes stay mechanically verifiable by the existing AGENTS.md verification commands.

**Non-Goals:**

- Any connector change; the connector repo is untouched.
- Modeling SENT/UIT/EKAER subject-goods criteria beyond gross weight; the value and high-risk criteria are named in message text, not computed (RON/HUF conversion and fiscal-goods lists are out of reach of the payload).
- Transcribing the customs row's country/postcode list (row 7 decision below).
- PostNord-side country advisories; the country table is DHL Freight Sweden scope.

## Decisions

**A second lane gate, not a wider `lane_of`.**
The new rules read a `country_lane_of` gate in `lanes.py` that admits recipients inside the EU VAT area (shipper still Nordic, carrier still gated per the scope requirement), while `lane_of` stays as-is.
Alternative rejected: widening `lane_of` to all recipients — every existing rule would start evaluating on EU lanes against requirement texts that promise outside-EU only.

**A new rule module `rules/dhl_country_requirements.py`.**
The six rules plus their shared helpers (product-set membership, summed weight) form one cohesive unit; `dhl_freight_sweden.py` is already ~350 lines and would cross the file-length guidance.
Alternative rejected: appending there and splitting later.

**Connector tables copied as literals, checked by importlib parity tests.**
`PARTY_TAX_ID_PRODUCTS`, the transport declaration product set, and the 500 kg limit are copied into the module and compared against the connector in tests that skip when the connector is not importable — the `JOINT_DECLARATION_COUNTRIES` precedent (`spec.md:366`).
Alternative rejected: importing the connector at runtime — the plugin installs and runs standalone.

**Weight is the summed parcel weight in kg, compared with `>=`.**
Parcel weights normalize to kg (LB converted); the comparison operator matches the connector's `create.py:1319` so the advisory's warning/info split lands where the connector starts demanding a declaration.

**A private individual is `residential` or no company name.**
No B2C notion exists in the plugin; `residential` defaults to false and is rarely set, so company-name absence is the practical signal for the Cyprus ID-copy sentence.
The false positive (a business recipient whose company name was never filled in) costs one extra sentence in a non-blocking warning.

**Levels.**
`warning` for Cyprus, Greece, and Spain (documents or numbers the shipment should not go without); `info` for SENT (the connector already handles the default, the advisory is a reminder); weight-split `warning`/`info` for UIT and EKAER (the weight criterion is the only one the payload can see, and it is the connector's own trigger).

**The CSR source constant and the spec's source-reference paragraph.**
`DHL_CSR_URL` follows the `DHL_MAN_URL` annotation style: page URL, document name "Country-specific shipping requirements (English)", accessed 2026-10-09.
The spec's Purpose edit (a direct main-spec edit, because deltas ignore `## Purpose` for existing capabilities) also adds the CSR shorthand to the source-reference paragraph, so the spec's `(W, CSR)` citations resolve the way FN, PNS, and DFS do.

**Row 7 stays covered by the customs machinery.**
The customs row's "countries and postal codes subject to customs requirements" is enforced by the connector's EU VAT area and territory tables and advised by the five existing customs advisories; no verbatim country/postcode list is transcribed from CSR.
The row itself defers to "DHL Freight's customs information for current requirements", which the EU VAT area tables encode, and a second transcription would add drift risk with no behavioral gain — the tables are already parity-tested across both repos.

**README and vocabulary.**
Six new rows in the Advisory reference table under the DHL Freight Sweden from Sweden group (the territory precedent for EU-destination advisories); the Requirements matrix is unchanged, and the "EU destinations, Northern Ireland included, need nothing" sentence is rewritten to name the six countries and link their advisories.
`AGENTS.md`'s Destinations vocabulary gains the six country names.

## Risks / Trade-offs

- [Business recipient without a company name receives the ID-copy sentence] → the message says the recipient "appears to be" a private individual; non-blocking, and the condition is pinned by a scenario.
- [Copied tables drift from the connector] → parity tests run in the cross-repo suite with the connector on `PYTHONPATH`; drift fails the suite.
- [Wrong dangerous-goods option key] → the test pins the universal `dangerous_good` key as the SDK registry defines it.
- [Six new codes appear on lanes that previously returned nothing] → additive and non-blocking; consumers that key on codes see new codes only on the new lanes.

## Migration Plan

Single change, advisor-only, non-blocking messages; deployment is installation of the new plugin version.
Rollback is reverting the release; no state, API, or data migration exists.

## Open Questions

- The direct PDF URL for CSR: the help-center page URL stands in the constant's annotation; a direct link can replace it later as an annotation-only change.
