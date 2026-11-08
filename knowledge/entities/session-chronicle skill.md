---
genitor: "[[entities]]"
tags: [entity, skill, meta-claude]
---

# session-chronicle skill

`meta-claude:session-chronicle`. Writes the two-layer session journal in `docs/chronicle/` (a neutral
chronicle plus a first-person reflection) and evolves the project's `reflective-practice.md`. It is this
graph's synthesis producer: `/process` invokes it, never reimplements it.

Step 6 picks a review tier. Since 1.9.0 the count that decides it is a script,
`scripts/deep-review-status.py`, which counts daily files since the newest **deep review** and prints JSON.
A deep review writes `#### YYYY-MM-DD (deep review)` and then re-runs the script to confirm it was
recognized. Lightweight notes no longer move the count. See
[[session-chronicle counts entries since the newest deep review, in tested code]].

- **2026-11-06** — the counter fix, three review passes, and a scratch-harness end-to-end test with a 1.8.3 negative control. Source: [[session 9d4bafbd — the deep-review counter fix, tested end to end]].
