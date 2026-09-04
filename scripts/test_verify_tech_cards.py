#!/usr/bin/env python3
"""Regression tests for the tech-cards verification wrapper."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
WRAPPER_PATH = ROOT / "scripts" / "verify_tech_cards.py"


def load_wrapper():
    spec = importlib.util.spec_from_file_location("verify_tech_cards_under_test", WRAPPER_PATH)
    if spec is None or spec.loader is None:
        raise AssertionError(f"cannot load wrapper from {WRAPPER_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@contextmanager
def wrapper_argv(*args: str):
    with patch.object(sys, "argv", [str(WRAPPER_PATH), *args]):
        yield


def test_default_runs_regressions_before_full_checks() -> None:
    module = load_wrapper()
    labels: list[str] = []

    def fake_run_step(label: str, command: list[str]) -> bool:
        labels.append(label)
        return True

    with patch.object(module, "run_step", fake_run_step), wrapper_argv():
        assert module.main() == 0

    assert labels == [
        "link verifier regression",
        "index verifier regression",
        "sample index regression",
        "link verifier",
        "index verifier",
        "sample index verifier",
    ]


def test_full_only_skips_regressions() -> None:
    module = load_wrapper()
    labels: list[str] = []

    def fake_run_step(label: str, command: list[str]) -> bool:
        labels.append(label)
        return True

    with patch.object(module, "run_step", fake_run_step), wrapper_argv("--full-only"):
        assert module.main() == 0

    assert labels == ["link verifier", "index verifier", "sample index verifier"]


def test_failure_stops_at_first_failed_step() -> None:
    module = load_wrapper()
    labels: list[str] = []

    def fake_run_step(label: str, command: list[str]) -> bool:
        labels.append(label)
        return label != "index verifier regression"

    with patch.object(module, "run_step", fake_run_step), wrapper_argv():
        assert module.main() == 1

    assert labels == ["link verifier regression", "index verifier regression"]


def test_run_step_flushes_heading_before_subprocess() -> None:
    module = load_wrapper()
    events: list[str] = []

    def fake_print(*args, **kwargs) -> None:
        events.append(f"print:{args[0]}:flush={kwargs.get('flush')}")

    def fake_run(command: list[str], cwd: Path, check: bool) -> subprocess.CompletedProcess[str]:
        events.append("subprocess")
        return subprocess.CompletedProcess(command, 0)

    with patch.object(module, "print", fake_print), patch.object(module.subprocess, "run", fake_run):
        assert module.run_step("link verifier", ["python", "verify.py"])

    assert events == ["print:==> link verifier: python verify.py:flush=True", "subprocess"]


def test_printable_command_uses_relative_script_paths() -> None:
    module = load_wrapper()

    rendered = module.printable_command([
        sys.executable,
        str(ROOT / "scripts" / "verify_tech_cards_links.py"),
    ])

    assert rendered == f"{Path(sys.executable).name} scripts/verify_tech_cards_links.py"
    assert str(ROOT) not in rendered


def main() -> int:
    tests = [
        test_default_runs_regressions_before_full_checks,
        test_full_only_skips_regressions,
        test_failure_stops_at_first_failed_step,
        test_run_step_flushes_heading_before_subprocess,
        test_printable_command_uses_relative_script_paths,
    ]
    for test in tests:
        test()
    print(f"verify_tech_cards wrapper regression tests ok: {len(tests)} test(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
