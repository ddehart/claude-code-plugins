#!/usr/bin/env python3
"""
Tests for deep-review-status.py.

Run from this directory:
    python3 -m unittest test_deep_review_status.py
"""

import importlib.util
import json
import re
import subprocess
import sys
import tempfile
import textwrap
import unittest
from datetime import date, timedelta
from pathlib import Path

SCRIPT = Path(__file__).with_name('deep-review-status.py')
SKILL_DIR = SCRIPT.parent.parent
spec = importlib.util.spec_from_file_location('deep_review_status', SCRIPT)
deep_review_status = importlib.util.module_from_spec(spec)
spec.loader.exec_module(deep_review_status)
status = deep_review_status.status


def days_after(start, count):
    """ISO dates for the `count` days following `start`."""
    first = date.fromisoformat(start)
    return [(first + timedelta(days=n)).isoformat() for n in range(1, count + 1)]


def practice(notes, before='', after=''):
    """A practice file with `notes` under Evolution Notes."""
    return (
        f'# Reflective Practice\n\n## Current Approach\n\n- A question?\n\n{before}'
        f'## Evolution Notes\n\n{notes}\n{after}'
    )


class ChronicleCase(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = Path(tmp.name)

    def chronicle(self, practice_text, entries=()):
        """Build a chronicle directory and return its status."""
        if practice_text is not None:
            (self.dir / 'reflective-practice.md').write_text(practice_text, encoding='utf-8')
        for entry in entries:
            (self.dir / f'{entry}.md').write_text('entry\n', encoding='utf-8')
        return status(self.dir)


class LightweightNotesDoNotResetTheCount(ChronicleCase):
    """The reported bug: a dated lightweight note used to reset the count."""

    def lightweight_notes(self, entries):
        return ''.join(
            f'#### {entry} — Lightweight check (1 entry since the last anchor).\nNothing changed.\n\n'
            for entry in reversed(entries)
        )

    def test_review_is_due_when_every_entry_has_its_own_lightweight_note(self):
        entries = days_after('2026-04-12', 12)
        notes = self.lightweight_notes(entries) + '#### 2026-04-12 (deep review)\nRead them all.\n'
        result = self.chronicle(practice(notes), entries)
        self.assertEqual(result['last_deep_review'], '2026-04-12')
        self.assertEqual(result['count'], 12)
        self.assertTrue(result['due'])

    def test_ten_entries_is_the_threshold(self):
        entries = days_after('2026-04-12', 10)
        notes = self.lightweight_notes(entries) + '#### 2026-04-12 (deep review)\nRead them all.\n'
        result = self.chronicle(practice(notes), entries)
        self.assertEqual(result['count'], 10)
        self.assertTrue(result['due'])

    def test_nine_entries_is_not_due(self):
        entries = days_after('2026-04-12', 9)
        notes = self.lightweight_notes(entries) + '#### 2026-04-12 (deep review)\nRead them all.\n'
        result = self.chronicle(practice(notes), entries)
        self.assertEqual(result['count'], 9)
        self.assertFalse(result['due'])


class RealHeadingShapes(ChronicleCase):
    """Shapes copied from the practice files of real projects."""

    def test_daily_briefing_marker_with_between_reviews_workaround(self):
        before = (
            '## Between Deep Reviews\n\nThe lightweight check writes no dated note. '
            'It adds one line to Cross-pass Log.\n\n'
        )
        after = (
            '## Retired\n\n- A retired question *(retired 2026-08-02)*\n\n'
            '## Cross-pass Log\n\nOne line per lightweight check.\n\n'
            '2026-11-08 Gemini 3.8 Flash (High): nothing new.\n'
            '#### 2026-11-20\nA stray dated heading outside Evolution Notes.\n'
        )
        notes = (
            '#### 2026-11-06 (deep review)\n`/session-chronicle reflect`, the first full review.\n\n'
            '#### 2026-11-06\nLightweight, earlier the same day.\n\n'
            '#### 2026-09-29\nTwo entries since the last note, so no deep review by count.\n'
        )
        entries = ['2026-11-06'] + days_after('2026-11-06', 10)
        result = self.chronicle(practice(notes, before, after), entries)
        self.assertEqual(result['last_deep_review'], '2026-11-06')
        self.assertEqual(result['count'], 10)
        self.assertTrue(result['due'])

    def test_daily_briefing_old_review_named_only_in_the_body(self):
        notes = (
            '#### 2026-04-12\nDeep review at the 10-entry threshold. Read reflections from Apr 1-9.\n\n'
            '#### 2026-04-29\nLightweight check escalated into a partial deep review after the pass.\n\n'
            '#### 2026-04-29 (later)\nNext deep review can decide.\n'
        )
        result = self.chronicle(practice(notes), days_after('2026-04-12', 3))
        self.assertEqual(result['last_deep_review'], '2026-04-12')
        self.assertEqual(result['count'], 3)

    def test_devbox_lightweight_headings_and_older_review_headings(self):
        notes = (
            '#### 2026-10-30 (latest; the 10-30 22:20 file-transfer entry) — Lightweight check '
            '(1 entry since the 10-17 anchor), augmented by an `agy` cross-pass.\n'
            'One watch-item promoted.\n\n'
            '#### 2026-08-23 (later) — The cross-pass named a stagnation the practice had been circling\n'
            'Text.\n\n'
            '#### 2026-07-12 — Deep review (14 entries since the 05-02 anchor). This review retires more.\n'
            'Text.\n\n'
            '#### 2026-07-12 (later) — Lightweight check, and the first cross-pass to actually run\n'
            'Second note today; the deep review above ran in an earlier session.\n\n'
            '### 2026-07-05 — Escalated deep review (after a miscount) + first subagent cross-pass\n'
            'Text.\n\n'
            '### 2026-04-05 — Deep review across 16 reflections\nText.\n'
        )
        result = self.chronicle(practice(notes), ['2026-07-12', '2026-07-13', '2026-10-30'])
        self.assertEqual(result['last_deep_review'], '2026-07-12')
        self.assertEqual(result['count'], 2)

    def test_older_h3_review_headings_are_recognized_alone(self):
        for heading in ('### 2026-07-05 — Escalated deep review (after a miscount) + first subagent',
                        '### 2026-04-05 — Deep review across 16 reflections'):
            with self.subTest(heading=heading):
                result = self.chronicle(practice(f'{heading}\nText.\n'))
                self.assertEqual(result['last_deep_review'], heading[4:14])

    def test_review_escalated_in_a_bold_opening_line(self):
        notes = '#### 2026-07-28\n\n**Escalated from the lightweight check to a deep review.** One entry.\n'
        self.assertEqual(self.chronicle(practice(notes))['last_deep_review'], '2026-07-28')

    def test_previous_no_op_note_shape(self):
        notes = '#### 2026-05-01\nDeep review ran; no changes warranted.\n'
        self.assertEqual(self.chronicle(practice(notes))['last_deep_review'], '2026-05-01')


class NotesThatAreNotDeepReviews(ChronicleCase):
    """A false match suppresses a review, which is the bug, so matching stays strict."""

    def test_notes_mentioning_a_deep_review_are_not_one(self):
        for heading, opening in (
            ('#### 2026-05-01', 'Recorded for the next deep review, not adopted.'),
            ('#### 2026-05-01', 'One entry since the last note, so no deep review by count.'),
            ('#### 2026-05-01', 'Lightweight check escalated into a partial deep review.'),
            ('#### 2026-05-01', 'Deep review not due; three entries.'),
            ('#### 2026-05-01 (fifth, lightweight — concurrent with the fourth)', 'Text.'),
            ('#### 2026-05-01 — Lightweight check; deep review deferred', 'Text.'),
            ('#### 2026-05-01 — Held for the next deep review', 'Text.'),
        ):
            with self.subTest(heading=heading, opening=opening):
                result = self.chronicle(practice(f'{heading}\n{opening}\n'))
                self.assertIsNone(result['last_deep_review'])

    def test_deep_review_later_in_a_note_body_is_not_one(self):
        notes = '#### 2026-05-01\nA lightweight note.\nDeep review ran elsewhere.\n'
        self.assertIsNone(self.chronicle(practice(notes))['last_deep_review'])

    def test_fenced_examples_are_not_notes_and_do_not_end_the_section(self):
        notes = (
            '#### 2026-03-01 (deep review)\nText.\n\n'
            '#### 2026-04-01\nThe prompt:\n\n'
            '```\n## Not a section\n#### 2026-05-01 (deep review)\nDeep review ran.\n```\n\n'
            '#### 2026-04-02 (deep review)\nAfter the fence.\n'
        )
        self.assertEqual(self.chronicle(practice(notes))['last_deep_review'], '2026-04-02')

    def test_invalid_date_is_ignored(self):
        notes = '#### 2026-13-45 (deep review)\nText.\n'
        self.assertIsNone(self.chronicle(practice(notes))['last_deep_review'])


class NoRecognizableDeepReview(ChronicleCase):
    """With no deep review on record, every entry is unreviewed."""

    def test_dated_notes_without_a_review_count_every_entry(self):
        notes = '#### 2026-05-01\nA lightweight note.\n\n#### 2026-04-01\nAnother.\n'
        result = self.chronicle(practice(notes), days_after('2026-03-01', 10))
        self.assertIsNone(result['last_deep_review'])
        self.assertEqual(result['count'], 10)
        self.assertTrue(result['due'])

    def test_young_project_is_not_due(self):
        notes = '#### 2026-05-01\nA lightweight note.\n'
        result = self.chronicle(practice(notes), days_after('2026-03-01', 9))
        self.assertEqual(result['count'], 9)
        self.assertFalse(result['due'])

    def test_seed_file_counts_every_entry(self):
        seed = (SKILL_DIR / 'assets/reflective-practice-seed.md').read_text(encoding='utf-8')
        result = self.chronicle(seed, ['2026-03-01'])
        self.assertIsNone(result['last_deep_review'])
        self.assertEqual(result['count'], 1)

    def test_missing_practice_file_counts_every_entry(self):
        result = self.chronicle(None, days_after('2026-03-01', 2))
        self.assertIsNone(result['last_deep_review'])
        self.assertEqual(result['count'], 2)

    def test_bold_dated_paragraph_is_not_a_note(self):
        notes = '**2026-04-05 — Deep review after 6 entries (2 with reflections, 4 migrated)**\n'
        result = self.chronicle(practice(notes), ['2026-03-01'])
        self.assertIsNone(result['last_deep_review'])
        self.assertEqual(result['count'], 1)


class Dates(ChronicleCase):
    def test_entry_dated_the_same_as_the_review_is_excluded(self):
        notes = '#### 2026-05-01 (deep review)\nText.\n'
        result = self.chronicle(practice(notes), ['2026-04-30', '2026-05-01', '2026-05-02'])
        self.assertEqual(result['entries'], ['2026-05-02.md'])

    def test_lightweight_note_on_the_day_of_the_review_changes_nothing(self):
        notes = (
            '#### 2026-05-01\nLightweight, same day.\n\n'
            '#### 2026-05-01 (deep review)\nText.\n\n'
            '#### 2026-05-01 (later)\nLightweight again.\n'
        )
        result = self.chronicle(practice(notes), ['2026-05-01', '2026-05-02'])
        self.assertEqual(result['last_deep_review'], '2026-05-01')
        self.assertEqual(result['count'], 1)

    def test_newest_review_wins_wherever_it_sits_in_the_file(self):
        notes = (
            '#### 2026-03-01 (deep review)\nText.\n\n'
            '#### 2026-05-01 (deep review)\nText.\n\n'
            '#### 2026-04-01 (deep review)\nText.\n'
        )
        self.assertEqual(self.chronicle(practice(notes))['last_deep_review'], '2026-05-01')

    def test_only_daily_files_count(self):
        (self.dir / 'daily-digest-lessons.md').write_text('notes\n', encoding='utf-8')
        (self.dir / '2026-05-02-extra.md').write_text('notes\n', encoding='utf-8')
        (self.dir / '2026-13-45.md').write_text('notes\n', encoding='utf-8')
        result = self.chronicle(practice('#### 2026-05-01 (deep review)\nText.\n'), ['2026-05-02'])
        self.assertEqual(result['entries'], ['2026-05-02.md'])


class CommandLine(ChronicleCase):
    def run_script(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)

    def test_prints_json(self):
        self.chronicle(practice('#### 2026-05-01 (deep review)\nText.\n'), ['2026-05-02', '2026-05-03'])
        result = self.run_script(str(self.dir))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), {
            'last_deep_review': '2026-05-01',
            'count': 2,
            'threshold': 10,
            'due': False,
            'entries': ['2026-05-03.md', '2026-05-02.md'],
        })

    def test_missing_directory_fails(self):
        result = self.run_script(str(self.dir / 'absent'))
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, '')
        self.assertIn('No chronicle directory', result.stderr)


class SkillInstructions(ChronicleCase):
    """The script only helps if SKILL.md uses it and writes notes it can read."""

    def setUp(self):
        super().setUp()
        self.skill = (SKILL_DIR / 'SKILL.md').read_text(encoding='utf-8')

    def no_op_template(self):
        template = re.search(r'^ *```\n( *#### YYYY-MM-DD.*?Deep review ran.*?)^ *```', self.skill, re.S | re.M)
        self.assertIsNotNone(template, 'no-op template not found in SKILL.md')
        return textwrap.dedent(template[1])

    def test_step_6a_runs_the_script(self):
        self.assertIn('${CLAUDE_SKILL_DIR}/scripts/deep-review-status.py', self.skill)

    def test_no_instruction_counts_from_the_newest_dated_note(self):
        self.assertNotIn('most recent `#### YYYY-MM-DD` heading', self.skill)
        self.assertNotIn('since the last dated Evolution Note', self.skill)

    def test_skill_no_op_template_is_recognized_as_a_review(self):
        note = self.no_op_template().replace('YYYY-MM-DD', '2026-05-01')
        self.assertEqual(self.chronicle(practice(note))['last_deep_review'], '2026-05-01')

    def test_skill_no_op_template_carries_the_marker_in_its_heading(self):
        self.assertTrue(self.no_op_template().startswith('#### YYYY-MM-DD (deep review)\n'))

    def test_seed_shows_the_marker(self):
        seed = (SKILL_DIR / 'assets/reflective-practice-seed.md').read_text(encoding='utf-8')
        self.assertIn('#### YYYY-MM-DD (deep review)', seed)


if __name__ == '__main__':
    unittest.main()
