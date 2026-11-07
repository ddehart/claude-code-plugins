#!/usr/bin/env python3
"""
Report whether a session-chronicle deep review is due.

Counts daily chronicle files dated strictly after the last deep review recorded
under Evolution Notes in reflective-practice.md.

Usage:
    python3 deep-review-status.py [chronicle-dir]    (default: docs/chronicle)

Prints JSON: last_deep_review, count, threshold, due, entries (newest first).
Exits 2 if the chronicle directory does not exist.
"""

import json
import re
import sys
from datetime import date
from pathlib import Path

THRESHOLD = 10

ENTRY_FILE = re.compile(r'^(\d{4}-\d{2}-\d{2})\.md$')
HEADING = re.compile(r'^(#{1,6})\s+(.*?)\s*$')
DATED_NOTE = re.compile(r'^(\d{4}-\d{2}-\d{2})\b(.*)$')
FENCE = re.compile(r'^\s*(```|~~~)')


def is_date(text):
    try:
        date.fromisoformat(text)
    except ValueError:
        return False
    return True


def evolution_notes(text):
    """Return the dated notes under Evolution Notes, in file order.

    Each note is a dict: date, rest (the heading after the date), and opening
    (the first line of its body). Dated notes are `###` or `####` headings; older
    practice files use `###`. Fenced code is skipped, so a quoted prompt or
    template can neither add a note nor end the section.
    """
    notes = []
    in_section = in_fence = False
    awaiting_opening = None
    for line in text.splitlines():
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        heading = HEADING.match(line)
        if heading and len(heading[1]) <= 2:
            in_section = heading[2].lower() == 'evolution notes'
            awaiting_opening = None
        elif not in_section:
            continue
        elif heading:
            awaiting_opening = None
            dated = DATED_NOTE.match(heading[2])
            if dated and len(heading[1]) >= 3 and is_date(dated[1]):
                awaiting_opening = {'date': dated[1], 'rest': dated[2], 'opening': ''}
                notes.append(awaiting_opening)
        elif awaiting_opening and line.strip():
            awaiting_opening['opening'] = line.strip()
            awaiting_opening = None
    return notes


def is_deep_review(note):
    """Whether a dated note records a deep review."""
    return True


def status(chronicle_dir):
    """Compute the deep-review status of a chronicle directory."""
    chronicle_dir = Path(chronicle_dir)
    practice = chronicle_dir / 'reflective-practice.md'
    text = practice.read_text(encoding='utf-8') if practice.is_file() else ''

    reviews = [n['date'] for n in evolution_notes(text) if is_deep_review(n)]
    last_review = max(reviews, default=None)

    entries = sorted(
        (p.name for p in chronicle_dir.iterdir()
         if ENTRY_FILE.match(p.name) and is_date(p.stem)),
        reverse=True,
    )
    if last_review:
        entries = [name for name in entries if name[:10] > last_review]

    return {
        'last_deep_review': last_review,
        'count': len(entries),
        'threshold': THRESHOLD,
        'due': len(entries) >= THRESHOLD,
        'entries': entries,
    }


def main(argv):
    if len(argv) > 2:
        print('Usage: deep-review-status.py [chronicle-dir]', file=sys.stderr)
        return 2
    chronicle_dir = Path(argv[1] if len(argv) == 2 else 'docs/chronicle')
    if not chronicle_dir.is_dir():
        print(f'No chronicle directory at {chronicle_dir}', file=sys.stderr)
        return 2
    print(json.dumps(status(chronicle_dir), indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
