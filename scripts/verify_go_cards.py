#!/usr/bin/env python3
"""Verify Go tech-card examples by running extracted Markdown code blocks.

The Go chapter keeps each card as one Markdown file with one runnable `go` code
block. This script extracts the blocks into a temporary directory and verifies
them with `go run`. The table-driven testing card is verified with `go test`
because its code block is intentionally a `_test.go` file.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GO_DIR = ROOT / "tech-cards-handbook" / "chapters" / "go"
README = GO_DIR / "README.md"
TEST_CARD = "table-driven-tests-boundaries.md"


@dataclass(frozen=True)
class CheckResult:
    card: str
    command: str
    stdout: str


def read_cards(readme: Path) -> list[str]:
    text = readme.read_text(encoding="utf-8")
    cards: list[str] = []
    for match in re.finditer(r"\[`[^`]+`\]\(([^)]+\.md)\)", text):
        filename = match.group(1)
        if filename != "README.md" and filename not in cards:
            cards.append(filename)
    return cards


def extract_go_blocks(markdown: str) -> list[str]:
    return re.findall(r"```go\s*\n(.*?)\n```", markdown, flags=re.DOTALL)


def run(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=True)


def verify_card(card: str, code: str, temp_dir: Path) -> CheckResult:
    stem = Path(card).stem
    if card == TEST_CARD:
        source = temp_dir / "email_test.go"
        source.write_text(code, encoding="utf-8")
        command = ["go", "test", "email_test.go"]
    else:
        source = temp_dir / f"{stem}.go"
        source.write_text(code, encoding="utf-8")
        command = ["go", "run", source.name]

    result = run(command, cwd=temp_dir)
    return CheckResult(card=card, command=" ".join(command), stdout=result.stdout.strip())


def verify() -> list[CheckResult]:
    cards = read_cards(README)
    if len(cards) != 17:
        raise RuntimeError(f"expected 17 Go cards in README, found {len(cards)}")

    results: list[CheckResult] = []
    with tempfile.TemporaryDirectory(prefix="go-card-verify-") as directory:
        temp_dir = Path(directory)
        for card in cards:
            card_path = GO_DIR / card
            blocks = extract_go_blocks(card_path.read_text(encoding="utf-8"))
            if len(blocks) != 1:
                raise RuntimeError(f"{card}: expected exactly one go code block, found {len(blocks)}")
            results.append(verify_card(card, blocks[0], temp_dir))
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify Go tech-card examples.")
    parser.add_argument("--verbose", action="store_true", help="print each captured program output")
    args = parser.parse_args()

    try:
        results = verify()
    except Exception as error:  # noqa: BLE001 - CLI should surface a concise failure.
        print(f"FAIL: {error}", file=sys.stderr)
        return 1

    print(f"verified {len(read_cards(README))} Go cards with {len(results)} runnable checks")
    for result in results:
        print(f"ok: {result.card} :: {result.command}")
        if args.verbose and result.stdout:
            indented = "\n".join(f"    {line}" for line in result.stdout.splitlines())
            print(indented)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
