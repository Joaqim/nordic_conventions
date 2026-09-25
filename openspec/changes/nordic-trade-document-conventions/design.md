# Design

## Context

See proposal.md for motivation and specs/plugins/nordic-conventions/spec.md for required behaviour, including the source legend (FN, PNS, DFS) used below.

The hook contract is the karrio fork's `feat-shipment-advisors` branch at 92c5d1ec0.
`PluginMetadata.shipment_advisors` is a list of callables `(request, context) -> Iterable[Message]` (`modules/sdk/karrio/core/metadata.py:68-70`), collected as `(plugin_id, advisor)` pairs and run by `karrio.core.advisors.run_advisors` (`modules/sdk/karrio/core/advisors.py:55-82`).
Each advisor runs on its own deep copy of the request and is isolated by the SDK: a raising advisor becomes one `shipment_advisor_failed` warning naming the plugin, and the other advisors still run (`advisors.py:85-116`).
The SDK fills `carrier_name` and `carrier_id` when a message leaves them `None`, and reports any level other than `info` or `warning` as `warning` (`advisors.py:119-125`).
`AdvisorContext` exposes `carrier_name`, `carrier_id`, `account_country_code`, `test_mode`, `operation`, and `config` (`advisors.py:26-52`); shipper and recipient come only from the request, which for returns is the swapped copy (`apps/www/docs/carriers/sdk/advisors.mdx`, "When advisors run").

`ShipmentRequest.service` holds the unified service name, `options` the shipment options, and `customs` the `Customs` model with `commercial_invoice`, `content_type`, and `options` (`modules/sdk/karrio/core/models.py:105-144`); `CustomsContentType` keys are `documents`, `gift`, `sample`, `merchandise`, `return_merchandise`, `other` with upper-case values (`modules/sdk/karrio/core/units.py:62-68`).
The PostNord connector distinguishes letter services and International Parcel from parcel products (`modules/connectors/postnord/karrio/providers/postnord/units.py:264-285` on karrio `develop` at 7a56ffa5b), and the DHL Freight Sweden connector names Parcel Connect `dhl_freight_sweden_parcel_connect_b2c` (`"109"`) and its customs service options `dhl_freight_sweden_customs_handling_standard`, `_customs_handling_full_service`, `_customs_own_declaration`, and `_customs_joint_declaration` (`modules/connectors/dhl_freight_sweden/karrio/providers/dhl_freight_sweden/units.py:180-220`, same commit).
Both connectors implement the EU VAT area test as a country set plus postal-code ranges (`dhl_freight_sweden/units.py:115-149`).

The template for plugin layout is `plugins/hay_post/` in this repository: setuptools `pyproject.toml`, `dependencies = ["karrio"]` unpinned, entry point `[project.entry-points."karrio.plugins"]`, namespace packages under `karrio/`, and unittest tests under `tests/<id>/`.

## Goals / Non-Goals

Goals: ten independent, pure advisory rules sharing one scope gate and one territory table; every message traceable to its sources; no import of carrier connector code at runtime; a plugin that loads harmlessly on karrio without the hook.
Non-goals: configurable rules or per-organisation overrides, localisation of message texts, rating-time advice, and any check that duplicates a connector field error.

## Decisions

### Package layout

```
plugins/nordic_conventions/
  pyproject.toml                 name karrio_nordic_conventions, entry point nordic_conventions
  README.md
  karrio/plugins/nordic_conventions/
    __init__.py                  METADATA and the hook guard
    territories.py               EU VAT area table and territory test
    lanes.py                     Lane value and the scope gate
    sources.py                   Source values cited by the rules
    rules/postnord.py            the five PostNord advisories
    rules/dhl_freight_sweden.py  the four DHL Freight Sweden advisories
    rules/invoice_type.py        the invoice type advisory
  tests/__init__.py
  tests/nordic_conventions/      fixture.py and one test module per rules module, territories, and the plugin
```

The logic lives under `karrio.plugins.nordic_conventions` rather than `karrio.providers`, because `providers` and `mappers` are carrier namespaces and this plugin is not a carrier.

### One advisor per rule behind a shared scope gate

Each advisory is its own advisor callable registered in `shipment_advisors`, so the SDK's per-advisor isolation keeps one faulty rule from silencing the other nine.
Every rule starts from `lanes.lane_of(request, context) -> Optional[Lane]`, which returns `None` unless the operation is `shipping`, the carrier and shipper country are in scope, the shipper is inside and the recipient outside the EU VAT area; rules then return an empty list or one message.
`Lane` is a frozen attrs value holding the carrier name, shipper country, recipient country, whether the recipient is Norway, the service name, the PostNord product group (letter, international parcel, parcel product), whether customs data is present, `commercial_invoice`, the normalised content type, the VOEC number, the set of selected DHL customs service options, and the derived `sale_like` and `commercial` flags.
`lanes.sale_like(customs)` and `lanes.commercial(customs)` implement the spec's single determination of commercial content; content types are compared by lower-casing the value and matching `CustomsContentType` names (`gift`, `sample`, `documents`, `return_merchandise`), so both `gift` and `GIFT` match.
The PostNord commercial-letter advisory and the invoice type advisory both read these flags rather than re-deriving them.
Building `Lane` once per advisor call repeats a few dictionary reads ten times per shipment, which is negligible next to a carrier call.
Alternative considered: a single advisor returning all messages; rejected because one exception would drop every advisory and the SDK's failure message could not tell which rule failed.

### Own territory table instead of `EUCountry`

`territories.in_eu_vat_area(country_code, postal_code) -> bool` uses a literal frozenset of the 27 member states with `GR` (and `EL`, which the connectors also accept through `EUCountry`) and a tuple of `(country, low, high)` postal ranges equal to the connectors' `NON_EU_VAT_POSTAL_RANGES`, with `AX`, `IC`, and the French overseas departments outside by country code.
Postal codes are stripped of spaces and compared numerically only when purely numeric.
Mirroring the connectors keeps the plugin's notion of "outside the EU VAT area" identical to where the connectors send customs data, so an advisory never talks about customs documents for a shipment whose customs data the connector dropped.
Monaco, Northern Ireland, and Mount Athos are listed by Tullverket (FN:58-65) but not handled by the connectors; they follow the connectors' country-level treatment here, and changing them is a deferred cross-repository change covering both connectors and this table together.
Alternative considered: importing the connectors' tables; rejected because the plugin must work with either connector absent and must not couple its release to connector internals.
A test cross-checks the table against the connectors' tables when those modules are importable and is skipped otherwise.

### Service and option names without importing connectors

`rules/postnord.py` holds the PostNord letter service names, copied from the connector's `LETTER_SERVICES` as listed in the spec, the International Parcel name `postnord_postpaket_utrikes`, and their carrier codes, and classifies every other `postnord` service as a parcel product, matching PNS lines 10-11.
`rules/dhl_freight_sweden.py` recognises Parcel Connect by `dhl_freight_sweden_parcel_connect_b2c` or `109`, and the customs service options by their unified names and their DHL keys (`customsHandlingStandard`, `customsHandlingFullService`, `customsCustomersOwnDeclaration`, `customsJointDeclaration`).
An option counts as selected when karrio's bool option parsing (`karrio.lib`) would select it, so the plugin and the connector agree on string values such as `"true"`.
The same cross-check test compares these names with the connectors' enums when importable.

### Messages and sources

`sources.py` defines frozen `Source(tag, reference, statement)` values, one per cited document or code location, each carrying its FN line reference and the original URL or path.
A rule builds `models.Message(carrier_name=None, carrier_id=None, code=..., level=..., message=..., details=dict(plugin="nordic_conventions", lane="SE-NO", sources=[...]))`, where each source is serialised as `{tag, reference, statement}`; the SDK fills the carrier identity.
For conflicting sources the rule's message states the stricter requirement, and `details.sources` lists each disagreeing source with its own statement, so the consumer sees who says what.
Codes are module-level constants prefixed `nordic_` and are part of the plugin's public contract; renaming one is a breaking change noted in the README.

### Levels

| Code | Level | Reason |
|---|---|---|
| `nordic_postnord_se_no_digital_invoice` | `info` for parcel products with customs data, else `warning` | the connector already transmits the invoice data for parcel products (PNS lines 28-31), so the consumer only needs to know no paper is needed; otherwise the consumer must supply the digital invoice through a route they own |
| `nordic_postnord_se_export_cn23_invoice` | `warning` | the connector sends CN22 data, so the consumer must supply the CN23 and the invoice |
| `nordic_postnord_se_export_paper_invoice` | `warning` | a physical action by the consumer is required |
| `nordic_postnord_fi_export_invoice` | `warning` | the stricter source requires a signed paper invoice, or for Norway electronic data before the shipment |
| `nordic_postnord_dk_export_documents` | `warning` | a physical action by the consumer is required |
| `nordic_dhl_freight_sweden_customs_mode_missing` | `warning` | DHL requires a selection the booking lacks (FN:180) |
| `nordic_dhl_freight_sweden_invoice_copy` | `warning` | a separate consumer action is required and missing documents stop the shipment with a fee (FN:200) |
| `nordic_dhl_freight_sweden_attached_documents` | `warning` | a physical action by the consumer is required |
| `nordic_dhl_freight_sweden_voec_marking` | `warning` | a marking the connector does not guarantee is required |
| `nordic_invoice_type_content_mismatch` | `warning` for proforma with sale-like content, `info` for commercial with gift or sample | the sources restrict the proforma invoice to goods not sold (FN:56) but do not forbid a commercial invoice for gifts or samples |

### Hook guard

`__init__.py` checks `"shipment_advisors" in attr.fields_dict(metadata.PluginMetadata)`; when present it passes the ten advisors, and when absent it builds `METADATA` without the field and emits one `logging.getLogger(__name__).warning` at import, which Python performs once per process.
The stdlib logger is used because `karrio.core.utils.logger` is not guaranteed on older karrio versions.
Without advisors the plugin is typed `unknown` by older karrio, which is harmless.

### Testing

Tests use `unittest` in the repository's style: module-level payload constants in `fixture.py`, requests built with `lib.to_object(models.ShipmentRequest, payload)`, advisors called directly with an `AdvisorContext`, and one `assertListEqual` over `lib.to_dict(messages)` per scenario with `unittest.mock.ANY` for message texts only where the scenario does not constrain them.
Each spec scenario maps to one test method.
A plugin test runs `references.import_extensions()` and `run_advisors` to assert the plugin is collected as `advisor` and its messages reach the SDK runner.
The guard test substitutes a `PluginMetadata` stand-in without the field, reloads the package, and asserts no advisors and one log record with `assertLogs`.

Tests run against the SDK of the karrio fork worktree `/home/joaqim/projects/karrio/.worktrees/feat-shipment-advisors`: inside `nix develop 'git+file:///home/joaqim/projects/karrio?ref=dev-nix-flake#upstream'` started from that worktree, create a virtual environment at `plugins/nordic_conventions/.venv` (ignored by `.gitignore`), install `-e <worktree>/modules/sdk` and `-e plugins/nordic_conventions` so the entry point is registered, and run `python -m unittest discover -v -f plugins/nordic_conventions/tests` from the repository root.
If the editable install is not possible in that shell, `PYTHONPATH=<worktree>/modules/sdk:plugins/nordic_conventions` covers the direct advisor tests, and the plugin collection test uses `KARRIO_PLUGINS` pointing at the plugin directory.

## Risks / Trade-offs

- [Carrier rules change or the sources are outdated] → every message cites dated sources in `details`, the README lists the source dates, and codes stay stable while wording is updated.
- [The PostNord service lists drift from the connector] → the cross-check test fails when the connector is importable and its letter or International Parcel set changes.
- [Consumers treat advisories as compliance guarantees] → the README and every message frame them as reminders; the consumer owns compliance (FN:19).
- [Advice volume on busy lanes, for example three DHL warnings on every Swedish Parcel Connect shipment to Norway] → accepted for v1; each code is stable so consumers can filter; configuration is a possible follow-up.
- [The hook is not yet upstream] → the guard keeps the plugin inert on released karrio versions, and the README states the requirement.

## Migration Plan

The plugin is new and opt-in: installing it adds messages, uninstalling it removes them.
No data or schema migration is involved.
Work happens on branch `feat-nordic-conventions` of the fork `Joaqim/karrio-community-plugins`; submission upstream waits until the advisors hook is released in karrio.

## Open Questions

- Whether PostNord FI's web guidance or its 2026 contract terms govern (FN:249), and PostNord SE's copy count (FN:248); the advisories already state the stricter reading, so resolving either only changes wording and cited sources.
- Whether DHL Freight Sweden requires outside copies for 112 and road freight (FN:250); a confirmation would extend the attached-documents advisory's service set.
