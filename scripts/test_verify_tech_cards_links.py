#!/usr/bin/env python3
"""Regression tests for verify_tech_cards_links.py."""

from __future__ import annotations

import contextlib
import importlib.util
import io
import tempfile
from pathlib import Path

SCRIPT_PATH = Path(__file__).with_name("verify_tech_cards_links.py")


def load_verifier():
    spec = importlib.util.spec_from_file_location("verify_tech_cards_links", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_verifier(module, book_dir: Path) -> tuple[int, str]:
    module.BOOK_DIR = book_dir.resolve()
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        code = module.main()
    return code, output.getvalue()


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_valid_local_links_and_directory_readme(module) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        book = Path(tmp) / "tech-cards-handbook"
        write(book / "README.md", "# Book\n\nSee [AI](chapters/ai-agent/) and [sample](samples/example.md).\n")
        write(book / "chapters/ai-agent/README.md", "# AI Agent\n")
        write(book / "samples/example.md", "# Example\n\nBack to [book](../README.md).\n")

        code, output = run_verifier(module, book)

    assert code == 0, output
    assert "verified tech-cards links" in output


def test_broken_local_link_fails(module) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        book = Path(tmp) / "tech-cards-handbook"
        write(book / "README.md", "# Book\n\nMissing [target](chapters/ai-agent/missing.md).\n")
        write(book / "chapters/ai-agent/README.md", "# AI Agent\n")

        code, output = run_verifier(module, book)

    assert code == 1
    assert "tech-cards link verification failed" in output
    assert "broken local link -> chapters/ai-agent/missing.md" in output


def test_ignores_external_anchor_drafts_and_fenced_code(module) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        book = Path(tmp) / "tech-cards-handbook"
        write(
            book / "README.md",
            "# Book\n\n"
            "[external](https://example.com/missing.md) [anchor](#local)\n\n"
            "```text\n[not checked](missing-in-code.md)\n```\n",
        )
        write(book / ".drafts/draft.md", "[not checked](missing-draft-target.md)\n")

        code, output = run_verifier(module, book)

    assert code == 0, output
    assert "across 1 markdown file(s)" in output


def main() -> int:
    module = load_verifier()
    tests = [
        test_valid_local_links_and_directory_readme,
        test_broken_local_link_fails,
        test_ignores_external_anchor_drafts_and_fenced_code,
    ]
    for test in tests:
        test(module)
        print(f"ok {test.__name__}")
    print(f"verify_tech_cards_links regression tests ok: {len(tests)} test(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
