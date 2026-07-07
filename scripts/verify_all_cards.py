#!/usr/bin/env python3
"""Unified tech-card verifier — runs all language-specific verifiers.

Discovers `verify_*_cards.py` scripts in the same directory and runs each one,
collecting pass/fail results. This is the single entry point for CI-style batch
verification of the entire tech-cards-handbook.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parent
HANDBOOK_DIR = SCRIPTS_DIR.parent / "tech-cards-handbook"
CHAPTERS_DIR = HANDBOOK_DIR / "chapters"

# Map verifier script → (language name, expected card count).
# The expected count is asserted against the chapter directory before the child
# verifier runs, so this table fails fast when a chapter gains or loses cards.
VERIFIERS: dict[str, tuple[str, int]] = {
    "verify_flutter_cards.py": ("Flutter", 14),
    "verify_rust_cards.py": ("Rust", 20),
    "verify_go_cards.py": ("Go", 18),
    "verify_python_cards.py": ("Python", 23),
    "verify_react_cards.py": ("React", 54),
    "verify_typescript_cards.py": ("TypeScript", 31),
    "verify_swift_cards.py": ("Swift", 14),
}


@dataclass(frozen=True)
class LanguageResult:
    language: str
    script: str
    passed: bool
    output: str


def chapter_dir_for(language: str) -> Path:
    """Return the chapter directory for a verifier language label."""
    return CHAPTERS_DIR / language.lower().replace(" ", "-")


def count_chapter_cards(language: str) -> int:
    """Count formal card files in a language chapter, excluding README.md."""
    chapter_dir = chapter_dir_for(language)
    if not chapter_dir.exists():
        raise FileNotFoundError(f"chapter directory not found: {chapter_dir}")
    return sum(1 for path in chapter_dir.glob("*.md") if path.name != "README.md")


def run_verifier(script: str, language: str, expected_count: int, verbose: bool) -> LanguageResult:
    try:
        actual_count = count_chapter_cards(language)
    except FileNotFoundError as exc:
        return LanguageResult(language, script, False, str(exc))
    if actual_count != expected_count:
        chapter_dir = chapter_dir_for(language).relative_to(HANDBOOK_DIR)
        return LanguageResult(
            language,
            script,
            False,
            f"expected {expected_count} cards in {chapter_dir}, found {actual_count}",
        )

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
    supported_languages = {language.lower() for language, _ in VERIFIERS.values()}
    unknown_languages = sorted(languages_to_run - supported_languages)
    if unknown_languages:
        supported = ", ".join(sorted(language for language, _ in VERIFIERS.values()))
        parser.error(
            "unknown --language value(s): "
            f"{', '.join(unknown_languages)}. Supported languages: {supported}"
        )

    results: list[LanguageResult] = []
    for script, (language, expected_count) in sorted(VERIFIERS.items(), key=lambda kv: kv[1][0]):
        if languages_to_run and language.lower() not in languages_to_run:
            continue
        print(f"--- {language} ({script}) ---")
        lang_result = run_verifier(script, language, expected_count, args.verbose)
        results.append(lang_result)
        # Stream output for visibility
        for line in lang_result.output.splitlines():
            print(f"  {line}")
        status = "PASS" if lang_result.passed else "FAIL"
        print(f"  => {status}\n")

    # Run index count verifier
    index_passed = True
    if not languages_to_run:
        index_script = SCRIPTS_DIR / "verify_tech_cards_index.py"
        if index_script.exists():
            print("--- Index counts (verify_tech_cards_index.py) ---")
            idx_result = subprocess.run(
                [sys.executable, str(index_script)],
                capture_output=True, text=True, timeout=120,
            )
            idx_output = (idx_result.stdout + "\n" + idx_result.stderr).strip()
            for line in idx_output.splitlines():
                print(f"  {line}")
            index_passed = idx_result.returncode == 0
            print(f"  => {'PASS' if index_passed else 'FAIL'}\n")
        else:
            print("--- Index counts: SKIPPED (script not found) ---\n")

    # Summary
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    failed = [r for r in results if not r.passed]

    print(f"{'=' * 40}")
    print(f"Total: {total} languages, {passed} passed, {len(failed)} failed")
    if failed:
        for r in failed:
            print(f"  FAILED: {r.language}")
    if not index_passed:
        print("  FAILED: Index counts")
    if failed or not index_passed:
        return 1

    print("All card verifiers and index counts passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
