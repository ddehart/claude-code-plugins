---
genitor: "[[observations]]"
tags: [graph-patch, agents, fleet]
date: 2026-11-08
supports: ["[[a fleet patch run drafts every graph before applying any, under one batched approval]]", "[[in-place rewrite of a shipped delta requires that nothing has stamped it]]", "[[execution against real data catches what authoring and review miss]]"]
---
The first fleet patch run sent a read-only drafter into each of 13 graphs before any graph was patched. Three drafters independently reported that the new delta's cadence test required a marker form their graph didn't use, and a fourth found a graph that kept the record another way. Because nothing had been applied yet, no graph had stamped the delta, so it could be corrected in place in the plugin (0.8.1) instead of through yet another superseding delta. Had each graph been patched interactively in turn, the graphs that happened to match the literal test would have stamped the flawed delta first. The convergence of independent drafters on the same defect was what settled that the test, not the graphs, was wrong.
