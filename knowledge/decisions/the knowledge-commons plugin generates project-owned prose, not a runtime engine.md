---
genitor: "[[decisions]]"
tags: [knowledge-commons, architecture, generator]
---

# the knowledge-commons plugin generates project-owned prose, not a runtime engine

The plugin scaffolds two skills into the target project — a process orchestrator and a knowledge-graph
skill — that the project owns and is expected to edit and drift, exactly like the reference's hand-written
skills. A config file (`.commons.yml`) declares the *shapes* (types, directories, frontmatter fields,
sources, sinks, promotion target); the interview fills the *procedures* (extraction workflows, judgment
rules) as prose in the generated skills. Because the generated artifacts are target-owned, there is no
`--upgrade` flow, no invariant markers, and no fork anxiety — corrections land directly in the
project-owned prose where they belong.

## evidence
- [[a soft if-applicable instruction produced two promotion runs that disagreed]]
- [[the instantiator faithfully reproduced a bare-heading example from its own conventions doc]]

## related
- [[knowledge-commons ships at the weight of the system it generalizes]]
- [[graph-init skill]]
