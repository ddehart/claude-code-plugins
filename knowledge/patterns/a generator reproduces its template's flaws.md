---
genitor: "[[patterns]]"
tags: [generator, templates, root-cause]
---

# a generator reproduces its template's flaws

A generator faithfully reproduces whatever its templates and worked examples show, including their
defects. When generated output is wrong, the template or example is the likely source of truth — fix it
there, not only in the instance. In this session a conventions doc showed map files as bare headings
(missing required frontmatter), and the scaffolding run reproduced bare-heading maps exactly; the durable
fix corrected the example and made the scaffold step state the requirement explicitly, rather than
patching only the generated file.

*Two witnesses (2026-07-15, 2026-07-26). Open.*

## evidence
- [[the instantiator faithfully reproduced a bare-heading example from its own conventions doc]]
- [[the generator's own instruction would have regenerated the defect just fixed]]

## related
- [[ambiguous prose in an LLM-executed skill is a correctness bug]]
- [[the generated knowledge-graph skill]]
