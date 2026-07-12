# Knowledge Commons Plugin — Specification

> **Version:** 0.4 (draft) · **Status:** pre-build · **Date:** 2026-07-12
>
> **Supersedes v0.3** (`knowledge-commons-plugin.md`), which was built and merged (PR #62) and then found to
> be architecturally wrong. v0.3 assumed domain variation is **data-shaped** — that a generic runtime engine
> reading `.commons.yml` could serve any graph. The proven reference implementation shows the opposite: most
> of what makes a knowledge graph work is **procedure-shaped**, and cannot be expressed in YAML.
>
> This is the public **mechanism** spec. Content — graphs, their configs, their notes — never lives in this
> repository.

---

## 1. What went wrong, and why it matters

v0.3 was written from a de-identified design document without reading the **reference implementation** it was
generalizing — a working `/process` + knowledge-graph system that has run in one professional domain for over
a year, producing 676 notes with 93% touched in 90 days and a 2:1 derived-to-source ratio.

Reading it afterward showed the error immediately. The reference's value is not in its type names or its
directory layout. It is in things like:

- *"Split observations from proposed solutions before evaluating either — the speculative-ness of a proposed
  solution does not bear on the observation."*
- *"When uncertain between promote-single-source and skip-cleanly, lean promote — a thin captured insight is
  recoverable on a future pass; a missed observation is invisible damage."*
- *"Disqualifiers like 'obvious' or 'speculative' often attach to the surface framing rather than the
  underlying observation; re-check which one the disqualifier is actually applying to before skipping."*

These are **debiasing instructions for an LLM**. They are the reason the graph produces insight instead of
transcription. **No YAML key can hold them.** A generic engine reading a config file could never reproduce the
system it was built to generalize — which means v0.3 was, in principle, incapable of passing its own
acceptance test.

**The corrected model: the plugin is a generator.** It scaffolds a project-owned skill set carrying the
invariants, and interviews for the procedure that only the domain knows.

## 2. Goals

- **G1.** Knowledge accrues as a byproduct of work through a ledgered `/process` pipeline. The human's role is
  a single plan approval per run.
- **G2.** The plugin **generates** an instantiation — a project-owned skill set plus config — rather than
  serving all instantiations from one runtime engine.
- **G3.** Applied to the reference implementation, the generated system is a **functional equivalent**: it
  performs every workflow the reference performs. *(The acceptance test, §9.)*
- **G4.** Professional and personal knowledge stay structurally separated; crossing the boundary is derivation
  under explicit review, never migration.

## 3. Non-goals

- **NG1.** No ambient/push discovery. No SessionStart hook. Discovery is pull.
- **NG2.** No retrieval infrastructure — no MCP, embeddings, or vector search. The index is small and read
  directly. *You cannot retrieve a surprising connection by similarity search:* if a claim were semantically
  near the current task, the connection would not be surprising.
- **NG3.** The plugin never contains content. Graphs, configs-in-use, and notes live in private repos.
- **NG4.** Not a byte-for-byte clone of the reference. The reference has latent bugs (§8); the generated
  system fixes them and reports the delta.

---

## 4. Architecture

### D1 — Three tiers, and the dead-vault diagnosis depends on all three

The motivating natural experiment: two vaults, one author, one tool, one format. One thrives (93% of notes
touched in 90 days); the other is a landfill (0.3%, effectively zero lateral links).

The dead vault's failure is usually described as "it was a taxonomy." That is imprecise, and the imprecision
is what v0.3 got wrong. **The dead vault had maps.** Its wikilinks were parent-pointers to `[[decisions]]`,
`[[ideas]]`, `[[coding]]` — that *is* a navigation tier, and it worked fine for navigation. What it lacked was
**attractors and the enforced lateral edge.**

So a graph needs three distinct tiers, and they answer three different questions:

| Tier | Question | Artifact | Retrieval mode |
|---|---|---|---|
| **Navigation** | *"Where does this live?"* | atlas → maps → notes, via `genitor:` | browse |
| **Reasoning** | *"What do we believe, and on what evidence?"* | evidence → attractors | association |
| **Reference** | *"What's the fact I already know I need?"* | reference notes | lookup |

Maps without attractors is a taxonomy. Attractors without maps is unbrowsable. **Every graph has to have a
map** — and every graph has to have attractors. v0.3 shipped the second and dropped the first.

The **index** is not the map. The map is *complete* and answers "show me what's here." The index is
*editorial*, renders attractors only, and is the **stimulus** for association. Both are generated artifacts;
they are not interchangeable.

### D2 — The navigation tier, precisely

One frontmatter field: **`genitor:`**, a single-valued wikilink to the note's navigation parent.

```
atlas (the one note with no genitor)
  └─ maps        (genitor → atlas or a parent map)
       └─ notes  (genitor → their type's map)
```

Three properties, each load-bearing:

1. **`genitor` is the navigation parent, deliberately *not* the semantic parent.** An evidence note's
   `genitor` is its type's map — **not the source it came from.** Provenance lives in `source:`; associations
   live in other frontmatter fields and body wikilinks. *`genitor` answers "where do I file this," never "what
   is this about."* This is what keeps the navigation tree **flat and stable** while the provenance mesh grows
   arbitrarily deep. Conflate them and maps become recursive and unbrowsable.

2. **Reachability is enforced by two independent local invariants, not by traversal:**
   - **Up-link:** every note has a `genitor` that resolves.
   - **Down-link:** every note appears as an entry **in its parent map's body**, and every map appears as an
     entry in the atlas.

   Both are checked separately. **The down-link is the one people forget** — a valid `genitor` alone does not
   make a note reachable, because a human navigates by *reading the map's bullet list*, not by querying
   inbound `genitor` fields. The redundancy is the point: the up-link is machine-checkable metadata, the
   down-link is the human-browsable index.

3. **A map entry is the *first* wikilink on a bullet line.** Any further wikilinks on that line are
   annotations, not entries. Without this rule, an annotated entry — `- [[Note]] (context, see [[Other]])` —
   corrupts completeness and duplicate checking.

**Growth rules** (thresholds are config; the shapes are invariant): create a map when ≥N notes cluster with no
existing map (never create an empty one); promote a map heading to a sub-map at ≥M entries; adding a top-level
map obliges updating the atlas. Entries and headings are alphabetically ordered, inserted in position, never
appended.

### D3 — Four type roles, not two

v0.3 had evidence and attractors. The reference has four, and the two it added carry real constraints.

| Role | Behavior | Reference | Commons |
|---|---|---|---|
| **Source** | raw, inert, addressable, preserved *exactly* as received | transcript | chronicle session |
| **Evidence** | atomic, quote-anchored, provenanced; **must point at ≥1 attractor** | insight | claim |
| **Attractor** | accumulates evidence; has a "so what"; has a lifecycle | opportunity, decision | principle, question |
| **Hub** *(optional)* | curated entry point for an entity; **bidirectional obligation with attractors** | firm, person | — |
| **Reference** | lookup-retrieved; unbounded; never indexed | research | tool facts |
| **Dispatch** | routed *out* to an external sink; never becomes a note | task, tracker row | task |

**The hub role and its bidirectional obligation.** A hub is a curated link-section note — *"the most important
things to know about this entity right now."* It is **editorial, not exhaustive**; the *map* is the exhaustive
index. Losing that distinction turns hubs into duplicate maps.

The obligation runs **both ways** and is checked in both directions:

- every attractor an entity's hub lists in its `## <attractors>` section must name that entity in its own
  frontmatter, **and**
- every entity an attractor names in frontmatter must link back to that attractor in its hub body.

Hubs are **optional** — a graph with no entities worth curating omits them and the check doesn't run.

**Entity/reference/hub are lookup-only and never promote across a boundary.**

### D4 — The invariant, stated once

> Every note is reachable from the atlas: its `genitor` resolves, and its parent map lists it. Evidence must
> point at ≥1 attractor. Attractors accumulate evidence and carry a lifecycle whose statuses each graph names
> for itself: **proposed → earned → retired**. Hubs and attractors maintain bidirectional link obligations.
> Reference is lookup-only. Dispatch routes out. A health check enforces the structure. A changelog records
> why the graph looks the way it does. An index renders attractors for association. Promotion *derives*
> portable notes upward; it never moves them.

Note what it does **not** say: it does not name the statuses. Lifecycles are declared per type as an ordered
list, and every rule in every skill resolves the status **by position**. A rule that says "flag it `held`" is
wrong — a `question` has no `held`.

### D5 — The specialization split (the correction to v0.3's D6)

Three kinds, not two. v0.3 had the first two and gave the third nowhere to live.

| Kind | Lives in | Examples |
|---|---|---|
| **Invariant** | the **plugin** | reachability, the evidence→attractor edge, bidirectional obligations, link resolution, the changelog discipline, the severity policy, the ledger |
| **Data-shaped** | **`.commons.yml`** | type names, directories, controlled vocabularies, required/forbidden fields per type, growth thresholds, skip lists, sink routing, approval modes |
| **Procedure-shaped** | **generated, project-owned skills** | how *this* domain turns *its* sources into *its* notes — and everything in §5 |

**This is what v0.3 missed.** Its config had exactly two edge-skill hooks — `resolve-via` (source → text) and
`via` (class → sink) — because it read "(source resolution, sink handlers)" as the complete taxonomy of
project-local skills. The **extraction procedure** — the single biggest procedure-shaped thing in the system —
had no hook, so it fell into the generic orchestrator, where it cannot live.

### D6 — Generated skills are thin; the plugin owns the obligations

The original objection to generating skills was real: *a generated copy is a fork that stops receiving
mechanism updates.* The answer is to make the fork surface small.

**A generated skill carries only domain procedure and delegates every write to the plugin's
`knowledge-graph`.** The plugin enforces the obligations at write time and **refuses** violations:

- an evidence note naming no attractor → refused
- a half-written bidirectional pair → refused
- a note with no `genitor`, or absent from its map → refused
- a wikilink that resolves outside the graph → refused

So the generated skill decides **which** types, in **what** order, with **what** side-effects — the domain
choreography. It cannot route around the invariants, and it does not need to know what a "firm" is.
Invariant fixes reach every project for free, because they live in the plugin, not in the copy. What drifts is
the procedure, and the procedure is *supposed* to drift.

### D7 — Discovery is pull; steering-grade principles graduate outward

Cross-domain connections are made **at refinement time**, by the processing session — the one moment that
holds both the new material and the full index at once. That is the ideal condition for association, and it is
the only moment the system is paid to look. Consuming sessions **pull** (read the index, follow links).

The few principles that ought to change how sessions *behave* are promoted — deliberately, under approval —
into the always-loaded instruction tier (e.g. `~/.claude/rules/`). The graph is the **epistemic** tier where
stances accumulate evidence; the instruction tier is the **behavioral** view of the few that earned it. Rules
are the graduation *target*, not a parallel store. **Read the instruction tier before proposing a promotion** —
a graph built from sessions that were steered by those rules will keep re-deriving them.

### D8 — Promotion is derivation; the boundary is defense in depth

A domain note **never moves**. Promotion writes a **new, self-contained note** carrying only portable
substance, with provenance as a non-resolving field (`domain: <originating-graph-name>`) — never a path, never
a link. *If a derived note needs its source to make sense, it has not generalized.*

Three layers, none sufficient alone:

1. **Mechanical.** No wikilink resolves outside the target graph.
2. **LLM review.** Three questions; **every answer must be "no"**; a single "yes" refuses:
   - Does this name or identify any person, organization, or client?
   - Does it disclose any fact specific to one engagement — a figure, a date, a timeline, a contract term?
   - **Would it stop being true or useful if every party involved vanished?**

   Run them against the **`domain:` value** as well as the body. That field carries the originating graph's
   name and nothing else in the three layers reads it — a graph named for its client would sail through every
   prose check and stamp that name into every note it promotes. **Name professional graphs for their kind of
   work, not their party.**
3. **Human approval.** Every cross-boundary promotion, explicitly. Non-negotiable.

> *v0.3 phrased the third question positively — "would it remain true and useful" — while requiring "three
> noes," which inverts one limb: a portable note answers* yes *to it. Read literally, the gate admitted only
> non-portable notes and refused every legitimate one. An adversarial execution test caught it. **The same
> inversion is present in the private v0.2 design document**, so this is a real defect in the reference
> thinking, not a transcription error.*

Additional rules, all learned from execution:

- **An attractor's evidence list never crosses a boundary.** It holds titles from the source graph, and a
  title can itself be a leak. Rebuild it from what was actually promoted.
- **A promotion may create the attractor it lands on** — otherwise the first promotion into an empty graph is
  impossible, since evidence cannot cross without an attractor to support.
- **A promoted note is dated by its promotion**, not by the originating note: the source's date is itself an
  engagement fact.

---

## 5. What only a generated skill can hold

This is the class v0.3 under-built. It is not a short list, and it is the substance of the system.

1. **The source → note extraction procedure**, per source type. A call and an email get *structurally
   different* pipelines: a call is a rich bounded event warranting an intermediate synthesis; email is
   transactional, needs no synthesis artifact, and must be **batched at the entity level rather than
   thread-by-thread, because cross-thread synthesis is where the value is.** No config expresses that.
2. **Debiasing instructions.** *"Split observations from proposed solutions before evaluating either."*
   *"Re-check which one the disqualifier is actually applying to before skipping."*
3. **The promote-vs-skip bar and its error asymmetry.** *"Lean promote — a missed observation is invisible
   damage."* v0.3 **inverted this**, calling a singleton claim "a smell" and dropping it. The correct
   resolution — and the reason the two-attractor model exists — is: **evidence is captured freely; attractors
   are gated at ≥2 domains; questions absorb the singletons.** Nothing is dropped; nothing is enshrined early.
4. **The vault-worthiness gate.** What is *durable* vs *ephemeral* here. Deal amounts, contract status, live
   dates belong in operational systems, not the graph.
5. **Cross-type propagation choreography.** The ordered set of side-effects when a note is created — create the
   attractor before the evidence that must name it; update the attractor's evidence section *and* its
   frontmatter; update the hub's section; add to the map at the right alphabetical position; backfill the
   synthesis note; append to the entity's interaction log. **The ordering is load-bearing** and the side-effect
   set is domain-specific.
6. **Title conventions per type.** *"Outcome-focused: enable X, reduce Y."* *"An evidence title is a concise,
   entity-neutral statement of the claim"* — i.e. strip the source entity out of the claim.
7. **Quote selection.** *"Find the strongest supporting quote."*
8. **Per-section writing briefs.** Not section *names* — briefs. *"Never collapse multi-directional flows into
   'bidirectional' at the aggregate level; name each element's direction."* *"Contract-safe language legal can
   lift."* *"Don't manufacture a moat from a thin constraint."*
9. **Conditional secondary extractions** that fire on recognizing a situation in the material, each with its
   own distinguishing rule and anti-fabrication guard.
10. **Source-fetch procedure** — how to resolve this source type's canonical identifier, and its prohibitions
    (*"never WebFetch the app; use its API"*).
11. **The sink's tool-adapter gotchas** — a set of hard-won facts about a CLI or API, not a set of values.
12. **Tag-vs-field adjudication at creation time.** The *rule* is invariant (below); applying it is judgment.

**The tag-vs-field discriminator** (invariant, and the sharpest idea in the reference): *every level of a tag
hierarchy must be independently useful for retrieval. **If searching the parent tag alone wouldn't return a
useful set, it's a field, not a tag.*** This is what keeps a tag namespace from rotting. Promote it to a
first-class plugin concept.

---

## 6. Plugin components

```
plugins/knowledge-commons/
  references/          # the contract, read by every skill via ${CLAUDE_PLUGIN_ROOT}
    mechanism.md       #   roles, the invariant, navigation, lifecycles, the boundary
    note-formats.md    #   frontmatter contract, note shapes, index + changelog formats
    commons-yml.md     #   config schema
    templates/         #   the generator's skill templates (extraction, sink, resolver)
  skills/
    commons-init/      # the GENERATOR: interview → config + scaffold + project skills
    process/           # the orchestrator: resolve → inspect → plan → approve → run → stamp
    knowledge-graph/   # write mechanics; enforces every invariant; refuses violations
    commons-check/     # health check + index generation
```

### commons-init — the generator

**Interviews deeply, then writes a working skill set — not stubs.** A stub would mean the domain procedure is
hand-authored anyway, and the acceptance test would measure the author, not the generator.

It produces:

- **`.commons.yml`** — the data-shaped half.
- **`.claude/skills/<extract>/SKILL.md`** — the domain's extraction skill, **generated with its procedure
  filled in from the interview**, carrying the invariants and delegating every write to the plugin's
  `knowledge-graph`. One per source type where the pipelines differ structurally.
- **`.claude/skills/<resolver>/`, `.claude/skills/<sink>/`** — stubs, where they don't already exist.
- **A project `/process` command** — a thin alias to the plugin's orchestrator.
- **Scaffolding** — the atlas, the maps directory, the type directories, an empty changelog.

**`--seed <path>`** reads an existing skill set and *proposes* each interview answer for confirmation
(*"evidence is called `insight`; the promote bar is lean-promote; on new evidence you also update the
opportunity's `## evidence` and the entity hub's section — correct?"*). Far less typing, and the confirmations
are exactly where a misreading gets caught. This is the path the reference regeneration takes.

**`--upgrade`** re-runs the templates against an existing project and diffs.

**It never copies `process`, `knowledge-graph`, or `commons-check` into the project.** Those are the
mechanism.

### process — the orchestrator

A **thin router and sequencer**. It never reimplements a downstream skill's logic.

**resolve → inspect → plan → approve → run → stamp → report**

1. **Resolve and identify.** Match the input to a source tier; normalize to its **canonical `source:`
   identity**; invoke the tier's resolver if it needs one.
2. **Find the ledger note** by searching the graph for that `source:`. Found → read its `processed:` stamp,
   enter **augment mode**: do only what's not yet done, and say what already exists rather than recreating it.
   **If the identity can't be confidently matched, fall back to searching and asking — never trust a fuzzy
   match as the ledger.**
3. **Inspect, size-adaptive.** Short inputs inline; long ones **fan out one subagent per signal class**, each
   returning a structured finding list. Read the **full index** — holding new material and the distilled corpus
   at once is what makes association possible at all.
4. **Propose a plan** — which skills run, what each will do, what is skipped and why. **Editable:
   `[y / edit / explain]`.** Surface cross-domain connections and steering-grade candidates. Suggest skills
   *outside* the plan rather than auto-running them.
5. **One approval**, then run to completion.
6. **Run in dependency order** (`after:` in config). A sink that reads a note must run after the note exists.
7. **Approval is heterogeneous, and fine-grained subsumes coarse-grained.** Graph writes run under the plan
   approval. A record sink re-confirms at field level. A task sink confirms **per item** — and *because* it
   does, it needs no separate batch gate. **Never stack both.**
8. **Continue-and-collect** on failure. Never silently swallow.
9. **Stamp and report.**

**Re-pause only for:** genuine ambiguity, or **conflict with the existing record** — which is not an error to
route around but the most interesting thing that can happen. Do **not** pause to create a new entity that
doesn't exist yet; that runs under the approved plan.

### knowledge-graph — the write layer

The only skill that writes graph notes. It enforces, and **refuses**:

- `genitor` present and resolving; the note entered in its parent map, **alphabetically in position**
- evidence names ≥1 attractor, and each resolves
- bidirectional obligations consistent in both directions
- no wikilink resolves outside the graph
- **check before creating** — search first; if a note on the topic exists, **update it**
- **stub before linking** — you may not link a note that doesn't exist; a one-line stub is fine, and stubs
  accumulate content over time. This is what makes "unresolved link = error" tenable.
- controlled values drawn from their declared sets; required fields present; forbidden fields absent

It appends the changelog and knows nothing about any domain.

### commons-check — the health check

**Reimplemented natively.** The reference delegates link resolution and orphan detection to a desktop-app CLI
that is unusable from a second user account. The plugin's check must run anywhere, with **no external
dependency**, and must be **alias-aware** (the reference's Python layer is not — see §8).

Checks, each classified invariant with its config:

| Check | Config |
|---|---|
| Frontmatter present; `genitor` present and resolving | field name |
| `genitor` matches the expected parent for the note's type | type → expected-parent table |
| Every note appears in its map; every map appears in the atlas | type → map bindings, atlas name |
| Map entries alphabetically ordered within headings | ordering-exempt list |
| No duplicate entries within a map | — |
| Every evidence note names ≥1 attractor, each resolving | evidence type, attractor field |
| Bidirectional hub↔attractor obligations, checked both ways | the type pairs |
| Controlled values drawn from their sets; required present; forbidden absent | the per-type schema |
| Wikilinks resolve (**alias-aware**) | — |
| Orphans (no inbound link of any kind) | expected-orphan allowlist |
| Attractor lifecycle: graduation (≥2 domains → position 1), demotion, staleness | thresholds |
| The `processed:` ledger stamp is well-formed | — |

**Severity policy** (invariant): a **dangling reference is an error**; an **incomplete index is a warning**.
Exit non-zero **iff** an error. Warnings do not fail the run.

**Flags, never applies.** Lifecycle transitions are applied by `/process` under plan approval.

`--index` regenerates `index.md`: attractors only, one line each — **bold title — the "so what" in one clause
— `[domains]`.**

---

## 7. Configuration (`.commons.yml`)

The data-shaped half. Sketch — finalized against the reference regeneration, not in the abstract.

```yaml
graph:
  root: ~/Obsidian/<graph>
  name: <graph-name>            # the domain: stamped on notes this graph promotes elsewhere
  atlas: principium.md
  maps-dir: maps/
  parent-field: genitor
  growth: { new-map-at: 5, promote-heading-at: 7, split-note-at: 200 }

types:
  # `type:` in frontmatter is AUTHORITATIVE. Directory is a default, not a rule —
  # a graph with no folders still validates.
  source:    { name: transcript, dir: transcripts/, preserve-verbatim: true }
  evidence:  { name: insight,    dir: insights/, attractor-field: opportunities, min-attractors: 1 }
  attractors:
    - { name: opportunity, dir: opportunities/, lifecycle: [provisional, held, stale] }
    - { name: decision,    dir: decisions/,     lifecycle: [open, settled, superseded] }
  hubs:                                          # optional
    - { name: firm,   dir: firms/,  bidir-with: opportunity, section: "## opportunities" }
    - { name: person, dir: people/, bidir-with: null }
  reference: { name: research, dir: research/ }

schema:                                          # per-type frontmatter contract
  insight:
    required:  [date, source, product-area, signal]
    forbidden: []
    filename:  { case: natural, date-prefix: false }
  firm:
    forbidden: [firms, date]                     # a hub doesn't reference itself; not a dated event
  controlled-values:
    product-area: [api, billing, ...]
    signal:       [pain-point, feature-request, ...]

sources:
  - type: call-transcript
    domain: <name>
    resolve-via: <resolver-skill>                # URL → text
    extract-via: <extraction-skill>              # ← the hook v0.3 lacked
    inspect-classes: [follow-up, entity-change, decision, ...]
    ledger: source-note                          # the source's own note carries `processed:`
  - type: email-thread
    extract-via: <different-skill>               # structurally different pipeline

outputs:
  insight:     { sink: graph }
  follow-up:   { sink: <tasks>, via: <sink-skill>, approval: per-item, after: [graph],
                 defaults: { project: <x>, labels: [next] } }
  record-sync: { sink: <db>, via: <sink-skill>, approval: field-level, after: [graph] }

boundary:
  posture: professional          # personal | professional
  promotion-gate: [mechanical, llm-review, human-approval]
```

### The ledger

**The unit of input is one event, not one file.** The reference keys its ledger on a canonical `source:`
identity — a recording URL, a thread permalink — and *searches the graph* for the note carrying it.

v0.3 mapped "the source note is the ledger" onto **one file**, but a chronicle *file* is a day holding several
sessions. That single mis-mapping produced an append problem the reference doesn't have, and then a pile of
machinery to solve it (`through:`, `digest:`, self-match bugs, unit-scoped augment). **All of it is deleted.**
One session block = one event = one canonical identity.

```yaml
processed:
  - date: 2026-06-08
    ran:     [<skill>, <skill>]
    skipped: [<skill>]
    errored: []
```

A **list**, so it keeps a history. Keyed by **skill**, matching the reference. Augment mode reads it to decide
what still needs doing.

*(The reference references this stamp but never defines or validates it — §8. v0.4 adds it to the frontmatter
contract and checks it.)*

### The sink contract

Generalized from the reference's task sink; every sink handler implements it:

- **Extract only commitments.** *"A topic being mentioned isn't a follow-up."*
- **Over-propose rather than drop** — justified *because* the per-item gate makes skipping cheap. **The recall
  bias and the gate are coupled; don't take one without the other.**
- **Dedupe by surfacing, never suppressing.** Show the suspected duplicate verbatim inside the item's prompt
  and let the human decide.
- **One item at a time: accept / edit / skip.** Never a bulk multi-select.
- **No inferred deadlines.** Due dates only when the source states one.
- **Owner-derived routing.** Items owned by others are still created, labeled differently — *tracked, not
  dropped.*
- **Return a three-way tally.** A skipped item is a real outcome, not a failure.

---

## 8. The reference's latent bugs

Found by reading it. The generated system **fixes these and reports the delta** — "functional equivalent"
means the workflow is reproduced, not the defects.

1. **The checker is not alias-aware.** Its Python layer resolves wikilinks against bare filenames while the
   conventions actively encourage `aliases:`. Any link written via an alias would be reported unresolved. It
   only works today because the bash layer delegates resolution to an alias-aware external CLI — the very
   dependency the plugin must drop. **The most likely latent bug; fold aliases into the file index.**
2. **Three note types get zero validation.** Required-field and controlled-value checks early-return unless the
   directory is in one lookup table, and map-completeness iterates another — both omit the same three types.
3. **A dead config key.** A required-fields entry is keyed on a namespaced tag that the notes never carry, so
   that branch never fires.
4. **First-match-wins on multi-tag notes.** Validation breaks after the first entity type found, so a note
   tagged with two validates only one.
5. **Four of six controlled vocabularies are documented but unenforced.**
6. **Heading ordering is required by the docs and never checked.**
7. **Directory is authoritative in the checker while the docs say it is "a convenience."** v0.4 resolves this:
   **`type:` in frontmatter is authoritative; directory is a default.**
8. **A section heading is matched by a hardcoded case-sensitive regex** — renaming it silently disables a
   cross-reference check.
9. **The `processed:` stamp has no schema and no check.**

---

## 9. Verification — the reference is the regression harness

**Side-by-side, non-destructive. Nothing is ripped out.**

1. **Regenerate.** Run `commons-init --seed <reference-skills>` into a scratch location. The interview's
   proposed answers are confirmed or corrected.
2. **Plan-level equivalence (dry run).** Feed the regenerated system an input the reference has already
   processed. Compare its **proposed plan** against what the reference actually produced for that input. No
   writes. Anything the generalization dropped shows up immediately, with nothing at risk.
3. **Live run.** Process the next real input through the regenerated system, reviewed as usual.

**Gate:** the regenerated system performs every workflow the reference performs. Divergences are triaged as
*deliberate generalization*, *bug fixed* (§8), or *regression* — and only the third fails.

**Second metric — proposal precision:** of the notes `/process` proposes, the fraction accepted unedited.
High precision is what makes this an approval flow rather than an editing job. Sustained low precision fails
G1 regardless of how sound the architecture is.

**Method note.** Every defect found in v0.3 across six rounds — a ledger that silently dropped material, a
`through:` field that matched itself, a cold-start deadlock, a boundary gate with one limb inverted, an
interview that never asked for a required field — was found by **executing the thing** or by **checking two
documents against each other.** Author review found none of them. Build accordingly: the cold-read and the
execution test are not optional finishing steps.

---

## 10. Phasing

| Phase | Work | Gate |
|---|---|---|
| **1** | Build the plugin. Regenerate the reference with `--seed`. Side-by-side equivalence. | The regenerated system reproduces the reference's workflows (§9) |
| **2** | Instantiate the personal commons from the *proven* generator. | Proposal precision holds over ~2 weeks of real runs |
| **3** | Register in `marketplace.json`; README and docs. | Installable by a stranger; examples fresh-authored |
| **4** | Scheduled cross-graph sweep + LLM contradiction pass. | The sweep surfaces a promotion the in-band path missed |
| **5** | Bulk-source processing (read-later archives, highlight exports). | Signal-to-noise justifies the stage |

**The reference comes first, and that ordering is the whole lesson of v0.3.** It is the only instantiation
whose correct output is already known — which is what makes it a regression harness. Validating a generator
against a graph where nobody knows what right looks like is precisely the mistake that produced v0.3.

The plugin stays **unregistered** until Phase 3.

---

## 11. Risks & open items

- **R1. Proposal precision at the abstraction level.** Deriving portable principles is genuine abstraction,
  harder than structured extraction against a tight ontology. Measured directly in Phase 2.
- **R2. Boundary leaks via prose.** D8's layers reduce but cannot eliminate; the human gate is the backstop.
  **Nothing engagement-, client-, or employer-specific ever enters this public repo — every commit is public
  history, including examples and fixtures. Fresh-authored examples only.**
- **R3. The attractor partition is unstable, and proposal precision cannot detect it.** Two runs over the same
  corpus produce different attractors. "Cluster by the stance they imply" is the right instruction and an
  underdetermined one. The partition is where nearly all the value lives, and the Phase-2 gate is blind to it:
  it measures whether the human accepts what's put in front of them, not whether a different run would have
  proposed better clusters. **Measure it deliberately** — re-process known material into a scratch graph and
  compare — rather than discovering it in Phase 4.
- **R4. The interview may not elicit the procedure.** The generator's premise is that ~25 questions can
  surface what took a year to accumulate in the reference. `--seed` mitigates by proposing from an existing
  skill, but greenfield projects have no seed. **This is the generator's central unvalidated assumption**, and
  Phase 1 tests it directly.
- **R5. Generated-skill drift.** The fork surface is small (D6), but it is not zero. `--upgrade` diffs
  templates; it cannot reconcile a procedure the project has rewritten.
- **O1.** The `.commons.yml` schema — finalized against the reference regeneration, not in the abstract.
- **O2.** Staleness threshold N — pick empirically after ~6 months of real attractors.
- **O3.** Whether the personal commons needs hub notes (entities that span domains). Currently no; revisit.
