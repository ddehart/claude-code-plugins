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

*Decided 2026-07-21. Shipped in knowledge-commons v0.3.0.*

## related
- [[the knowledge-commons plugin generates project-owned prose, not a runtime engine]]
- [[a generator reproduces its template's flaws]]
