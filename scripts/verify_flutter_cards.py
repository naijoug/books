#!/usr/bin/env python3
"""Verify Flutter tech-card structure.

The Flutter chapter currently contains Flutter widget snippets that are meant for
reading, not standalone execution without a Flutter SDK/project. This verifier
therefore checks the maintainable contract that every card must satisfy:
README registration, required sections, at least one Dart code block, and no
machine-local absolute paths.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FLUTTER_DIR = ROOT / "tech-cards-handbook" / "chapters" / "flutter"
README = FLUTTER_DIR / "README.md"
EXPECTED_CARD_COUNT = 14
REQUIRED_SECTION_RE = {
    "问题": re.compile(r"(?:^##\s+问题|\*\*问题\*\*)", re.MULTILINE),
    "要点": re.compile(r"(?:^##\s+要点|\*\*要点\*\*)", re.MULTILINE),
    "示例": re.compile(r"(?:^##\s+示例|\*\*示例\*\*)", re.MULTILINE),
    "坑": re.compile(r"(?:^##\s+坑|\*\*坑\*\*)", re.MULTILINE),
    "检查": re.compile(r"(?:^##\s+检查|\*\*检查\*\*)", re.MULTILINE),
}
CODE_BLOCK_RE = re.compile(r"```dart\s*\n(.*?)\n```", re.DOTALL)
LOCAL_PATH_RE = re.compile(re.escape(str(Path.home())) + r"[^\s)`]*")


@dataclass(frozen=True)
class CheckResult:
    card: str
    block_count: int


def read_cards(readme: Path) -> list[str]:
    text = readme.read_text(encoding="utf-8")
    cards: list[str] = []
    for match in re.finditer(r"\[`[^`]+`\]\(([^)]+\.md)\)", text):
        filename = match.group(1)
        if filename != "README.md" and filename not in cards:
            cards.append(filename)
    return cards


def verify_card(card: str) -> CheckResult:
    card_path = FLUTTER_DIR / card
    if not card_path.exists():
        raise RuntimeError(f"{card}: file listed in README but not found")

    text = card_path.read_text(encoding="utf-8")
    missing_sections = [name for name, pattern in REQUIRED_SECTION_RE.items() if not pattern.search(text)]
    if missing_sections:
        raise RuntimeError(f"{card}: missing required sections: {', '.join(missing_sections)}")

    if LOCAL_PATH_RE.search(text):
        raise RuntimeError(f"{card}: contains machine-local absolute path")

    blocks = CODE_BLOCK_RE.findall(text)
    if not blocks:
        raise RuntimeError(f"{card}: expected at least one dart code block, found 0")

    return CheckResult(card=card, block_count=len(blocks))


def verify() -> list[CheckResult]:
    if not README.exists():
        raise RuntimeError(f"README not found: {README}")

    cards = read_cards(README)
    if len(cards) != EXPECTED_CARD_COUNT:
        raise RuntimeError(f"expected {EXPECTED_CARD_COUNT} Flutter cards in README, found {len(cards)}")

    if LOCAL_PATH_RE.search(README.read_text(encoding="utf-8")):
        raise RuntimeError("Flutter README contains machine-local absolute path")

    return [verify_card(card) for card in cards]


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify Flutter tech-card structure.")
    parser.add_argument("--verbose", action="store_true", help="print each checked card")
    args = parser.parse_args()

    try:
        results = verify()
    except Exception as error:  # noqa: BLE001 - CLI should surface a concise failure.
        print(f"FAIL: {error}", file=sys.stderr)
        return 1

    total_blocks = sum(result.block_count for result in results)
    print(f"verified {len(results)} Flutter cards with {total_blocks} dart code blocks")
    if args.verbose:
        for result in results:
            print(f"ok: {result.card} :: dart_blocks={result.block_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
