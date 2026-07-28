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

## 2026-07-28 — session f64160a1: the pipeline correction, specced not built

Processed the three-day session that diagnosed why this graph's `/process` pipeline was inverted. Exported
via `meta-claude:session-export` (98 KB / 13,964 words), inspected by four subagent readers, one per signal
class.

**All four reported explicitly and unprompted — the first fanout in this graph to do so.** The difference
was the spawn shape: they were created without `name:`, so their final message is the return value. Earlier
in the same session a *named* cold-read agent went idle four times, ignored two follow-ups and a stand-down,
and was invisible to `TaskList` while `TaskStop` resolved it by name at once. That answers the open question
`does a shared brief explain the original fanout symptom`: yes, but the mechanism is narrower than "a shared
brief" — the brief was wrong only for one spawn shape. The question is marked ready to graduate, and the
correction needs a superseding delta rather than an in-place rewrite, since `step4-explicit-negative` is
stamped here and pending in two other graphs. Task filed.

Written: 1 decision, 1 supersession, 1 pattern, 8 observations. Evidence added to five existing patterns and
one open question. The superseded decision — `session transcripts are primary and the chronicle is the lossy
fallback` — is kept unedited under a banner; it is the clearest instance this graph has of the new pattern
`a workaround written up as a decision stops reading as a workaround`.

Witness counts on all five updated patterns went from one to **two**, not more. Every new instance came from
this single session, and instances within one session are correlated evidence, not independent witnesses.
`a plausible story arrests the investigation` contributed three instances from this one session and is
annotated to say so.

Three of the eight observations record failures in the session's own output, found by the readers and
verified against the repo before recording: a spec revision log left out of order by a scripted
string-insert (fixed in this run); a scoped `find` whose empty result was reported to the user as "no
transcript exists" when the file sat one directory up; and the reference model the whole spec corrects
toward, never opened despite being on disk throughout. That last one is a task, not just a note — the
spec's central premise depends on it.

`maps/sources.md` was missing the previous run's source note as well as this one; both backfilled.

This run used the **pre-fix pipeline** on the session that diagnosed it — no preservation stage, export to
the gitignored directory the spec retires. The source note carries `pre-fix-pipeline: true` so a later
reader does not mistake it for a post-fix artifact. The spec's §6 step 6 calls for a second `/process` run
over this same session once the fix lands; that run, not this one, is the first exercise of all four stages.

[entity-type-gap: template deltas]

**Correction, same day.** The entry above recorded `does a shared brief explain the original fanout symptom`
as answered and ready to graduate, on a spawn-shape mechanism. Retracted while promoting: a claim reaching
the commons from osu-builders-studio the same day reports 43 of 44 delegated workers silent across four
briefs and two task shapes, which that mechanism cannot explain unless all of them were named teammates. The
question is open again with two competing mechanisms and a stated discriminator. The evidence here was n=1
named against n=5 unnamed inside one session, written up as settled — the same shape as three of the
observations this very run recorded. Caught only because `/promote` re-fetches the target before writing.
