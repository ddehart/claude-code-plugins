---
genitor: "[[observations]]"
tags: [review, method, verification]
date: 2026-08-01
supports: ["[[a stopping rule tuned on one artifact kind measures the wrong thing on another]]", "[[each fix round manufactures the next round's defects]]"]
---
A session halted its subagent review loop by auditing itself against the loop tells in
`spec-fresh-session-audit.md` — enumerating each tell, checking it against evidence, and finding three of
four satisfied where the rule's threshold is two. The reasoning was careful and the tells were real:
round 2's findings genuinely were defects round 1's fixes introduced, and the scanner genuinely had grown
to 270 lines guarding a directory holding one `.gitkeep`.

CI then found three more fail-open defects in the same scanner, each pre-existing and none a product of
the previous round. The session's own verdict: *"My stop call was defensible on the evidence I had, but
it was wrong."*

The rule was applied outside the domain it was calibrated for. Its tells come from a prose cold-read
loop, where defect yield measures the auditor's productivity against a static artifact. Here the artifact
was executable code with an adversarial input space, where yield measures how much of that space the last
reviewer happened to probe — which says nothing about what remains. Both accurate tells were
uninformative: the directory holding one `.gitkeep` received 430 KB three days later.
