---
genitor: "[[observations]]"
tags: [review, regression, method]
date: 2026-08-01
supports: ["[[each fix round manufactures the next round's defects]]"]
---
Four defects in one session were introduced by the immediately preceding fix. A per-line dedup added in
round 1 made only the first shape on a line report, which round 2 found. A template paragraph added in
round 1 left the generator enumerating two conditional pieces where there were now three. A multi-match
fix took a scan from 4 seconds to 541 on a 4.5 MB file, caught only because the run timed out and the
session chose to measure rather than move on. Removing a dead argument from a helper silently broke the
suite's own fail-closed injection, which began passing an empty regex — matching every line — instead of
a malformed one.

The last of those was caught by the suite itself, which is the difference that matters: the fixes pinned
by a test that goes red on their own reversal did not propagate; the ones pinned only by reasoning did.
