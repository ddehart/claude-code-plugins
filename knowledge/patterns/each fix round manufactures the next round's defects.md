---
genitor: "[[patterns]]"
tags: [review, method, regression]
---

## so what
When a review round's findings are mostly defects the *previous* round's fixes introduced, the process has
started generating work at roughly the rate it closes it. That is a real signal — but it says the fixes
need regression tests, not necessarily that the reviewing should stop.

Read it as a prompt to pin each fix with a test that goes red on its own reversal, before the next round.
Treating it purely as a stop-signal is how a genuinely defective artifact gets declared done.

## evidence
- [[each of four fixes in one session introduced the defect the next round found]]
- [[a stopping rule tuned on prose review misfired on executable code]]
