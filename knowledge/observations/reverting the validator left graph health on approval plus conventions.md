---
genitor: "[[observations]]"
tags: [architecture, validation, refinement]
date: 2026-07-15
supports: ["[[prose conventions plus human approval can replace a validator]]", "[[knowledge-commons ships at the weight of the system it generalizes]]"]
---
The knowledge-commons build reverted its executable validator (~1,900 lines), vendored YAML parser,
write-transactions, and lifecycle machinery after the year-old reference implementation showed those
failure modes don't occur under a human-in-the-loop workflow. Graph health rests instead on two things: an
LLM writing to prose conventions, and a human approving every plan. The one genuinely load-bearing
structural rule — every evidence note must support at least one attractor — survived as a single sentence
of convention, not as code.
