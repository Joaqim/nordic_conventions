---
title: "Plugin layout"
---

## Registration

The plugin registers through the `karrio.plugins` entry point group under the id `advisor_nordic_conventions` (`[project.entry-points."karrio.plugins"]` in `pyproject.toml`), exposing the `METADATA` object in `karrio/plugins/advisor_nordic_conventions/__init__.py`, so installing the package makes the advisors available to every karrio SDK runtime and uninstalling it removes them.
`METADATA` is a `PluginMetadata` that declares the advisors through `shipment_advisors`: the rules of `procedures.RULES` wrapped by `attestations.with_attestations`, plus the attestation-conflict advisor.
The plugin declares shipment advisors only, so karrio reports it with the plugin type `advisor` and derives no carrier capability from it.

On a karrio SDK whose plugin metadata has no `shipment_advisors` field, importing and loading the plugin does not raise: it registers no advisors and logs once, through the stdlib logger, that the hook is unavailable, because `karrio.core.utils.logger` is not guaranteed on karrio versions that predate the advisors hook.
Shipment responses are then unchanged.

## Module map

- `karrio/plugins/advisor_nordic_conventions/codes.py` — `AdvisoryClassification`, the stable advisory codes; renaming one is a breaking change.
- `karrio/plugins/advisor_nordic_conventions/lanes.py` — the scope gate and the shipment lane shared by every advisory: carrier, shipper country, service, and EU VAT area verdicts.
- `karrio/plugins/advisor_nordic_conventions/territories.py` — the EU VAT area table for goods movements and the postal-code normalisation.
- `karrio/plugins/advisor_nordic_conventions/exclusions.py` — the DHL Freight Sweden per-product postal-code exclusions copied from the connector, checked against it by a test.
- `karrio/plugins/advisor_nordic_conventions/rules/` — the advisory rules: `postnord.py`, `dhl_freight_sweden.py`, `dhl_country_requirements.py`, `invoice_type.py`, and `customs_values.py`, each producing the messages for its requirement.
- `karrio/plugins/advisor_nordic_conventions/sources.py` — the `Source` objects with their `S`, `W`, and `I` evidence tags and the URL constants the documentation footnotes name.
- `karrio/plugins/advisor_nordic_conventions/procedures.py` — the `Procedure` members and their option keys, the map of answering procedures per advisory, and `expected_procedures`.
- `karrio/plugins/advisor_nordic_conventions/attestations.py` — attestation parsing, the answering that omits covered advisories, and conflict detection.

Which advisory rule decides what is documented in the [Advisory reference](../../concepts/advisories.md); the normative source is the [specification](../../../openspec/specs/plugins/advisor-nordic-conventions/spec.md).
