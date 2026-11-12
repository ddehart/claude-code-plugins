---
genitor: "[[decisions]]"
tags: [knowledge-commons, graph-patch, append-only]
---

# a superseding delta states the full end state and the superseded one is never applied

When a shipped delta turns out partly wrong and graphs have already stamped it, its entry can't be
edited: a graph that recorded the id would never see the change. So a new delta carries the correction
and names the old id in an optional `supersedes:` field. The successor states **the whole corrected end
state, with its own complete `satisfied-test`**. While the old id is still pending in a graph,
`/graph-patch` never selects it, and stamps it once the successor verifies or is found already
satisfied. A graph that already applied the old delta just gets the successor, whose test fails only on
the corrected part, so redundancy detection confines the edit to that.

Without the field, selection runs in log order, so a graph that never applied the old delta would be
offered the wrong content first and its removal second: two contradictory approvals, with a skip on the
second leaving the wrong content standing.

The first form of the fix had the patcher apply the old delta *as the successor amended it*. That made
the patcher merge two instructions by judgment and derive the post-condition at runtime, which gives up
the one thing a delta's authored test exists to provide. Two cleanup reviewers flagged it independently,
and the "replaced, not applied" form took its place the same day. Before either, the supersession lived
only in a YAML comment the patcher had no rule to read.

The cost of a complete successor surfaced at once: restating the old delta's points for completeness
tightened one of them. See [[the successor delta's restated cadence test required a bracket the original never did]].

*Decided 2026-11-08 (spec D24). Shipped in knowledge-commons v0.8.0.*

## related
- [[in-place rewrite of a shipped delta requires that nothing has stamped it]]
- [[patches are semantic instructions anchored on headings, never diffs]]
- [[each fix round manufactures the next round's defects]]
