#!/usr/bin/env python3
"""Verify tech-cards-handbook sample index coverage.

The samples directory is a set of copy-ready agent inputs rather than formal
cards. Its README is the routing surface: every sample file should be linked
there, and the README should not point at deleted sample files.
"""

from __future__ import annotations

import re
from pathlib import Path

BOOK_DIR = Path(__file__).resolve().parents[1] / "tech-cards-handbook"
SAMPLES_DIR = BOOK_DIR / "samples"
SAMPLES_README = SAMPLES_DIR / "README.md"

SAMPLE_LINK_PATTERN = re.compile(r"\]\((ai-agent-[^)]+?\.md)\)")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def sample_files() -> set[str]:
    return {path.name for path in SAMPLES_DIR.glob("*.md") if path.name != "README.md"}


def readme_links() -> set[str]:
    return set(SAMPLE_LINK_PATTERN.findall(read(SAMPLES_README)))


def main() -> int:
    files = sample_files()
    links = readme_links()

    missing = sorted(files - links)
    stale = sorted(links - files)

    failures: list[str] = []
    if missing:
        failures.append(
            "sample README missing link(s): " + ", ".join(f"samples/{name}" for name in missing)
        )
    if stale:
        failures.append(
            "sample README has stale link(s): " + ", ".join(f"samples/{name}" for name in stale)
        )

    if failures:
        print("sample index verification failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(f"verified tech-cards sample index: {len(files)} sample file(s) linked from samples/README.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
