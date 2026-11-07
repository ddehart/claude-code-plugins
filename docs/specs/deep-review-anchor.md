# Deep Review Anchor for Session Chronicle

Amends the counting mechanics in [auto-trigger-deep-review.md](auto-trigger-deep-review.md). Everything else in that spec still stands.

## Problem

Step 6a counted chronicle files since the newest dated heading under Evolution Notes. That anchor means "the practice last changed," but the threshold needs "a deep review last ran." Lightweight checks also write dated notes, so each one reset the count and the mandatory review never fired.

Evidence on 2026-11-06: `daily-briefing` had 35 dated notes across 27 entries after 04-29, a count stuck at 0 to 2, and no full deep review from 04-12 to 11-06. `devbox` shows the same one-note-per-entry pattern, with 27 files since its last deep review on 07-12.

## Decisions

**R1. The anchor is the newest deep review, not the newest dated note.** Lightweight notes stay dated and stay in Evolution Notes. They no longer affect the count.

**R2. The count is code.** Step 6a was prose a model followed, so no test could be deterministic, and models had already miscounted it (`devbox` 07-05, "Escalated deep review (after a miscount)"). `scripts/deep-review-status.py` does the count and `test_deep_review_status.py` covers it. This follows session-export's script and stdlib `unittest` convention. An eval was rejected: it would test one model's reading of the prose rather than the rule, and it can't run deterministically.

**R3. New deep reviews write `#### YYYY-MM-DD (deep review)`.** No external state, per the original spec's goal. `daily-briefing` already used this marker by hand.

**R4. Recognition is deliberately strict.** Most notes that mention a deep review are lightweight notes deferring to the next one. A false match suppresses a review, which is the bug, while a miss costs one early review that then writes the current marker. So a note counts only if:

- the heading text right after the date is the marker or an older form: `(deep review)`, `— Deep review ...`, `— Escalated deep review ...`
- or its first body line is a known older opening: `Deep review ran`, `Deep review at`, `Escalated ... deep review`

Older files also use `###` for dated notes, so both levels count.

**R5. With no deep review on record, every chronicle file counts.** This matches the original spec's legacy-project case. Falling back to the newest dated note would keep the bug in exactly the projects it has hurt most: `wellstead` has 91 dated notes across 36 entries and no recorded review.

The cost is one review per project on its next chronicle write, capped at 20 entries. On 2026-11-06 that is 6 of the 14 practice files on the devbox: `devbox`, `claude-code-plugins`, `airbnb-prep`, `daily-digest`, `persimmon-care`, and `wellstead`. `daily-digest` was already due under the old rule, because it has no dated headings.

**R6. Unchanged:** the 10-file threshold, the unit (files, not sessions), excluding files dated the same as the anchor, and the 20-entry cap.

**R7. `daily-digest`'s bold dated paragraphs are not parsed.** `**2026-04-05 — Deep review after 6 entries**` is the only file with this shape, and the result matches today's behavior.

**R8. Minor version bump (1.9.0).** The diff is a fix, but deep reviews will now fire in projects where they didn't, and the rule says to round up when ambiguous.

## Compatibility

`daily-briefing`'s Between Deep Reviews workaround keeps working: its Cross-pass Log sits outside Evolution Notes, and its marker is the canonical one. The workaround is no longer needed, and removing it is that project's call.

The `chronicle-cross-pass` skill's Prompt B reads the three newest Evolution Notes. It doesn't depend on the anchor, so it needs no change.

## Verification

Tests were written against a literal transcription of the old rule and failed there (19 failures, including the core case) before the fix. Restoring the old rule in a copy fails them again.
