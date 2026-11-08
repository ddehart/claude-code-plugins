---
genitor: "[[patterns]]"
tags: [testing, evaluation, disclosure]
---

# a checker changed after seeing results needs each change stated with its reason

When a test harness is revised after it has graded runs, every revision is a chance to move the line to
where the results already are. Some revisions are genuine bug fixes in the checker, and they look exactly
like the other kind. The reader can only tell them apart from a per-change account: what changed, which
verdicts flipped, and why the old check was wrong. Re-running the checker's own self-test after the last
edit shows it still fails on tampered input. A summary that says "four now pass" hides the one change that
didn't deserve to land.

*One witness (2026-11-06). Open.*

## evidence
- [[five checker changes after seeing results flipped four verdicts]]

## related
- [[a check inherits the frame of whoever briefed it]]
