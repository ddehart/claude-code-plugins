---
genitor: "[[questions]]"
tags: [knowledge-commons, graph-patch, agents]
---

# should graph-patch carry a multi-graph proposal-only mode

`/graph-patch` runs inside one project and asks one person to approve each delta. Twice in one week a fix
had to reach every downstream graph, and both times the orchestration was built in conversation: a
read-only drafter per graph that stops at the approval point, a combined review file, a script check that
each proposed *before* block appears once, one approval pass, then the same drafters apply and stamp. None
of that is in the skill, so the next fleet run re-derives it from the last one's transcript, and per-run
overrides (push, PR routing for repos whose gate can't run locally) live only in each brief.

Arguments each way:

- **Codify it.** It ran twice in production and found a defect in a shared delta that no review caught.
  The drafting phase is mechanical enough to specify, and a stated mode would carry the environment
  preflight (dirty tree, behind remote, hook health, credentials) that the ad hoc runs met one repo at a
  time.
- **Leave it in orchestration.** The skill's per-delta approval in the project's own session is a real
  safeguard, and a multi-graph mode moves the human gate into a document someone may stop reading. Two
  uses in one week, both by the plugin's author, may be a burst rather than a need.

Would settle it: a third fleet run, especially one driven by someone other than the plugin's author, or a
fleet run where the batched review let a bad edit through.

## evidence
- [[drafting all thirteen graphs before applying any left the defective delta unstamped and fixable in place]]

## related
- [[a fleet patch run drafts every graph before applying any, under one batched approval]]
- [[build enforcement against demonstrated need, not anticipated failure]]
