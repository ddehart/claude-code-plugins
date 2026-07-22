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

*Decided 2026-07-22. Shipped in knowledge-commons v0.5.0.*

## related
- [[a check inherits the frame of whoever briefed it]]
- [[in-place rewrite of a shipped delta requires that nothing has stamped it]]
