---
genitor: "[[sources]]"
source: "session:284b79f5-c34f-4ad3-b97d-9c78cdc9c46f"
tags: [source, knowledge-commons]
processed:
  - date: 2026-07-15
    ran: [5 decisions, 8 patterns, 15 observations, 7 entities, 1 reference]
    skipped: ["version bumps 0.1.1–0.1.7 and one-off fixes (operational)", "repo-revert / PR-close / chronicle-writing logistics (session logistics)", "Aiwyn /process reference particulars (other-domain, stripped)"]
    errored: []
---

The commons-scaffold worktree session in which the **knowledge-commons** plugin was designed and shipped.
It opened with Derek's regret that the design had become "a monstrosity of validation, prematurely
solving a problem I don't have" — an accreted ~1,900-line executable validator, vendored YAML parser,
write-transactions, and lifecycle machinery. Reading the year-old working reference (all prose, a checker
it largely ignored, and thriving) refuted the machinery's premise. The validator PR was closed unmerged,
the design shrank to reference weight (~1,150 lines of prose across a few files), and the plugin then
drove seven use-triggered releases (0.1.0 → 0.1.7) in a single day, each bump from a real defect surfaced
by an actual run.

The durable spine: a knowledge-graph generator whose health rests on an LLM writing to prose conventions
plus a human approving every plan — no validator. This session is **one witness**; the patterns it seeds
are open, not settled.

**Off-tier source.** This is a raw session transcript, not a chronicle path or docs URL, so it is keyed on
the session UUID. `docs/chronicle/2026-07-15.md` is the curated write-up of the same arc and is still in
the processing queue — a later chronicle run should augment these notes rather than duplicate them.
