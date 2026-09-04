#!/usr/bin/env python3
"""Regression tests for verify_tech_cards_samples.py."""

from __future__ import annotations

import contextlib
import importlib.util
import io
import tempfile
from pathlib import Path

SCRIPT_PATH = Path(__file__).with_name("verify_tech_cards_samples.py")


def load_verifier():
    spec = importlib.util.spec_from_file_location("verify_tech_cards_samples", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def configure_module(module, book_dir: Path) -> None:
    module.BOOK_DIR = book_dir.resolve()
    module.SAMPLES_DIR = module.BOOK_DIR / "samples"
    module.SAMPLES_README = module.SAMPLES_DIR / "README.md"


def run_verifier(module, book_dir: Path) -> tuple[int, str]:
    configure_module(module, book_dir)
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        code = module.main()
    return code, output.getvalue()


def seed_samples(book: Path, *, readme: str | None = None) -> None:
    write(book / "samples/ai-agent-sample-pack.md", "# Sample pack\n")
    write(book / "samples/ai-agent-dirty-workspace-one-pager.md", "# Dirty workspace\n")
    write(
        book / "samples/README.md",
        readme
        if readme is not None
        else (
            "# Samples\n\n"
            "- [sample pack](ai-agent-sample-pack.md)\n"
            "- [dirty workspace](ai-agent-dirty-workspace-one-pager.md)\n"
        ),
    )


def test_valid_sample_index_passes(module) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        book = Path(tmp) / "tech-cards-handbook"
        seed_samples(book)

        code, output = run_verifier(module, book)

    assert code == 0, output
    assert "verified tech-cards sample index: 2 sample file(s) linked from samples/README.md" in output


def test_missing_sample_link_fails(module) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        book = Path(tmp) / "tech-cards-handbook"
        seed_samples(book, readme="# Samples\n\n- [sample pack](ai-agent-sample-pack.md)\n")

        code, output = run_verifier(module, book)

    assert code == 1
    assert "sample index verification failed" in output
    assert "sample README missing link(s): samples/ai-agent-dirty-workspace-one-pager.md" in output


def test_stale_sample_link_fails(module) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        book = Path(tmp) / "tech-cards-handbook"
        seed_samples(
            book,
            readme=(
                "# Samples\n\n"
                "- [sample pack](ai-agent-sample-pack.md)\n"
                "- [dirty workspace](ai-agent-dirty-workspace-one-pager.md)\n"
                "- [deleted](ai-agent-deleted-template.md)\n"
            ),
        )

        code, output = run_verifier(module, book)

    assert code == 1
    assert "sample README has stale link(s): samples/ai-agent-deleted-template.md" in output


def main() -> int:
    module = load_verifier()
    tests = [
        test_valid_sample_index_passes,
        test_missing_sample_link_fails,
        test_stale_sample_link_fails,
    ]
    for test in tests:
        test(module)
        print(f"ok {test.__name__}")
    print(f"verify_tech_cards_samples regression tests ok: {len(tests)} test(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
