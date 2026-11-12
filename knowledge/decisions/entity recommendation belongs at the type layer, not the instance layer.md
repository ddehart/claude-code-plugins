---
genitor: "[[decisions]]"
tags: [knowledge-commons, schema, process]
---

# entity recommendation belongs at the type layer, not the instance layer

"Proactively recommend new entities" was first built as instance-level recognition — noticing individual
nouns lacking an entity *note*. That was one abstraction layer too low, and it shipped, was reviewed five
times, and was applied to a live graph before the requester caught it in a sentence.

`.commons.yml`'s `entity:` list holds **types**, and the generator's interview asks the user to *name
them*. So the request was for a schema-level recommendation: notice that material keeps naming a *kind* of
thing the graph has no type for.

Two properties are deliberate. It is **not** conditional on an entity tier already existing — a graph that
declared none is precisely the one that may need its first, so gating on one disables the check where it
matters most. And it surfaces in the **run report**, not the plan: a schema change is not a note the plan
writes and should not ride a per-run approval.

The correction was made by replacing the two shipped deltas in place rather than superseding them, which
was legitimate only because nothing had stamped them — see
[[in-place rewrite of a shipped delta requires that nothing has stamped it]].

**The route, corrected 2026-11-08 (v0.8.0).** The shipped wording named re-interviewing the generator's
type block as the sanctioned way to add a type, and its delta's test required that. Owners had never
added types that way: they edited `.commons.yml`, the directory, the map, the atlas link, and the
skills' type lists directly, on their own yes. A re-interview also rewrites only the config, not the
hand-sharpened skills, so the skills' type lists go stale. The recommendation now names the direct edit,
lists the skill lines among the work, and calls a re-interview optional, never required. The run still
only recommends; it never makes the edit during the run.

*Decided 2026-07-22. Shipped in knowledge-commons v0.5.0; route corrected in v0.8.0.*

## related
- [[a check inherits the frame of whoever briefed it]]
- [[in-place rewrite of a shipped delta requires that nothing has stamped it]]
- [[the wrong route lived in a template, a delta, eleven skills, graph-init and a config comment]]
