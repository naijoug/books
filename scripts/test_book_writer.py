#!/usr/bin/env python3
"""Book-writing workflow contracts; all model calls are mocked."""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = Path(os.environ.get('BOOK_WRITER_SCRIPT', ROOT / '.agents/book_writer.py'))
spec = importlib.util.spec_from_file_location('book_writer', SCRIPT)
writer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(writer)


def response(text='正文', *, code=0, stderr='', subtype='success', is_error=False):
    return subprocess.CompletedProcess([], code, json.dumps({
        'subtype': subtype, 'is_error': is_error, 'result': text,
    }), stderr)


class BookWriterTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        (self.root / '.agents').mkdir()
        for name in ('writer_agent.md', 'editor_agent.md', 'search_prompt.md'):
            shutil.copyfile(SCRIPT.parent / name, self.root / '.agents' / name)
        (self.root / 'AGENTS.md').write_text('Root rules', encoding='utf-8')
        (self.root / 'book/chapters').mkdir(parents=True)
        (self.root / 'book/README.md').write_text('Target readers', encoding='utf-8')
        self.source = self.root / 'book/chapters/one.md'
        self.source.write_text('Original manuscript', encoding='utf-8')
        self.system = writer.BookWriterSystem(self.root)
        self.process = patch.object(writer.subprocess, 'run', return_value=response())
        self.run = self.process.start()
        self.addCleanup(self.process.stop)

    def test_review_has_no_file_side_effects_and_reads_only(self):
        before = set(self.root.rglob('*'))
        self.assertEqual('正文\n', self.system.review_chapter(self.source))
        self.assertEqual(before, set(self.root.rglob('*')))
        self.assertEqual('Original manuscript', self.source.read_text())
        arguments = self.run.call_args.args[0]
        self.assertEqual('Read', arguments[arguments.index('--tools') + 1])
        self.assertIn('Target readers', self.run.call_args.kwargs['input'])

    def test_explicit_report_output_and_no_overwrite(self):
        report = self.root / 'review.md'
        self.system.review_chapter(self.source, output=report)
        self.assertEqual('正文\n', report.read_text())
        with self.assertRaises(FileExistsError):
            self.system.review_chapter(self.source, output=report)
        self.assertEqual(1, self.run.call_count)

    def test_new_writing_stays_in_drafts_without_forced_search(self):
        self.system.write_chapter('Topic', 'book/.drafts/new.md')
        self.assertEqual('正文\n', (self.root / 'book/.drafts/new.md').read_text())
        self.assertEqual(1, self.run.call_count)
        with self.assertRaises(ValueError):
            self.system.write_chapter('Topic', 'book/chapters/new.md')
        with self.assertRaises(FileExistsError):
            self.system.write_chapter('Topic', 'book/.drafts/new.md')
        with self.assertRaises(ValueError):
            self.system.write_chapter('Topic', '../outside.md')
        self.assertEqual(1, self.run.call_count)

    def test_symlink_cannot_route_draft_into_chapters(self):
        (self.root / 'book/.drafts').symlink_to(self.root / 'book/chapters', target_is_directory=True)
        with self.assertRaises(ValueError):
            self.system.write_chapter('Topic', 'book/.drafts/new.md')
        self.run.assert_not_called()

    def test_errors_never_become_manuscripts(self):
        bad_results = [response(code=1, stderr='failed'), response(''),
                       response(subtype='error_max_turns', is_error=True),
                       subprocess.CompletedProcess([], 0, 'not JSON', '')]
        target = self.root / 'book/.drafts/failed.md'
        for result in bad_results:
            with self.subTest(result=result):
                self.run.return_value = result
                with self.assertRaises(RuntimeError):
                    self.system.write_chapter('Topic', target)
                self.assertFalse(target.exists())
        self.run.side_effect = subprocess.TimeoutExpired('claude', 300)
        with self.assertRaises(RuntimeError):
            self.system.write_chapter('Topic', target)
        self.assertFalse(target.exists())

    def test_stderr_is_not_saved_as_content(self):
        self.run.return_value = response('Manuscript', stderr='diagnostic')
        with patch.object(writer.sys, 'stderr'):
            self.system.write_chapter('Topic', 'book/.drafts/new.md')
        self.assertEqual('Manuscript\n', (self.root / 'book/.drafts/new.md').read_text())

    def test_rewrite_creates_candidate_preserving_source(self):
        self.run.side_effect = [response('Specific feedback'), response('Revised manuscript')]
        target = self.system.rewrite_chapter(self.source)
        self.assertEqual(self.root / 'book/.drafts/one_v2.md', target)
        self.assertEqual('Original manuscript', self.source.read_text())
        self.assertEqual('Revised manuscript\n', target.read_text())
        self.assertIn('Specific feedback', self.run.call_args.kwargs['input'])

    def test_apply_requires_unchanged_source(self):
        self.system.rewrite_chapter(self.source, apply=True, feedback='Fix this')
        self.assertEqual('正文\n', self.source.read_text())
        def concurrent_edit(*args, **kwargs):
            self.source.write_text('User edit', encoding='utf-8')
            return response('Replacement')
        self.run.side_effect = concurrent_edit
        with self.assertRaises(RuntimeError):
            self.system.rewrite_chapter(self.source, apply=True, feedback='Fix this')
        self.assertEqual('User edit', self.source.read_text())
        self.assertEqual([], list(self.source.parent.glob('.book-writer-*')))

    def test_research_uses_actual_prompt_and_read_web_tools(self):
        self.system.search_for_topic('An API fact')
        prompt = self.run.call_args.kwargs['input']
        self.assertIn('模型记忆', prompt)
        self.assertIn('An API fact', prompt)
        arguments = self.run.call_args.args[0]
        self.assertEqual('Read,WebSearch,WebFetch', arguments[arguments.index('--tools') + 1])

    def test_full_workflow_revises_and_returns_final_review(self):
        self.run.side_effect = [response('Draft'), response('Fix X'),
                                response('Revised'), response('Pending evidence Y')]
        result = self.system.run_full_workflow('Topic', 'book/.drafts/new.md')
        self.assertEqual(4, self.run.call_count)
        self.assertIn('Pending evidence Y', result)
        self.assertEqual('Revised\n', (self.root / 'book/.drafts/new_v2.md').read_text())
        self.assertFalse(list((self.root / 'book/chapters').glob('REVIEW_*')))

    def test_full_failure_preserves_prior_draft_and_stops(self):
        self.run.side_effect = [response('Draft'), response(code=1, stderr='Review failed')]
        with self.assertRaises(RuntimeError):
            self.system.run_full_workflow('Topic', 'book/.drafts/new.md')
        self.assertEqual('Draft\n', (self.root / 'book/.drafts/new.md').read_text())
        self.assertFalse((self.root / 'book/.drafts/new_v2.md').exists())
        self.assertEqual(2, self.run.call_count)

    def test_existing_candidate_blocks_full_before_generation(self):
        (self.root / 'book/.drafts').mkdir()
        (self.root / 'book/.drafts/new_v2.md').write_text('Previous candidate')
        with self.assertRaises(FileExistsError):
            self.system.run_full_workflow('Topic', 'book/.drafts/new.md')
        self.run.assert_not_called()


if __name__ == '__main__':
    unittest.main()
