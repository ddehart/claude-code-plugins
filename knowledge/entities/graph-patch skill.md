---
genitor: "[[entities]]"
tags: [entity, skill, knowledge-commons]
---

# graph-patch skill

`knowledge-commons:graph-patch`. Propagates template fixes into a project's already-generated,
hand-sharpened `process` and `knowledge-graph` skills without regenerating them.

Reads the plugin's delta log, applies each pending semantic change by judgment against the project's own
prose, verifies it landed by re-running the delta's `satisfied-test`, and records applied ids in a
`generated:` block in `.commons.yml`. Runs from inside the target project, with per-delta approval showing
a concrete diff.

Added in v0.3.0. `Write` is deliberately absent from its allowed-tools — every write is a surgical `Edit`,
and whole-file replacement is its first prohibition.

- **2026-07-22** — first real run, against this graph. Bootstrapped at 0.1.8, six deltas applied and
  verified, stamped to 0.5.0.
