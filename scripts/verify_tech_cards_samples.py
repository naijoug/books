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
CHAPTERS_DIR = BOOK_DIR / "chapters"
AI_AGENT_DIR = CHAPTERS_DIR / "ai-agent"
SAMPLES_DIR = BOOK_DIR / "samples"
SAMPLES_README = SAMPLES_DIR / "README.md"
SAMPLE_PACK = SAMPLES_DIR / "ai-agent-sample-pack.md"

SAMPLE_LINK_PATTERN = re.compile(r"\]\((ai-agent-[^)]+?\.md)\)")
SAMPLE_PACK_CARD_HEADING_PATTERN = re.compile(r"^## 卡片 (\d+)：", re.MULTILINE)
SAMPLE_PACK_SELECTED_COUNT_PATTERN = re.compile(r"(\d+) 张精选卡片")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def sample_files() -> set[str]:
    return {path.name for path in SAMPLES_DIR.glob("*.md") if path.name != "README.md"}


def ai_agent_card_count() -> int:
    return sum(1 for path in AI_AGENT_DIR.glob("*.md") if path.name != "README.md")


def readme_links() -> set[str]:
    return set(SAMPLE_LINK_PATTERN.findall(read(SAMPLES_README)))


def sample_pack_ai_agent_count_claims() -> list[int]:
    text = read(SAMPLE_PACK)
    patterns = [
        r"AI Agent 系列（共 (\d+) 张）",
        r"AI Agent 系列的 (\d+) 张卡片",
    ]
    claims: list[int] = []
    for pattern in patterns:
        claims.extend(int(match) for match in re.findall(pattern, text))
    return claims


def sample_pack_selected_card_count() -> int:
    headings = [int(match) for match in SAMPLE_PACK_CARD_HEADING_PATTERN.findall(read(SAMPLE_PACK))]
    return max(headings, default=0)


def sample_pack_selected_count_claims() -> list[int]:
    return [int(match) for match in SAMPLE_PACK_SELECTED_COUNT_PATTERN.findall(read(SAMPLE_PACK))]


def main() -> int:
    files = sample_files()
    links = readme_links()
    expected_ai_agent_count = ai_agent_card_count()
    selected_card_count = sample_pack_selected_card_count()

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

    for claimed in sample_pack_ai_agent_count_claims():
        if claimed != expected_ai_agent_count:
            failures.append(
                "sample pack AI Agent count says "
                f"{claimed}, actual chapter count is {expected_ai_agent_count}"
            )

    for claimed in sample_pack_selected_count_claims():
        if claimed != selected_card_count:
            failures.append(
                "sample pack selected-card count says "
                f"{claimed}, actual sample pack has {selected_card_count} card heading(s)"
            )

    if failures:
        print("sample index verification failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(
        f"verified tech-cards sample index: {len(files)} sample file(s) linked from samples/README.md; "
        f"AI Agent count claims match {expected_ai_agent_count} card(s); "
        f"sample pack selected-card claims match {selected_card_count} card(s)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
