# Changelog

## 2026-07

### 2026-07-28 — pipeline correction: preserve and synthesize (knowledge-commons 0.6.0)

Not a `/process` run. A structural correction to the pipeline itself, implemented from
`docs/specs/knowledge-commons-process-pipeline.md`, plus the graph notes recording it.

**Changed**
- Decisions (1 new, 1 superseded): `processing preserves the raw and synthesizes for a human, and
  extracts from the raw` records the four-stage model. `session transcripts are primary and the
  chronicle is the lossy fallback` is marked superseded with a pointer; its content is unedited.
- Source (1): **no change, and that is a correction.** This entry originally recorded the founding source
  note gaining `raw: unavailable`, on a check that globbed `*claude-code-plugins*` and found nothing. The
  glob was the wrong instrument — the session ran in a `commons-scaffold` worktree, so its transcript sat
  under a different slug and that pattern could never have matched it. The transcript is intact (2.8 MB,
  1,311 lines). The marker has been removed and spec v1.3 reverses the instruction to add it.
- `maps/decisions.md`: entry for the new decision, supersession marker on the old one.
- `.commons.yml`: the chronicle moves from `sources:` to `types.synthesis` (adopted at
  `docs/chronicle/`, outside the graph root); the session tier gains a committed
  `archive: knowledge/sources/raw/` and `gate: public`.
- Both generated skills patched through six template deltas.

**Decided**
- The chronicle is this pipeline's output, not a second input tier. Everything the old arrangement
  needed — a primary/fallback ordering, an overlapping-tier guard, a transcript-survival check — was
  machinery containing that one inversion, and all of it is gone.
- Raw material is archived in-repo and committed. The gitignored-scratch predecessor is what let the
  founding transcript vanish with nothing announcing the loss.

**Learned**
- Verifying a claim is not the same as verifying it against a query that could disprove it. The check
  that "confirmed" the founding transcript was gone was scoped to the one path it could not be in, and it
  was run precisely *because* the note's claim shouldn't be taken on trust. See
  [[a search scoped to one path returned nothing and was reported as absence]].
- The redaction floor's first run reported three findings and silently missed a planted private key:
  a pattern starting with `-` was eaten as grep options, grep exited 2, and stderr was discarded, so
  the miss was shaped exactly like a clean pass. The plant-a-failure test is the only reason it
  surfaced; an exit-code-only assertion stayed green throughout. The test now ships as
  `test-scan-secrets.sh` rather than having been performed once.
- Run against a real session export, the gate returned three hits and all three were false positives —
  prose describing that same test fixture. Concrete evidence for per-hit resolution over a blanket
  policy: withholding would have discarded a 100 KB transcript over three lines of documentation.

**Open**
- The nine existing chronicle entries stop being queued as sources. Those whose transcripts survive are
  reachable by processing the transcript, which will find and link the entry as its synthesis; those
  whose transcripts are gone are reachable through the orphaned path. Neither was done here.


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

## 2026-08-01 — the archive's first real use

Not a `/process` run. PR #71 merged (knowledge-commons 0.6.0), and the two session exports left in the
retired `.claude/session-exports/` were passed through the new preserve stage's redaction gate and moved
into `knowledge/sources/raw/`. That directory is now gone; the archive holds its first material.

**Gate result — 4 findings, all accepted as false positives.** Three were prose in the transcripts
*describing* the gate's own planted-secret fixture; one was a Python `key=` keyword argument. The
read-through found no credentials and no personal data. The other-domain names it did surface (Aiwyn,
osu-builders-studio, wellstead) are already present elsewhere in this public repo, and no employer content
is quoted — only a four-stage shape the merged spec already describes. Nothing redacted, nothing withheld.

**Learned, and it cost a round-trip:** the first read of that gate output was driven by grep counts and a
keyword match against the Never Capture rule, and it recommended withholding. Reading what the references
actually *said* reversed it — no quoted content, names already public, a shape already in the spec. A
count is not a finding. The read-through half of this gate is judgment by design, and judgment exercised
on a tally rather than on the text produces confident answers about the tally.

**Also:** both exports of one session are kept rather than only the fuller one. The 07-28 export (1,295
lines) is what the first processing pass actually read; the 08-01 export (4,078 lines) is the same session
after it grew, identical for its first 1,290 lines. Keeping both makes that note's partial-coverage claim
checkable instead of merely stated.

## 2026-08-01 — session f64160a1, augment pass

Second pass over the same source. The 2026-07-28 run read an export cut at 13:02 while the session kept
going; the transcript had since roughly doubled, and everything after that cut was unprocessed while the
stamp read as complete. That is now its own open question — a date says when a read happened, not how far it
reached, and a run over a live session is inside its own material and necessarily stops short of itself.

Written: 3 patterns, 11 observations, 1 question. Evidence and witness bumps to three existing patterns.

The three new patterns are all failures the graph could not see about itself. **A claim restated into
several artifacts starts reading as corroborated** — "the founding transcript is gone" went from one scoped
search into skill prose, a decision note, a spec's closing argument, and finally a spec *instruction* handed
to another session; during the original diagnosis the skill's own restatement was cited as evidence for the
claim. **Concurrent writers are invisible until write time** — the commons moved between the redundancy
screen and the write with both fetches reporting "already up to date," and two sessions independently wrote
the same decision note. **An index omission silently disables the check that reads it** — the commons claims
map listed 78 of 81, and one of the three missing was the claim closest to a candidate being promoted.

Three observations indict this run rather than its subject. The scoped-search error fired a **third** time
after two instances had been written into the graph the same day, under a pattern named for exactly it —
within-session immunization is not what the graph provides. The previous run's effort-ratio critique never
reached `knowledge/` at all, verified by grep: findings that name a fixable artifact convert into notes and
findings that indict the method producing them do not, and the omission leaves no trace, which is why it is
recorded now. And the augment read a transcript containing the prior run's reader reports verbatim,
including inference explicitly tagged as inference — tags that do not survive re-ingestion.

The chronicle for this session still does not exist. It was offered four times and deferred four times, each
with a locally good reason. The session arguing that a synthesize-for-a-human stage is a required part of
the pipeline is the session that never produced its own.

Todoist tasks were proposed and declined at plan review; no sink ran.

[entity-type-gap: template deltas]
