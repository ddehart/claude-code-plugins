---
genitor: "[[entities]]"
tags: [skill, knowledge-commons]
---

# graph-init skill

The [[knowledge-commons plugin]] scaffolding skill. Interviews the user, writes `.commons.yml`, scaffolds
the atlas / maps / type directories, and generates the project's own [[the generated process skill]] and
[[the generated knowledge-graph skill]] from templates. Has a `--config-only` mode that wires an existing
hand-built graph into promotion (writes only `.commons.yml`, touches no skills) and a find-or-create
preset for the commons. Its report step is expected to flag environmental blast radius — empty-dir
`.gitkeep`, CI path-trigger exclusions, missing promotion triggers; see
[[a scaffolder owns its environmental blast radius]].

## interaction log
- 2026-07-15 — config-only mode found to write `promotes-to:` without checking a promotion trigger
  existed; fixed to grep the pipeline and surface the gap.
