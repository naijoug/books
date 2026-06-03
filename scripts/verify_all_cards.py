#!/usr/bin/env python3
"""Unified tech-card verifier — runs all language-specific verifiers.

Discovers `verify_*_cards.py` scripts in the same directory and runs each one,
collecting pass/fail results. This is the single entry point for CI-style batch
verification of the entire tech-cards-handbook.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parent

# Map verifier script → (language name, expected card count).
# Add new entries as new language chapters get verifiers.
VERIFIERS: dict[str, tuple[str, int]] = {
    "verify_rust_cards.py": ("Rust", 12),
    "verify_go_cards.py": ("Go", 10),
    "verify_python_cards.py": ("Python", 18),
    "verify_react_cards.py": ("React", 18),
    "verify_typescript_cards.py": ("TypeScript", 14),
    "verify_swift_cards.py": ("Swift", 10),
}


@dataclass(frozen=True)
class LanguageResult:
    language: str
    script: str
    passed: bool
    output: str


def run_verifier(script: str, language: str, verbose: bool) -> LanguageResult:
    script_path = SCRIPTS_DIR / script
    if not script_path.exists():
        return LanguageResult(language, script, False, f"script not found: {script_path}")

    command = [sys.executable, str(script_path)]
    if verbose:
        command.append("--verbose")

    result = subprocess.run(command, capture_output=True, text=True, timeout=600)
    combined = (result.stdout + "\n" + result.stderr).strip()
    passed = result.returncode == 0
    return LanguageResult(language, script, passed, combined)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run all language-specific tech-card verifiers.")
    parser.add_argument("--verbose", action="store_true", help="pass --verbose to child scripts")
    parser.add_argument(
        "--language",
        action="append",
        default=None,
        help="run only the specified language(s); can be repeated",
    )
    args = parser.parse_args()

    languages_to_run = {lang.lower() for lang in (args.language or [])}

    results: list[LanguageResult] = []
    for script, (language, _expected) in sorted(VERIFIERS.items(), key=lambda kv: kv[1][0]):
        if languages_to_run and language.lower() not in languages_to_run:
            continue
        print(f"--- {language} ({script}) ---")
        lang_result = run_verifier(script, language, args.verbose)
        results.append(lang_result)
        # Stream output for visibility
        for line in lang_result.output.splitlines():
            print(f"  {line}")
        status = "PASS" if lang_result.passed else "FAIL"
        print(f"  => {status}\n")

    # Summary
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    failed = [r for r in results if not r.passed]

    print(f"{'=' * 40}")
    print(f"Total: {total} languages, {passed} passed, {len(failed)} failed")
    if failed:
        for r in failed:
            print(f"  FAILED: {r.language}")
        return 1

    print("All card verifiers passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
