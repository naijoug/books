#!/usr/bin/env python3
"""Verify local Markdown links inside tech-cards-handbook.

The book is maintained as many small Markdown cards and sample inputs. Index count
checks catch drift in card totals; this script catches broken relative links among
chapters, samples, and resources without requiring a static site build.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

BOOK_DIR = Path(__file__).resolve().parents[1] / "tech-cards-handbook"

# Matches Markdown inline links and images: [text](target "optional title").
LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
FENCED_RE = re.compile(r"```.*?```", re.DOTALL)


def strip_fenced_code(text: str) -> str:
    return FENCED_RE.sub("", text)


def split_link_target(raw_target: str) -> str:
    target = raw_target.strip()
    if not target:
        return ""
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1].strip()
    # Markdown titles are separated by whitespace after the URL. Existing book
    # links do not contain spaces in local file names; keep the parser small and
    # predictable instead of trying to implement the full CommonMark grammar.
    return target.split()[0]


def is_external_or_anchor(target: str) -> bool:
    if target.startswith("#"):
        return True
    parsed = urlsplit(target)
    return bool(parsed.scheme or parsed.netloc)


def candidate_paths(source: Path, target: str) -> list[Path]:
    parsed = urlsplit(target)
    path_text = unquote(parsed.path)
    if not path_text:
        return []
    base = (source.parent / path_text).resolve()
    candidates = [base]
    if base.suffix == "":
        candidates.append(base.with_suffix(".md"))
        candidates.append(base / "README.md")
    return candidates


def link_exists(source: Path, target: str) -> bool:
    for candidate in candidate_paths(source, target):
        try:
            candidate.relative_to(BOOK_DIR)
        except ValueError:
            continue
        if candidate.is_file():
            return True
    return False


def iter_markdown_files() -> list[Path]:
    return sorted(
        path
        for path in BOOK_DIR.rglob("*.md")
        if ".drafts" not in path.parts and ".git" not in path.parts
    )


def main() -> int:
    failures: list[str] = []
    checked_links = 0
    files = iter_markdown_files()

    for source in files:
        text = strip_fenced_code(source.read_text(encoding="utf-8"))
        for match in LINK_RE.finditer(text):
            target = split_link_target(match.group(1))
            if not target or is_external_or_anchor(target):
                continue
            checked_links += 1
            if not link_exists(source, target):
                rel_source = source.relative_to(BOOK_DIR.parent)
                failures.append(f"{rel_source}: broken local link -> {target}")

    if failures:
        print("tech-cards link verification failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(
        f"verified tech-cards links: {checked_links} local link(s) across {len(files)} markdown file(s)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
