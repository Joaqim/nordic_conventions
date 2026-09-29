# Agent instructions

## Keeping the README in sync with the code

The Advisories and Attestations sections of `README.md` document public contract that is defined in code.
Any change to the files below must update the README in the same commit, and any README edit to those sections must be checked against them.

- `karrio/plugins/nordic_conventions/codes.py` defines the advisory codes; each code has exactly one `###` section under Advisories.
- `karrio/plugins/nordic_conventions/procedures.py` defines the `Procedure` members, whose option keys are `nordic_conventions_` plus the member value; each has one row in the Attestations table.
- `karrio/plugins/nordic_conventions/rules/` decides each advisory's level and trigger; the `Level:` and `Trigger:` lines state what the rule does, not what it should do.
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
diff <(grep -oE '^### `nordic_conventions_[a-z_]+`' README.md | tr -d '#` ' | sort) <(grep -oE '"nordic_conventions_[a-z_]+"' karrio/plugins/nordic_conventions/codes.py | tr -d '"' | sort)
```

Run the test suite before committing.
The [specification](openspec/specs/plugins/nordic-conventions/spec.md) is the normative source when the README and the code disagree about intended behaviour; record the disagreement rather than resolving it silently.
