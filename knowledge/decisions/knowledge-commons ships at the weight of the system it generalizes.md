---
genitor: "[[decisions]]"
tags: [knowledge-commons, architecture, scope]
---

# knowledge-commons ships at the weight of the system it generalizes

The plugin mirrors the size of the proven reference it generalizes — roughly a thousand lines of prose
across a handful of files — and carries no validator, no write-transactions, and no lifecycle machinery.
The reference implementation ran for a year on prose conventions plus a checker it largely ignored, and
thrived; that is a natural experiment showing validation rigor is not what keeps such a graph alive. Scope
is set by one filter applied to every candidate feature: **"has the reference needed this in a year of
real use?"** Anything that fails the filter is deferred until a real run demonstrably hurts.

## evidence
- [[reading the working reference before speccing collapsed the design]]
- [[reverting the validator left graph health on approval plus conventions]]
- [[seven releases in one day were each driven by a real defect from actual use]]

## related
- [[build enforcement against demonstrated need, not anticipated failure]]
- [[prose conventions plus human approval can replace a validator]]
