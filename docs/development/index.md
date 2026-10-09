---
title: "Development"
---

This section is for working on the plugin itself.
[Plugin layout](architecture/plugin-layout.md) describes how the package registers with karrio and what each module carries, and [Documentation site](architecture/docs-site.md) describes how `docs/` is built and published.
Working notes are indexed in [docs/notes](../notes/README.md).

## Setup

Create a virtual environment and install the forked SDK and the plugin with `pip install -r requirements-dev.txt -e .`.
`requirements-dev.txt` installs the SDK editable from a local checkout of the fork's `feat-shipment-advisors` branch; a `git+https` install cannot replace this, because pip recursively fetches the monorepo's private `karrioapi` submodules that `modules/sdk` does not need.

## Tests

Tests use `unittest` and run from the repository root with an interpreter that can import a karrio SDK providing the advisors hook:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -v -f tests
```

The suite includes `tests/advisor_nordic_conventions/test_doc_links.py`, which checks that every relative link in the README and the published `docs/` pages resolves.
The connector cross-check tests run when the PostNord and DHL Freight Sweden connectors are importable, as in the karrio fork's `develop` dev shell (`nix develop 'git+file:///home/joaqim/projects/karrio?ref=dev-nix-flake#upstream'`, entered from the karrio checkout), and are skipped otherwise.

## Known limitations

The README is also the PyPI long description (`readme = "README.md"` in `pyproject.toml`), and its relative links into `docs/` do not resolve on PyPI; fixing them is deferred until the package is published.
