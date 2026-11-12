---
genitor: "[[decisions]]"
tags: [knowledge-commons, graph-patch, propagation]
---

# patches are semantic instructions anchored on headings, never diffs

Generated skills are project-owned and told to diverge, so a template fix reaches none of them.
Regeneration destroys the local prose that makes them useful; hand-editing rots silently.

`/graph-patch` propagates each fix as a **semantic instruction applied by judgment**, anchored on exact
heading text. Measured before the design rested on it: section headings survive generation byte-identical
across all three graphs while bodies diverge up to 78%. That asymmetry is the whole basis — textual diffing
cannot work when the same section holds three example classes in the template and eight domain-specific
ones downstream.

Each delta carries a `satisfied-test` doing double duty: it answers *is this already present?* before an
edit and *did it land?* after. One artifact, both directions — because a mechanism built to end
silent failure must not have that failure mode itself.

A missing or ambiguous anchor is skipped loudly and never stamped. Semantic relocation is forbidden:
guessing where content moved is where a patcher does real damage to hand-written prose.

**Amended 2026-11-08 (v0.8.0, spec D23).** The premise held for text and broke for numbers. Version
0.6.0 inserted two stages into the template and renumbered, while deltas insert relative to existing
headings and never renumber, so the patch path and the regenerate path forked the same section's heading
(`## 10. Report` in patched graphs, `## 12.` or `## 11.` in fresh ones). For `process` deltas the patcher
now drops the generated stage number from the anchor and from each heading and matches the remaining
title exactly; the number is the one part of the heading the generator assigns rather than the project
writes. A list of exact headings, one per known numbering, was the first form and was dropped the same day,
because each future delta's author would have had to enumerate the numberings and a missed one is a
permanent skip. `knowledge-graph` anchors carry no numbers and stay exact. In 0.9.0 an anchor may also be
an ordered fallback list, for a stage that some graphs don't have at all.

*Decided 2026-07-21. Shipped in knowledge-commons v0.3.0; title matching in v0.8.0.*

## evidence
- [[after 0.6.0 a single delta anchor would have skipped forever in about half the live graphs]]
- [[the anchor list that enumerated stage numberings missed a third one]]

## related
- [[the knowledge-commons plugin generates project-owned prose, not a runtime engine]]
- [[a generator reproduces its template's flaws]]
- [[a check keyed to the template's literal surface fails copies that diverged on purpose]]
