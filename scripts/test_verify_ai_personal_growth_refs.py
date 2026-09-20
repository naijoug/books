#!/usr/bin/env python3
"""Reference-format regressions; no network or manuscript writes."""
import contextlib
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import verify_ai_personal_growth_refs as verifier


class ReferenceFormatTests(unittest.TestCase):
    def check(self, line, heading='## 参考资料与延伸阅读'):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = root / 'chapter.md'
            path.write_text(f'{heading}\n\n{line}\n', encoding='utf-8')
            with patch.object(verifier, 'ROOT', root):
                return verifier.check_file(path)

    def test_valid_dates_including_historical_and_leap_day(self):
        for value in ('2026-07-23', '2026-09-20', '2024-02-29'):
            with self.subTest(value=value):
                self.assertEqual([], self.check(f'- [Docs](https://example.com/)（访问日期：{value}）'))

    def test_missing_malformed_and_impossible_dates(self):
        for value in ('', '2026-02-29', '2026-13-01', '2026-9-20', '2026-09-200', '0000-01-01'):
            with self.subTest(value=value):
                self.assertTrue(self.check(f'- [Docs](https://example.com/)（访问日期：{value}）'))

    def test_preserves_link_and_location_checks(self):
        self.assertTrue(self.check('- https://example.com/（访问日期：2026-09-20）'))
        self.assertTrue(self.check('- [Docs](https://example.com/)（访问日期：2026-09-20）', '# 正文'))
        self.assertTrue(self.check('/Users/guojian/notes.md'))

    def test_appendix_reference_section(self):
        self.assertEqual([], self.check('- [Docs](https://example.com/)（访问日期：2026-09-20）',
                                        '## A.19 推荐跟踪的公开资料源'))

    def test_empty_chapter_directory_fails(self):
        with tempfile.TemporaryDirectory() as temporary:
            with patch.object(verifier, 'CHAPTER_DIR', Path(temporary)):
                with contextlib.redirect_stderr(io.StringIO()):
                    self.assertEqual(2, verifier.main())


if __name__ == '__main__':
    unittest.main()
