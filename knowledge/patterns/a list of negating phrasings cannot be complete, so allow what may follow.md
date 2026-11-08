---
genitor: "[[patterns]]"
tags: [recognition, natural-language, strictness]
---

# a list of negating phrasings cannot be complete, so allow what may follow

Recognizing a phrase in free text while rejecting the cases that deny it invites a list of negating words:
"not due", "deferred", "held". Writers have more ways to say no than any list holds, and every missed
phrasing is accepted as the thing it denies. Naming what may follow the phrase inverts the failure: an
unlisted phrasing is rejected instead, which is visible and recoverable when something downstream checks
for it.

*One witness (2026-11-06). Open.*

## evidence
- [[a negation word list let a new phrasing through, and an allowlist replaced it]]

## related
- [[a fail-safe argument holds only if a miss happens once]]
