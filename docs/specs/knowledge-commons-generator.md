# Knowledge Commons Plugin — Specification

> **Version:** 0.6.1 (draft) · **Status:** pre-build · **Date:** 2026-07-12
>
> **Start here if you are implementing.** §6 (components) and §7 (config) are what you build from; §§1–5 are
> why. The build rewrites `plugins/knowledge-commons/` in place — that plugin was built from the superseded
> v0.3 (`knowledge-commons-plugin.md`) and its architecture is known-wrong, though roughly 40% of its content
> survives (see §6's note on `note-formats.md`). **Read `references/` in the existing plugin before deleting
> anything.**
>
> **v0.6** adds what a second, *non-adversarial* cold read found — an engineer told simply to build it, not to
> hunt for problems. Its verdict was **"buildable; I'd start Monday,"** and it independently arrived at two of
> v0.5's own corrections (the checker must be an executable, and *"I don't trust prose to refuse itself"*),
> which is the strongest available evidence those were right. What it still had to invent:
>
> - **A write is a transaction, not a file.** Creating one evidence note also edits its map, its attractor's
>   evidence section, and a hub's section. Validate-one-file cannot see that. `knowledge-graph` now performs
>   the whole set, re-validates the touched scope, and **reverts on any new error.**
> - **"Stdlib only" has a price v0.5 asserted away.** Verified: `python3` here is 3.9.6 with **no PyYAML**. The
>   validator must parse YAML itself (`bin/_miniyaml.py`). The reference's checker would not run on this
>   machine at all.
> - **The multi-event ledger was deleted but never replaced.** An event's canonical identity is now
>   `<artifact-path>#<verbatim-heading>`, found via an `event-delimiter:`, and the ledger note lives **in the
>   graph** — so `/process` never writes into the source repository, and the self-match bug cannot recur.
> - **Feeder graphs need a queue.** v0.5 made `/process` purely input-driven, which is right for a pasted URL
>   and wrong for a chronicle: it reintroduces "remember to hand it over," which is the failure the design
>   exists to eliminate. Both entry modes are now specified.
> - **`--upgrade` was undefinable.** Generated skills now carry `kc:invariant` / `kc:procedure` markers, which
>   is what makes D6's "the fork surface is only the procedure" a fact rather than an aspiration.
>
> **v0.5 corrected v0.4 after an adversarial cold-read audit returned "No."** An independent session with no
> context tried to build from v0.4 and could not. Its findings, all verified against the live reference before
> being acted on:
>
> - **The lifecycle was declared a universal invariant, and its example statuses were fabricated.** The
>   reference has no `status:` field and no lifecycle on any attractor; the values shown came from a different
>   design document and were presented as if observed. The lifecycle, graduation, and `domain:` are
>   **commons-tier mechanisms** (D5b), not invariants — and treating them as universal made the ≥2-domain bar
>   incoherent in every feeder graph.
> - **"Refuses" had no mechanism.** D6's entire architectural argument rests on the plugin refusing invariant
>   violations at write time, but a markdown skill cannot refuse — it can only be told to. The plugin now ships
>   an executable validator (`bin/validate.py`, stdlib only) that `knowledge-graph` runs before every write and
>   `commons-check` runs over the whole graph.
> - **The commons IS special-cased**, and v0.4 claimed otherwise on aesthetic grounds. The instruction tier is
>   a flat directory of markdown files, not a graph; promotion into it cannot share a code path. Stated
>   plainly rather than hidden behind a symmetry that breaks on contact with the filesystem.
> - **The navigation tier had no on-disk format**, and `map` was not even a declared type — despite `type:`
>   being authoritative and a folderless graph being required to validate.
> - The interview, the extraction-skill template, and `--seed`'s read contract were **named and motivated but
>   never defined.** All three are now specified.
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
directory layout. It is in instructions of a kind no configuration file can express — paraphrasing, to keep
this document's examples fresh-authored (§11, R2):

- **Separate what was observed from what was proposed in response, and evaluate them apart.** A speculative
  solution says nothing about the quality of the observation that prompted it, and collapsing the two loses
  the observation.
- **Under uncertainty, capture.** A thin note is recoverable on a later pass; an observation never written
  down is invisible damage. The error costs are asymmetric, so the bar is asymmetric.
- **Check what a disqualifier is actually attaching to.** Words like "obvious" or "speculative" often describe
  the *surface framing* of a thing rather than the thing, and skipping on that basis discards good material.

These are **debiasing instructions for an LLM**. They are the reason the graph produces insight rather than
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

### D3 — Six type roles, not two

v0.3 had evidence and attractors, and modelled the rest as an afterthought. There are six, and the ones it
missed carry real constraints. (`atlas` and `map` are declared types too — see §7 — because `type:` is
authoritative and a folderless graph must still be able to identify its own navigation tier.)

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
> point at ≥1 attractor. Attractors accumulate evidence. Hubs and attractors maintain bidirectional link
> obligations. Reference is lookup-only. Dispatch routes out. A health check enforces the structure. A
> changelog records why the graph looks the way it does. Promotion *derives* portable notes upward; it never
> moves them.

**What is deliberately NOT in it: the lifecycle, graduation, and `domain:`.** Those are **commons-tier
mechanisms** (D5b), not universal invariants — and getting this wrong is the single most consequential error
in the drafts of this spec.

The reference graph — the one that demonstrably works — has **no `status:` field, no lifecycle, and no
`domain:` field on any note.** Its attractors simply accumulate evidence and never graduate. An earlier draft
of this spec declared the lifecycle an invariant and illustrated it with statuses fabricated from a *different*
design document, presented as if observed in the reference. They were not.

The error was not cosmetic. It made the **≥2-domain graduation bar incoherent in every feeder graph** — in a
single-domain graph, "evidence from two domains" can never happen, so the bar either never fires or, worse,
gets quietly reinterpreted against whatever field happens to be handy.

### D5b — The commons tier: lifecycle, graduation, and `domain:`

A **feeder graph** is single-domain by construction: it holds one engagement, one project, one body of work.
Its attractors accumulate evidence and that is all they do.

The **commons** is the only graph that federates *across* domains, so it is the only graph where "this has now
appeared in a second domain" is a statement that can be made at all. Three mechanisms exist there and nowhere
else:

- **`domain:`** — carried by a note that arrived **by promotion**, and set to the **originating graph's
  `graph.name`**. A feeder graph's notes carry no `domain:`; their provenance is `source:` and their
  associations are link-lists. **One field, one writer, one meaning.**
- **A lifecycle** — an ordered `[proposed, earned, retired]`, named by the commons for itself. Resolved **by
  position**, never by literal name, so a rule that says "flag it `held`" is wrong for a type that has no
  `held`.
- **Graduation at ≥2 domains** — an attractor whose evidence spans two distinct originating graphs has earned
  a stance. Below that bar it hasn't; questions absorb the singletons (§5, item 3).

**A feeder graph declares no lifecycle, and `commons-check` runs no graduation check against it.** The
regenerated reference therefore has no lifecycle either — which is correct, because the original doesn't, and
adding one would make "functional equivalent" mean "equivalent, plus a tier we invented."

**A consequence worth stating plainly (entailed by D8):** the commons has **no source tiers of its own.**
Nothing is processed directly into it; everything in it arrived by promotion from a feeder. So a project whose
chronicles should feed the commons needs its **own `knowledge/` graph** first — that graph processes the
chronicles into local claims, and promotes the portable ones upward. The commons is the distillate, never the
inbox.

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

**"Refuses" must be mechanical, not rhetorical.** A skill is a markdown instruction file; a skill cannot
refuse anything — it can only be *told* to refuse, and an instruction to refuse is exactly the kind of
guardrail that the method note (§9) says author review never catches failing.

So the plugin ships an **executable validator**:

```
plugins/knowledge-commons/bin/validate.py     # stdlib only; no dependencies to install
```

`knowledge-graph` is instructed to run it **before every write**, passing the graph root and the proposed
note, and to **abort the write on a non-zero exit** and report. `commons-check` runs the *same* validator over
the whole graph. One implementation, two entrypoints — so the write-time gate and the health check can never
disagree about what the rules are.

The validator is where cross-file obligations live, because they are the ones a per-file check cannot see:
*does the parent map actually list this note? is the bidirectional pair consistent in both directions? does
this wikilink resolve, following aliases?* Those are the invariants, and they are only checkable with the
whole graph in view.

**A write is a transaction, not a file.** Creating one evidence note also edits its parent map (the down-link),
the attractor's evidence section, and — if a hub is named — the hub's section. Validating one file cannot see
that. So `knowledge-graph`:

1. performs the **whole set** of edits,
2. re-runs the validator scoped to the touched files,
3. and on any **new** error, **reverts the entire set** and reports the refusal.

Half a bidirectional pair is not a smaller violation than none; it is a worse one. The transaction is what
makes "refuses" mean something.

**Stdlib only — and this has a real cost that must be priced, not asserted.** The repository's `CLAUDE.md`
states there are no dependencies to install, and the plugin must run on a fresh machine and under any user
account. **Verified on this machine: `python3` is 3.9.6 and PyYAML is not installed.** So "stdlib only" means
the validator **parses YAML itself** — a vendored subset parser (`bin/_miniyaml.py`) covering exactly what
`.commons.yml` and note frontmatter use: block maps, block lists, inline flow maps and lists, quoted scalars,
comments. Prefer PyYAML when importable; fall back to the vendored parser otherwise.

This is not a footnote. The reference's checker does `import yaml` and delegates link resolution to a
desktop-app CLI — **it would not run on this machine at all.** Both are dependencies the plugin cannot inherit,
and the CLI is unusable from a second user account regardless. Writing the parser is a real line item in the
build.

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

### D8 — Graphs federate; the commons is fed, never authored

**A graph in isolation is a dead end, and a spec that generates isolated graphs has missed the point.** The
commons does not accumulate knowledge because someone sits down to write it. It accumulates because *every
other graph feeds it as a byproduct of work.* Remove the feeding and the commons starves — which is precisely
how the dead vault's `decision/` folder died at seven notes.

Graphs form a **tree of derivation**, and each edge is a boundary crossing under D9's gate:

```
project graphs        ──┐
(a repo's knowledge/    │   promotes-to
 tier; domain-local     ├──────────────▶   the commons
 material lives and     │                  (cross-domain; personal)
 dies here)             │                        │
professional graphs   ──┘                        │  promotes-to
(the reference; a                                ▼
 client engagement)                    the instruction tier
                                       (~/.claude/rules/ — behavioral)
```

Every feeder graph declares **`promotes-to:`** — the graph it derives upward into. A graph with no
`promotes-to:` is a leaf, and that is a deliberate choice, not a default.

**The commons IS special-cased, and an earlier draft claimed otherwise on aesthetic grounds.** That draft said
the commons was "simply the graph whose `promotes-to:` is the instruction tier," making D7's graduation the
same mechanism as every other promotion. It is not, because **the instruction tier is not a graph**:
`~/.claude/rules/` is a flat directory of markdown files with no atlas, no maps, no types, no
evidence→attractor edge, and no `.commons.yml`. Promotion into it cannot share a code path with promotion into
a graph, and pretending otherwise would have produced a spec whose central symmetry breaks on first contact
with the filesystem.

The commons is therefore special in three concrete ways, each stated rather than hidden:

1. It has **no source tiers** — nothing is processed into it; everything arrives by promotion (D5b).
2. It is the only graph with a **lifecycle, graduation, and `domain:`** (D5b).
3. Its `promotes-to:` names the **instruction tier**, which is a *different kind of target* — a rules
   directory, not a graph. Graduating a principle into it means writing a rule file, not deriving a note, and
   it runs its own gate: *is this steering-grade — does it change how a session should behave?* plus human
   approval. **Read the existing rules first**; a graph built from sessions those rules steered will keep
   re-deriving them.

**Three promotion paths, and the first is the load-bearing one:**

1. **In-band, at `/process` time.** Every run on a graph with a `promotes-to:` ends by asking *"does any of
   this generalize?"* and proposes derived notes for the target graph **inside the same plan**. This is
   capture-as-byproduct, and it is the single mechanism that separates a living graph from a dead one. **It is
   not optional and it is not a fast path** — v0.3 described it as a "non-load-bearing fast path" and then
   implemented nothing, which is how a described-but-absent mechanism survives review.
2. **The scheduled cross-graph sweep.** A periodic pass that reads a feeder graph in bulk, proposes what
   in-band missed, and — more valuably — spots patterns invisible note-by-note (*"this has now appeared in a
   third domain; it graduates"*). The safety net, which is why it is not optional either: the in-band protocol
   works best in a bounded domain where the skill is always loaded, and a session in some unrelated repo may
   simply never think to propose a claim.
3. **Explicit `/process --promote <graph>`.** The manual escape hatch.

**The commons must know its feeders.** `commons-init` registers each new graph with its target, so the sweep
can enumerate what to read. Without a registry, path 2 has no input and the safety net is imaginary.

**Nothing is authored directly into the commons.** If a claim did not derive from a feeder graph under the
gate, it does not belong there — the commons is the *distillate*, and hand-writing into it reintroduces the
exact "remember to write notes" failure that kills every personal knowledge system.

### D9 — Promotion is derivation; the boundary is defense in depth

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
2. **Debiasing instructions** — separate the observation from the solution proposed in response; check what a
   disqualifier is actually attaching to before acting on it.
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
  bin/
    validate.py        # THE validator. stdlib only. Cross-file invariants.
                       #   knowledge-graph runs it before every write (abort on non-zero);
                       #   commons-check runs it over the whole graph. One implementation,
                       #   two entrypoints — so the write gate and the health check can
                       #   never disagree about the rules.
  references/          # the contract, read by every skill via ${CLAUDE_PLUGIN_ROOT}
    mechanism.md       #   roles, the invariant, navigation, the boundary
    note-formats.md    #   frontmatter contract, note + map + atlas + hub shapes
    commons-yml.md     #   config schema
    templates/         #   the generator's skill templates — FRESH-AUTHORED (R2)
  skills/
    commons-init/      # the GENERATOR: interview → config + scaffold + project skills
    process/           # the orchestrator: resolve → inspect → plan → approve → run → stamp
    knowledge-graph/   # write mechanics; calls the validator; refuses violations
    commons-check/     # health check (same validator) + index generation
```

### commons-init — the generator

**Interviews deeply, then writes a working skill set — not stubs.** A stub would mean the domain procedure is
hand-authored anyway, and the acceptance test would measure the author, not the generator.

**It instantiates a graph *into a federation*, never in isolation.** Every invocation:

1. **Finds or creates the commons.** If no commons exists at the configured location, it creates one — the
   root graph, whose own `promotes-to:` is the instruction tier. This is the first thing it does, before
   touching the project.
2. **Creates and wires the project graph**, with `promotes-to:` pointing at that commons.
3. **Registers the project graph with the commons**, so the cross-graph sweep can enumerate its feeders.

A `commons-init` that generates a standalone graph has produced an island, and islands starve. The wiring is
not a follow-up step.

It produces:

- **`.commons.yml`** — the data-shaped half, including `promotes-to:`.
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

#### The interview

Six blocks. The first four fill `.commons.yml`; the last two fill the **extraction skill**, and they are the
ones that matter — R4 names them the generator's central unvalidated assumption.

**1. The graph.** Root; name; posture (personal/professional); is this a feeder or the commons; if a feeder,
what does it promote to (find-or-create).

**2. The types.** What does this domain call its evidence? Its attractors — and is each *open* (accumulating
toward an outcome) or *settled* (a decision with reasoning)? Are there entities worth curating a hub around,
and which attractor does each hub bind to? Is there a reference tier? A source tier that must be preserved
verbatim?

**3. The schema.** Per type: required fields, forbidden fields, controlled vocabularies. **And the tag-vs-field
question, asked explicitly for every candidate:** *would searching this tag's parent alone return a useful
set?* If no, it is a field, not a tag.

**4. Sources and sinks.** What arrives on its own, and how is it resolved? Does it produce a durable note (if
not → `ledger: none`)? What signal classes should inspection look for? Where do non-graph outputs go, with
what approval mode, and what must run before what?

**5. Extraction — the domain's procedure.** The block the whole generator exists for:
- Walk me through processing one source, start to finish. What gets created, in what order?
- When you create a piece of evidence, **what else must change?** (the attractor's evidence section; its
  frontmatter; the hub's section; the map entry; the source note's backfill) — this is the propagation
  choreography, and the ordering is load-bearing.
- **What is durable here, and what belongs in an operational system instead?**
- What distinguishes a good note of each type from a merely correct one?
- What conditional extractions fire on recognizing a situation in the material?
- **What must never be captured in this graph?**

**6. Judgment and bias — the debiasing block.** Elicited as *rules*, not preferences:
- When you're uncertain whether something clears the bar, do you capture or skip — **and which error costs
  more?** (In the reference: capture, because a missed observation is invisible damage. **This asymmetry must
  be stated, not assumed** — a graph where noise is the expensive error wants the opposite bar.)
- What are the failure modes you've *seen* in this domain — where has a plausible-looking note been wrong?
- What distinctions get collapsed that shouldn't be?

The interview writes the answers to blocks 5 and 6 into the extraction skill **as prose**, because that is
what they are. It does not attempt to reduce them to config.

#### What a generated extraction skill contains

Fixed shape, five slots. The template ships the invariant scaffolding; the interview fills the italics.

```markdown
---
name: <extract-via name>
description: >
  Turn a <source type> into notes in the <graph> knowledge graph. Called by the
  knowledge-commons orchestrator during /process; not usually invoked directly.
allowed-tools: ["Read", "Grep", "Glob", "Skill"]     # deliberately NO Write/Edit
---

<!-- kc:invariant v0.5 — plugin-owned. `commons-init --upgrade` replaces this block. -->
## the contract
Every write goes through the plugin's `knowledge-graph` skill, which runs the validator
and refuses violations. **This skill never writes a file.** It chooses which notes, in
what order, with what side-effects; the plugin enforces the invariants and you cannot
route around them — and you don't need to.

Check before creating: search first; if a note on the topic exists, update it.
Stub before linking. Every level of a tag hierarchy must be independently useful for
retrieval; if searching the parent alone wouldn't return a useful set, it's a field.
<!-- /kc:invariant -->

<!-- kc:procedure — project-owned. `--upgrade` NEVER touches this block. -->
## what this domain captures          <- interview block 5
*<what is durable here; what belongs in an operational system instead;
  what must never be captured>*

## the procedure                       <- interview block 5
*<walk of one source, start to finish: what is created, in what order>*

## propagation (ordered — the ordering is load-bearing)   <- interview block 5
*<when evidence is created, what else must change — and in what order>*

## judgment                            <- interview block 6
*<the promote-vs-skip bar and its error asymmetry; the debiasing rules;
  the distinctions that must not be collapsed>*
<!-- /kc:procedure -->
```

**`allowed-tools` deliberately omits `Write` and `Edit`.** The generated skill *cannot* write a file even if
its prose drifted — it has to go through `knowledge-graph`. This is the cheapest possible enforcement of D6,
and it costs nothing.

**The `kc:invariant` / `kc:procedure` markers are what make `--upgrade` possible at all.** Without a marked
boundary between plugin-owned and project-owned text, there is nothing to diff: `--upgrade` re-renders the
invariant block from the current template and leaves the procedure block untouched, forever. This is the
mechanism that makes D6's "the fork surface is only the procedure" a fact rather than an aspiration.

**The template is fresh-authored** (R2). Its scaffolding is written from the mechanism; only the *italic*
slots carry domain content, and that content comes from the interview — never lifted from a reference skill's
prose.

#### `--seed <path>`

Reads a directory of `SKILL.md` files plus any `references/` and checker script beside them, and **proposes**
each interview answer for confirmation. It never writes without confirmation.

Two rules, both forced by §8's bug list:

- **Prose is authoritative over code for *intent*; code is authoritative over prose for *current behavior*.**
  Where they disagree — and they will, since four of six controlled vocabularies are documented but unenforced
  — **surface the disagreement to the human rather than picking.** That divergence is a finding about the
  reference, not an ambiguity to be silently resolved.
- **`--seed` may not invent a field the source doesn't have.** If the reference has no lifecycle (it does not),
  seeding a feeder graph proposes none. A field absent from the source is absent from the proposal, and if the
  target config requires it, the interview asks cold and says why.

### process — the orchestrator

A **thin router and sequencer**. It never reimplements a downstream skill's logic.

**resolve → inspect → plan → approve → run → stamp → report**

0. **Two entry modes, and a graph may use both.**
   - **Handed an input** (`/process <url-or-path>`) — the reference's mode. The trigger is a human passing
     something in.
   - **Enumerating a queue** (`/process` with no argument) — for tiers that declare a `path:` and `glob:`.
     `/process` globs them, splits multi-event artifacts on `event-delimiter:`, and works the **unprocessed**
     events: those whose canonical identity has no ledger note in the graph.

   **A feeder graph fed by chronicles needs the queue mode**, and dropping it would be a quiet regression.
   The reference is input-driven because a call arrives as a URL someone pastes. A chronicle arrives by
   *existing* — and if a human has to remember to hand each one over, that is the "remember to write notes"
   failure the entire design exists to eliminate (D8), reintroduced one level up. **The trigger is a thing
   existing, not a person remembering.**

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
8. **Ask whether any of it generalizes.** On a graph with a `promotes-to:`, the run ends by proposing derived
   notes for the target graph — **in the same plan**, so the human approves capture and promotion together
   (D8, path 1). Every professional-posture promotion additionally passes D9's three layers, and its human
   gate is asked **separately, every time.** A run that writes to the graph and never asks this question is the
   failure mode the whole design exists to prevent: the source material is refined and the generalization is
   lost, silently, forever.
9. **Continue-and-collect** on failure. Never silently swallow.
10. **Stamp and report.** The stamp records promotion outcomes alongside everything else, so a partial failure
    resumes.

**Re-pause only for:** genuine ambiguity, or **conflict with the existing record** — which is not an error to
route around but the most interesting thing that can happen. Do **not** pause to create a new entity that
doesn't exist yet; that runs under the approved plan.

#### `--promote <target-graph>` — the explicit path

Step 8 is the *in-band* promotion path and it is the load-bearing one. `--promote` is the manual escape hatch,
and it is its own mode because a promotion has no source queue.

It **loads two configs**, and confusing them is the first way this goes wrong:

- **The target's `.commons.yml` governs every write** — its type names, its directories, its map structure,
  its attractor field. You are writing into *that* graph.
- **The source's is read for exactly one value: `graph.name`**, which becomes the promoted note's `domain:`.

Derive candidates (write the note you *would* write — the rewrite is where sanitization happens), run D9's
three layers on each **including on the `domain:` value**, present for explicit human approval, then write via
`knowledge-graph` against the *target's* config. A promotion **may create the attractor it lands on**, since
evidence cannot cross without one and a fresh commons has none. **Never carry an attractor's evidence list
across** — rebuild it from what was actually promoted; a source-graph note title can itself be a leak.

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

### Operational constants

Small individually; collectively a day of guessing if left unstated.

| Thing | Value |
|---|---|
| **Inspect fan-out threshold** | ~1,500 words. Below → inline single pass; above → one subagent per `inspect-classes` entry. **A tunable heuristic, not a hard rule.** |
| **Subagent finding-list format** | Each returns a JSON list of `{class, summary, evidence_quote, entities[], confidence}`. The orchestrator synthesizes; it does not re-read the source. |
| **`split-note-at-lines`** | Lines. Renamed from `split-note-at` to say so. |
| **Who creates a map** | `knowledge-graph`, at write time: if a note's `genitor` names a map that does not exist and ≥`new-map-at` notes now cluster there, it proposes the map **in the plan**. Maps are never created silently, and `commons-check` **flags** a needed map rather than creating one. *(v0.4 left this ownerless — the growth thresholds were config and the rule shapes invariant, and no component created anything.)* |
| **`min-attractors`** | Config, floor of 1. **A config value below the invariant is a config error, not an override** — `commons-check` rejects `min-attractors: 0`. D4 wins. |
| **Filename case** | Content notes: the natural title, spaces and all — the filename **is** the link target and the display name. Maps and the atlas: lowercase concept names (`insights.md`, `principium.md`). Date prefixes only where the note *is* a dated event, per type (`date-prefix: true`). |
| **Aliases** | `aliases:` — a list of display synonyms. **The validator resolves wikilinks through them.** The reference's checker does not, which is §8's most likely latent bug; the plugin must not inherit it. |
| **`map:` per type** | Every type declares which map it is entered in. The check table needs a type→expected-parent binding and there was none; without it the down-link check has no target. |
| **`hubs[].field`** | The frontmatter field **on the attractor side** that names the hub. `bidir-with` and `section` give the hub's half; this gives the attractor's. (Guessing it by pluralizing the hub's type name is the kind of silent convention that breaks on the first type that doesn't pluralize.) |
| **`promotes-to`** | An object, `{kind: graph\|instruction-tier, path: <path>}` — not a bare path. The instruction tier is not a graph (D8) and the code path differs, so the config must say which kind it is rather than making the reader infer it from the path. |
| **Schema violations** | **Errors, not warnings.** `knowledge-graph` *refuses* a missing required field at write time; a health check that merely warns about what the writer refuses is incoherent. (The reference warns. That is a divergence, and a deliberate one.) |

### What happens to the existing `references/note-formats.md`

The superseded plugin ships a coherent on-disk contract that knows nothing of `genitor`, maps, the atlas,
hubs, `source:`, or `processed:`. **Half of it survives and half is obsolete, and a builder must not have to
guess which.**

- **Survives:** the index line format; the changelog format and monthly rotation; the closed flag vocabulary;
  the evidence/attractor/question/reference body shapes; filesystem-safe titles.
- **Obsolete:** anything implying a graph has no navigation tier; the `YYYY-MM ` prefix as universal (it is
  per-type); `domain:` on every evidence note (commons-only, per D5b).
- **Missing entirely, and must be added:** the frontmatter contract (`genitor`, `tags`, `aliases`, `type`,
  `source`, `processed`); the map file shape (category headings at `heading-level`, entries as the *first*
  wikilink on a bullet line, alphabetical within heading); the atlas shape; the hub shape (curated link
  sections — *editorial, not an exhaustive mirror of the map*).

It is an **amendment**, not a rewrite.

---

## 7. Configuration (`.commons.yml`)

The data-shaped half. Sketch — finalized against the reference regeneration, not in the abstract.

**A FEEDER graph** (a project tier, or a professional engagement graph):

```yaml
graph:
  root: <path>
  name: <graph-name>            # becomes `domain:` on notes this graph promotes UPWARD.
                                # Notes in THIS graph carry no `domain:` — see D5b.
  atlas: principium.md          # the one note with no genitor
  maps-dir: maps/
  parent-field: genitor
  growth: { new-map-at: 5, promote-heading-at: 7, split-note-at-lines: 200 }
  promotes-to: { kind: graph, path: <path-to-commons> }   # D8. A leaf omits it.

types:
  # `type:` in frontmatter is AUTHORITATIVE. Directory is a default, not a rule —
  # a graph with no folders still validates. That is why `map` and `atlas` are
  # declared types: in a folderless graph, nothing else identifies them.
  # Every type declares the `map:` it is entered in — that is the down-link's target.
  atlas:     { name: atlas }
  map:       { name: map, heading-level: 1 }     # category headings inside a map
  source:    { name: transcript, dir: transcripts/, map: transcripts, preserve-verbatim: true }
  evidence:  { name: insight,    dir: insights/,    map: insights,
               attractor-field: opportunities, min-attractors: 1 }
  attractors:
    # NO lifecycle. A feeder graph is single-domain; nothing graduates. See D5b.
    - { name: opportunity, dir: opportunities/, map: opportunities }
    - { name: decision,    dir: decisions/,     map: decisions }
  hubs:                                          # optional
    # `field:` is the frontmatter key ON THE ATTRACTOR that names this hub.
    - { name: firm,   dir: firms/,  map: firms,  bidir-with: opportunity,
        section: "## opportunities", field: firms }
    - { name: person, dir: people/, map: people, bidir-with: null }
  reference: { name: research, dir: research/, map: research }

schema:                                          # per-type frontmatter contract
  insight:
    required:  [genitor, tags, date, source, <controlled-field>, <controlled-field>]
    forbidden: [domain]                          # `domain:` exists only in the commons
    filename:  { case: natural, date-prefix: false }
  firm:
    forbidden: [firms, date]                     # a hub doesn't reference itself; not a dated event
  controlled-values:
    <field>: [<value>, <value>, ...]

sources:
  # Two entry modes. A tier may support either or both.
  - type: call-transcript                        # HANDED IN: a human pastes a URL
    resolve-via: <resolver-skill>                #   URL → text
    extract-via: <extraction-skill>              #   ← the hook v0.3 lacked
    inspect-classes: [follow-up, entity-change, decision, ...]
    ledger: source-note                          #   a source note in THE GRAPH holds `processed:`

  - type: session-chronicle                      # ENUMERATED: the trigger is a thing existing
    path: <repo>/docs/chronicle/                 #   globbed by `/process` with no argument
    glob: "20*.md"                               #   required; a permissive default queues non-sources
    event-delimiter: "^## \\d{2}:\\d{2}"         #   one FILE is a day; one EVENT is a session
    extract-via: <extraction-skill>
    ledger: source-note

  - type: email-thread
    extract-via: <different-skill>               #   structurally different pipeline
    ledger: none                                 #   produces no note; treated as new each pass.
                                                 #   DECLARED, not discovered.

outputs:
  insight:     { sink: graph }
  follow-up:   { sink: <tasks>, via: <sink-skill>, approval: per-item, after: [graph],
                 defaults: { project: <x>, labels: [next] } }
  record-sync: { sink: <db>, via: <sink-skill>, approval: field-level, after: [graph] }

boundary:
  posture: professional          # personal | professional
  promotion-gate: [mechanical, llm-review, human-approval]
```

**The COMMONS** — genuinely different, and the differences are the ones D5b and D8 name:

```yaml
graph:
  root: ~/commons
  name: commons
  atlas: principium.md
  maps-dir: maps/
  # The instruction tier is NOT a graph (D8), and `kind:` says so explicitly rather
  # than making /process infer it from the path.
  promotes-to: { kind: instruction-tier, path: ~/.claude/rules/ }

types:
  atlas:    { name: atlas }
  map:      { name: map, heading-level: 1 }
  evidence: { name: claim, dir: claims/, attractor-field: supports, min-attractors: 1 }
  attractors:
    # ONLY the commons has these. See D5b.
    - { name: principle, dir: principles/, lifecycle: [provisional, held, stale] }
    - { name: question,  dir: questions/,  lifecycle: [open, graduated, abandoned],
        graduates-to: principle }
  reference: { name: reference, dir: reference/ }

schema:
  claim:
    required: [genitor, tags, date, domain]   # `domain:` REQUIRED here and nowhere else
    filename: { case: natural, date-prefix: true }

# NO `sources:` block. Nothing is processed into the commons; everything arrives
# by promotion from a feeder (D5b). The commons is the distillate, never the inbox.

graduation:
  bar: 2                          # distinct `domain:` values (i.e. distinct feeder graphs)
  staleness-months: 6

feeders:                          # the registry; commons-init appends on each wiring
  - { name: <graph>, root: <path>, posture: personal }
  - { name: <graph>, root: <path>, posture: professional }

boundary:
  posture: personal
  promotion-gate: [mechanical, llm-review, human-approval]
```

### The ledger

**The unit of input is one event, not one file.** The reference keys its ledger on a canonical `source:`
identity — a recording URL, a thread permalink — and *searches the graph* for the note carrying it.

v0.3 mapped "the source note is the ledger" onto **one file**, but a chronicle *file* is a day holding several
sessions. That single mis-mapping produced an append problem the reference doesn't have, and then a pile of
machinery to solve it (`through:`, `digest:`, self-match bugs, unit-scoped augment). **All of it is deleted.**
One session block = one event = one canonical identity.

**And here is what actually replaces it, because "one event" is an assertion until the identity is named.**

An artifact holding several events (a chronicle file = one *day*, holding two or three sessions) declares an
**`event-delimiter:`** — a heading regex that finds the boundaries. `/process` splits on it and treats each
block as its own input. Nothing else about the artifact matters.

**The canonical identity of an event is `<artifact-path>#<verbatim-heading>`**, e.g.
`docs/chronicle/2026-07-12.md### 14:01 — Converged the design`. The heading is copied **verbatim** — it exists
to be *found again*, and a heading you normalized is a heading you cannot match.

**What verbatim costs, stated rather than discovered.** Two edges follow from keying on the heading text, and
both are accepted deliberately:

- **Editing a heading after processing orphans its ledger note**, and the event re-processes as new. Fixing a
  typo in a session title costs one duplicate proposal.
- **Two identical headings in one artifact collide** on the same identity; the second is treated as already
  processed.

Both are rare, and the human-in-the-loop catches the re-proposal — but they are the price of an identity that
can be *found again*, and the alternative (a normalized or generated id) buys stability by making the identity
unmatchable against the artifact, which is the failure v0.3 spent three rounds discovering. `commons-check`
flags a duplicate-heading collision as an error, since that one is silent.

**The ledger note lives in the graph, not in the source repo.** For each processed event, `knowledge-graph`
writes a **source-role note** into the graph carrying that identity in `source:` and holding the `processed:`
stamp — exactly as the reference writes a transcript note carrying a recording URL. `/process` finds it by
searching the *graph* for the `source:`, which is what §6 step 2 already says.

Two things fall out, and both are wins:

- **`/process` never writes into the source repository.** A project graph whose source tier globs its own
  repo's `docs/chronicle/` leaves no trace there — no stamped frontmatter, no diff in a tree you are actively
  working in. v0.3's `ledger: source-note` wrote the stamp *into the chronicle file*, which is also what made
  the self-match bug possible.
- **The self-match bug cannot occur.** The stamp is not in the file it describes, so nothing can match itself.

**The scope limit — an input that produces no durable note has no ledger.** The ledger *is* the source's note,
so a tier that deliberately creates none (an email tier, which needs no synthesis artifact and is batched at
the entity level) has nothing to carry `processed:`. Such a tier declares **`ledger: none`** and is **treated
as new on every pass** — acceptable *only* where the tier is low-volume and a human is in the loop to notice
re-proposals, which is the same limit the reference accepts and names.

**It must be declared, not discovered.** A tier that produces no note and does not say `ledger: none` is a
config error: `/process` would search for a ledger note forever, find nothing, and silently re-read and
re-propose that source on every run, compounding. `commons-check` flags it.

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
| **2** | Instantiate the commons from the *proven* generator. Wire the reference to it with `promotes-to:`. | **A real claim derives from the reference upward into the commons, through all three layers of D9's gate.** |
| **3** | A project knowledge tier in a third repo, wired to the same commons. | **An attractor in the commons carries evidence from two different domains** — i.e. the federation actually produced a cross-domain connection, which is the entire premise |
| **4** | Register in `marketplace.json`; README and docs. | Installable by a stranger; examples fresh-authored |
| **5** | Scheduled cross-graph sweep + LLM contradiction pass. | The sweep surfaces a promotion the in-band path missed |
| **6** | Bulk-source processing (read-later archives, highlight exports). | Signal-to-noise justifies the stage |

**Phases 2 and 3 are the gates that would have caught this spec's own blind spot.** A phase that ends with a
working graph proves the generator. Only a phase that ends with **a claim having crossed a boundary**, and
then with **an attractor spanning two domains**, proves the *federation* — and the federation is the product.
Every earlier version of this spec gated on graphs existing, which is why every earlier version shipped
islands.

**The reference comes first, and that ordering is the whole lesson of v0.3.** It is the only instantiation
whose correct output is already known — which is what makes it a regression harness. Validating a generator
against a graph where nobody knows what right looks like is precisely the mistake that produced v0.3.

The plugin stays **unregistered** until Phase 3.

---

## 11. Risks & open items

- **R1. Proposal precision at the abstraction level.** Deriving portable principles is genuine abstraction,
  harder than structured extraction against a tight ontology. Measured directly in Phase 2.
- **R2. Boundary leaks via prose.** D9's layers reduce but cannot eliminate; the human gate is the backstop.
  **Nothing engagement-, client-, or employer-specific ever enters this public repo — every commit is public
  history, including examples and fixtures. Fresh-authored examples only.**

  **This applies to the generator's own templates.** `references/templates/` must be written from the
  *mechanism*, never lifted from a reference skill's prose — a template is the most-copied artifact in the
  plugin, and a phrase lifted into it propagates into every project anyone ever generates. The same rule
  governs this spec: its illustrations are paraphrased, not quoted.
- **R6. The federation may not fire outside a bounded domain.** In-band capture (D8, path 1) works in the
  reference partly *because* the domain is bounded and the skill is always loaded. A session in some unrelated
  repo may simply never think to propose a claim — which is why the scheduled sweep is a safety net rather
  than a nicety, and why Phase 3 gates on an attractor actually spanning two domains rather than on a project
  graph merely existing. If the sweep is what produces every cross-domain connection and in-band produces
  none, the in-band premise is wrong and should be said so plainly.
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
