#!/usr/bin/env python3
"""Regression tests for verify_tech_cards_index.py."""

from __future__ import annotations

import contextlib
import importlib.util
import io
import tempfile
from pathlib import Path

SCRIPT_PATH = Path(__file__).with_name("verify_tech_cards_index.py")


def load_verifier():
    spec = importlib.util.spec_from_file_location("verify_tech_cards_index", SCRIPT_PATH)
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
    module.CHAPTERS_DIR = module.BOOK_DIR / "chapters"
    module.TOP_README = module.BOOK_DIR / "README.md"
    module.CHAPTERS_README = module.CHAPTERS_DIR / "README.md"


def run_verifier(module, book_dir: Path) -> tuple[int, str]:
    configure_module(module, book_dir)
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        code = module.main()
    return code, output.getvalue()


def seed_book(book: Path, *, total: int = 2, ai_count: int = 1, python_count: int = 1) -> None:
    write(
        book / "README.md",
        "# Tech Cards Handbook\n\n"
        f"当前共 {total} 张正式卡片。\n\n"
        "| 章节 | 路径 | 数量 |\n"
        "| --- | --- | --- |\n"
        f"| AI Agent | `chapters/ai-agent/` | {ai_count} 张 |\n"
        f"| Python | `chapters/python/` | {python_count} 张 |\n",
    )
    write(
        book / "chapters/README.md",
        "# Chapters\n\n"
        "| 类型 | 目录 | 数量 |\n"
        "| --- | --- | --- |\n"
        f"| AI Agent 系统实践卡片 | [`ai-agent/`](ai-agent/) | {ai_count} |\n"
        f"| Python 技术卡片 | [`python/`](python/) | {python_count} |\n",
    )
    write(
        book / "chapters/ai-agent/README.md",
        f"# AI Agent\n\n本目录按“一张卡片一个 Markdown 文件”维护，共 {ai_count} 张。\n",
    )
    write(
        book / "chapters/ai-agent/startup-snapshot.md",
        "# Startup snapshot\n",
    )
    write(
        book / "chapters/python/README.md",
        f"# Python\n\n本目录按“一张卡片一个 Markdown 文件”维护，共 {python_count} 张。\n",
    )
    write(book / "chapters/python/pathlib-boundary.md", "# Pathlib boundary\n")


def test_valid_index_counts_pass(module) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        book = Path(tmp) / "tech-cards-handbook"
        seed_book(book)

        code, output = run_verifier(module, book)

    assert code == 0, output
    assert "verified tech-cards index counts: 2 cards across 2 chapters" in output


def test_top_level_total_drift_fails(module) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        book = Path(tmp) / "tech-cards-handbook"
        seed_book(book, total=3)

        code, output = run_verifier(module, book)

    assert code == 1
    assert "index count verification failed" in output
    assert "top-level total says 3, actual count is 2" in output


def test_chapter_and_table_count_drift_fails(module) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        book = Path(tmp) / "tech-cards-handbook"
        seed_book(book, ai_count=2, python_count=1)

        code, output = run_verifier(module, book)

    assert code == 1
    assert "AI Agent chapter README intro says 2, actual is 1" in output
    assert "AI Agent top README count says 2, actual is 1" in output
    assert "AI Agent chapters README count says 2, actual is 1" in output


def main() -> int:
    module = load_verifier()
    tests = [
        test_valid_index_counts_pass,
        test_top_level_total_drift_fails,
        test_chapter_and_table_count_drift_fails,
    ]
    for test in tests:
        test(module)
        print(f"ok {test.__name__}")
    print(f"verify_tech_cards_index regression tests ok: {len(tests)} test(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
