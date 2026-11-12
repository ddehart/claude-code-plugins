---
genitor: "[[observations]]"
tags: [generated-skills, fleet, graph-init]
date: 2026-11-08
supports: ["[[a generator reproduces its template's flaws]]"]
---
None of the deltas in the first fleet run touched the plugin paths written into generated skills, yet almost every drafter reported one as stale in its own graph. A live check found six of 13 knowledge-graph skills pointing at a conventions file that no longer existed (old plugin versions, another machine's home directory, a remote-plugin cache), and the other seven resolving only because an old cache directory hadn't been pruned. The pattern was invisible from inside any one graph. It traced to the generator stamping resolved, version-pinned paths at generation time. The fix was spun into its own spec-first session, which shipped 0.9.0 (reach plugin files through skills, not paths), and a second fleet run applied it the same week.
