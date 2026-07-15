---
genitor: "[[patterns]]"
tags: [verification, testing, generator]
---

# execution against real data catches what authoring and review miss

The most reliable way to find a just-authored mechanism's defects is to run it end-to-end against
representative real input — not to review the design, and not to run it against a toy stub. Textual review
by the author reliably misses what first execution exposes immediately. A corollary for guards: a check
that has only ever been observed passing a happy path proves nothing, because it may be structurally
incapable of failing; verify a guard by feeding it a planted failure it must catch. The
"guard-reports-success-it-never-earned" defect recurred four times inside a single run and was escaped
only by testing against a known-bad input.

*One witness (2026-07-15). Open.*

## evidence
- [[a real transcript surfaced three defects a design review had missed]]
- [[the guard-reports-success-it-never-earned failure recurred four times in one run]]
- [[seven releases in one day were each driven by a real defect from actual use]]

## related
- [[added complexity generates its own defect supply]]
- [[break the self-review chain with a different agent]]
