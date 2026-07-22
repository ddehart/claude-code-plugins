---
genitor: "[[questions]]"
tags: [knowledge-commons, schema, process]
---

# should the type-gap check cover attractor types, not just entity types

`step10-entity-type-gap` has the run report recommend a new **entity** type when material keeps naming a
category the graph has no type for. Hours after it shipped, its first real run surfaced a missing type in a
different tier: this graph had no `question` attractor, so a genuinely open matter had nowhere to live. The
check could not see it.

The asymmetry may be principled or may be an oversight. Arguments each way:

- **Entity types are cheap and additive** — a lookup tier, no association surface, low blast radius. An
  attractor type changes what evidence can support and how association works, so recommending one is a
  heavier suggestion.
- **But the failure is identical in shape.** A category with no home is a schema gap whichever tier it
  belongs to, and the graph that most needs the recommendation is the one whose type set is narrowest —
  exactly the case here.

**What would settle it:** whether a second graph hits the same wall in a tier the check doesn't cover. One
instance is not yet a case for widening a check that is days old.

Note the sibling graphs diverge here: one declares `question`, one declares `hypothesis` and `constraint`,
one declared neither until now. There may be no single right attractor vocabulary to recommend — which is
itself an argument for the check naming the gap rather than proposing the type.

*Opened 2026-07-22. One instance.*

## related
- [[naming a failure shape confers no immunity to it]]
