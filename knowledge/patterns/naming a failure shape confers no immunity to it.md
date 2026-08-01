---
genitor: "[[patterns]]"
tags: [verification, silent-failure, blind-spots]
---

# naming a failure shape confers no immunity to it

A check that finds nothing concludes *nothing exists* rather than *I learned nothing*, and proceeds. The
wrong path emits no error, so the run is indistinguishable from a correct one.

The origin instances are ordinary — four bugs sharing one shape. The load-bearing claim is what happened
next: **the shape survived being named, specified against, reviewed for, and built around.** It reappeared
four more times *inside the machinery built to eliminate it* — a generator that would stamp every fix as
already-applied against files containing none; a discovery hook that would report "nothing pending" from a
version-pinned stale log; an installed cache that would re-apply deleted work; a suppression marker whose
free-form key made every run look locally correct while re-raising forever.

Fluency is not application. The session named the shape in its first message and restated it in a dozen
commits and briefs, then committed it repeatedly — because inference from silence is the cheaper default at
every individual site, and nothing downstream can tell the two outcomes apart. The correction is always the
same and always structural: require an explicit negative; never infer one from absence.

*Three witnesses (2026-07-22, 2026-07-26, 2026-08-01). Open.*

## evidence
- [[the anti-silent-loss machinery shipped four instances of the shape it was built to eliminate]]
- [[a completed subagent report and an absent one produce the same symptom]]
- [[the generator's own instruction would have regenerated the defect just fixed]]
- [[an unnamed subagent returns its report where a named teammate delivers it nowhere]]
- [[a scoped-search error recurred a third time after two instances were written into the graph]]
- [[the synthesis stage was deferred four times and never produced]]

## related
- [[a plausible story arrests the investigation before the mechanism is found]]
- [[ambiguous prose in an LLM-executed skill is a correctness bug]]
