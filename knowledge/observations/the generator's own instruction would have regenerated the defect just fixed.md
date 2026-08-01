---
genitor: "[[observations]]"
tags: [knowledge-commons, generator, templates, silent-failure]
date: 2026-07-26
supports: ["[[a generator reproduces its template's flaws]]", "[[naming a failure shape confers no immunity to it]]"]
---
The spec correcting an inverted pipeline listed every artifact needing a change and omitted the one that
emits new pipelines. A SLOT instruction in the process template told the generator that when two source
tiers cover the same events it must name a primary and state a guard — the exact arrangement being removed,
since under the correction a synthesis is not a tier at all. Left unchanged, every newly generated graph
would have been built with the inversion baked in by the generator, after the fix shipped. The author's own
audit missed it; an independent cold read found it while planning the template edits. The author had spent
the session tracing how this defect reached four artifacts and none of the producing ones, and then
reproduced that shape in the change list meant to correct it.

## source
- [[session f64160a1 — the process pipeline correction, specced not built]]
