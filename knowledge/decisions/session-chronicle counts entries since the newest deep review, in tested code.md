---
genitor: "[[decisions]]"
tags: [session-chronicle, testing, prose-as-instructions]
---

# session-chronicle counts entries since the newest deep review, in tested code

The mandatory 10-entry deep review never fired, because the count anchored on the newest *dated*
Evolution Note, and lightweight checks write dated notes too. The anchor is now the newest note that
records a deep review, and new reviews write a canonical `(deep review)` marker.

**The count is code, not prose.** Step 6a was an instruction a model followed, so no test could be
deterministic, and models had already miscounted it by hand. An eval was rejected, because it would test
one model's reading of the prose rather than the rule. The script has unit tests, including ones that hold
`SKILL.md`'s note template to what the script recognizes.

**With no review on record, every entry counts.** Falling back to the newest dated note would have kept
the bug in exactly the projects it hurt most. The cost is one review per project, which is why the bump
was minor.

**Recognition of older shapes is an allowlist.** What may follow `deep review` in a heading is named, not
the words that negate it, since that list could never be complete. Matching only the new marker was
proposed and rejected: it would report a project's real older review as missing.

*Decided 2026-11-06. Spec: `docs/specs/deep-review-anchor.md`.*

## related
- [[ambiguous prose in an LLM-executed skill is a correctness bug]]
- [[a list of negating phrasings cannot be complete, so allow what may follow]]
- [[session-chronicle skill]]
