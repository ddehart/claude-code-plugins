---
genitor: "[[decisions]]"
tags: [knowledge-commons, graph-patch, append-only]
---

# in-place rewrite of a shipped delta requires that nothing has stamped it

The delta log is append-only by convention. A shipped delta is normally superseded, not rewritten, because
downstream graphs record applied ids and a rewritten entry silently changes what a recorded id means.

The exception, stated with its precondition: **rewrite in place only when no graph has stamped the delta in
any durable state.** The convention exists to protect what a graph has already recorded; where nothing has
recorded it, there is nothing to protect.

Applied once, to remove two wrong-layer entity deltas. Verified on three independent axes before relying on
it — no graph carried a `generated:` block, none carried the corresponding template prose, and selection is
set-membership on id with no reverse lookup, so a removed id simply never surfaces.

The boundary matters and was tested within the same session: a *different* defect in an already-stamped
delta's rationale surfaced hours later, and the exception correctly did not apply — durable state existed,
so correcting it requires a superseding delta.

Applied again on 2026-11-08, on the unstamped side: a superseding delta shipped with a satisfied-test
stricter than the delta it replaced, the first fleet patch run's drafters found it before any graph had
applied it, and a check of every graph's `generated:` block confirmed no graph carried the id. It was
corrected in place (knowledge-commons 0.8.1). The delta it superseded was stamped everywhere, which is why
the correction to *that* one had to be a new delta.

*Decided 2026-07-22.*

## evidence
- [[drafting all thirteen graphs before applying any left the defective delta unstamped and fixable in place]]

## related
- [[entity recommendation belongs at the type layer, not the instance layer]]
- [[does a shared brief explain the original fanout symptom]]
