#!/usr/bin/env python3
"""Verify Swift tech-card examples by running extracted Markdown blocks.

The Swift chapter keeps each card as one Markdown file with one or more
`swift` code blocks. This script extracts the blocks, concatenates the
blocks from the same card into a temporary `.swift` file, and runs `swift`
to compile and execute the code.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SWIFT_DIR = ROOT / "tech-cards-handbook" / "chapters" / "swift"
README = SWIFT_DIR / "README.md"
EXPECTED_CARD_COUNT = 10


@dataclass(frozen=True)
class CheckResult:
    card: str
    block_count: int
    command: str
    stdout: str
    stderr: str


def read_cards(readme: Path) -> list[str]:
    text = readme.read_text(encoding="utf-8")
    cards: list[str] = []
    for match in re.finditer(r"\[`[^`]+`\]\(([^)]+\.md)\)", text):
        filename = match.group(1)
        if filename != "README.md" and filename not in cards:
            cards.append(filename)
    return cards


def extract_swift_blocks(markdown: str) -> list[str]:
    return re.findall(r"```swift\s*\n(.*?)\n```", markdown, flags=re.DOTALL)


def command_text(command: list[str]) -> str:
    return " ".join(command)


def verify_card(card: str, blocks: list[str], temp_dir: Path) -> CheckResult:
    stem = Path(card).stem
    source = temp_dir / f"{stem}.swift"
    source.write_text("\n\n".join(blocks), encoding="utf-8")
    command = ["swift", str(source)]
    result = subprocess.run(command, cwd=temp_dir, text=True, capture_output=True)
    return CheckResult(
        card=card,
        block_count=len(blocks),
        command=command_text(command),
        stdout=result.stdout.strip(),
        stderr=result.stderr.strip(),
    )


def verify() -> list[CheckResult]:
    if shutil.which("swift") is None:
        raise RuntimeError("swift is required to run Swift card checks")

    cards = read_cards(README)
    if len(cards) != EXPECTED_CARD_COUNT:
        raise RuntimeError(f"expected {EXPECTED_CARD_COUNT} Swift cards in README, found {len(cards)}")

    results: list[CheckResult] = []
    with tempfile.TemporaryDirectory(prefix="swift-card-verify-") as directory:
        temp_dir = Path(directory)
        for card in cards:
            card_path = SWIFT_DIR / card
            blocks = extract_swift_blocks(card_path.read_text(encoding="utf-8"))
            if not blocks:
                raise RuntimeError(f"{card}: expected at least one swift code block, found 0")
            results.append(verify_card(card, blocks, temp_dir))
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify Swift tech-card examples.")
    parser.add_argument("--verbose", action="store_true", help="print captured compiler output")
    args = parser.parse_args()

    try:
        results = verify()
    except Exception as error:  # noqa: BLE001 - CLI should surface a concise failure.
        print(f"FAIL: {error}", file=sys.stderr)
        return 1

    total_blocks = sum(result.block_count for result in results)
    failures = [r for r in results if "error:" in r.stderr.lower() or r.stdout.startswith("error")]
    print(f"verified {len(results)} Swift cards with {total_blocks} code blocks")
    for result in results:
        status = "ok" if result not in failures else "FAIL"
        print(f"{status}: {result.card} :: blocks={result.block_count} :: {result.command}")
        if args.verbose:
            combined = "\n".join(part for part in [result.stdout, result.stderr] if part)
            if combined:
                indented = "\n".join(f"    {line}" for line in combined.splitlines())
                print(indented)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
