# Knowledge Commons — The `/process` Pipeline Correction

> **Version:** 1.3 · **Status:** implementation in flight on `feat/process-pipeline-correction` · **Date:** 2026-07-28
> **Parent spec:** [`knowledge-commons.md`](./knowledge-commons.md) (v1.0.1)
> **Plugin version at draft:** knowledge-commons 0.5.0 → ships as 0.6.0
>
> **Implementation is for a fresh session, not the authoring one.** A session implementing its own spec
> implements its intent rather than the document, so thin or misstated passages get papered over silently
> and stay wrong for the next reader. The §7.5 cold read simulated a fresh reader; executing §6 is the
> real test. Everything needed is in this document and the files it names — start at §6 step 1.
>
> The authoring session is `session:f64160a1-e82b-4015-bd19-08331d49a995`. It is the subject of §6 step 6
> and §7.3, and is not the session that will implement this.

---

## 1. Problem

The `/process` pipeline was modeled on a working reference implementation whose flow has **four stages**:

1. **Take in** a source — a call transcript, a website, a Claude Code session, any raw stream of material.
2. **Preserve** the raw material durably, on disk, in a repository for raw data.
3. **Synthesize** it into a document that serves a human reader.
4. **Extract** the graph's atomic notes — insights, decisions, observations — **from the raw material**,
   not from the synthesis.

The generated `process` skill has eleven numbered steps. Two of those four stages are not among them.

### 1.1 Preservation is never instructed

The template has no step that writes the source note. Step 3 *searches* for one ("search the graph for the
source note carrying this `source:`"); step 9 *stamps* one ("write or update the `processed:` stamp on the
source note"). Nothing creates it. `graph-conventions.md` describes its shape — "raw and preserved, this is
the one note type that keeps its source's own words" — but a convention describing a note is not a pipeline
stage that produces it.

For a small chronicle file the gap is invisible: the source note can hold the whole input, and an
implementer fills in the obvious. For anything large it fails silently. In `claude-code-plugins` it
degraded to a pointer into `.claude/session-exports/`, which is **gitignored**. The generated skill records
what it takes to be the consequence:

> That pointer can dangle, and already has. [...] This graph's founding source note,
> `session:284b79f5-c34f-4ad3-b97d-9c78cdc9c46f`, already points at a transcript that no longer exists.

**That claim is false, and its falsity sharpens the argument rather than weakening it.** Checked
2026-07-28: the founding transcript exists — 2.8 MB, 1,311 lines — and the founding source note recorded no
pointer at all, so nothing could have been dangling. The session spanned two repositories (590 turns in
`commons`, 190 in `claude-code-plugins`, four working directories, three branches). A transcript gets one
home however many projects a session touches; that one landed under a `commons` worktree slug, which the
resolve step's `~/.claude/projects/*claude-code-plugins*/` glob can never match. A scoped search returned
nothing and was written up as loss. (The same error shape recurred twice more while drafting this spec; see
`knowledge/observations/a search scoped to one path returned nothing and was reported as absence.md`.)

So stage 2's absence had not destroyed anything. What it had done is leave the material undefended: in no
repository, backed up by nothing, its originating worktree already deleted, unreachable by the pipeline's
own queue, and recoverable only because someone happened to look outside the glob. It has since been
archived at `~/Developer/session-archive/` and moved under this project's slug, where the resolver can see
it. A preservation stage is what converts "not yet lost, and findable only by luck" into "preserved." The
urgency is real; the past-tense loss was not.

**A third defect, out of scope here but worth recording.** The resolver identifies a project's sessions by
globbing that project's slug, which assumes a session belongs to one project. It does not — a session is a
conversation, and a cross-project one lands under whichever slug it happens to land under. Relocating a
transcript repairs an instance; the assumption stays. Not addressed by this spec.

### 1.2 Synthesis is never produced

The synthesis role exists in every artifact except the one that would create a note in it: `graph-init`
interviews for it (block 2, question 9b), `.commons.yml` has a slot for it, `graph-conventions.md`
documents the note shape, the plugin README lists it as a type, the knowledge-graph template describes it
under "Types in This Graph." No step of the process template writes one.

The parent spec records how this happened. The v1.0.1 amendment note says the synthesis role was added
"to the conventions, the knowledge-graph template, and interview block 2." The process template is not in
that list. The role was added everywhere except the pipeline that produces it.

### 1.3 The inversion

Because the pipeline cannot *produce* a synthesis, `claude-code-plugins` put its synthesis on the **input**
side. Its chronicle — written by `meta-claude:session-chronicle`, for a human reader, about a session — is
registered in `.commons.yml` as a second source tier. The generated knowledge-graph skill states the
reasoning and then draws the opposite conclusion from it:

> **Synthesis** — none. A chronicle entry is already a session-level synthesis, so evidence is extracted
> straight from the source; there is no intermediate synthesis tier in this graph.

The first clause is correct. The chronicle *is* the session-level synthesis — which makes it stage 3
output, not stage 1 input.

Everything downstream is machinery built to contain that inversion:

- a primary/fallback ordering between two tiers that describe the same events,
- an "overlapping tiers" guard section warning that processing both double-counts evidence,
- a `grep -l '"timestamp":"<date>' ~/.claude/projects/*/*.jsonl` transcript-survival check run before any
  chronicle is processed,
- a decision note, `session transcripts are primary and the chronicle is the lossy fallback`, elevating the
  workaround to a recorded design decision.

None of it would exist if the synthesis sat on the output side, where the run produces it.

### 1.4 The synthesis role is itself defined backwards

A second, subtler inversion, and probably the reason nothing was ever written to produce a synthesis.
`graph-conventions.md` defines the type as:

> an optional **intermediate** between a rich bounded source (a call, a meeting) and the atomic evidence
> extracted from it

The knowledge-graph template repeats it: "one note distilling the whole event, from which atomic evidence
is then extracted." That places the synthesis *inside* the extraction path — evidence passes through the
distillation on its way to the graph.

The reference model is the opposite, and explicitly so: evidence is extracted from the raw material
**because** you do not want it extracted from the synthesis. A distillation written for a human reader
compresses away exactly the corrections, dead ends, and exact wording that atomic evidence needs. The
synthesis is a **sibling output** of the same raw material, not a filter the evidence passes through.

Defined as an intermediate, the type has no clear place in a pipeline whose extraction step already reads
the source directly — which is a plausible reason it was specified into four artifacts and implemented in
none.

---

## 2. The corrected model

```
                    ┌──────────────────────────────┐
   raw source  ──►  │  2. PRESERVE  (source note)  │
                    │     + durable raw archive    │
                    └──────────────┬───────────────┘
                                   │
                    ┌──────────────┴───────────────┐
                    ▼                              ▼
        ┌───────────────────────┐      ┌──────────────────────┐
        │  3. SYNTHESIZE        │      │  4. EXTRACT          │
        │  human-facing doc     │      │  atomic graph notes  │
        │  (chronicle entry)    │      │  FROM THE RAW        │
        └───────────────────────┘      └──────────────────────┘
```

Stages 3 and 4 are **siblings, both fed by the raw material**. Neither is upstream of the other. The
synthesis links to its source note and records what was extracted alongside it; the evidence cites the
source note, never the synthesis.

---

## 3. Goals and non-goals

**G1.** The generated `process` skill has a named, numbered stage that writes the source note and preserves
the raw material durably — for every graph, not only ones whose sources are small enough to inline.

**G2.** The generated `process` skill has a stage that produces the human-facing synthesis, generated only
into graphs that declared a synthesis tier.

**G3.** Evidence extraction reads the raw material. Where both a raw source and a synthesis exist, the
synthesis is never the extraction input.

**G4.** `claude-code-plugins` is migrated onto the corrected model: chronicle moves from source tier to
synthesis tier, and the containment machinery it required is removed.

**G5.** The corrections reach already-generated graphs through the delta log, without breaking any existing
delta's anchor.

**Non-goals.**

- **N1.** Rewriting the extraction, planning, approval, stamping, or promotion steps. Stages 1 and 4 work;
  this spec adds the two missing stages and corrects what the synthesis is.
- **N2.** A general secret-scanning capability. The redaction gate (D6) exists to guard one specific new
  action — committing raw material to a possibly-public destination — and is scoped to that.
- **N3.** Retroactively reprocessing already-processed sources. Migration (§6) corrects the model going
  forward and marks the record; it does not re-extract.
- **N4.** Changing how `session-chronicle` writes a chronicle, including its reflection-ordering rules.
  `/process` invokes it; it does not reimplement it.

---

## 4. Design decisions

### D1 — Preservation is a named stage in every generated pipeline

The preserve stage is generated into every `process` skill, unconditionally. What varies is its *form*, not
its presence:

- **Small, self-contained sources** (a chronicle file, a fetched docs page): the source note carries the
  material verbatim in its body, as `graph-conventions.md` already describes. No separate archive.
- **Large sources** (session transcripts, recordings): the raw material is written to the graph's raw
  archive and the source note carries identity, date, a one-line description, the `processed:` stamp, and a
  pointer to the archived file.

*Rationale.* Unconditional presence is the fix. A stage generated only when config asks for it reproduces
the defect being corrected — a stage absent from the pipeline is a stage nobody notices is missing. The
form varies because inlining a multi-megabyte transcript into a note is not possible and archiving a
200-word chronicle entry is pointless.

### D2 — Raw material is committed, in-repo, under the graph

The archive is a real directory in the project, committed to version control. For `claude-code-plugins`
that is `knowledge/sources/raw/`, and `.claude/session-exports/` is removed from `.gitignore` and retired.

*Rationale.* The gitignored-scratch-directory model has already lost this graph's founding transcript. A
committed archive is versioned, backed up wherever the repo is backed up, and travels with the graph. The
alternative — a durable location outside the repo — reintroduces the dangling pointer through a different
door.

*Cost, accepted:* repo size grows with every processed session, and the material is as public as the repo.
D5 and D6 address the second.

### D3 — The synthesis is a sibling output, not an extraction intermediate

Correct the type's definition in `graph-conventions.md`, the knowledge-graph template, and the plugin
README. A synthesis note:

- distills one bounded source into a document written **for a human reader**,
- carries `source:` provenance as a wikilink to its source note,
- records what was extracted alongside it,
- is **never** the input to evidence extraction when the raw material is available.

*Rationale.* §1.4. The intermediate framing puts a lossy distillation in the evidence path, which is the
thing the reference model most specifically avoids.

### D4 — Extraction reads the raw material

Where both exist, inspection reads the raw source. The synthesis may be read for orientation — it is a
useful map of a long transcript — but a finding is sourced from, and quoted from, the raw material.

*Rationale.* A synthesis compresses away corrections, dead ends, and exact wording. The first real
`/process` run on this graph found three divergences between a session's self-account and what its
transcript showed (recorded in the `step4-explicit-negative` delta's rationale); every one of those is
invisible to a reader of the synthesis alone.

### D5 — The redaction gate is conditional on the destination

`graph-init` asks whether the raw archive's destination is public or shared. The gate is generated into the
preserve stage only when it is. A private, single-user destination gets preservation with no gate.

*Rationale.* The hazard is publication, not archival. A graph writing to a private repo pays nothing.

*Risk, stated:* a repo that is private today can be made public later, and no run would notice. Mitigation
is in the generated prose — the preserve stage states which destination assumption it was generated under,
so a reader of the skill can see the assumption rather than having to infer it.

### D6 — The gate is a deterministic floor plus an agent read-through; both must pass

**Floor (always runs, fails closed).** A fixed scan for credential shapes over the rendered raw material:
private-key blocks (`-----BEGIN * PRIVATE KEY-----`), common token prefixes (`sk-`, `sk-ant-`, `ghp_`,
`gho_`, `github_pat_`, `xox[baprs]-`, `AKIA`), `KEY|TOKEN|SECRET|PASSWORD|CREDENTIAL` assignments with a
non-placeholder value, connection strings carrying a password (`://user:pass@host`), and `Authorization:`
headers with a bearer value. If the scan cannot run, the preserve stage **stops** — no archive, no commit.

**Read-through (always runs).** A subagent reads the rendered material for what patterns cannot catch:
third-party and client names, personal details, unreleased plans, anything whose sensitivity is semantic.

*Rationale.* The floor is dumb, testable, and verifiable against a planted secret; the read-through covers
the majority of a transcript's sensitive surface, which is not credential-shaped. Neither alone is
adequate: patterns miss meaning, and an agent read is judgment that varies run to run and cannot be proven
to work. This decision reversed an initial choice of read-through alone; the floor was added because the
failure it guards is irreversible and public.

*Verification requirement (per `proactive-failure-analysis.md`):* the floor must be tested against a
deliberately planted secret before this ships. A preflight that passes while the thing it guards is broken
manufactures confidence.

### D7 — A gate hit is decided per finding

Each hit is surfaced with surrounding context and resolved individually: **redact** (replace with a marker),
**withhold** (this material is not archived at all), or **accept** (a false positive). The source note
records every redaction and every withholding, so the degradation is visible in the graph rather than
silent.

*Rationale.* Per-hit friction is real and lands on every run. It buys the ability to keep a transcript
that contains one false positive, which blanket-withholding would discard entirely, and to withhold a
single genuinely sensitive session without a blanket policy.

*Failure posture:* if the run cannot present hits for decision — a non-interactive invocation, an
unattended run — the stage withholds rather than committing. Fail closed.

### D8 — A synthesis tier's directory may sit outside the graph root

`types.synthesis.dir` may name a path outside `graph.root`. For `claude-code-plugins` it is
`docs/chronicle/` — the chronicle entries *are* the synthesis notes, at the path they already occupy.

This is a new capability in the generic template. `graph-init`'s scaffold step must not create or overwrite
a synthesis directory that already exists outside the root, and the conventions must state that a synthesis
note may be an existing project artifact adopted into the tier rather than a note the graph authored.

*Rationale.* Faithful to the decision that the chronicle *is* the synthesis. The alternative — a thin note
inside `knowledge/` whose only content is a link to the chronicle — creates a second artifact per session
whose sole job is to point at the first.

*Cost, accepted:* synthesis notes at an adopted path won't carry the graph's frontmatter conventions
(`genitor:`, `tags:`). The tier tolerates this; the link direction that matters is source note → synthesis,
which lives on the source note side.

### D9 — `/process` writes the synthesis when it is missing, links it when it exists

The synthesis stage checks for an existing synthesis for this source. If one exists, it is linked from the
source note and the stage ends. If none exists, the stage invokes the graph's configured synthesis producer
— for `claude-code-plugins`, `meta-claude:session-chronicle` — and links the result.

*Rationale.* Both workflows are real: a chronicle written at session end and processed later, and a session
processed with no chronicle yet. A stage that only links imposes a hard prerequisite; a stage that always
invokes fires the chronicle's reflection and cross-pass machinery on every reprocessing run.

*Constraint (N4):* `/process` does not reimplement or reorder anything inside `session-chronicle`. The
reflection-ordering rules in `chronicle-gemini-synthesis.md` remain that skill's to enforce.

### D10 — The orphaned-synthesis path is permanent, not a migration step

When a synthesis exists but its raw source is gone — a pruned transcript, a dead URL — the pipeline extracts
from the synthesis and records `raw: unavailable` on the source note, with the reason.

This is a named, permanent path in the pipeline, not a one-time backfill.

*Rationale.* Transcripts will keep being pruned. This is the genuine case that made the chronicle a
"fallback tier"; it deserves an honest name and an explicit degradation marker rather than a co-equal input
tier. It is also the only route by which this graph's nine pre-existing chronicle entries can be processed.

*Constraint:* the path fires only when the raw material is verifiably absent — never as a convenience when
the raw material is merely large or inconvenient. Extracting from a synthesis that has a live raw source is
the D4 violation this path must not become a loophole for.

### D11 — New deltas anchor on existing headings and instruct insertion

No delta renumbers a heading. Each new delta anchors on a heading that exists in already-generated prose
and instructs that a new stage be added relative to it.

*Rationale.* The delta log's premise is that `## N. Title` headings survive byte-identical across diverged
graphs, and "a delta whose anchor doesn't resolve is skipped and reported loudly, never relocated by
guess." Renumbering invalidates all six existing anchors at once. Anchoring on survivors keeps every
existing delta resolvable.

*Cost, accepted and documented in the log:* after patching, an old graph and a freshly generated one are
numbered differently. Future deltas targeting these stages must anchor on the pre-existing heading, not on
the new stage's own heading, until the log records that every live graph has been patched.

### D12 — Superseded graph notes are marked, not rewritten

`knowledge/decisions/session transcripts are primary and the chronicle is the lossy fallback.md` is marked
superseded with a pointer to a new decision note recording the four-stage model. Its content is not edited.

*Rationale.* Per the global `keep-design-history` rule. The inversion and its correction are the most
useful thing this episode produced; a graph that shows only the corrected model loses the record of how a
role got specified into four artifacts and implemented in none.

---

## 5. Changes by file

### 5.1 Plugin — `plugins/knowledge-commons/`

| File | Change |
|---|---|
| `references/templates/process.md` | Add the preserve stage after `## 2. Resolve`; add the synthesis stage (conditional SLOT, like §11) after inspection; state in `## 4. Inspect` that extraction reads raw, never the synthesis, and add the orphaned-synthesis path to `## 2. Resolve`. **Also correct the `source-tiers` SLOT instruction**, which currently tells the generator that when two tiers cover the same underlying events it must "name which tier is primary and state the guard." The corrected model removes that case — a synthesis is not a tier — so the instruction would generate the inversion into every new graph. |
| `references/templates/knowledge-graph.md` | Correct the synthesis type description under `## Types in This Graph` from intermediate to sibling output (D3). |
| `references/graph-conventions.md` | Same correction in the "Entity and synthesis notes" section; add that a synthesis note may be an adopted project artifact outside the graph root (D8). |
| `references/deltas.md` | Five new entries (§5.4). |
| `skills/graph-init/SKILL.md` | Block 3: new question on the raw archive destination and whether it is public/shared. Block 2 q9b: reword to the sibling-output definition and ask what produces the synthesis. Step 4: `.commons.yml` gains `archive:` and `gate:` under a source tier, and `synthesis:` may name a path outside the root. Step 5: scaffold the raw archive directory; never create or overwrite an out-of-root synthesis directory. Step 6: generation rules for the two new stages. |
| `README.md` | Correct the synthesis row in the type table. |
| `.claude-plugin/plugin.json` | `0.5.0` → `0.6.0` (minor — new capability, per `plugin-updates.md`). |
| `.claude-plugin/marketplace.json` | Same bump. |

### 5.2 This project — configuration and skills

| File | Change |
|---|---|
| `.commons.yml` | Remove the `chronicle` source tier. Add `types.synthesis: { name: chronicle, dir: docs/chronicle/, produced-by: meta-claude:session-chronicle }`. Under the `session` tier, replace `export-to:` with `archive: knowledge/sources/raw/` and `gate: public`. |
| `.gitignore` | Remove the `.claude/session-exports/` entry. |
| `.claude/skills/process/SKILL.md` | Apply the five deltas via `/graph-patch`, in this project's own voice. Remove the "guard on overlapping tiers" subsection and the transcript-survival `grep` (D10 replaces both). |
| `.claude/skills/knowledge-graph/SKILL.md` | Replace the "Synthesis — none" line with this graph's real synthesis tier. |

### 5.3 This project — graph notes

| Note | Change |
|---|---|
| `decisions/session transcripts are primary and the chronicle is the lossy fallback.md` | Mark superseded with a pointer (D12). Content unedited. |
| `decisions/processing preserves the raw and synthesizes for a human, and extracts from the raw.md` | **New.** The four-stage model and why extraction reads raw. |
| `observations/…` | New observations from the authoring session's findings, written by the `/process` run over it (§6 step 6) — not hand-authored here. |
| `maps/decisions.md` | Entry for the new decision; annotation on the superseded one. |

### 5.4 Concrete shapes

**Template numbering after insertion.** The template itself renumbers freely — only *deltas* are
anchor-constrained (D11). Resulting sequence:

```
1. Entry              5. Inspect            9.  Continue-and-collect
2. Resolve            6. Synthesize         10. Stamp
3. Preserve           7. Propose the plan   11. Report
4. Find the ledger    8. Run to completion  12. The promotion tail
```

Synthesize sits at 6 — after inspection, before the plan — because what the synthesis covers is one of the
things the plan presents for approval. The stage *proposes* the synthesis at 6 and *writes* it during 8,
like every other write in the run. Nothing is authored before the single approval gate.

**`.commons.yml` for `claude-code-plugins`,** the changed keys only:

```yaml
types:
  # ...existing evidence, attractors, entity, reference...
  synthesis:
    name: chronicle
    dir: docs/chronicle/                    # outside graph.root, by D8 — pre-existing project artifacts
    produced-by: meta-claude:session-chronicle
sources:
  - type: session
    # ...existing path, glob, identity, resolver...
    archive: knowledge/sources/raw/         # replaces export-to:; committed, by D2
    gate: public                            # public | shared | private — selects the gate, by D5
  # the chronicle tier is REMOVED; it is now types.synthesis
  - { type: claude-code-docs, resolve: url }
```

`archive:` and `gate:` are new sub-keys on a source tier; `produced-by:` is a new sub-key on
`types.synthesis`. No new *top-level* key is introduced, so `graph-init`'s "never invent `.commons.yml`
keys" list stands unchanged — but that list's sentence should be checked during implementation to confirm
it constrains top-level keys only, and sharpened if it reads as constraining all keys.

**Where the floor scan lives.** `plugins/knowledge-commons/scripts/scan-secrets.sh` — a real file in the
plugin, so it is testable in isolation (§7.1) and identical across every graph that generates the gate.
The generated preserve stage invokes it by the path `graph-init` resolves at generation time, the same way
generated skills already reference `references/graph-conventions.md`. Exit non-zero on any hit, non-zero on
its own failure; the stage treats both the same way, which is what "fails closed" means here.

**Whether the run commits.** The preserve stage writes the archive file and stages nothing. Committing
stays with the project's normal flow, so the archive lands in the same commit as the notes the run
produced. The gate is what guards publication, and it runs before the file is written — not before the
push.

### 5.5 Deltas

Six entries, all anchored on headings that exist in already-generated prose (D11). Every anchor below was
verified to resolve exactly once in both the template and this project's generated skill:

| `id` | `file` | `anchor` | Substance |
|---|---|---|---|
| 1.3 | 2026-07-28 | Corrected a factual claim that had become load-bearing: the founding transcript was never lost. §1.1's "already destroyed material" is withdrawn, and **§6's instruction to mark its source note `raw: unavailable` is reversed** — it is archived and now reachable, and migrating it through the gate is the recommended first exercise of the preserve stage. Also records a third defect as out of scope: the resolver globs a project slug, which assumes a session belongs to one project, and a cross-project session's transcript lands under whichever slug it happens to. |
| 1.2 | 2026-07-28 | Pinned the authoring session's UUID in §6 step 6, §7.3, and §5.3, and stated in the header that implementation is for a fresh session. "This session" meant the authoring session when written; an implementing session would have read all three as its own and processed the wrong transcript. |
| 1.1 | 2026-07-26 | Independent cold read (implementer brief, no context). Four changes: the template's `source-tiers` SLOT instruction added to §5.1 &mdash; it would have generated the inversion into every new graph; `synthesis-stage` split into `synthesis-in-plan` + `synthesis-write` because its substance straddles the approval gate; the unanchored hand edit under `## 3. Find the ledger` called out; §7.1 given a pass criterion declared in advance. Cold read returned no blocking items. |
| 1.0 | 2026-07-26 | Initial draft, from an interview settling twelve decisions. |
| `preserve-stage` | process | `## 2. Resolve` | A stage that writes the source note and durably preserves the raw material, with the small/large form split (D1, D2) and the gate when the destination is public/shared (D5–D7). |
| `resolve-orphaned-synthesis` | process | `## 2. Resolve` | The orphaned-synthesis path: extract from the synthesis only when raw is verifiably absent; mark the source note `raw: unavailable` (D10). Also removes any primary/fallback ordering between tiers covering the same events. |
| `extract-from-raw` | process | `## 4. Inspect` | Where both exist, inspection reads the raw material; the synthesis may orient but never sources a finding (D4). |
| `synthesis-in-plan` | process | `## 5. Propose the plan` | The plan names what the synthesis stage will do — link the existing synthesis, or invoke the configured producer — so it is covered by the single approval (D9). Conditional on the graph declaring a synthesis tier. |
| `synthesis-write` | process | `## 6. Run to completion` | Write the synthesis as a **sibling** of evidence extraction, neither upstream nor downstream of it, and link it from the source note (D3, D9). Conditional on the graph declaring a synthesis tier. |
| `synthesis-is-sibling` | knowledge-graph | `## Types in This Graph` | Correct the synthesis role from extraction intermediate to sibling output (D3). |

**Why the synthesis stage is two deltas.** Its substance straddles the approval gate: the plan must name it
(step 5) and the run must write it (step 6/8). A single delta anchored on run-to-completion would edit only
the write side, leaving a step 6 that requires something step 5 never produces — the patcher edits one
section per anchor and cannot reach backward. Two deltas on adjacent anchors is the idiom the log already
uses (`## 10. Report` carries two).

Each needs all seven fields. Write the `satisfied-test` for `extract-from-raw` sharply — a section that
merely *mentions* the synthesis passes a vague test while still routing extraction through it.

**One hand edit falls outside the deltas.** The "A guard on overlapping tiers" subsection sits under
`## 3. Find the ledger`, which no delta anchors on. `/graph-patch` must not touch unanchored prose, so its
removal is a manual edit — and it has to land in the same unit as the patch run, or the patched skill
contradicts itself.

---

## 6. Migration for `claude-code-plugins`

Order matters; each step depends on the one before.

1. **Plugin changes first** (§5.1), including the delta entries, so `/graph-patch` has something to read.
2. **Verify the redaction floor against a planted secret** (D6) before any raw material is committed.
3. **`.commons.yml` and `.gitignore`** (§5.2).
4. **`/graph-patch`** to apply the five deltas to this project's generated skills, under per-delta approval.
5. **Graph notes** (§5.3): supersede the old decision, write the new one, update the map.
6. **A real `/process` run** on **the authoring session,
   `session:f64160a1-e82b-4015-bd19-08331d49a995`** — not on whatever session performs the
   implementation. That transcript holds the diagnosis this spec came from; an implementing session's own
   transcript holds only the implementation. This is both the verification (§7) and the first exercise of
   all four stages.

**Already-processed sources are not reprocessed** (N3). The two existing source notes keep their stamps.
The founding session's transcript **is not gone** (§1.1) — it is archived at
`~/Developer/session-archive/`, and its source note should gain that pointer rather than a
`raw: unavailable` marker. Migrating it into the graph's own raw archive is a first, well-understood
exercise of the preserve stage, on material whose provenance is already known.

**The nine existing chronicle entries** stop being queued as sources. Those whose transcripts survive are
reachable by processing the transcript, which will find and link the chronicle as its synthesis. Those whose
transcripts are gone are reachable through the orphaned-synthesis path (D10). Neither is done as part of
this migration.

---

## 7. Verification

Per `spec-fresh-session-audit.md`, the preserve stage is partly unattended-shaped — it writes files and
commits them — so textual review is insufficient for it.

1. **Planted-secret test (blocking).** Write a file containing a fake `sk-ant-` key, a fake private-key
   block, and a `DATABASE_URL` with a password. Run the floor scan against it. It must exit non-zero and
   report all three as distinct findings. Add a negative fixture — `API_KEY=<your-key-here>` and prose
   mentioning `sk-` — and confirm it exits zero.

   Then break the scan deliberately (`chmod -x` it, or empty its pattern list) and run the preserve stage.
   **Pass criterion, declared before running:** the run reports the scan as unavailable *and* writes no file
   under `knowledge/sources/raw/`. Stating it in advance matters — the break-it half judges an agent's
   behavior rather than a process's exit code, and a criterion invented after seeing the output will be
   satisfied by whatever happened.
2. **False-positive path.** Run the gate against a real session export and confirm hits are presented with
   context and individually resolvable (D7). `.claude/session-exports/` is empty and being retired, so
   export a session to a scratch path for this test rather than expecting one to be there.
3. **End-to-end run.** `/process session:f64160a1-e82b-4015-bd19-08331d49a995` (the authoring session, per
   §6 step 6 — not the implementing one). It must: write a source note, archive the transcript through
   the gate, link or write the chronicle as synthesis, extract evidence from the transcript, and stamp. Each
   of the four stages must be individually observable in the run's output.
4. **Delta resolution.** After `/graph-patch`, confirm all six pre-existing deltas still resolve against the
   patched prose (D11's whole premise), and that each of the five new deltas' `satisfied-test` passes
   post-edit.
5. **Cold read.** An independent no-context read of this spec before implementation, briefed as an
   implementer ("produce a plan; can you build this?"), not as an adversary.

---

## 8. Risks and open items

**R1 — The gate is the only thing between a session and a public remote.** The floor is testable; the
read-through is not. A miss is irreversible: git history, GitHub caching, and forks all outlive a later
deletion. Accepted with the D6 floor as mitigation. Worth revisiting if the archive grows to where
per-session review stops happening honestly.

**R2 — Repo growth.** Session transcripts are large and the archive only grows. Not addressed here. When it
becomes a real cost, the options are compression, retention windows, or moving the archive to a private
sibling repo — all of which reopen D2.

**R3 — Numbering divergence between patched and freshly generated graphs** (D11's accepted cost). The delta
log must record this explicitly, or a future delta author will anchor on the new stage's heading and it will
silently fail to resolve in every patched graph.

**R4 — `/process` invoking `session-chronicle` couples two skills with their own ordering rules.** D9 keeps
the coupling to invoke-and-link, but the interaction has not been exercised. The end-to-end run (§7.3) is
the first test.

**R5 — Adopted synthesis notes lack graph frontmatter** (D8's accepted cost). If a later need requires
`genitor:`/`tags:` on synthesis notes, the tier will need either a frontmatter-injection step or a retreat
to in-graph synthesis notes.

**O1 — Does the commons need any of this?** The commons has no sources and no `process` skill, so stages 2
and 3 do not apply to it. Confirmed out of scope; noted because a reader may reasonably ask.

**O2 — Do the other two live graphs need patching?** The delta log says three graphs have been generated.
Their owners run `/graph-patch` on their own cadence; nothing here reaches them automatically. Not blocking.

---

## 9. Revision log

| Version | Date | Change |
|---|---|---|
