---
genitor: "[[entities]]"
tags: [skill, knowledge-commons, generated]
---

# the generated process skill

The project-owned orchestrator emitted by [[graph-init skill]] into a target project. Flow: resolve input
to a canonical `source:` → search the graph for the ledger note (augment mode if found) → size-adaptive
inspect (inline under a threshold, subagent fan-out above) → propose a plan `[y / edit / explain]` → single
approval → run in dependency order with continue-and-collect on failures → write the `processed:` stamp →
report and append a changelog entry. When `promotes-to:` is set, a promotion tail asks "does any of this
generalize?" and folds candidates into the same approved plan. Owned by the target project and expected to
drift.

## interaction log
- 2026-07-15 — first cold run surfaced three defects (called a human-facing skill not the headless script,
  UUID-keyed unreadable queue, a named de-dup safeguard with no mechanism).
