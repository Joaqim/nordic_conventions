# Agent instructions

## Keeping the README in sync with the code

The Requirements at a glance, Advisory reference, and Attestations sections of `README.md` document public contract and public claims that are defined in code.
Any change to the files below must update the README in the same commit, and any README edit to those sections must be checked against them.

- `karrio/plugins/nordic_conventions/codes.py` defines the advisory codes; each code has exactly one `<details>` block under Advisory reference, preceded by an `<a id="...">` anchor whose id is the code and placed under the `###` group for its carrier and origin, or under Across carriers when it spans carriers.
- `karrio/plugins/nordic_conventions/procedures.py` defines the `Procedure` members, whose option keys are `nordic_conventions_` plus the member value; each has one row in the Attestations table.
- `karrio/plugins/nordic_conventions/rules/` decides each advisory's level, trigger, and destinations; the `Level:`, `Destinations:`, and `Trigger:` lines state what the rule does, not what it should do.
  The `<summary>` line repeats the code in `<code>` tags (markdown does not render inside it), the level, and one of `Norway only`, `outside the EU VAT area except Norway`, or `all destinations outside the EU VAT area`.
- Requirements at a glance restates in plain language what the rule messages say, per carrier and origin, split into Norway and other destinations outside the EU VAT area.
  Each cell states only what a rule's message states, marks a requirement returned at level `info` as a *reminder*, links to the advisory's anchor, and footnotes the document behind its main `Source`; a service or destination no rule covers reads *Not covered*.
  A change to a rule's trigger, level, or message text updates the matching cells, and the territory summary under Which destinations count follows `territories.py`.
- `karrio/plugins/nordic_conventions/sources.py` holds the `Source` objects each rule cites; the `Sources:` list of an advisory names one item per cited document, not per `Source` object, and inference-only sources citing `FACTS_NOTE` are not listed.

Every item in a `Sources:` list ends with a footnote reference.
Each footnote cites one document constant from `sources.py` (a URL constant, `PN_FI_TERMS`, `PNS`, or `DFS`), repeats its URL and date annotation verbatim, and names the constant in backticks at the end.
When a document constant is added, renamed, or its URL or date changes, add or update its footnote; remove a footnote once no advisory cites the document.
The item text before the footnote uses the same document name wherever that document is cited.

## Verification

After editing either side, confirm that every footnote reference has a definition and vice versa:

```bash
diff <(grep -v '^\[\^' README.md | grep -oE '\[\^[a-z-]+\]' | sort -u) <(grep -oE '^\[\^[a-z-]+\]' README.md | sort -u)
```

Then confirm that the advisory codes in the README match those in `codes.py`:

```bash
diff <(grep -oE '^<summary><code>nordic_conventions_[a-z_]+' README.md | sed 's/.*<code>//' | sort) <(grep -oE '"nordic_conventions_[a-z_]+"' karrio/plugins/nordic_conventions/codes.py | tr -d '"' | sort)
```

Then confirm that the advisory anchors match those codes and that every advisory link resolves to an anchor:

```bash
diff <(grep -oE '^<a id="nordic_conventions_[a-z_]+"' README.md | sed 's/.*id="//;s/"//' | sort) <(grep -oE '"nordic_conventions_[a-z_]+"' karrio/plugins/nordic_conventions/codes.py | tr -d '"' | sort)
comm -23 <(grep -oE '\]\(#nordic_conventions_[a-z_]+\)' README.md | sed 's/](#//;s/)//' | sort -u) <(grep -oE '^<a id="nordic_conventions_[a-z_]+"' README.md | sed 's/.*id="//;s/"//' | sort -u)
```

Run the test suite before committing.
The [specification](openspec/specs/plugins/nordic-conventions/spec.md) is the normative source when the README and the code disagree about intended behaviour; record the disagreement rather than resolving it silently.
