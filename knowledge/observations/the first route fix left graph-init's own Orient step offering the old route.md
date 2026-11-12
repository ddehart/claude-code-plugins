---
genitor: "[[observations]]"
tags: [graph-init, review]
date: 2026-11-08
supports: ["[[a generator reproduces its template's flaws]]"]
---
The fix for the wrong entity-type route corrected the process template, the knowledge-graph template, and the delta log. A code review then found that graph-init itself, when run on an already-initialized graph, still offered to re-interview its blocks with no word that adding a type is a direct edit. A user running it to add a type would have re-created the stale-list problem the fix was retiring. The opening sweep had grepped for the claim's wording and missed the generator's own step because it never used those words.
