---
genitor: "[[reference]]"
tags: [knowledge-commons, config, reference]
---

# the .commons.yml config schema

`.commons.yml` is both the [[graph-init skill]] input and standing metadata a session can read. It declares
the graph's **shapes**, leaving procedures to interview-authored prose in the generated skills:

- `graph` — name, root, atlas file.
- `types` — evidence, attractors, entities, reference, and optional synthesis; the type names and their
  directories.
- `sources` — each with a `domain:` label, defining what the process skill resolves and keys on.
- `sinks` — non-graph outputs (e.g. a task manager) the process skill routes to.
- `promotes-to:` — the promotion target graph, if any; its presence is what switches on the process
  skill's promotion tail.

Config drives shapes; the interview fills procedures as prose — see
[[the knowledge-commons plugin generates project-owned prose, not a runtime engine]].
