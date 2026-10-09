# Agent instructions

## Keeping the README and docs pages in sync with the code

The Requirements at a glance matrix and the Advisory reference and Attestations summaries in `README.md`, together with `docs/concepts/advisories.md` and `docs/guides/attestations.md`, document public contract and public claims that are defined in code.
Any change to the files below must update the README and the named docs page in the same commit, and any edit to those sections must be checked against them.

- `karrio/plugins/advisor_nordic_conventions/codes.py` defines the advisory codes.
  Each code has one row in an Advisory reference table in `docs/concepts/advisories.md`, under the `##` group for its carrier and origin or under Across carriers, and one line in that page's Codes list, `- <short name>: ` followed by the code in backticks.
  The row's Advisory cell starts with an `<a id="...">` anchor whose id is the code, followed by the same short name as in the Codes list; short names are unique.
  The README's matrix and summaries link to these anchors.
- `karrio/plugins/advisor_nordic_conventions/procedures.py` defines the `Procedure` members, whose option keys are `advisor_nordic_conventions_` plus the member value; each has one row in the Attestations table in `docs/guides/attestations.md`.
- `karrio/plugins/advisor_nordic_conventions/rules/` decides each advisory's level, trigger, and destinations; the Level, Destinations, and Trigger cells in `docs/concepts/advisories.md` state what the rule does, not what it should do.
  The Level cell states conditional levels briefly, the Destinations cell is one of `Norway`, `Switzerland`, `Great Britain`, `Switzerland and Great Britain`, `Cyprus`, `Greece`, `Poland`, `Romania`, `Spain`, `Hungary`, `non-EU except Norway`, or `all non-EU`, and the Trigger cell leaves out the carrier and origin its group heading names.
- The Requirements at a glance matrix in `README.md` has one row per carrier, origin, and service group, with a Norway and an other non-EU column.
  Each cell is a few words stating only what a rule's message states, links to the advisory's anchor in `docs/concepts/advisories.md`, marks an `info` advisory with "(reminder)", and reads — where no rule advises; it carries no footnotes.
  A change to a rule's trigger, level, or message text updates the matching cells.
- `karrio/plugins/advisor_nordic_conventions/sources.py` holds the `Source` objects each rule cites; the Sources cell of an advisory names one item per cited document, comma-separated, not per `Source` object, and inference-only sources citing `FACTS_NOTE` are not listed.

Every item in a Sources cell ends with a footnote reference.
Each footnote cites one document constant from `sources.py` (a URL constant, `PN_FI_TERMS`, `PNS`, or `DFS`), repeats its URL and date annotation verbatim, and names the constant in backticks at the end; the footnote definitions live at the end of `docs/concepts/advisories.md`.
When a document constant is added, renamed, or its URL or date changes, add or update its footnote; remove a footnote once no advisory cites the document.
The item text before the footnote uses the same document name wherever that document is cited.

## Verification

After editing either side, confirm that every footnote reference has a definition and vice versa in `docs/concepts/advisories.md`:

```bash
diff <(grep -v '^\[\^' docs/concepts/advisories.md | grep -oE '\[\^[a-z-]+\]' | sort -u) <(grep -oE '^\[\^[a-z-]+\]' docs/concepts/advisories.md | sort -u)
```

Then confirm that the Codes list matches `codes.py`:

```bash
diff <(grep -oE '^- [^:]+: `advisor_nordic_conventions_[a-z_]+`$' docs/concepts/advisories.md | grep -oE 'advisor_nordic_conventions_[a-z_]+' | sort) <(grep -oE '"advisor_nordic_conventions_[a-z_]+"' karrio/plugins/advisor_nordic_conventions/codes.py | tr -d '"' | sort)
```

Then confirm that each reference row pairs its anchor with the short name the Codes list gives that code, and that every advisory link in the README and the docs pages resolves to an anchor:

```bash
diff <(grep -oE '^\| <a id="advisor_nordic_conventions_[a-z_]+"></a>[^|]*[^ |]' docs/concepts/advisories.md | sed -E 's/^\| <a id="([a-z_]+)"><\/a>(.*)$/\2: \1/' | sort) <(grep -E '^- [^:]+: `advisor_nordic_conventions_[a-z_]+`$' docs/concepts/advisories.md | sed -E 's/^- (.*): `(.*)`$/\1: \2/' | sort)
comm -23 <(grep -r --exclude-dir=notes -ohE '#advisor_nordic_conventions_[a-z_]+' README.md docs | sed 's/^#//' | sort -u) <(grep -oE '<a id="advisor_nordic_conventions_[a-z_]+"' docs/concepts/advisories.md | sed 's/.*id="//;s/"//' | sort -u)
```

Run the test suite before committing; `tests/advisor_nordic_conventions/test_doc_links.py` checks that every relative link in the README and the docs pages resolves.
The [specification](openspec/specs/plugins/advisor-nordic-conventions/spec.md) is the normative source when the README, the docs pages, and the code disagree about intended behaviour; record the disagreement rather than resolving it silently.

## Documentation site

The `docs/` tree is published by the external harness as described in [docs/development/architecture/docs-site.md](docs/development/architecture/docs-site.md).
Preview it locally from the repository root:

```bash
DOCS_DIR=$PWD/docs SITE_BASE=/karrio-advisor-nordic-conventions REPO_URL=https://github.com/PrimePack-AB/karrio-advisor-nordic-conventions bun run --cwd ../starlight-docs-harness dev
```
