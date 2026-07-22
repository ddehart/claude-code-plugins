---
genitor: "[[sources]]"
tags: [source, session]
source: "session:5912a7cc-0cd3-44cb-829f-fe1130ef07c6"
date: 2026-07-21
---

# session 5912a7cc — four knowledge-commons bugs, the patch mechanism, and a wrong-layer correction

Two-day session (2026-07-21 → 2026-07-22). Fixed four documented `knowledge-commons` bugs; specced and
shipped `/graph-patch`, the mechanism that propagates template fixes into already-generated project skills;
ran five independent code reviews, each of which found a real merge-blocker; corrected a feature that had
been built one abstraction layer below the request; and declared session transcripts as this graph's
primary source tier.

Six PRs merged, plugin 0.1.8 → 0.5.0.

**Transcript:**
`~/.claude/projects/-Users-derek-personal-Developer-claude-code-plugins--claude-worktrees-session-tier/5912a7cc-0cd3-44cb-829f-fe1130ef07c6.jsonl`
(2 MB / 1,705 lines). Per the session tier's convention this note holds a pointer, not the body — and that
pointer can dangle: this graph's founding source note already points at a pruned transcript.

**Coverage is partial, deliberately.** This was processed while the session was still live. The export read
by the inspection fanout ends mid-conversation and does not include the run that produced these notes, nor
anything after it. The `processed:` stamp below records what was actually inspected; a later augment-mode
run against the same `source:` should expect new material rather than treating this as complete.

**Inspection:** exported via `meta-claude:session-export` (534 KB / 76k words), then four subagent readers,
one per signal class. All four completed their reads and reported nothing until chased — the cause was a
briefing error, not the fanout property the pipeline's own delta asserts. See
[[a completed subagent report and an absent one produce the same symptom]] and
[[does a shared brief explain the original fanout symptom]].

72 findings returned; 23 notes written. The remainder were instances of shapes already represented.

## processed
- date: 2026-07-22
  ran:
    - patterns: naming a failure shape confers no immunity to it; a check inherits the frame of whoever briefed it; a plausible story arrests the investigation before the mechanism is found; justifying prose drifts from the thing it justifies
    - questions: does a shared brief explain the original fanout symptom; should the type-gap check cover attractor types, not just entity types
    - decisions: patches are semantic instructions anchored on headings, never diffs; session transcripts are primary and the chronicle is the lossy fallback; entity recommendation belongs at the type layer, not the instance layer; in-place rewrite of a shipped delta requires that nothing has stamped it; processing a live session is not delegable to a subagent
    - observations: 7
    - entities: graph-patch skill; session-export skill
    - updated: break the self-review chain with a different agent (2 evidence entries + a qualifier)
    - maps: patterns, decisions, questions, observations, entities
  skipped:
    - ~50 findings judged instances of shapes already represented rather than new material
    - 5 operational one-offs (merge ordering, branch cleanup, gitignore) — reasoned but not durable
    - 4 items the corrections reader self-excluded; reviewed and agreed
    - 2 proposed evidence links to existing patterns, dropped rather than forced — see the changelog note
  errored: []
  partial: session still live at processing time; export ends mid-conversation
