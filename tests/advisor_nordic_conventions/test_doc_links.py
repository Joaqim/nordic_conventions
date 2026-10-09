"""Relative links in the documentation.

The checked documents are the README, every page under ``docs/`` outside the
ephemeral ``docs/notes/`` tree, and the notes index, which together carry
every published claim. Working notes are not checked. Reference definitions
are not followed: every one in this repository is a source-citation footnote
that names an external URL, not a link to a repository file.
"""

import pathlib
import re
import typing
import unittest

REPO = pathlib.Path(__file__).resolve().parents[2]

INLINE_LINK = re.compile(r"\]\(([^)\s]+)\)")
FENCE = re.compile(r"^```.*?^```", re.M | re.S)
EXTERNAL = re.compile(r"^[a-z][a-z0-9+.-]*:", re.I)


def checked_documents() -> typing.List[pathlib.Path]:
    docs = REPO / "docs"
    return [
        REPO / "README.md",
        docs / "notes" / "README.md",
        *sorted(
            path
            for path in docs.rglob("*.md")
            if (docs / "notes") not in path.parents
        ),
    ]


def relative_links(document: pathlib.Path) -> typing.List[str]:
    text = FENCE.sub("", document.read_text())
    return [
        target
        for target in INLINE_LINK.findall(text)
        if not EXTERNAL.match(target) and not target.startswith("#")
    ]


def resolve(document: pathlib.Path, target: str) -> pathlib.Path:
    return (document.parent / target.split("#", 1)[0]).resolve()


class TestDocLinks(unittest.TestCase):
    def test_relative_links_resolve(self):
        for document in checked_documents():
            for target in relative_links(document):
                with self.subTest(document=str(document.relative_to(REPO)), target=target):
                    self.assertTrue(resolve(document, target).exists())


if __name__ == "__main__":
    unittest.main()
