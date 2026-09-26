# Design

## Context

See proposal.md for motivation and `specs/plugins/nordic-conventions/spec.md` for required behaviour.
Source references use the same FN convention as the main spec: the karrio fork's `docs/notes/customs/nordic-trade-documents-facts.md` (branch `docs-openspec`, commit baf8eb3dd) with line numbers and evidence tags.

The plugin's territory table lives in `karrio/plugins/nordic_conventions/territories.py`: a frozenset `EU_VAT_AREA_COUNTRIES` (the member states plus `EL`, which the connectors also accept through `EUCountry`), a tuple `NON_EU_VAT_POSTAL_RANGES` of `(country, low, high)` exclusions, and `in_eu_vat_area(country_code, postal_code)`, which strips spaces and compares postal codes numerically only when purely numeric.
Both connectors implement the same three things: `modules/connectors/postnord/karrio/providers/postnord/units.py:294-327` and `modules/connectors/dhl_freight_sweden/karrio/providers/dhl_freight_sweden/units.py:115-149` on the karrio fork, with the country set built as `frozenset([*(country.name for country in units.EUCountry), "GR"])`.
The main specs of both connectors state the definition their EU VAT checks follow (karrio `docs-openspec` branch, `openspec/specs/postnord/customs-declaration/spec.md:184-188`, `openspec/specs/dhl-freight-sweden/customs/spec.md:110-114`), and the plugin's `test_matches_connector_tables` asserts table equality with each connector when importable and skips otherwise.

Tullverket's table (FN:58-65, W) rows that diverge from the connectors' country-level treatment: Monaco and Northern Ireland are "treated as EU" (Northern Ireland for goods, W InterTradeIreland, FN:64), and Mount Athos is inside the customs union but outside the VAT area.
Skatteverket corroborates the Northern Ireland split: "Nordirland räknas som ett EU-land vid varuhandel med andra EU-länder. Vid handel med tjänster med andra EU-länder räknas Nordirland som ett land utanför EU." (Sälja varor till länder utanför EU, skatteverket.se).
The karrio fork's `develop` branch is generated from upstream-bound feature branches (`docs/notes/workflow/develop-assembly.md`); connector code changes ride a feature branch, and the facts note and the connector main specs live on `docs-openspec`.

## Goals / Non-Goals

Goals: one territory verdict, identical in the plugin and both connectors, that follows Tullverket for goods movements; the smallest data-model extension that can express Northern Ireland; a cross-check test that keeps failing loudly on any future divergence.
Non-goals: a services-VAT verdict; changes to karrio's `EUCountry` (which lacks `AX`, `XI`, and `MC`, FN:235, FN:276); renaming the helper; any new advisory, code, level, or message contract; re-litigating territories whose country-level verdict already matches Tullverket (San Marino, the Faroe Islands, Greenland, Andorra, the Vatican, the Channel Islands).

## Decisions

### Territory model: one inclusion table beside the exclusion ranges

`EU_VAT_AREA_COUNTRIES` gains `"MC"`, keeping its meaning "the country codes of the EU VAT area": the set already carries the non-member alias `EL`, and Monaco is treated as EU (FN:64).
`NON_EU_VAT_POSTAL_RANGES` gains `("GR", 63086, 63086)` for Mount Athos; Greek postal codes are numeric, so the existing space-stripped numeric comparison handles "630 86" unchanged.
A new tuple `EU_VAT_POSTAL_PREFIXES` of `(country, prefix)` pairs, holding `(("GB", "BT"),)`, carries Northern Ireland: United Kingdom postcodes are alphanumeric, so a numeric range cannot express them.
The test becomes `inside = (country in EU_VAT_AREA_COUNTRIES and not excluded_range(country, postal)) or matches_prefix(country, postal)`, with the prefix compared against the space-stripped postal code upper-cased, because `GB` is not in the country set and no exclusion range targets it, so the two mechanisms cannot interact.
Alternative considered: a general postal-zone engine (for example United Kingdom postcode areas); rejected because one prefix does not justify a parser that both connectors would have to mirror.
Alternative considered: admitting Northern Ireland by postal range; rejected for the same reason the ranges cannot express it: `BT1 1AA` is not a number.

### Goods semantics without renaming

`in_eu_vat_area` keeps its name; its docstring states that the Northern Ireland verdict is the goods-movement verdict and names the authority split: inside for goods, outside for services.
Every caller decides customs handling for goods movements — the plugin's lane gate and both connectors' customs-omission logic — so no caller needs a services verdict, and the spec records the same caveat.
Alternative considered: renaming to `in_eu_vat_area_for_goods` across the plugin and both connectors; rejected because the rename ripples through connector code and tests without changing any verdict, and it is recorded here as the follow-up should a services consumer ever appear.

### Connector lockstep and landing order

Both connectors receive byte-identical changes: `"MC"` appended beside `"GR"` in the set construction, the Mount Athos range, the prefix tuple, and the prefix disjunct in their `in_eu_vat_area`.
The plugin's cross-check test extends to assert tuple equality of `EU_VAT_POSTAL_PREFIXES` as well, so equality of all three tables remains the invariant that fails loudly on divergence.
Because the cross-check runs against whichever connectors are importable, either side merging alone leaves a window in which the test fails against the mixed state; the window closes by merging in one session, connectors first (both connector branches, then a `develop` rebuild), then this plugin branch, so the plugin's final test run sees the new connector tables and passes.

### Karrio-side distribution

The facts note gains, on `docs-openspec` and append-only so existing FN citations stay valid, the Skatteverket quotation and GOV.UK VAT Notice 725 ("VAT on movements of goods between Northern Ireland and the EU") as corroboration of the Northern Ireland row; the karrio-side spec deltas cite the new line numbers.
Connector code and connector unit tests go on two per-stack branches, because the connectors live on separate unmerged stacks and no single branch can carry both files: `fix-postnord-eu-vat-territories`, branched from `feat-postnord-customs-invoice`, and `fix-dhl-freight-se-eu-vat-territories`, branched from `feat-dhl-freight-se-customs`, both upstream-bound like their parents and registered in `BRANCHES` in `assemble-develop.sh` on `docs-openspec` right after their parents.
The PNS and DFS requirement texts gain the same three territories on `docs-openspec`; `develop` is regenerated with `rebuild-develop.sh`, which assembles `develop-next`, runs the touched connector suites and the SDK suite, and moves `develop` only when every check passes, and `develop` is never committed to directly.

### Nothing else in the plugin changes

The lane gate, the rules, `sources.py`, and every message contract stay as they are: the territory test is infrastructure whose authorities are cited in the spec text, and no advisory's cited sources change.
The README drops its non-goal sentence about Monaco, Northern Ireland, and Mount Athos and states the goods-movement alignment instead.

## Risks / Trade-offs

- [Consumers relied on the old verdicts for Northern Ireland or Monaco] → advisories are non-blocking reminders and the README makes compliance the consumer's; the verdicts now match the declared authority rather than a connector shortcut.
- [A `GB` address in Northern Ireland with a missing or malformed postal code] → falls back to the country-level outside verdict, which over-advises rather than staying silent; accepted because the conservative direction states duties that may not apply.
- [The two repositories disagree during the merge window] → the cross-check fails loudly in exactly that window instead of silently diverging, and the landing order above keeps the window inside one session.
- [karrio's `EUCountry` later grows `MC` or `XI` upstream] → the connectors' set construction is a union, so an upstream addition collapses into the appended entry without conflict; `XI` remains unused because addresses do not carry it.

## Migration Plan

Land the connector branch and regenerate `develop`, then merge this plugin branch; rollback is the reverse order.
No data, schema, or API migration is involved, and advisory codes and levels are untouched.

## Open Questions

- Whether PostNord or DHL Freight Sweden publish their own treatment of Northern Ireland or Monaco shipments that differs from Tullverket's; the answer could add carrier citations to the facts note but does not change the verdicts, because Tullverket is the authority this table follows.
