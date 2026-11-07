#!/usr/bin/env python3
"""
Report whether a session-chronicle deep review is due.

Counts daily chronicle files dated strictly after the last deep review recorded
under Evolution Notes in reflective-practice.md.

Usage:
    python3 deep-review-status.py [chronicle-dir]    (default: docs/chronicle)

Prints JSON: last_deep_review, count, due, entries (newest first).
Exits 2 if the chronicle directory does not exist.
"""

import json
import re
import sys
from datetime import date
from pathlib import Path

THRESHOLD = 10

HEADING = re.compile(r'^(#{1,6})\s+(.*?)\s*$')
EVOLUTION_SECTION = re.compile(r'evolution notes\b', re.I)
DATED_NOTE = re.compile(r'^(\d{4}-\d{2}-\d{2})\b(.*)$')
FENCE = re.compile(r'^\s*(`{3,}|~{3,})(.*)$')

# `(deep review)` is the marker SKILL.md writes. The other shapes come from older
# notes: headings like `— Deep review (14 entries...)`, `— Deep review across 16
# reflections`, and `— Escalated deep review (after a miscount)`, and plain dated
# headings over `Deep review at the 10-entry threshold`, the previous no-op note
# `Deep review ran; ...`, or `**Escalated from the lightweight check to a deep review.**`
# A parenthetical qualifier may come first, as in `(later) (deep review)`.
# What follows `deep review` is an allowlist: `Deep review can wait` must not match.
REVIEW_HEADING = re.compile(
    r'^[\s—–:-]*(?:\([^)]*\)[\s—–:-]*)*?'
    r'\(?(?:(?:escalated|full) )?deep review(?:\)|\s*$|\s+\(|\s+across\b)',
    re.I,
)
REVIEW_OPENING = re.compile(
    r'^[*_]*(?:deep review ran[;:,.]'
    r'|deep review at the \d+-entry threshold'
    r'|escalated (?:from [^.]*? )?to a deep review\b)',
    re.I,
)


def is_date(text):
    try:
        return date.fromisoformat(text).isoformat() == text
    except ValueError:
        return False


def closes_fence(opening, line):
    """Whether `line` closes the fence opened by the FENCE match `opening`."""
    fence = FENCE.match(line)
    return bool(
        fence
        and fence[1][0] == opening[1][0]
        and len(fence[1]) >= len(opening[1])
        and not fence[2].strip()
    )


def unfenced_lines(text):
    """Yield the lines outside fenced code. An unclosed fence hides nothing."""
    lines = text.splitlines()
    index = 0
    while index < len(lines):
        opening = FENCE.match(lines[index])
        if opening:
            close = next(
                (n for n in range(index + 1, len(lines)) if closes_fence(opening, lines[n])),
                None,
            )
            if close is not None:
                index = close + 1
                continue
        yield lines[index]
        index += 1


def evolution_notes(text):
    """Return the dated notes under Evolution Notes, in file order.

    Each note is a dict: date, rest (the heading after the date), and opening
    (the first line of its body). Older practice files date their notes with `###`
    rather than `####`, so any heading inside the section can be a note. Fenced
    code is skipped, so a quoted prompt or template can neither add a note nor end
    the section.
    """
    notes = []
    section_level = None
    awaiting_opening = None
    for line in unfenced_lines(text):
        heading = HEADING.match(line)
        if heading:
            level = len(heading[1])
            awaiting_opening = None
            if section_level and level <= section_level:
                section_level = None
            if not section_level:
                if level <= 3 and EVOLUTION_SECTION.match(heading[2]):
                    section_level = level
                continue
            dated = DATED_NOTE.match(heading[2])
            if dated and is_date(dated[1]):
                awaiting_opening = {'date': dated[1], 'rest': dated[2], 'opening': ''}
                notes.append(awaiting_opening)
        elif awaiting_opening and line.strip():
            awaiting_opening['opening'] = line.strip()
            awaiting_opening = None
    return notes


def is_deep_review(note):
    """Whether a dated note records a deep review.

    Most notes that mention a deep review are lightweight notes deferring to the
    next one, and a false match suppresses a review. So only the known heading
    and opening shapes count. A miss costs an early review, and SKILL.md has the
    review confirm its own note was recognized.
    """
    return bool(REVIEW_HEADING.match(note['rest']) or REVIEW_OPENING.match(note['opening']))


def status(chronicle_dir):
    """Compute the deep-review status of a chronicle directory."""
    practice = chronicle_dir / 'reflective-practice.md'
    text = practice.read_text(encoding='utf-8', errors='replace') if practice.is_file() else ''

    # A future date can only be a typo, and as the anchor it would stop the count.
    today = date.today().isoformat()
    reviews = [
        note['date'] for note in evolution_notes(text)
        if is_deep_review(note) and note['date'] <= today
    ]
    last_review = max(reviews, default=None)

    entries = sorted(
        (p.name for p in chronicle_dir.glob('*.md')
         if p.is_file() and is_date(p.stem) and p.stem > (last_review or '')),
        reverse=True,
    )

    return {
        'last_deep_review': last_review,
        'count': len(entries),
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
