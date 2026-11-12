---
genitor: "[[decisions]]"
tags: [knowledge-commons, graph-patch, agents, approval]
---

# a fleet patch run drafts every graph before applying any, under one batched approval

`/graph-patch` is built for one project and one person answering y / edit / skip per delta. Propagating a
fix to every downstream graph that way means one session and one round of approvals per graph. Instead,
when Derek asked for the propagation to be run rather than handed back as a list, it ran in two phases:

1. **Draft everywhere.** One read-only subagent per graph follows the skill up to the approval point and
   writes the exact before and after text for each pending delta to a shared review file. A script then
   checks that every *before* block appears exactly once in its file.
2. **One review, then apply.** Derek reads the combined file; uniform edits are approved in bulk and only
   the flagged judgment calls get their own question. The same subagents then apply, re-run each test,
   stamp, and commit.

Two properties carry the weight. The drafting round reaches every graph before any graph stamps anything,
so a defect in the shared delta can still be fixed at its source; see
[[drafting all thirteen graphs before applying any left the defective delta unstamped and fixable in place]].
And the approval stays in the main context, with the parallelism one level down, the same split as
[[processing a live session is not delegable to a subagent]].

Pushing each project's commit was a per-run override Derek chose, so the change was backed up
off-machine. `/graph-patch`'s own default, commit and never push, is unchanged. A repo whose quality gate
can't run on the patching machine lands through a pull request so CI runs the gate instead.

*Decided 2026-11-08; used twice that week, for 25 and 19 edits across 13 graphs.*

## evidence
- [[drafting all thirteen graphs before applying any left the defective delta unstamped and fixable in place]]

## related
- [[a superseding delta states the full end state and the superseded one is never applied]]
- [[should graph-patch carry a multi-graph proposal-only mode]]
- [[break the self-review chain with a different agent]]
