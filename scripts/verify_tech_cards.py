#!/usr/bin/env python3
"""Run the standard tech-cards-handbook verification suite.

This wrapper keeps the routine preflight small for book edits: run the regression
fixtures for the two verifier scripts first, then run the full index and link
checks against the current manuscript.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "scripts"

REGRESSION_COMMANDS = [
    ("link verifier regression", [sys.executable, str(SCRIPT_DIR / "test_verify_tech_cards_links.py")]),
    ("index verifier regression", [sys.executable, str(SCRIPT_DIR / "test_verify_tech_cards_index.py")]),
]
FULL_COMMANDS = [
    ("link verifier", [sys.executable, str(SCRIPT_DIR / "verify_tech_cards_links.py")]),
    ("index verifier", [sys.executable, str(SCRIPT_DIR / "verify_tech_cards_index.py")]),
]


def printable_command(command: list[str]) -> str:
    """Render a command without leaking machine-local absolute paths."""
    rendered: list[str] = []
    for part in command:
        path = Path(part)
        if path.is_absolute():
            try:
                rendered.append(path.resolve().relative_to(ROOT).as_posix())
                continue
            except ValueError:
                if path.resolve() == Path(sys.executable).resolve():
                    rendered.append(Path(sys.executable).name)
                    continue
        rendered.append(part)
    return " ".join(rendered)


def run_step(label: str, command: list[str]) -> bool:
    printable = printable_command(command)
    print(f"==> {label}: {printable}", flush=True)
    result = subprocess.run(command, cwd=ROOT, check=False)
    if result.returncode != 0:
        print(f"tech-cards verification failed at `{label}` with exit {result.returncode}", flush=True)
        return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Run tech-cards verifier regressions and full checks.")
    parser.add_argument(
        "--full-only",
        action="store_true",
        help="Skip verifier regression fixtures and run only full manuscript checks.",
    )
    args = parser.parse_args()

    commands = [] if args.full_only else REGRESSION_COMMANDS.copy()
    commands.extend(FULL_COMMANDS)

    for label, command in commands:
        if not run_step(label, command):
            return 1

    print(f"tech-cards verification suite ok: {len(commands)} step(s)", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
