#!/usr/bin/env python3
"""Verify Rust tech-card examples by compiling extracted Markdown code blocks.

The Rust chapter keeps each card as one Markdown file with one runnable `rust`
code block. This script extracts those blocks into a temporary directory,
compiles them with `rustc`, and runs the produced binaries. The tests card is
checked twice: once as a normal program and once with `rustc --test`.
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
RUST_DIR = ROOT / "tech-cards-handbook" / "chapters" / "rust"
README = RUST_DIR / "README.md"


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


def extract_rust_blocks(markdown: str) -> list[str]:
    return re.findall(r"```rust\s*\n(.*?)\n```", markdown, flags=re.DOTALL)


def run(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=True)


def compile_and_run(card: str, source: Path, temp_dir: Path) -> list[CheckResult]:
    stem = Path(card).stem
    executable = temp_dir / stem
    rustc = ["rustc"]
    if card == "async-is-not-parallel.md":
        rustc.append("--edition=2021")
    compile_cmd = [*rustc, str(source), "-o", str(executable)]
    run(compile_cmd, cwd=temp_dir)
    program = run([str(executable)], cwd=temp_dir)
    results = [
        CheckResult(
            card=card,
            command=" ".join([*compile_cmd, "&&", str(executable)]),
            stdout=program.stdout.strip(),
        )
    ]

    if card == "tests-cover-success-and-failure.md":
        test_executable = temp_dir / f"{stem}-test"
        test_compile_cmd = ["rustc", "--test", str(source), "-o", str(test_executable)]
        run(test_compile_cmd, cwd=temp_dir)
        test_run = run([str(test_executable)], cwd=temp_dir)
        results.append(
            CheckResult(
                card=card,
                command=" ".join([*test_compile_cmd, "&&", str(test_executable)]),
                stdout=test_run.stdout.strip(),
            )
        )

    return results


def verify() -> list[CheckResult]:
    cards = read_cards(README)
    if len(cards) != 13:
        raise RuntimeError(f"expected 13 Rust cards in README, found {len(cards)}")

    results: list[CheckResult] = []
    with tempfile.TemporaryDirectory(prefix="rust-card-verify-") as directory:
        temp_dir = Path(directory)
        for card in cards:
            card_path = RUST_DIR / card
            blocks = extract_rust_blocks(card_path.read_text(encoding="utf-8"))
            if len(blocks) != 1:
                raise RuntimeError(f"{card}: expected exactly one rust code block, found {len(blocks)}")
            source = temp_dir / f"{Path(card).stem}.rs"
            source.write_text(blocks[0], encoding="utf-8")
            results.extend(compile_and_run(card, source, temp_dir))
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify Rust tech-card examples.")
    parser.add_argument("--verbose", action="store_true", help="print each captured program output")
    args = parser.parse_args()

    try:
        results = verify()
    except Exception as error:  # noqa: BLE001 - CLI should surface a concise failure.
        print(f"FAIL: {error}", file=sys.stderr)
        return 1

    print(f"verified {len(read_cards(README))} Rust cards with {len(results)} runnable checks")
    for result in results:
        print(f"ok: {result.card} :: {result.command}")
        if args.verbose and result.stdout:
            indented = "\n".join(f"    {line}" for line in result.stdout.splitlines())
            print(indented)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
