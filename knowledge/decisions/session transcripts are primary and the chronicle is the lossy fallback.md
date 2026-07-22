---
genitor: "[[decisions]]"
tags: [knowledge-commons, process, sources]
---

# session transcripts are primary and the chronicle is the lossy fallback

A chronicle entry is a post-hoc account written by the agent whose blind spots the graph exists to catch,
and it compresses away exactly the corrections and dead ends that turn out to matter. The transcript holds
what happened; the chronicle holds what was remembered about it.

So the transcript is the primary source tier. The chronicle survives as a fallback rather than being
dropped, for two reasons: transcripts get pruned — this graph's founding source note already points at one
that is gone — and a Reflection section is *authored, not recorded*, so it can carry something no
transcript could.

Identity is `session:{uuid}`, never the path: a transcript relocates between project directories when a
worktree is created or removed, and a path key would resolve to a second note for one session. This proved
itself the same session it was written, when the transcript moved mid-run.

An overlapping-tier guard makes both tiers safe: before processing a chronicle, check whether its
transcript survives; if it does, process the transcript instead. Two views of one event is how a single
incident becomes three pieces of corroborating evidence.

*Decided 2026-07-22.*

## related
- [[the generated process skill]]
- [[naming a failure shape confers no immunity to it]]
