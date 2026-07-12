# Knowledge Commons Plugin — Specification

> **Version:** 0.3 (draft) · **Status:** pre-build · **Date:** 2026-07-12
>
> This is the public **mechanism** spec. It supersedes an earlier private draft (v0.2, retained as design
> history in the author's private notes) that designed the same system around ambient discovery and a
> standalone mechanism repo; the design has since converged on the pull-based, plugin-packaged shape
> described here. Content — actual graphs, their configs, and their notes — never lives in this repository.

---

## 1. Problem

Personal knowledge systems die the same way: automated **capture** with no **refinement** stage. Articles,
highlights, and transcripts pile up; nothing turns them into claims anyone stands behind; the graph view
shows a hub-and-spoke starburst of folder pointers and no lateral edges. A vault with thousands of captured
notes and a derived-to-source ratio of 1:100+ is a landfill with a search box.

The counterexample that motivates this plugin is a natural experiment: two vaults, same author, same tool,
same file format. One — a work-domain knowledge graph — thrives: ~93% of its notes touched in the last 90
days, a derived-to-source ratio of roughly 2:1, and mechanically enforced lateral edges. The other — a
personal vault an order of magnitude larger — had 0.3% of notes touched in the same window and effectively
zero lateral links. The difference is architectural, and every element of it is operationalizable:

1. **Claude is the primary writer; the human approves.** Capture happens as a byproduct of work, never as a
   separate act of authorship. Systems that require the human to remember to write notes starve.
2. **Evidence must point at an attractor.** One enforced constraint is why edges exist at all. Unenforced
   graphs decay into taxonomies.
3. **Sources are refined, not surfaced.** Raw material (transcripts, sessions, articles) is processed into
   atomic derived notes. The missing stage in dead vaults is never discoverability — it is refinement.
4. **A ledger makes processing idempotent.** Inputs are enumerable artifacts stamped when processed, so
   nothing silently evaporates and re-runs resume instead of redoing.

The working instance is private and domain-specific. This plugin is its post-hoc generalization: the same
mechanism, instantiable over any domain, with the domain-specific parts pushed into configuration and
project-local skills.

## 2. Goals

- **G1.** Knowledge accrues as a byproduct of work through a ledgered `/process` pipeline. The human's
  role is a single plan approval per run — no manual authorship, no review-as-editing.
- **G2.** The mechanism is domain-agnostic: one plugin instantiates a work product graph, a personal
  cross-domain commons, or a project-scoped knowledge tier, differing only in config and edge skills.
- **G3.** Professional and personal knowledge stay structurally separated; promotion across that boundary
  is derivation under explicit review, never migration.
- **G4.** Applied to the existing known-good private instance, the plugin reproduces its workflow
  unchanged — the proven instance is the regression harness (§8).

## 3. Non-goals

- **NG1.** No ambient/push discovery in v1 — no SessionStart injection, no hooks (D3).
- **NG2.** No retrieval infrastructure: no MCP server, embeddings, or vector search. The index is small
  and read directly.
- **NG3.** No bulk backfill of existing capture archives (read-later services, highlight exports). Bulk
  sources are a late phase and must not sink the seed.
- **NG4.** The plugin never contains content. Graphs, configs-in-use, and notes live in private repos.

---

## 4. Design decisions

### D1 — One shared mechanism; per-graph types

What generalizes is not a type list but a set of **roles**. Each instantiation declares its own types for
each role in config:

| Role | Behavior | Work-graph example | Personal-commons example |
|---|---|---|---|
| **Source** | raw, inert, arrives on its own, carries the ledger stamp | call transcript | session chronicle / transcript |
| **Intermediate** | bounded-event synthesis; disposable scaffolding | call synthesis | — |
| **Evidence** | atomic, provenanced, **must point at ≥1 attractor** | insight | claim |
| **Attractor** | accumulates evidence; has a "so what"; has a lifecycle | opportunity, decision | principle, question |
| **Entity** | the nouns; lookup-only; **never promotes** | account, person | — |
| **Reference** | lookup-retrieved facts; unbounded; never indexed | integration notes | tool facts |
| **Dispatch** | extracted but routed *out* of the graph to an external sink | task, tracker update | task |

The mechanism, stated once:

> Evidence must point at ≥1 attractor. Attractors accumulate evidence and carry a lifecycle
> (`provisional` → `held` → `stale`). Entities and reference are lookup-only. Dispatch classes route to
> external sinks under per-sink approval semantics and are exempt from graph constraints. A health check
> enforces the structure. A changelog records why the graph looks the way it does. An index renders
> attractors for consultation. Promotion *derives* portable notes upward; it never moves them.

**Rejected — one shared type set for every graph.** A work graph's `opportunity` is not a personal
commons' `principle`. Forcing shared types would make working graphs worse to make the model tidier.

### D2 — Capture is a ledgered pipeline, not an act of memory

The pipeline mirrors a proven `/process` workflow:

**inspect → propose plan → single approval → run to completion → stamp → report**

- **Inputs are artifacts that arrive on their own** — call recordings, session chronicles, documents. The
  trigger is a thing existing, not a person remembering. For a personal commons, the source tier is the
  session record itself (chronicle entries, session transcripts): sessions already produce durable
  artifacts, and processing them is the exact structural analogue of processing call transcripts.
- **The source note is the ledger.** A `processed:` stamp (date, ran, skipped, errored) makes the queue
  enumerable and re-runs idempotent. Augment mode processes only what's new.
- **One approval gate.** The orchestrator proposes a concrete plan (what it found, what it will write,
  what it skips and why); the human approves once; the chain runs to completion, pausing only on genuine
  ambiguity or conflict with the existing record. Failures are collected and reported together
  (continue-and-collect), never silently swallowed.
- An **in-band awareness path** (a session proposes a graph note mid-work) remains as the fast path, but
  it is not load-bearing: anything it misses is still in the source artifact and gets caught by the next
  `/process` run.

### D3 — Discovery is pull, not push

Cross-domain connections are made **at refinement time**, by the processing session — which holds both the
new material and the full index in context simultaneously. That is the ideal condition for association:
distilled claim against distilled corpus. "This is the third domain where this pattern has appeared — it
graduates to a principle" surfaces in the `/process` report, at the moment the system is paid to look.

Consuming sessions **pull**: a skill answers "what do we know about X" by reading the index and following
links. There is no ambient injection into every session — the per-session cost is paid forever, the value
event is rare, and the proven private instance has no push channel anywhere in it.

**Steering-grade principles graduate outward.** The few principles that ought to change how sessions behave
are promoted — deliberately, at `/process` time — into whatever always-loaded instruction tier the user
already operates (e.g. global rules). The graph is the epistemic tier where stances accumulate evidence;
the instruction tier is the behavioral view of the few that earned it.

**Deferred, revisit on evidence:** if real use keeps producing "the session should have known this at the
time," a push channel is an afternoon's work — added then on evidence, not now on assumption.

### D4 — Promotion is derivation; the boundary is defense in depth

A domain note never *moves* to a more general graph. A **new, self-contained** note is written carrying
only the portable substance, with provenance as a non-resolving field (`domain: <name>`) — never a path,
never a link. If a derived note needs its source to make sense, it has not generalized.

For any promotion out of a professional domain, three layers — none sufficient alone:

1. **Mechanical.** No wikilink in the target graph may resolve outside it. Catches structure. (Entity
   names in free prose cannot be mechanically excluded — a denylist would import the very names it
   protects — so this layer is necessary, not sufficient.)
2. **LLM review gate.** Before writing: does this name or identify any person, organization, or client?
   Does it disclose any fact specific to one engagement? Would it remain true and useful if every party
   involved vanished? Three noes required. Catches prose.
3. **Human approval.** Every cross-boundary promotion is approved explicitly. Non-negotiable.

### D5 — Outputs are typed and routed to sinks

The graph is one sink among several; the orchestrator is a router. Each instantiation's config declares
its signal classes: what to extract, where it lands, which skill handles it, and what approval mode it
carries. Approval semantics are heterogeneous by design — graph writes run under plan approval; external
trackers may re-confirm at field level; task managers may confirm interactively per item. The ledger stamp
records outcomes per class, so partial failures resume cleanly.

Dispatch classes (e.g. `task`) are first-class outputs that never become graph notes: extracted, routed to
their sink with sink-specific defaults (project routing, labels) built into the config, and recorded in
the stamp.

### D6 — Config over code; specialization splits by kind

The plugin ships the invariant mechanism. Instantiations specialize in two ways, and the split is by
*kind*, not by location:

- **Data-shaped specialization → `.commons.yml`.** Type declarations per role, directory layout, output
  classes and sinks, boundary posture, staleness thresholds.
- **Procedure-shaped specialization → project-local skills.** How to resolve a recording URL, how to
  format a raw transcript, how to write to a particular tracker. The orchestrator discovers these at
  runtime from the live skill list — never from a hardcoded catalog — and routes to them without owning
  them.

The init skill **generates config and scaffolding, never copies of the mechanism**. Generated
project-edge skill stubs are fine — they are owned by the project and expected to specialize and drift.
A generated copy of the orchestrator would be a fork that stops receiving mechanism updates; that is
prohibited by design.

### D7 — The index renders attractors only

Generated, never hand-edited. One line per attractor: **bold title — the "so what" in one clause —
`[domains]`**. Claims and reference never appear in it. Growth is controlled epistemically, not
budgetarily: attractor graduation requires evidence from ≥2 domains, single-domain attractors that were
promoted anyway get flagged for demotion, and stale attractors (no new evidence in N months) get flagged
for review. Index size is a smoke alarm, not a wall.

---

## 5. Plugin components

```
plugins/knowledge-commons/
  .claude-plugin/plugin.json
  references/            # shared contract, read by the skills via ${CLAUDE_PLUGIN_ROOT}
    mechanism.md         #   roles, the invariant, lifecycles, the boundary layers (D1, D4)
    note-formats.md      #   on-disk note formats, index and changelog formats (D7)
    commons-yml.md       #   config schema — DRAFT until the first two instantiations land (O1)
  skills/
    commons-init/        # interview → .commons.yml + scaffold + edge-skill stubs (D6)
    process/             # the orchestrator: inspect → plan → approve → run → stamp (D2, D5)
    knowledge-graph/     # graph read/write mechanics, driven by .commons.yml types (D1)
    commons-check/       # health check + index generation (D7)
```

The `references/` tier exists because three of the four skills need the note formats and the role model.
Inlining them in each `SKILL.md` would guarantee drift between the skill that *writes* a note and the skill
that *validates* it — so the contract is stated once and read by all of them.

- **commons-init** checks for an existing graph at the configured location and creates one if absent;
  interviews for the instantiation's types, sources, sinks, and boundary posture; writes `.commons.yml`;
  scaffolds directories; and stubs any missing project-edge skills (source resolution, sink handlers).
- **process** implements the D2 flow. Inspection adapts to input size (inline for short inputs, subagent
  fan-out by signal class for long ones). It reads the live skill catalog at runtime to find edge skills.
- **knowledge-graph** writes evidence/attractor/entity/reference notes per the configured types, enforces
  the attractor-link requirement at write time, and appends to the changelog.
- **commons-check** runs the mechanical checks (structural integrity, link containment, graduation,
  staleness) and regenerates the index. A scheduled LLM contradiction pass — attractors that conflict,
  evidence that undercuts its own attractor — is a later phase.

### `.commons.yml` sketch (O1 — to be finalized against the first two instantiations)

```yaml
graph:
  root: ~/commons
  types:
    evidence:   { name: claim,     dir: claims/,     requires: attractor-link }
    attractors:
      - { name: principle, dir: principles/, lifecycle: [provisional, held, stale] }
      - { name: question,  dir: questions/,  lifecycle: [open, graduated, abandoned] }
    reference:  { name: reference, dir: reference/ }
sources:
  - { type: session-chronicle, resolve-via: <edge-skill>, ledger: source-note }
outputs:
  claim:     { sink: graph }
  principle: { sink: graph }
  task:      { sink: todoist, via: <edge-skill>, approval: per-item, defaults: { labels: [next] } }
boundary:
  posture: personal          # personal | professional
  promotion-gate: [mechanical, llm-review, human-approval]
```

### Note formats (verbatim)

Notes are markdown files with YAML frontmatter. Links are Obsidian-style wikilinks (`[[Note title]]`),
resolved by filename within the graph root. Filenames are the note title; evidence filenames are prefixed
`YYYY-MM `. All examples below are fresh-authored and illustrative.

```yaml
# claims/2026-07 A dry run caught a config error that review missed.md
---
type: claim
date: 2026-07-08
domain: homelab                # provenance only — set by the processor, confirmed at plan approval;
                               # never a link, never content
supports:                      # ≥1 REQUIRED — enforced by knowledge-graph at write time
  - "[[Execution beats review for validating configuration]]"
---
One self-contained paragraph of substance. If it needs its source to make sense, it has not generalized.
```

```yaml
# principles/Execution beats review for validating configuration.md
---
type: principle
status: provisional            # provisional | held | stale
---
## so what
Run the artifact in the environment it will actually run in before trusting any textual audit of it.

## evidence
- [[2026-07 A dry run caught a config error that review missed]]   (homelab)
```

```yaml
# questions/When is a checklist better than automation.md
---
type: question
status: open                   # open | graduated | abandoned
---
## why I care

## partial answers
- [[…]]                        # graduates to a principle at ≥2 domains
```

Reference notes carry `type: reference` and `verified: <date>`; they have no `supports:` field and are
exempt from the attractor requirement.

**Lifecycle transitions are flagged, never applied silently.** `commons-check` flags graduation
(`provisional` with evidence from ≥2 domains → promote to `held`), demotion (`held` on single-domain
evidence), and staleness (no new evidence in N months). Flags are applied during the next `/process` run
under plan approval.

**Fixed locations at the graph root:** `index.md` (generated by `commons-check --index`, committed, never
hand-edited) and `changelog.md` (current month; archived monthly to `changelog/YYYY-MM.md`). The changelog
entry format is one dated bullet per graph-shaping event: what changed and why.

---

## 6. Instantiations

Three shapes the same mechanism serves; only config and edge skills differ:

1. **A work product graph** — sources: call transcripts; evidence: insights; attractors: opportunities and
   decisions; entities: accounts and people; sinks: graph + task manager + external trackers. The maximal
   instantiation: multi-sink, heterogeneous approvals.
2. **A personal cross-domain commons** — sources: session chronicles and transcripts; evidence: claims;
   attractors: principles and open questions; sinks: graph + task manager. Near-minimal, single graph.
3. **A project knowledge tier** — a `knowledge/` directory inside a project repo; attractors are the
   project's own design questions and deliverable artifacts; domain-local material lives and dies there,
   with only derived, boundary-checked claims promoting to the commons.

## 7. What the graph is *for* (retrieval model)

Two retrieval modes, two tiers:

- **Reference** is retrieved by **lookup** — you know what you want. It can grow without bound precisely
  because it never enters the index.
- **Reasoning** (evidence → attractors) is retrieved by **association** — at `/process` time, when new
  claims meet the full corpus, and on demand when a session pulls the index for a judgment-heavy task.

You could never look up a principle you don't know applies; that connection has to be *made*, and D3 fixes
where: in the refinement loop, by the session whose job it is.

## 8. Verification — the known-good instance is the regression harness

The plugin's acceptance test is not synthetic. The existing private work-domain instance already runs this
workflow end to end; the plugin passes when, applied to that instance (as config + edge skills, on its own
private account), it retains the known-good behavior:

1. **Plan-level equivalence (dry run).** Feed the plugin orchestrator an already-processed source; compare
   its proposed plan against the incumbent's on the same input. No writes, immediate signal on anything
   the generalization dropped.
2. **Next-real-input (live run).** Process the next real source through the plugin instead of the
   incumbent skill, reviewed as usual. The user is a calibrated instrument for degradation.

The second acceptance metric is **proposal precision** on the personal commons: of the claims and
principles `/process` proposes from real session records, the fraction accepted unedited. High precision
is what makes the experience an approval flow rather than an editing job; sustained low precision fails
the premise (G1) regardless of how sound the architecture is.

## 9. Phasing

| Phase | Work | Gate |
|---|---|---|
| **1** | `commons-init`, `process`, `knowledge-graph`, `commons-check`. Instantiate the personal commons (private repo); run `/process` over real recent session records. | Proposal precision holds up over ~2 weeks of real runs |
| **2** | Apply the plugin to the reference work instance: config + edge skills on that account. | Plan-level equivalence, then a clean live run (§8) |
| **3** | Register the plugin in `marketplace.json`; README and docs. | Installable by a stranger; examples fresh-authored |
| **4** | Scheduled cross-graph sweep + LLM contradiction pass. | Sweep surfaces a promotion the in-band path missed |
| **5** | Bulk-source processing (read-later archives, highlight exports). | Signal-to-noise justifies the stage |

The plugin directory exists unregistered until Phase 3 — the marketplace never advertises an installable
that installs nothing.

## 10. Risks & open items

- **R1. Proposal precision at the abstraction level.** Deriving portable principles is genuine abstraction,
  harder than structured extraction against a tight work ontology. Measured directly in Phase 1; the
  design lowers stakes (evidence is cheap; attractor promotion is rare and gated) but cannot substitute
  for precision.
- **R2. Boundary leaks via prose.** D4's layers reduce but cannot eliminate; the human gate is the
  backstop, and **nothing engagement-, client-, or employer-specific ever enters this public repo — every
  commit is public history, including examples and fixtures. Fresh-authored examples only.**
- **R3. Two graphs' instruction tiers drift** (graph principles vs. always-loaded rules). Resolved by
  design: rules are the graduation *target*, not a parallel store (D3).
- **O1.** `.commons.yml` schema — finalize against the first two instantiations, not in the abstract.
- **O2.** Chronicle/session-record ledger format — where the `processed:` stamp lives for repos that don't
  yet keep chronicles (fall back to session transcript IDs?). Existing chronicle entries carry no
  `processed:` field today; the stamp is additive frontmatter on the chronicle file (or a sidecar ledger
  for stamp-less sources), settled in Phase 1.
- **O3.** Staleness threshold N — pick empirically after ~6 months of attractors.

**Resolution path for O1/O2 (deliberate):** these are finalized *during* Phases 1–2 by the author's own
sessions, against the live personal instantiation and the private reference instance — which is exactly
why public registration (Phase 3) comes after them. A cold implementer starting from this spec alone is
expected to be blocked on O1/O2; that is sequencing, not an omission. Everything needed to build the
skills' skeletons and the personal instantiation alongside the author is specified above.

---

## Revision log

### v0.3.1 — 2026-07-12 (Phase 1 build)

The four skills were built (plugin v0.2.0, still unregistered). Three decisions taken during the build, all
recorded here rather than left in the commit history:

- **Skill names ship as specced** — `commons-init`, `process`, `knowledge-graph`, `commons-check`. The
  repo's README convention (action-oriented gerunds) was **relaxed** rather than the names being deformed to
  fit it. Research established that skill naming has no ecosystem standard: the slash command derives from
  the *directory* name, auto-invocation is driven by the `description` field rather than the name, and
  Anthropic's own bundled skills are mostly bare verbs (`/run`, `/loop`, `/simplify`). Plugin skills are
  namespaced (`knowledge-commons:process`) regardless, which supplies the disambiguation a generic name
  lacks.
- **A plugin-level `references/` tier was added** (§5) as the single source of truth for the mechanism,
  the note formats, and the config schema.
- **Working defaults adopted for the open items,** marked provisional in `references/commons-yml.md`:
  **O2** — the `processed:` stamp is additive frontmatter on the source note, with a sidecar
  `.commons-ledger.yml` for sources that cannot carry frontmatter; the stamp is **per output class**, so a
  partial failure resumes only the errored class. **O3** — staleness N defaults to 6 months.

**A cold-read dry run was run before the build was called done.** A no-context agent was given only the skill
files and a throwaway config, and asked to execute `/process --dry-run` against three real chronicle entries.
The proposals themselves were sound — atomic claims, attractors with real "so what" clauses — which is the
first (weak, n=1) signal on **R1 proposal precision**. But the run surfaced three load-bearing defects that
author review had not:

- **`domain:` had no defined origin.** It gates graduation, demotion, and the index — and no field in
  `.commons.yml` produced it. Now a required field on each source tier.
- **Nothing regenerated `index.md` after a run.** The index *is* the distilled corpus that the next run's
  association step reads, so every run after the first would have read a stale one — quietly degrading the
  exact capability D3 is built on.
- **The ledger stamped whole files, but chronicle files hold several sessions and are appended to.** A file
  stamped in the afternoon would have silently dropped that evening's session forever.

**This materially advances O2.** The open item existed because the ledger format could not be settled in the
abstract — and the thing that settled it was a real source with real structure. The stamp now records *how
far it got* (`through:`) rather than a boolean, and inspect re-queues any source that has grown since. That
is the shape to confirm against the live instance, not a guess to replace.

The third finding is also the strongest available evidence for the design's own thesis: **an independent
reader with no stake in the author's intent caught what the author's review could not.** Worth noticing that
the failure mode it caught — a plausible artifact that passes textual review and fails on contact with a real
input — is the same one the previous session recorded, one entry earlier in this same chronicle.

O1 and O2 remain open: they are confirmed against the live personal instance, per the resolution path above.
