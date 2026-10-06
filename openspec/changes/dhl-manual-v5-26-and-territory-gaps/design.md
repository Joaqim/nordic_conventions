# Design

## Context

See proposal.md for motivation and `specs/plugins/nordic-conventions/spec.md` for required behaviour.
Manual references were checked against a text copy of the v5.26 PDF (sha256 050660c37ba93d1ae9514c50dfa42c2010bc87763ccaff51a740b2526af11b73) whose page numbers are the printed page numbers, and compared with the same copy of v5.23 (sha256 c16b0a0dcb1a1cfe8c7ca767ff11e2192d8d86fd233ed6ef77693981fc5d3295).
The PDF itself was not re-fetched; the plugin cites the listing page <https://dhlpaket.se/dashboard/specifications/products/>, where DHL lists the newest manual, with the version, dates, and sha256 that identify the copy that was read.

## Manual v5.26 against each DHL rule

FN line references stay where a source has one, because they record where the finding was first made; the manual location beside them now names the v5.26 section and page.

| Rule | v5.23 basis | v5.26 basis | Change |
|---|---|---|---|
| `customs_mode_missing` | §7.6.1 p169, §6.7 p101 | §7.6.1 p163, §6.7 p96 | None: the country list (CH, GB, GE, GI, LI, MK, NO, RS, RU, SM, TR, UA, FI 22) and the own-declaration valid countries are identical. |
| `invoice_copy` | §7.6.2 p169 | §7.6.2 p163 | None: "A copy of the invoice must still be sent" is unchanged. |
| `attached_documents` | §5.16 p66 | §5.14 p62 | None for 109; 112's instructions (§5.3 p18) still ask only for documents by e-mail, so 112 stays unconfirmed. |
| `voec_marking` | §6.5 p97, §6.6 p99 | §6.5 p92, §6.6 p94, §9.4.2 p168 | Strengthened, not changed: v5.26 now names the API field `additionalServices.voecSupplyVAT.vatId` for 109, which the facts note previously sourced outside the manual. |
| `parcel_connect_not_served` | §5.3 p14, §5.16 p67, §5.17 p70 | §5.3 p18, §5.14 p63, §5.15 p66 | Verdicts unchanged (no Parcel Connect product lists CH; 107 does not list GB); the Switzerland alternatives are renamed Road Freight Standard (202), Road Freight Direct (205), and Road Freight Priority (233), and PPI, which the source statement named, is removed. |
| `parcel_connect_gb_agreement` | §5.3 p14, §5.16 p67 | §5.3 p18, §5.14 p63 | Unchanged in the manual; corroborated by the connector's sandbox rejection of a 112 SE to GB booking without the agreement. |

No rule's basis changed materially.
The Parcel Connect source statement changes in substance: 112 now lists FR (print and transportInstruction APIs required, 97100-99999 excluded; release notes p7) and no longer lists Åland among its excluded regions, and product 232 is gone; none of these feeds a rule trigger.

The connector sandbox evidence is the committed fixture `tests/dhl_freight_sweden/fixtures/sandbox/rejection-22005-112-se-gb.json` of the DHL Freight Sweden connector repository at 28c1ccb, cited by its GitHub URL at that commit as the document constant `DHL_CONNECTOR_REJECTION_112_GB_URL` and tagged S, because it is evidence committed to a repository rather than published carrier documentation.

## Territory ranges

Tullverket's list, as recorded at FN:58-65, already states the status: the French overseas departments are inside the customs union and outside the VAT area (FN:62), and the Faroe Islands and Greenland are outside both (FN:63).
The table expressed them only by their own country codes, so an address under `FR` or `DK` stayed inside.
Tullverket names territories, not postal codes, so the ranges come from elsewhere.
`("DK", 3800, 3999)` is the range DHL's v5.26 exclusion tables give for "Greenland & The Faroe Islands" (§5.3 p18, §5.14 p63, §5.15 p66).
`("FR", 97000, 97999)` is the operator's range for the overseas departments under `FR`; DHL's exclusion tables give "97100-99999", a delivery exclusion that also covers Monaco's 98000, which Tullverket treats as EU, so the manual range is not adopted.
DHL §7.4 (p162) names only Åland and the Canary Islands as examples of areas outside the tax area, so it confirms the concept but not these two ranges.
The ranges are appended after the existing ones so the tuple stays byte-identical with the connector's when the parallel connector change appends them in the same order: `("FR", 97000, 97999)`, then `("DK", 3800, 3999)`.

## Country-prefixed postal codes

Addresses sometimes carry the country in the postal code, as in `FI-22100`, `DK-3900`, or `fi 22100`, and such a code is not purely numeric, so the range comparison skipped it.
`in_eu_vat_area` now upper-cases and trims the postal code and removes a leading copy of the address's own country code when a hyphen, whitespace, or a digit follows it, before removing spaces.
Only the address's own country code is removed: `AX-22100` under `FI` keeps falling back to `FI`'s inside verdict, as the existing test states, and legacy distinguishing signs such as `N-` or `D-` are left alone.
Requiring a separator or a digit keeps alphanumeric postal codes that start with the country's letters intact, such as Maltese `MTF 1234` under `MT`.
The prefix comparison uses the normalised code, so `GB-BT1 1AA` is inside like `BT1 1AA`, and Northern Ireland stays inside per Tullverket.

## Connector parity and running the parity test

The cross-check `test_matches_connector_tables` (and the two DHL cross-checks in `test_lanes.py` and `test_dhl_freight_sweden.py`) skip in this repository's virtual environment because `karrio.providers.dhl_freight_sweden` is not importable there.
With `PYTHONPATH=../karrio-dhl-freight-sweden` the module imports against the forked SDK already installed, and the three DHL cross-checks run and pass against the connector's current tables; the PostNord subtests still skip.
Proposed, not applied: add `-e ../karrio-dhl-freight-sweden` to `requirements-dev.txt` beside the SDK line, so `pip install -r requirements-dev.txt -e .` makes the DHL cross-checks run by default.
That install also registers the connector's `dhl_freight_sweden` plugin entry point in the environment, so `test_plugin.py` should be re-run under it before adopting the change; the PostNord connector lives in the karrio fork and would need its own editable line from a branch carrying the same tables.
Once installed, the cross-check fails while the two repositories disagree, so this change and the connector change land in one session, connector first.

## Candidate territory advisories

Recorded for the operator to decide; none is implemented here.

- Åland, the Canary Islands, and the French overseas departments: an `info` reminder that these are inside the EU customs union but outside the VAT area, so goods need an export declaration for VAT while the customs status differs from a third country.
- The Faroe Islands and Greenland under `DK`: a reminder that they are outside both the customs union and the VAT area, unlike the customs-union territories above.
- DHL Parcel Connect excluded regions: 109, 112, and 107 exclude the Canary Islands, Ceuta, Melilla, Greenland and the Faroe Islands, French regions 97100-99999, Jersey, Guernsey, and Northern Ireland (`BT`), several Italian enclaves, the Dutch Caribbean, Jan Mayen and Svalbard, and the Azores and Madeira (§5.3 p18, §5.14 p63, §5.15 p66); a `parcel_connect_not_served` extension by postal range, unless the connector's rating and booking gates already make it redundant.
- Northern Ireland: inside for goods, so the plugin is silent, yet 109 and 112 do not deliver to `BT`; an advisory would need to bypass the lane gate, which only admits recipients outside the EU VAT area.
- Channel Islands: `JE` and `GY` are third countries (FN:65, inference), and under `GB` postal codes beginning `JE` or `GY` they are already outside; a note could name them where carriers treat them separately.
- Monaco: Tullverket treats it as EU, but DHL lists `MC` among the valid countries of its customs services (§6.5 p92, §6.7 p96); a reminder could state that DHL may still require customs handling.
- Büsingen and Campione d'Italia: inside Swiss customs territory, so a reminder could state that goods clear Swiss customs.

## Open Questions

- Whether `FR` 98600-98899 (Wallis and Futuna, French Polynesia, New Caledonia) should also be outside when addressed under `FR`; Tullverket's list as recorded does not name them, and DHL's 97100-99999 covers them.
- Whether country-prefix normalisation should also remove another country's code, such as `AX-22100` under `FI`, which today stays inside.
- Whether the S tag fits sandbox evidence, or whether it needs its own tag.
- `NON_EU_VAT_POSTAL_RANGES` keys Mount Athos on `GR`, so `EL` 63086 stays inside; this is pre-existing and unchanged here.
