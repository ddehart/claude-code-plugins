---
genitor: "[[decisions]]"
tags: [knowledge-commons, graduation, triggers]
---

# question graduation is triggered where evidence lands, from the plugin, not from the receiving graph

A question in a receiving graph is ready to become a principle once a second domain's evidence lands under
it, and nothing prompted that review. The only trigger was an awareness line in the receiving graph's own
generated skill, which loads only in sessions working inside that graph. Promotions run from the source
graph's session, so that skill never loaded at the moment a question became eligible.

The check therefore runs at the end of `promote`, the one operation that adds evidence, and a `graduate`
skill works the backlog with review marks so a held question doesn't come back. Both live in the
knowledge-commons plugin rather than in any one graph's generated skills, so every graph the plugin
generates gets them without regenerating anything.

*Decided 2026-11-08. Built in a separate session and merged as knowledge-commons 0.7.0. Spec:
`docs/specs/knowledge-commons-question-graduation.md`.*

## related
- [[promotion is scheduled into the process pipeline, never left to memory]]
- [[each stage of a staged pipeline needs its own trigger, and closing one gap exposes the next]]
- [[graduate skill]]
