# Agent instructions

## Keeping the README in sync with the code

The Requirements at a glance, Advisory reference, and Attestations sections of `README.md` document public contract and public claims that are defined in code.
Any change to the files below must update the README in the same commit, and any README edit to those sections must be checked against them.

- `karrio/plugins/nordic_conventions/codes.py` defines the advisory codes; each code has exactly one row under Advisory reference, in the table of the `### ... advisories` group for its carrier and origin, or of Advisories across carriers when it spans carriers.
  The Advisory cell starts with an `<a id="...">` anchor whose id is the code, followed by the code in backticks; the group headings end in "advisories" so their anchors differ from the at-a-glance headings.
- `karrio/plugins/nordic_conventions/procedures.py` defines the `Procedure` members, whose option keys are `nordic_conventions_` plus the member value; each has one row in the Attestations table.
- `karrio/plugins/nordic_conventions/rules/` decides each advisory's level, trigger, and destinations; the Level, Destinations, and Trigger cells state what the rule does, not what it should do.
  The Level cell states conditional levels briefly, the Destinations cell is one of `Norway only`, `outside the EU VAT area except Norway`, or `all destinations outside the EU VAT area`, and the Trigger cell leaves out the carrier and origin its group heading names.
- Requirements at a glance restates in plain language what the rule messages say, per carrier and origin, split into Norway and other destinations outside the EU VAT area.
  Each cell states only what a rule's message states, marks a requirement returned at level `info` as a *reminder*, links to the advisory's anchor, and footnotes the document behind its main `Source`; a service or destination no rule covers reads *Not covered*.
  A change to a rule's trigger, level, or message text updates the matching cells, and the territory summary under Which destinations count follows `territories.py`.
- `karrio/plugins/nordic_conventions/sources.py` holds the `Source` objects each rule cites; the Sources cell of an advisory names one item per cited document, comma-separated, not per `Source` object, and inference-only sources citing `FACTS_NOTE` are not listed.

Every item in a Sources cell ends with a footnote reference.
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
diff <(grep -oE '^\| <a id="nordic_conventions_[a-z_]+"></a>`nordic_conventions_[a-z_]+`' README.md | sed 's/.*`\(.*\)`/\1/' | sort) <(grep -oE '"nordic_conventions_[a-z_]+"' karrio/plugins/nordic_conventions/codes.py | tr -d '"' | sort)
```

Then confirm that each reference row's anchor matches the code in its cell, and that every advisory link resolves to an anchor:

```bash
grep -E '^\| <a id="nordic_conventions_' README.md | grep -vE '^\| <a id="([a-z_]+)"></a>`\1`'
comm -23 <(grep -oE '\]\(#nordic_conventions_[a-z_]+\)' README.md | sed 's/](#//;s/)//' | sort -u) <(grep -oE '<a id="nordic_conventions_[a-z_]+"' README.md | sed 's/.*id="//;s/"//' | sort -u)
```

Run the test suite before committing.
The [specification](openspec/specs/plugins/nordic-conventions/spec.md) is the normative source when the README and the code disagree about intended behaviour; record the disagreement rather than resolving it silently.
