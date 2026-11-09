---
genitor: "[[entities]]"
tags: [entity, skill, knowledge-commons]
---

# graduate skill

`knowledge-commons:graduate`. Walks a receiving graph's open questions that have evidence from two or more
domains, one at a time. Each one can graduate to a principle, split, move claims, retitle, or hold, with
human approval, and a review mark keeps a held question out of the queue until it gains new evidence.
`promote` runs the same review procedure at its end when a promotion makes a question eligible. Turning a
principle into a rule is not this skill; that is `promote`'s instruction-tier branch.

- **2026-11-08** — specced, tested on five sample questions, built as knowledge-commons 0.7.0, and run once on the commons. That run went from 4 to 11 principles, with 69 questions left. See [[question graduation is triggered where evidence lands, from the plugin, not from the receiving graph]]. Source: [[session 9d4bafbd — the deep-review counter fix, tested end to end]].
