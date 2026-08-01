---
genitor: "[[observations]]"
tags: [verification, evidence, silent-failure]
date: 2026-08-01
supports: ["[[naming a failure shape confers no immunity to it]]"]
---
Checking whether a session transcript had been pruned, a run searched
`ls ~/.claude/projects/*claude-code-plugins*/284b79f5….jsonl`, got no match, and reported *"Verified
independently: 284b79f5 is genuinely absent, so `raw: unavailable` is a true statement rather than a
copied claim."*

That session had run in a `commons-scaffold` worktree, so its transcript sat under a *commons* slug. The
glob could not have matched it whether or not the file existed. It existed: 2.8 MB, 1,311 lines, findable
in one command by UUID across all slugs.

Two things make this more than an ordinary mistake. The check was run *because* the claim shouldn't be
taken on trust — the discipline fired and produced a false confirmation, because the probe presupposed
its answer. And the claim was load-bearing: it was the closing argument for the whole change and had
propagated into four artifacts, one of them a shipped delta rationale that a future `/graph-patch` reads
to adapt the edit into other repositories.

A verification only counts if it could have come back the other way.
