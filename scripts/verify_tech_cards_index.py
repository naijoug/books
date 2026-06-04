#!/usr/bin/env python3
"""Verify tech-cards-handbook index card counts.

The language chapter READMEs are the source of reading order, while the top-level
indexes summarize total/card counts. This script keeps those summary numbers from
silently drifting when cards are added.
"""

from __future__ import annotations

import re
from pathlib import Path


BOOK_DIR = Path(__file__).resolve().parents[1] / "tech-cards-handbook"
CHAPTERS_DIR = BOOK_DIR / "chapters"
TOP_README = BOOK_DIR / "README.md"
CHAPTERS_README = CHAPTERS_DIR / "README.md"

LANGUAGE_LABELS = {
    "ai-agent": "AI Agent",
    "flutter": "Flutter",
    "go": "Go",
    "python": "Python",
    "react": "React",
    "rust": "Rust",
    "swift": "Swift",
    "typescript": "TypeScript",
}


def count_cards(chapter_dir: Path) -> int:
    return sum(1 for path in chapter_dir.glob("*.md") if path.name != "README.md")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def main() -> int:
    counts = {
        chapter_dir.name: count_cards(chapter_dir)
        for chapter_dir in sorted(CHAPTERS_DIR.iterdir())
        if chapter_dir.is_dir()
    }
    total = sum(counts.values())

    failures: list[str] = []
    top = read(TOP_README)
    chapters = read(CHAPTERS_README)

    total_match = re.search(r"当前共 (\d+) 张正式卡片。", top)
    if not total_match:
        failures.append(f"missing total count in {TOP_README.relative_to(BOOK_DIR.parent)}")
    elif int(total_match.group(1)) != total:
        failures.append(
            f"top-level total says {total_match.group(1)}, actual count is {total}"
        )

    for slug, expected in counts.items():
        label = LANGUAGE_LABELS.get(slug, slug)
        chapter_readme_path = CHAPTERS_DIR / slug / "README.md"
        chapter_readme = read(chapter_readme_path)
        intro_match = re.search(
            r"本目录按[\"“]一张卡片一个 Markdown 文件[\"”]维护，共 (\d+) 张。",
            chapter_readme,
        )
        if not intro_match:
            failures.append(
                f"missing chapter intro count in {chapter_readme_path.relative_to(BOOK_DIR.parent)}"
            )
        elif int(intro_match.group(1)) != expected:
            failures.append(
                f"{label} chapter README intro says {intro_match.group(1)}, actual is {expected}"
            )

        top_pattern = rf"\| {re.escape(label)} \| `chapters/{re.escape(slug)}/` \| (\d+) 张"
        top_match = re.search(top_pattern, top)
        if not top_match:
            failures.append(f"missing {label} row in {TOP_README.relative_to(BOOK_DIR.parent)}")
        elif int(top_match.group(1)) != expected:
            failures.append(f"{label} top README count says {top_match.group(1)}, actual is {expected}")

        chapters_pattern = rf"\| {re.escape(label)} (?:技术卡片|系统实践卡片) \| \[`{re.escape(slug)}/`\]\({re.escape(slug)}/\) \| (\d+) \|"
        chapters_match = re.search(chapters_pattern, chapters)
        if not chapters_match:
            failures.append(f"missing {label} row in {CHAPTERS_README.relative_to(BOOK_DIR.parent)}")
        elif int(chapters_match.group(1)) != expected:
            failures.append(
                f"{label} chapters README count says {chapters_match.group(1)}, actual is {expected}"
            )

    if failures:
        print("index count verification failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(f"verified tech-cards index counts: {total} cards across {len(counts)} chapters")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
