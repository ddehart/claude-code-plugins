---
genitor: "[[observations]]"
tags: [generator, templates, root-cause]
date: 2026-07-15
supports: ["[[a generator reproduces its template's flaws]]", "[[the knowledge-commons plugin generates project-owned prose, not a runtime engine]]"]
---
The conventions reference showed map files as bare headings, missing their required frontmatter. The
scaffolding run reproduced bare-heading maps exactly — because that is what the worked example modeled. The
root-cause fix corrected the example in the conventions doc and made the scaffold step state the frontmatter
requirement explicitly, rather than only patching the generated output. Same shape as the stamp-format and
pointer-path fixes: the generated instance was wrong because its template was.
