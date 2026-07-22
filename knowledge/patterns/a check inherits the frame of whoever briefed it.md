---
genitor: "[[patterns]]"
tags: [review, delegation, agents, blind-spots]
---

# a check inherits the frame of whoever briefed it

Independence of the *reader* does not buy independence of the *frame*. When the author writes the
reviewer's brief, the review can verify the implementation against the stated intent — and can never ask
whether the stated intent matches what was actually requested.

Two inheritances, both observed:

- **Intent.** Five independent reviews each found real blockers, and none could see that a feature had been
  built one abstraction layer below the request. Every brief encoded the author's own reading of what the
  feature was for. One sentence from the requester caught it.
- **Scope.** Every implementing brief was scoped to one directory, so the repo-level documentation went
  stale for three releases — and the reviews, scoped identically, were blind to it by construction.

This **qualifies** [[break the self-review chain with a different agent]] rather than restating it: a
different agent is necessary and not sufficient. A restatement of a request is itself an unverified
artifact, and no amount of downstream review checks it, because every downstream check is derived from the
restatement.

The practical consequence is that intent needs its own verification, and it cannot come from the same
chain — only from the requester, or from grounding the restatement against the artifact's own vocabulary
before designing against it.

*One witness (2026-07-22). Open.*

## evidence
- [[four independent reviews could not see a layer error because the author wrote every brief]]
- [[the root README went stale because every brief was scoped below it]]

## related
- [[break the self-review chain with a different agent]]
- [[a plausible story arrests the investigation before the mechanism is found]]
