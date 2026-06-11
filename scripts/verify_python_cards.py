#!/usr/bin/env python3
"""Verify Python tech-card examples by running extracted Markdown code blocks.

The Python chapter keeps each card as one Markdown file with one runnable
`python` code block. This script extracts each block into a temporary directory
and runs the same kind of check documented in the README:

- normal cards: execute the extracted file with Python 3.11 by default;
- type-hint card: additionally run pyright;
- testing card: run pytest through uv so pytest does not need to be preinstalled.
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
PYTHON_DIR = ROOT / "tech-cards-handbook" / "chapters" / "python"
README = PYTHON_DIR / "README.md"
TYPE_CARD = "type-hints-express-contracts.md"
TEST_CARD = "tests-cover-behavior-first.md"
EXPECTED_CARD_COUNT = 22


@dataclass(frozen=True)
class CheckResult:
    card: str
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


def extract_python_blocks(markdown: str) -> list[str]:
    return re.findall(r"```python\s*\n(.*?)\n```", markdown, flags=re.DOTALL)


def run(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=True)


def command_text(command: list[str]) -> str:
    return " ".join(command)


def verify_card(card: str, code: str, temp_dir: Path, python_bin: str) -> list[CheckResult]:
    stem = Path(card).stem
    source = temp_dir / f"{stem}.py"
    source.write_text(code, encoding="utf-8")

    if card == TEST_CARD:
        command = ["uv", "run", "--with", "pytest", "python", "-m", "pytest", "-q", source.name]
        result = run(command, cwd=temp_dir)
        return [CheckResult(card=card, command=command_text(command), stdout=result.stdout.strip(), stderr=result.stderr.strip())]

    results: list[CheckResult] = []
    command = [python_bin, source.name]
    result = run(command, cwd=temp_dir)
    results.append(CheckResult(card=card, command=command_text(command), stdout=result.stdout.strip(), stderr=result.stderr.strip()))

    if card == TYPE_CARD:
        command = ["npx", "-y", "pyright@1.1.407", source.name]
        result = run(command, cwd=temp_dir)
        results.append(CheckResult(card=card, command=command_text(command), stdout=result.stdout.strip(), stderr=result.stderr.strip()))

    return results


def verify(python_bin: str) -> list[CheckResult]:
    if shutil.which(python_bin) is None:
        raise RuntimeError(f"Python executable not found: {python_bin}")
    if shutil.which("uv") is None:
        raise RuntimeError("uv is required to verify the pytest card")
    if shutil.which("npx") is None:
        raise RuntimeError("npx is required to verify the pyright check")

    cards = read_cards(README)
    if len(cards) != EXPECTED_CARD_COUNT:
        raise RuntimeError(f"expected {EXPECTED_CARD_COUNT} Python cards in README, found {len(cards)}")

    results: list[CheckResult] = []
    with tempfile.TemporaryDirectory(prefix="python-card-verify-") as directory:
        temp_dir = Path(directory)
        for card in cards:
            card_path = PYTHON_DIR / card
            blocks = extract_python_blocks(card_path.read_text(encoding="utf-8"))
            if len(blocks) != 1:
                raise RuntimeError(f"{card}: expected exactly one python code block, found {len(blocks)}")
            results.extend(verify_card(card, blocks[0], temp_dir, python_bin))
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify Python tech-card examples.")
    parser.add_argument("--python", default="python3.11", help="Python executable used for normal cards")
    parser.add_argument("--verbose", action="store_true", help="print each captured program output")
    args = parser.parse_args()

    try:
        results = verify(args.python)
    except Exception as error:  # noqa: BLE001 - CLI should surface a concise failure.
        print(f"FAIL: {error}", file=sys.stderr)
        return 1

    print(f"verified {len(read_cards(README))} Python cards with {len(results)} runnable checks")
    for result in results:
        print(f"ok: {result.card} :: {result.command}")
        if args.verbose:
            combined = "\n".join(part for part in [result.stdout, result.stderr] if part)
            if combined:
                indented = "\n".join(f"    {line}" for line in combined.splitlines())
                print(indented)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
