---
genitor: "[[observations]]"
tags: [graph-patch, anchors, review]
date: 2026-11-08
supports: ["[[a check keyed to the template's literal surface fails copies that diverged on purpose]]", "[[a list of negating phrasings cannot be complete, so allow what may follow]]"]
---
The first fix for the split heading numbers let a delta's anchor list every exact heading the section was known to carry: `## 10. Report` and `## 12. Report`. A code review found a third: a graph generated at 0.6.0 without a synthesis tier omits that stage and renumbers, so its section is `## 11. Report`. No live graph had that heading, but nothing prevented one, and a graph with it would have skipped the delta on every run. The heading was added to the list, and then the list itself was replaced by title matching, because every future delta's author would have had to enumerate the numberings and a missed one becomes a permanent skip.
