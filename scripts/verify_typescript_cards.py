#!/usr/bin/env python3
"""Verify TypeScript tech-card examples by type-checking extracted Markdown blocks.

The TypeScript chapter keeps each card as one Markdown file with one or more
`ts`/`typescript` code blocks. This script extracts the blocks, concatenates the
blocks from the same card into a temporary `.ts` file, and runs the same minimal
strict type check documented in the chapter README.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TYPESCRIPT_DIR = ROOT / "tech-cards-handbook" / "chapters" / "typescript"
README = TYPESCRIPT_DIR / "README.md"
EXPECTED_CARD_COUNT = 11
TYPESCRIPT_VERSION = "5.9.3"


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


def extract_typescript_blocks(markdown: str) -> list[str]:
    return re.findall(r"```(?:ts|typescript)\s*\n(.*?)\n```", markdown, flags=re.DOTALL)


def command_text(command: list[str]) -> str:
    return " ".join(command)


def run(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=True)


def verify_card(card: str, blocks: list[str], temp_dir: Path) -> CheckResult:
    stem = Path(card).stem
    source = temp_dir / f"{stem}.ts"
    source.write_text("\n\n".join(blocks), encoding="utf-8")
    command = [
        "npx",
        "-y",
        "-p",
        f"typescript@{TYPESCRIPT_VERSION}",
        "tsc",
        "--noEmit",
        "--strict",
        "--lib",
        "es2020,dom",
        source.name,
    ]
    result = run(command, cwd=temp_dir)
    return CheckResult(
        card=card,
        block_count=len(blocks),
        command=command_text(command),
        stdout=result.stdout.strip(),
        stderr=result.stderr.strip(),
    )


def verify() -> list[CheckResult]:
    if shutil.which("npx") is None:
        raise RuntimeError("npx is required to run TypeScript compiler checks")

    cards = read_cards(README)
    if len(cards) != EXPECTED_CARD_COUNT:
        raise RuntimeError(f"expected {EXPECTED_CARD_COUNT} TypeScript cards in README, found {len(cards)}")

    results: list[CheckResult] = []
    with tempfile.TemporaryDirectory(prefix="typescript-card-verify-") as directory:
        temp_dir = Path(directory)
        for card in cards:
            card_path = TYPESCRIPT_DIR / card
            blocks = extract_typescript_blocks(card_path.read_text(encoding="utf-8"))
            if not blocks:
                raise RuntimeError(f"{card}: expected at least one ts/typescript code block, found 0")
            results.append(verify_card(card, blocks, temp_dir))
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify TypeScript tech-card examples.")
    parser.add_argument("--verbose", action="store_true", help="print captured compiler output")
    args = parser.parse_args()

    try:
        results = verify()
    except Exception as error:  # noqa: BLE001 - CLI should surface a concise failure.
        print(f"FAIL: {error}", file=sys.stderr)
        return 1

    total_blocks = sum(result.block_count for result in results)
    print(f"verified {len(results)} TypeScript cards with {total_blocks} code blocks")
    for result in results:
        print(f"ok: {result.card} :: blocks={result.block_count} :: {result.command}")
        if args.verbose:
            combined = "\n".join(part for part in [result.stdout, result.stderr] if part)
            if combined:
                indented = "\n".join(f"    {line}" for line in combined.splitlines())
                print(indented)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
