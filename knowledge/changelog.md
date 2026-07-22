# Changelog

## 2026-07

### 2026-07-15 — founding pass: commons-scaffold session `284b79f5`

First `/process` run against the graph (previously an empty scaffold). Source was the raw session
transcript of the knowledge-commons design work, processed at Derek's direction (chosen over the curated
`2026-07-15` chronicle, which remains queued as a future augment).

**Created**
- Source (1): the commons-scaffold session note, keyed off-tier on `session:284b79f5…`.
- Decisions (5): reference-weight shipping, generator-of-project-owned-prose, local-processing/receive-only-commons, promotion-scheduled-not-remembered, commons-as-evidence-tier-beneath-rules.
- Patterns (8): prose+approval-replaces-validator, build-against-demonstrated-need, complexity-generates-its-own-defects, execution-catches-what-review-misses, break-the-self-review-chain, generator-reproduces-template-flaws, ambiguous-prose-is-a-correctness-bug, scaffolder-owns-its-blast-radius.
- Observations (15): evidence for the above, all from this single session.
- Entities (7): knowledge-commons plugin; graph-init, promote, generated process, generated knowledge-graph, dev-workflow spec-writing skills; the commons (concept).
- Reference (1): the `.commons.yml` config schema.
- Map entries added across all six maps.

**Decided (by Derek, via plan approval)**
- Process the raw transcript rather than the chronicle write-up of the same arc.
- Ship all 8 patterns despite one-witness status (each distinct and portable); marked open, no verdicts.

**Learned**
- The founding session is unusually dense: one design session seeded ~13 attractors. Guarded against
  over-proliferation by folding near-duplicate facets (silent/compounding/frequent criterion, planted-failure
  guard-testing, delegate-then-verify) into evidence rather than minting separate attractors.
- Several of the session's lessons were already promoted into the commons during the work itself, and
  several already steer as global rules — so the promotion tail proposes only the genuinely-new claims.

**Open questions**
- The queued `docs/chronicle/2026-07-15.md` covers the same arc; a later chronicle run should augment these
  notes (cross-linked from the source) rather than duplicate them.
- Patterns are one-witness — do future sessions corroborate build-against-demonstrated-need and
  execution-catches-what-review-misses, or are they artifacts of this one build?

### 2026-07-22 — first transcript-tier /process run (session:5912a7cc)

Processed the two-day knowledge-commons session directly from its transcript — the first run under the new
`session` source tier, which is now primary with the chronicle demoted to lossy fallback. Exported via
`meta-claude:session-export` (534 KB / 76k words), inspected by four subagent readers, one per signal class.

Added a third attractor type, `question`, with its directory and map. This graph was the only one of four
without somewhere to hold an unresolved matter — osu and the commons declare `question`, wellstead declares
`hypothesis` and `constraint`. Surfaced because a finding from this very run had no home.

Written: 4 patterns, 2 questions, 5 decisions, 7 observations, 2 entities. Updated
`break the self-review chain with a different agent` with two evidence entries and a qualifier — a
different agent buys independence from execution, never from the author's intent or scope.

72 findings returned; 23 notes written. ~50 were instances of shapes already represented. Two proposed
evidence links to existing patterns were dropped rather than forced: manufacturing corroboration is the
failure the promote screen exists to prevent, and it applies inside a graph as much as across graphs.

All four readers completed their reads and reported nothing until chased. The cause was a briefing error —
they were told to reply in a channel that could not reach the orchestrator — not the fanout property the
pipeline's own delta asserts. That discrepancy is now an open question and a task.

Coverage is partial by construction: the session was still live when processed, so the export ends
mid-conversation. Recorded in the source note's stamp rather than implied away.

[patch-check-suggested] — `/graph-patch` ran today; all six deltas applied and stamped at 0.5.0.
