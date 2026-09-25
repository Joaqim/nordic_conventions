# Tasks

## 1. Scaffolding and test environment

- [x] 1.1 Create `plugins/nordic_conventions/` following `plugins/hay_post/`: `pyproject.toml` (name `karrio_nordic_conventions`, version matching the siblings, `dependencies = ["karrio"]` unpinned, entry point `nordic_conventions = "karrio.plugins.nordic_conventions:METADATA"` in group `karrio.plugins`), an empty package `karrio/plugins/nordic_conventions/`, and `tests/__init__.py` plus `tests/nordic_conventions/__init__.py`, and verify `python -c "import tomllib; tomllib.load(open('plugins/nordic_conventions/pyproject.toml','rb'))"` succeeds and the file tree matches design.md
- [x] 1.2 In `nix develop 'git+file:///home/joaqim/projects/karrio?ref=dev-nix-flake#upstream'` started from `/home/joaqim/projects/karrio/.worktrees/feat-shipment-advisors`, create `plugins/nordic_conventions/.venv`, install `-e` the worktree's `modules/sdk` and `-e plugins/nordic_conventions`, and verify `python -m unittest discover -v -f plugins/nordic_conventions/tests` runs from the repository root with zero tests and exit status 0, or record the `PYTHONPATH` and `KARRIO_PLUGINS` fallback from design.md if the editable install fails
  - Note: an editable install of a karrio `modules/sdk` writes an untracked `karrio.egg-info` into the karrio checkout, so the SDK and connectors come from `PYTHONPATH` instead (design.md fallback) and the venv holds only the plugin.
  - The dev shell is entered from the karrio `develop` checkout (`cd /home/joaqim/projects/karrio && nix develop 'git+file:///home/joaqim/projects/karrio?ref=dev-nix-flake#upstream'`), which puts that checkout's `modules/sdk` and its connector directories, including `postnord` and `dhl_freight_sweden`, on `PYTHONPATH`; `develop` contains `feat-shipment-advisors` merged with `feat-document-stamping`, so the advisors hook and `StampSeed` both exist and every plugin entry point loads without errors (verified at `develop` 1174c5cb6).
  - The venv is created with `python -m venv --system-site-packages plugins/nordic_conventions/.venv` so it sees the shell's dependencies, and the plugin is installed with `pip install --no-deps -e plugins/nordic_conventions`, which registers the entry point (no `KARRIO_PLUGINS` needed).
  - The karrio checkout is read only; `PYTHONDONTWRITEBYTECODE=1` keeps imports from writing bytecode into it.
  - Run from this repository's root inside the shell: `PYTHONDONTWRITEBYTECODE=1 plugins/nordic_conventions/.venv/bin/python -m unittest discover -v -f plugins/nordic_conventions/tests`.
  - With zero tests Python 3.12 exits with status 5 ("NO TESTS RAN") rather than 0; discovery itself succeeded.

## 2. Territories, sources, and scope gate

- [x] 2.1 Implement `territories.py` with the EU VAT area table and `in_eu_vat_area(country_code, postal_code)`, and verify unit tests for Greece (`GR`) inside, Åland by `AX` and by `FI` 22100 outside, the Canary Islands by `ES` "35 001" outside, `ES` 28001 inside, a non-numeric postal code falling back to the country, and a cross-check against the PostNord and DHL Freight Sweden connector tables that is skipped when those connectors are not importable
- [x] 2.2 Implement `sources.py` with one frozen `Source(tag, reference, statement)` per source cited in the spec (FN line, original URL or repository path, and the quoted statement), and verify a unit test that every source has a tag in `S`, `W`, `I` and a non-empty reference and statement
- [x] 2.3 Implement `lanes.py` with the frozen `Lane` value, `lane_of(request, context)`, and the `sale_like` and `commercial` determinations, and verify unit tests for every scenario of the requirement "Commercial content is determined once" and unit tests for every scenario of the requirement "Advice is limited to Nordic shippers at shipment creation" (rating, other carrier, Norwegian shipper, Danish shipper on DHL Freight Sweden, intra-EU, return from Norway, Åland shipper) and for the product-group classification of `postnord_parcel`, `postnord_export_letter`, `postnord_postpaket_utrikes`, and their carrier codes, including the connector enum cross-check skipped when not importable

## 3. PostNord advisories

- [x] 3.1 Implement `nordic_postnord_se_no_digital_invoice` in `rules/postnord.py` with the predicate shared with the Postpaket advisory, and verify tests for the parcel-with-customs `info` scenario, the letter-to-Norway scenario (commercial invoice and VOEC from SEK 0 on `postnord_export_letter` and `postnord_rek`, SV page cited), the Varubrev and tracked letter to Norway scenarios without the SEK 0 statement, the commercial Postpaket Utrikes to Norway receiving only `nordic_postnord_se_postpaket_commercial_invoice`, and the non-commercial Postpaket Utrikes to Norway `warning`, asserting the full message dictionary including the Skicka Direkt Business, email, and MyCustoms routes and the cited sources
- [x] 3.2 Implement `nordic_postnord_se_postpaket_commercial_invoice`, and verify tests for commercial Postpaket Utrikes to the United States (CN23, three invoice copies, terms and web pages attributed with their copy counts and triggers), sale-like content with the flag false, commercial Postpaket Utrikes to Norway (CN23 and digital invoice routes, no paper copies, terms, web pages, and Norway rule cited), gift Postpaket Utrikes, a commercial letter, and a Finnish shipper, each as in the spec scenarios
- [x] 3.3 Implement `nordic_postnord_se_export_paper_invoice`, and verify tests for the Switzerland scenario (triplicate, parcel no. 1, three attributed sources with their copy counts), the Norway exclusion, the International Parcel exclusion, and the Åland-by-postal-code scenario
- [x] 3.4 Implement `nordic_postnord_fi_export_invoice`, and verify tests for the Great Britain scenario (tullaus.fi@postnord.com, signed triplicate, both sources attributed) and the Norway scenario (electronic before shipment, no triplicate)
- [x] 3.5 Implement `nordic_postnord_dk_export_documents`, and verify tests for Norway (2), Liechtenstein (3), Great Britain (2), and the United States (1 CN23 and 2 invoices, recommended), each asserting the conditional export-declaration copy to eksport@postnord.com without any value check

## 4. DHL Freight Sweden advisories

- [x] 4.1 Implement `nordic_dhl_freight_sweden_customs_mode_missing` in `rules/dhl_freight_sweden.py`, and verify tests for no option to Norway, each of the four customs service options silencing it by unified name, each DHL key (for example `customsHandlingStandard`) not silencing it because the connector ignores DHL-keyed options, a string `"true"` value parsed as selected, and a string `"false"` value parsed as selected as the connector parses it
- [x] 4.2 Implement `nordic_dhl_freight_sweden_invoice_copy`, and verify tests for Norway (390 kr) and Great Britain (650 kr), asserting the email address, myDHL Freight, and cited sources
- [x] 4.3 Implement `nordic_dhl_freight_sweden_attached_documents`, and verify tests for Parcel Connect by `dhl_freight_sweden_parcel_connect_b2c` and by `109` to Norway (details state 112 and road freight unconfirmed) and for no advisory on `dhl_freight_sweden_parcel_connect_plus`
- [x] 4.4 Implement `nordic_dhl_freight_sweden_voec_marking`, and verify tests for a VOEC number to Norway, no VOEC number to Norway, and a VOEC number to Switzerland (no advisory)

## 5. Invoice type advisory and plugin wiring

- [x] 5.1 Implement `nordic_invoice_type_content_mismatch` in `rules/invoice_type.py` on top of the `lanes` determinations, and verify tests for merchandise with the flag omitted (DHL Freight Sweden, `warning`), content type omitted with the flag false (PostNord parcel, `warning`), upper-case `MERCHANDISE` (`warning`), gift, documents, and return merchandise with the flag false (no advisory), sample with the flag true (`info`), and merchandise on a PostNord export letter (no advisory)
- [x] 5.2 Implement `__init__.py` with `METADATA` (id `nordic_conventions`, label, status `beta`, the ten advisors) and the hook guard, and verify the plugin test (collected through `references.import_extensions()` as type `advisor`, messages reaching `run_advisors`), the "Several advisories on one shipment" scenario through `run_advisors`, a test that every returned code starts with `nordic_` and levels are `info` or `warning`, and the guard test (stand-in `PluginMetadata` without the field, no advisors, one log record)
- [x] 5.3 Write `plugins/nordic_conventions/README.md` (purpose, the required karrio version or the fork branch `feat-shipment-advisors` until the hook is released, installation, the advisory table with codes, levels, triggers, and dated sources, the statement that the consumer owns compliance, and the non-goals), add a Nordic Conventions entry under utility plugins in the root `README.md`, one sentence per line, sentence-case headings, no emojis, and verify every code in the README matches a code constant and every spec requirement is represented

## 6. Review and integration

- [x] 6.1 Run the full suite with `python -m unittest discover -v -f plugins/nordic_conventions/tests` in the environment from 1.2, and verify it passes with one test per spec scenario, listing the scenario-to-test mapping in the task notes
  - Result: 80 tests, all passing, none skipped (SDK and connector cross-checks from karrio `develop` 1174c5cb6, no plugin-load errors in the output); the 49 spec scenarios map one-to-one to the tests below, and the remaining 31 tests cover task-level checks (territory table, sources, product groups, cross-checks, message invariants, DHL option parsing).
  - Scenario to test (modules under `plugins/nordic_conventions/tests/nordic_conventions/`):
    - Installed plugin is collected as an advisor: `test_plugin.TestNordicConventionsPlugin.test_installed_plugin_is_collected_as_an_advisor`
    - Older karrio loads the plugin without advisors: `test_plugin.TestNordicConventionsHookGuard.test_older_karrio_loads_the_plugin_without_advisors`
    - Rating receives no advice: `test_lanes.TestNordicConventionsScope.test_rating_receives_no_advice`
    - Other carriers receive no advice: `test_lanes.TestNordicConventionsScope.test_other_carriers_receive_no_advice`
    - Norwegian shippers receive no advice: `test_lanes.TestNordicConventionsScope.test_norwegian_shippers_receive_no_advice`
    - Danish shippers receive no DHL Freight Sweden advice: `test_lanes.TestNordicConventionsScope.test_danish_shippers_receive_no_dhl_freight_sweden_advice`
    - Intra-EU shipments receive no advice: `test_lanes.TestNordicConventionsScope.test_intra_eu_shipments_receive_no_advice`
    - Return from Norway receives no advice: `test_lanes.TestNordicConventionsScope.test_return_from_norway_receives_no_advice`
    - Åland shipper receives no advice: `test_lanes.TestNordicConventionsScope.test_aland_shipper_receives_no_advice`
    - Åland by postal code is outside: `test_postnord.TestNordicConventionsPostNordSEExportPaperInvoice.test_aland_by_postal_code_gets_the_paper_invoice_advisory`
    - Greece is inside: `test_lanes.TestNordicConventionsScope.test_greece_recipient_is_out_of_scope`
    - Canary Islands by postal code are outside: `test_lanes.TestNordicConventionsScope.test_canary_islands_recipient_by_postal_code_is_in_scope`
    - Conflicting sources are both attributed: `test_postnord.TestNordicConventionsPostNordSEExportPaperInvoice.test_conflicting_sources_are_both_attributed`
    - Several advisories on one shipment: `test_plugin.TestNordicConventionsPlugin.test_several_advisories_on_one_shipment`
    - Merchandise is sale-like: `test_lanes.TestNordicConventionsCommercialContent.test_merchandise_is_sale_like`
    - Omitted content type is sale-like: `test_lanes.TestNordicConventionsCommercialContent.test_omitted_content_type_is_sale_like`
    - Gift with commercial flag is commercial but not sale-like: `test_lanes.TestNordicConventionsCommercialContent.test_gift_with_commercial_flag_is_commercial_but_not_sale_like`
    - Return merchandise without commercial flag is not commercial: `test_lanes.TestNordicConventionsCommercialContent.test_return_merchandise_without_commercial_flag_is_not_commercial`
    - Parcel booking with customs data is informational: `test_postnord.TestNordicConventionsPostNordSENoDigitalInvoice.test_parcel_booking_with_customs_data_is_informational`
    - Letter to Norway states invoice and VOEC from SEK 0: `test_postnord.TestNordicConventionsPostNordSENoDigitalInvoice.test_letter_to_norway_states_invoice_and_voec_from_sek_0`
    - Letter not named by the Swedish page omits the SEK 0 statement: `test_postnord.TestNordicConventionsPostNordSENoDigitalInvoice.test_letter_not_named_by_the_swedish_page_omits_the_sek_0_statement`
    - Commercial Postpaket Utrikes to Norway receives the invoice routes once: `test_postnord.TestNordicConventionsPostNordSENoDigitalInvoice.test_commercial_postpaket_utrikes_to_norway_receives_the_invoice_routes_once`
    - Non-commercial Postpaket Utrikes to Norway is a warning: `test_postnord.TestNordicConventionsPostNordSENoDigitalInvoice.test_non_commercial_postpaket_utrikes_to_norway_is_a_warning`
    - Parcel to Switzerland gets the paper invoice advisory: `test_postnord.TestNordicConventionsPostNordSEExportPaperInvoice.test_parcel_to_switzerland_gets_the_paper_invoice_advisory`
    - Norway is excluded: `test_postnord.TestNordicConventionsPostNordSEExportPaperInvoice.test_norway_is_excluded`
    - International Parcel is excluded: `test_postnord.TestNordicConventionsPostNordSEExportPaperInvoice.test_international_parcel_is_excluded`
    - Commercial Postpaket Utrikes to the United States: `test_postnord.TestNordicConventionsPostNordSEPostpaketCommercialInvoice.test_commercial_postpaket_utrikes_to_the_united_states`
    - Sale-like content triggers the advisory: `test_postnord.TestNordicConventionsPostNordSEPostpaketCommercialInvoice.test_sale_like_content_triggers_the_advisory`
    - Commercial Postpaket Utrikes to Norway sends the invoice digitally: `test_postnord.TestNordicConventionsPostNordSEPostpaketCommercialInvoice.test_commercial_postpaket_utrikes_to_norway_sends_the_invoice_digitally`
    - Gift Postpaket Utrikes is not advised: `test_postnord.TestNordicConventionsPostNordSEPostpaketCommercialInvoice.test_gift_postpaket_utrikes_is_not_advised`
    - Letters are not advised: `test_postnord.TestNordicConventionsPostNordSEPostpaketCommercialInvoice.test_letters_are_not_advised`
    - Finnish Postpaket Utrikes is not advised: `test_postnord.TestNordicConventionsPostNordSEPostpaketCommercialInvoice.test_finnish_postpaket_utrikes_is_not_advised`
    - Finnish parcel to Great Britain: `test_postnord.TestNordicConventionsPostNordFIExportInvoice.test_finnish_parcel_to_great_britain`
    - Finnish parcel to Norway: `test_postnord.TestNordicConventionsPostNordFIExportInvoice.test_finnish_parcel_to_norway`
    - Danish parcel to Liechtenstein: `test_postnord.TestNordicConventionsPostNordDKExportDocuments.test_danish_parcel_to_liechtenstein`
    - Danish parcel to the United States: `test_postnord.TestNordicConventionsPostNordDKExportDocuments.test_danish_parcel_to_the_united_states`
    - No customs option to Norway: `test_dhl_freight_sweden.TestNordicConventionsDHLFreightSwedenCustomsModeMissing.test_no_customs_option_to_norway`
    - Selected customs option silences the advisory: `test_dhl_freight_sweden.TestNordicConventionsDHLFreightSwedenCustomsModeMissing.test_selected_customs_option_silences_the_advisory`
    - Invoice copy advisory to Great Britain states the higher fee: `test_dhl_freight_sweden.TestNordicConventionsDHLFreightSwedenInvoiceCopy.test_invoice_copy_advisory_to_great_britain_states_the_higher_fee`
    - Parcel Connect to Norway: `test_dhl_freight_sweden.TestNordicConventionsDHLFreightSwedenAttachedDocuments.test_parcel_connect_to_norway`
    - Parcel Connect Plus is not advised: `test_dhl_freight_sweden.TestNordicConventionsDHLFreightSwedenAttachedDocuments.test_parcel_connect_plus_is_not_advised`
    - VOEC number to Norway: `test_dhl_freight_sweden.TestNordicConventionsDHLFreightSwedenVOECMarking.test_voec_number_to_norway`
    - No VOEC number: `test_dhl_freight_sweden.TestNordicConventionsDHLFreightSwedenVOECMarking.test_no_voec_number`
    - Merchandise declared as proforma: `test_invoice_type.TestNordicConventionsInvoiceTypeContentMismatch.test_merchandise_declared_as_proforma`
    - Omitted content type declared as proforma: `test_invoice_type.TestNordicConventionsInvoiceTypeContentMismatch.test_omitted_content_type_declared_as_proforma`
    - Gift declared as proforma is consistent: `test_invoice_type.TestNordicConventionsInvoiceTypeContentMismatch.test_gift_declared_as_proforma_is_consistent`
    - Return merchandise declared as proforma is consistent: `test_invoice_type.TestNordicConventionsInvoiceTypeContentMismatch.test_return_merchandise_declared_as_proforma_is_consistent`
    - Sample declared as commercial is informational: `test_invoice_type.TestNordicConventionsInvoiceTypeContentMismatch.test_sample_declared_as_commercial_is_informational`
    - Letters carry no invoice type: `test_invoice_type.TestNordicConventionsInvoiceTypeContentMismatch.test_letters_carry_no_invoice_type`
- [x] 6.2 Run `openspec validate nordic-trade-document-conventions --strict`, and verify it reports the change valid
- [x] 6.3 Run a fresh-context review gate with an agent that has not seen the implementation session, against the spec, design, facts note, and the karrio repository checklists (spec compliance with no scope creep, a test for every scenario, `karrio.lib` usage and functional style, no duplication of connector field errors or the intra-EU warning, every advisory citing its sources and tags, stricter wording on conflicts, no credentials or network access in advisors), address findings, and verify the reviewer reports no blocking issue
