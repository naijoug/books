#!/usr/bin/env python3
"""Verify reference-link hygiene for ai-personal-growth chapters.

The check is intentionally narrow: it protects the publishing pass that
standardized external references into Markdown links with explicit access dates.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOOK_DIR = ROOT / "ai-personal-growth"
CHAPTER_DIR = BOOK_DIR / "chapters"
ACCESS_DATE = "访问日期：2026-07-23"
ABSOLUTE_HOME = "/Users/guojian"
URL_RE = re.compile(r"https?://[^\s)>）]+")
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\(https?://[^)]+\)")
REFERENCE_HEADING_RE = re.compile(r"^#{2,3}\s*(?:\d+(?:\.\d+)*\.?\s*)?(?:本章)?参考(?:资料)?与延伸阅读\s*$")
APPENDIX_SOURCE_HEADING_RE = re.compile(r"^##\s*A\.19\s+推荐跟踪的公开资料源\s*$")
HEADING_RE = re.compile(r"^#{1,3}\s+")


def strip_markdown_links(line: str) -> str:
    return MARKDOWN_LINK_RE.sub("", line)


def in_reference_block(line: str, in_block: bool) -> bool:
    if REFERENCE_HEADING_RE.match(line) or APPENDIX_SOURCE_HEADING_RE.match(line):
        return True
    if in_block and HEADING_RE.match(line):
        return False
    return in_block


def check_file(path: Path) -> list[str]:
    errors: list[str] = []
    in_refs = False
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        rel = path.relative_to(ROOT)
        if ABSOLUTE_HOME in line:
            errors.append(f"{rel}:{lineno}: contains absolute user home path")

        previous = in_refs
        in_refs = in_reference_block(line, in_refs)
        if in_refs and not previous:
            continue

        urls = URL_RE.findall(line)
        if not urls:
            continue

        without_links = strip_markdown_links(line)
        if URL_RE.search(without_links):
            errors.append(f"{rel}:{lineno}: raw URL remains outside Markdown link")

        if not in_refs:
            errors.append(f"{rel}:{lineno}: external URL outside recognized reference/source block")
        elif ACCESS_DATE not in line:
            errors.append(f"{rel}:{lineno}: external reference missing {ACCESS_DATE}")
    return errors


def main() -> int:
    if not CHAPTER_DIR.exists():
        print(f"missing chapter directory: {CHAPTER_DIR.relative_to(ROOT)}", file=sys.stderr)
        return 2

    errors: list[str] = []
    files = sorted(CHAPTER_DIR.glob("*.md"))
    if not files:
        print("no chapter markdown files found", file=sys.stderr)
        return 2

    for path in files:
        errors.extend(check_file(path))

    if errors:
        print("ai-personal-growth reference verification failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"ai-personal-growth reference verification ok: {len(files)} chapter file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
