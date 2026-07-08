#!/usr/bin/env python3
"""Regression tests for the unified tech-card verifier."""

from __future__ import annotations

import importlib.util
import io
import sys
from contextlib import contextmanager, redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
WRAPPER_PATH = ROOT / "scripts" / "verify_all_cards.py"


def load_wrapper():
    spec = importlib.util.spec_from_file_location("verify_all_cards_under_test", WRAPPER_PATH)
    if spec is None or spec.loader is None:
        raise AssertionError(f"cannot load wrapper from {WRAPPER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@contextmanager
def wrapper_argv(*args: str):
    with patch.object(sys, "argv", [str(WRAPPER_PATH), *args]):
        yield


def test_unknown_language_fails_before_running_verifiers() -> None:
    module = load_wrapper()
    calls: list[str] = []
    stderr = io.StringIO()

    def fake_run_verifier(script: str, language: str, expected_count: int, verbose: bool):
        calls.append(language)
        return module.LanguageResult(language, script, True, "")

    with patch.object(module, "run_verifier", fake_run_verifier), wrapper_argv("--language", "Python", "--language", "TypoScript"):
        try:
            with redirect_stderr(stderr):
                module.main()
        except SystemExit as exc:
            assert exc.code == 2
        else:
            raise AssertionError("unknown --language should exit with argparse error")

    assert calls == []
    message = stderr.getvalue()
    assert "unknown --language value(s): typoscript" in message
    assert "Supported languages:" in message
    assert "Python" in message


def test_known_language_filter_runs_only_selected_language() -> None:
    module = load_wrapper()
    calls: list[str] = []
    stdout = io.StringIO()

    def fake_run_verifier(script: str, language: str, expected_count: int, verbose: bool):
        calls.append(language)
        return module.LanguageResult(language, script, True, f"{language} ok")

    with patch.object(module, "run_verifier", fake_run_verifier), wrapper_argv("--language", "Python"):
        with redirect_stdout(stdout):
            assert module.main() == 0

    assert calls == ["Python"]
    output = stdout.getvalue()
    assert "--- Python (verify_python_cards.py) ---" in output
    assert "Index counts" not in output


def test_missing_script_message_uses_repo_relative_path() -> None:
    module = load_wrapper()

    with patch.object(module, "count_chapter_cards", lambda language: 23):
        result = module.run_verifier("verify_missing_cards.py", "Python", 23, verbose=False)

    assert result.passed is False
    assert result.output == "script not found: scripts/verify_missing_cards.py"
    assert str(ROOT) not in result.output


def test_missing_chapter_message_uses_repo_relative_path() -> None:
    module = load_wrapper()

    with patch.object(module, "CHAPTERS_DIR", module.HANDBOOK_DIR / "_missing_chapters"):
        result = module.run_verifier("verify_python_cards.py", "Python", 23, verbose=False)

    assert result.passed is False
    assert result.output == "chapter directory not found: tech-cards-handbook/_missing_chapters/python"
    assert str(ROOT) not in result.output


def main() -> int:
    tests = [
        test_unknown_language_fails_before_running_verifiers,
        test_known_language_filter_runs_only_selected_language,
        test_missing_script_message_uses_repo_relative_path,
        test_missing_chapter_message_uses_repo_relative_path,
    ]
    for test in tests:
        test()
    print(f"verify_all_cards regression tests ok: {len(tests)} test(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
