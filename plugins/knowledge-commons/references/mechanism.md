# The Mechanism

The invariant shared by every knowledge commons graph. Type names differ per graph; **this does not.**

Read this before writing to or checking a graph. The authoritative design is
`docs/specs/knowledge-commons-generator.md` (D1–D9). This file is the operational statement of it, and
**`bin/validate.py` is the executable statement of it** — where prose and the validator could diverge, the
validator is the contract. Every check code named below (`KC…`) is one the validator actually emits.

All examples are drawn from the fixture graphs in `tests/fixtures/` — a community **orchard** (a feeder) and
the **commons** it promotes into. They are fresh-authored, neutral, and real: they pass the validator, so an
example that cites them is also true.

## Three tiers, and a graph needs all three

The motivating natural experiment is two vaults, one author, one tool, one format. One thrives; the other is a
landfill with effectively zero lateral links. The dead one is usually described as "a taxonomy," and that
description is imprecise in the way that matters: **the dead vault had maps.** Its wikilinks were
parent-pointers — `[[decisions]]`, `[[ideas]]` — and that *is* a navigation tier, and it navigated fine. What
it lacked was **attractors and the enforced lateral edge.**

So a graph has three tiers, answering three different questions:

| Tier | Question | Artifact | Retrieval mode |
|---|---|---|---|
| **Navigation** | *"Where does this live?"* | atlas → maps → notes, via `genitor:` | browse |
| **Reasoning** | *"What do we believe, and on what evidence?"* | evidence → attractors | association |
| **Reference** | *"What's the fact I already know I need?"* | reference notes | lookup |

Maps without attractors is a taxonomy. Attractors without maps is unbrowsable. **Every graph has both.**

You could never *look up* a principle you don't know applies. That connection has to be **made**, and the
design fixes where it is made: at refinement time, by the session whose job it is to look.

**The index is not the map.** The map is *complete* and answers "show me what's here." The index is
*editorial*, renders attractors only, and exists as the **stimulus** for association. Both are generated;
they are not interchangeable.

## The navigation tier, precisely

One frontmatter field: **`genitor:`**, a single-valued wikilink to the note's navigation parent. The field
name is configurable (`graph.parent-field`) and defaults to `genitor`.

```
atlas (the one note with no genitor)
  └─ maps        (genitor → the atlas, or a parent map)
       └─ notes  (genitor → their type's map)
```

Three properties, each load-bearing.

**1. `genitor` is the navigation parent, deliberately *not* the semantic parent.** An evidence note's
`genitor` is its type's map — **not the source it came from, and not the attractor it supports.** Provenance
lives in `source:`; association lives in the attractor field and in body wikilinks. *`genitor` answers "where
do I file this," never "what is this about."* That is what keeps the navigation tree flat and stable while
the association mesh grows arbitrarily deep. Conflate them and maps become recursive and unbrowsable.

The validator enforces this literally: each type declares the `map:` it is filed under, and **KC005** fires
when a note's `genitor` resolves to anything else. In the orchard, every `observation` has
`genitor: "[[observations]]"` — never `[[Cold air pools at the low end of the slope]]`, the pattern it
supports.

**2. Reachability is two independent local invariants, not a traversal.**

- **Up-link** — every note has a `genitor` that resolves. Missing: **KC003**. Unresolvable: **KC004**. Wrong
  map: **KC005**. The atlas is the sole exception, and it must have *no* `genitor` (**KC006**); two rootless
  notes is also KC006.
- **Down-link** — every note appears as an entry **in its parent map's body**, and every map appears as an
  entry in the atlas. Missing: **KC007**.

**The down-link is the one people forget.** A valid `genitor` alone does not make a note reachable, because a
human navigates by *reading the map's bullet list*, not by querying inbound frontmatter fields. The
redundancy is the point: the up-link is machine-checkable metadata, the down-link is the human-browsable
index. Both are checked, separately, and **KC007 is an error, not a warning** — the severity policy's
"an incomplete index is a warning" governs `index.md` and map *tidiness* (ordering, KC008/KC031), not
reachability, which is half the invariant.

**3. A map entry is the *first* wikilink on a bullet line.** Any further wikilinks on that line are
annotations, not entries. Without this rule an annotated entry — `- [[Note]] (context, see [[Other]])` —
corrupts both completeness and duplicate checking. A duplicated entry is ambiguity, not untidiness: **KC009**,
error.

**Growth rules** — the thresholds are config, the shapes are invariant. Create a map when ≥`new-map-at` notes
cluster with no existing map, and never create an empty one; promote a map heading to a sub-map at
≥`promote-heading-at` entries; adding a top-level map obliges updating the atlas. Entries and headings are
alphabetically ordered, **inserted in position, never appended** (KC008 / KC031, warnings).

**Maps are never created silently.** `knowledge-graph` proposes one *in the plan* when a note's `genitor`
names a map that does not exist and the cluster has reached the threshold; `commons-check` **flags** the need
(**KC030**, warning) and creates nothing.

## Six type roles, not two

| Role | Behavior | Orchard (feeder) | Commons |
|---|---|---|---|
| **Source** | raw, inert, addressable, preserved *exactly* as received; carries the ledger stamp | `logbook` | — |
| **Evidence** | atomic, provenanced; **must point at ≥1 attractor** | `observation` | `claim` |
| **Attractor** | accumulates evidence; has a "so what" | `pattern`, `practice` | `principle`, `question` |
| **Hub** *(optional)* | curated entry point for an entity; **bidirectional obligation with attractors** | `plot` | — |
| **Reference** | lookup-retrieved; unbounded; never indexed | `varietal` | `reference` |
| **Dispatch** | routed *out* to an external sink; **never becomes a note** | — | — |

`atlas` and `map` are declared types too, because **`type:` in frontmatter is authoritative** and a folderless
graph must still be able to identify its own navigation tier. The directory is a *default*, not a rule: a note
sitting outside its declared `dir:` is reported (**KC032**, warning) and never acted on. An undeclared or
missing `type:` is **KC002**.

**The evidence → attractor edge is the reasoning tier's whole point.** Evidence declares its attractors in the
frontmatter field named by `types.evidence.attractor-field` (`supports:` in both fixtures). Fewer than
`min-attractors`: **KC010**. A link that doesn't resolve, or that resolves to something that is not an
attractor: **KC011**. `min-attractors` has a floor of 1 and **a config value below the invariant is a config
error, not an override** (**KC102**) — evidence that points at nothing is a note nobody will ever find again.

**An attractor with no evidence is a topic** (**KC025**, warning), and so is an attractor with no "so what"
(**KC034**, warning, when the type declares a `stake-section:`).

**The attractor's evidence section is a cache; the evidence note's frontmatter is authoritative.** When a type
declares an `evidence-section:`, the validator reconciles the two in both directions and reports any drift as
**KC035** (error): evidence naming an attractor that the section omits means the propagation is half-done;
a section listing a note that does not name the attractor back means the cache is stale. A missing section is
KC035 too — there is nowhere to accumulate.

**The hub role and its bidirectional obligation.** A hub is a curated link-section note — *the most important
things to know about this entity right now.* It is **editorial, not exhaustive**; the *map* is the exhaustive
index, and losing that distinction turns hubs into duplicate maps.

The obligation runs both ways and is checked in both directions:

- every attractor a hub lists in its declared `section:` must name that hub in the attractor's declared
  `field:` (**KC012**), **and**
- every hub an attractor names in that field must link back to the attractor in its section (**KC013**).

In the orchard, the hub `North Plot` lists `- [[Cold air pools at the low end of the slope]]` under
`## patterns`, and that pattern carries `plots: ["[[North Plot]]"]`. Remove either half and the pair fails.
**Renaming or dropping the section fails loudly** (**KC033**) rather than silently disabling the check that
depends on it. Hubs are **optional** — a graph with no entities worth curating declares none and the check
never runs.

**Reference and hub are lookup-only and never promote across a boundary.**

## The invariant, stated once

> Every note is reachable from the atlas: its `genitor` resolves, and its parent map lists it. Evidence must
> point at ≥1 attractor. Attractors accumulate evidence. Hubs and attractors maintain bidirectional link
> obligations. Reference is lookup-only. Dispatch routes out. A health check enforces the structure. A
> changelog records why the graph looks the way it does. Promotion *derives* portable notes upward; it never
> moves them.

## What is deliberately NOT in the invariant

**The lifecycle, graduation, and `domain:` are commons-tier mechanisms — not universal invariants.** Getting
this wrong is the single most consequential error in this design's history, and it is worth stating in the
negative before it is stated in the positive.

**A feeder graph is single-domain by construction.** It holds one project, one body of work, one orchard. Its
attractors accumulate evidence and that is *all* they do. They have no `status:`, they never graduate, and
their notes carry no `domain:`. The reference implementation this design generalizes — the graph that
demonstrably works, at 676 notes — has no `status:` field and no `domain:` field on any note.

The error is not cosmetic. It makes the **≥2-domain graduation bar incoherent in every feeder graph**: in a
single-domain graph "evidence from two domains" can never happen, so the bar either never fires or gets
quietly reinterpreted against whatever field happens to be handy.

The validator makes this mechanical. **The switch is the presence of a `graduation:` block** (`is_commons`).
A feeder declares none, and:

- an attractor type that declares a `lifecycle:` without a `graduation:` block is **KC104** (warning);
- a note carrying `status:` whose type declares no lifecycle is **KC024** (error);
- the graduation checks (**KC021** / **KC022**) do not run at all.

The orchard config says so in one line — `forbidden: [domain, status]` on every content type — and the
validator refuses either field on sight (**KC015**).

## The commons tier: lifecycle, graduation, and `domain:`

The commons is the only graph that federates *across* domains, so it is the only graph where "this has now
appeared in a second domain" is a sentence that can be said at all. Three mechanisms exist there and nowhere
else.

**`domain:`** — carried by a note that arrived **by promotion**, set to the **originating graph's
`graph.name`**. One field, one writer, one meaning. In the commons fixture, one claim carries
`domain: orchard` and another `domain: workshop`; the principle they both support therefore spans two domains.

**A lifecycle** — an ordered list, named by the commons for itself, and **resolved by position, never by
literal name**. A rule that says "flag it `held`" is wrong for a type whose lifecycle has no `held`.

| Position | Meaning | `principle` | `question` |
|---|---|---|---|
| **0 — proposed** | created; has not yet earned its keep | `provisional` | `open` |
| **1 — earned** | evidence from ≥`bar` distinct domains | `held` | `graduated` |
| **2 — retired** | no longer live | `stale` | `abandoned` |

Every attractor type in the commons must declare one (**KC104**, error, if it doesn't), every note of that
type must carry a `status:` drawn from it, and a status outside the list is **KC024**.

**Graduation at ≥2 domains.** An attractor whose evidence spans two distinct originating graphs has earned a
stance; below that bar it hasn't, and questions absorb the singletons. The count is taken **off the evidence
notes' `domain:` fields, never off the bullets in the attractor's evidence section** — the two can drift, and
a stale annotation would otherwise graduate an attractor that has not earned it.

- **KC021** (warning) — at position 0 with evidence from ≥`graduation.bar` domains: has earned position 1.
- **KC022** (warning) — at position 1 on fewer: promoted early.

**`commons-check` flags; it never applies.** Transitions are applied by `/process`, under plan approval.

**A consequence worth stating plainly: the commons has no source tier of its own.** Nothing is processed
directly into it; everything in it arrived by promotion from a feeder. So a project whose chronicles should
feed the commons needs its **own graph** first — that graph processes the chronicles into local evidence and
promotes the portable claims upward. **The commons is the distillate, never the inbox.** Hand-writing into it
reintroduces the exact "remember to write notes" failure that kills every personal knowledge system.

## The validator refuses; a write is a transaction

The obligations above are cross-file, and that is why they cannot be prose. *Does the parent map actually list
this note? Is the bidirectional pair consistent in both directions? Does this wikilink resolve, following
aliases?* None of those is answerable from the file being written.

A markdown skill cannot refuse anything — it can only be *told* to refuse, and an instruction to refuse is
exactly the guardrail that author review never catches failing. So the plugin ships an **executable
validator**, `bin/validate.py`, stdlib only. `knowledge-graph` runs it before every write and aborts on a
non-zero exit; `commons-check` runs the *same* validator over the whole graph. One implementation, two
entrypoints — so the write-time gate and the health check can never disagree about what the rules are.

> ### ⚠️ Status: the validator exists; the gate is not yet wired
>
> **`knowledge-graph` does not currently invoke `bin/validate.py`.** Its `allowed-tools` carries no `Bash`, so
> it physically cannot. The skills in `skills/` are still the superseded v0.3 versions and are rewritten in
> **PR-B**, which is where the transaction (`begin` → edit the whole set → re-validate → **revert on any new
> error**) actually lands.
>
> This paragraph describes the contract the validator is *built to serve*, and it is stated here so PR-B has a
> specification to hit. It is **not** a description of what runs today. Saying otherwise would be precisely the
> defect this plugin exists to catch — a guard that is documented, believed, and never fires — and an
> independent cold read of this branch caught exactly that claim in this exact sentence.

Two facts govern its design, and both matter to callers:

- **Scoping narrows reporting, never analysis.** Every run parses every note under the graph root and builds
  the complete file, alias, link and map indexes, because every invariant that matters is cross-file. What
  `--scope` filters is the *finding list*, via each finding's **fix set** — the files whose content would have
  to change to fix it, which is not the same as the file the problem was discovered in. A note absent from its
  map is a finding about **both** the note and the map, and a transaction that touched only one of them must
  still see it.
- **"New" is defined against a baseline, by fingerprint.** A real graph has pre-existing findings, and a write
  must not be refused for a violation it did not cause. `validate.py baseline` writes the fingerprint set;
  `check --baseline` marks everything absent from it as new and exits `3` if any *new* error appeared.

**A write is a transaction, not a file.** Creating one evidence note also edits its parent map (the
down-link), the attractor's evidence section, and — if a hub is named — the hub's section. Validating one file
cannot see that. So `knowledge-graph`:

1. performs the **whole set** of edits,
2. re-runs the validator scoped to the touched files, against the pre-write baseline,
3. and on any **new** error, **reverts the entire set** and reports the refusal.

**Half a bidirectional pair is not a smaller violation than none; it is a worse one.** The transaction is what
makes "refuses" mean something.

Two rules follow, and they are what make "an unresolved link is an error" tenable at all:

- **Check before creating.** Search first; if a note on the topic exists, **update it**.
- **Stub before linking.** You may not link a note that does not exist; a one-line stub is fine, and stubs
  accumulate content over time. An unresolved body wikilink is **KC017**, an error; an ambiguous one — a
  target that two notes answer to, by title or alias — is **KC019**, also an error, because ambiguity is
  silently-wrong rather than loudly-broken.

**Severity policy:** a dangling reference is an **error**; an incomplete or untidy *index* is a **warning**; a
schema violation is an **error**. `knowledge-graph` refuses a missing required field at write time, and a
health check that merely warns about what the writer refuses would be incoherent. Exit non-zero **iff** an
error.

**Exit codes.** `0` clean · `1` **the validator could not run** — never mistake this for clean · `2` errors ·
`3` new errors against a baseline.

## Discovery is pull; steering-grade principles graduate outward

Cross-domain connections are made **at refinement time**, by the processing session — the one moment that
holds both the new material and the full index at once. That is the ideal condition for association, and it is
the only moment the system is paid to look. Consuming sessions **pull**: they read the index and follow links.
There is no ambient injection into every session; the per-session cost is paid forever and the value event is
rare.

The few principles that ought to change how sessions *behave* are promoted — deliberately, under approval —
into the always-loaded instruction tier (e.g. `~/.claude/rules/`). The graph is the **epistemic** tier where
stances accumulate evidence; the instruction tier is the **behavioral** view of the few that earned it. Rules
are the graduation *target*, not a parallel store. **Read the instruction tier before proposing a promotion**
— a graph built from sessions those rules already steered will keep re-deriving them.

## Graphs federate; the commons is fed, never authored

**A graph in isolation is a dead end.** The commons does not accumulate knowledge because someone sits down to
write it; it accumulates because *every other graph feeds it as a byproduct of work.* Remove the feeding and
the commons starves.

Graphs form a tree of derivation, and each edge is a boundary crossing under the gate below:

```
project graphs        ──┐
(a repo's knowledge     │   promotes-to
 tier; domain-local     ├──────────────▶   the commons
 material lives and     │                  (cross-domain; personal)
 dies here)             │                        │
professional graphs   ──┘                        │  promotes-to
(a body of client work)                          ▼
                                       the instruction tier
                                       (~/.claude/rules/ — behavioral)
```

Every feeder declares **`promotes-to:`** — `{kind: graph|instruction-tier, path: <path>}`, an object and not a
bare path, because the two kinds take different code paths and the config must say which rather than making
the reader infer it (**KC107**). A graph with no `promotes-to:` is a leaf, and that is a deliberate choice,
not a default.

**The commons is special-cased, and saying otherwise on grounds of symmetry does not survive contact with the
filesystem.** The instruction tier is *not a graph*: `~/.claude/rules/` is a flat directory of markdown files
with no atlas, no maps, no types, no evidence→attractor edge, and no `.commons.yml`. Promotion into it means
writing a rule file, not deriving a note, and it runs its own gate — *is this steering-grade; does it change
how a session should behave?* — plus human approval.

**Three promotion paths, and the first is the load-bearing one:**

1. **In-band, at `/process` time.** Every run on a graph with a `promotes-to:` ends by asking *"does any of
   this generalize?"* and proposes derived notes for the target graph **inside the same plan**, so the human
   approves capture and promotion together. This is capture-as-byproduct, and it is the single mechanism that
   separates a living graph from a dead one. **It is not optional and it is not a fast path.** A run that
   writes to the graph and never asks the question is the failure the whole design exists to prevent: the
   source material is refined and the generalization is lost, silently, forever.
2. **The scheduled cross-graph sweep.** A periodic pass that reads a feeder in bulk, proposes what in-band
   missed, and — more valuably — spots patterns invisible note-by-note (*"this has now appeared in a third
   domain"*). The safety net, and not optional either: in-band works best in a bounded domain where the skill
   is always loaded, and a session in some unrelated repo may simply never think to propose a claim. The
   commons therefore keeps a **`feeders:`** registry, so the sweep has something to enumerate; without it the
   safety net is imaginary.
3. **Explicit `/process --promote <graph>`.** The manual escape hatch. It loads **two** configs, and confusing
   them is the first way this goes wrong: the **target's** config governs every write (its type names, its
   directories, its maps, its attractor field — you are writing into *that* graph), and the **source's** is
   read for exactly one value, `graph.name`, which becomes the promoted note's `domain:`.

## Promotion is derivation; the boundary is defense in depth

A domain note **never moves**. Promotion writes a **new, self-contained note** carrying only portable
substance, with provenance as a non-resolving field (`domain: <originating-graph-name>`) — never a path, never
a link. *If a derived note needs its source to make sense, it has not generalized.*

Three layers, **none sufficient alone**:

**1. Mechanical.** No wikilink resolves outside the target graph. Catches structure. It cannot catch a name in
free prose — a denylist would import the very names it protects — so this layer is necessary, not sufficient.

**2. LLM review.** Three questions. **Every answer must be "no."** A single "yes" refuses the promotion.

- Does this name or identify any person, organization, or client?
- Does it disclose any fact specific to one engagement — a figure, a date, a timeline, a contract term?
- **Would it stop being true or useful if every party involved vanished?**

The third is phrased for a "no" on purpose, and the phrasing is load-bearing: a genuinely portable note
*survives* the disappearance of everyone concerned, so it answers **no**. If erasing the parties would gut it,
its substance *is* the engagement. An earlier draft phrased it positively — *"would it remain true and
useful"* — while still requiring three noes, which inverts that limb: read literally, the gate admitted only
non-portable notes and refused every legitimate one.

**Run all three against the `domain:` value as well as the body.** That field carries the originating graph's
name, the promotion mechanism writes it into the target's frontmatter automatically, and nothing else in the
three layers reads it. A graph named for its client would sail through every prose check and stamp that name
into every note it ever promotes. **Name professional graphs for their kind of work, not their party** — and
if a name fails, refuse the promotion and *fix the name*, rather than quietly substituting one while the
graph's own config still carries it.

**3. Human approval.** Every cross-boundary promotion, explicitly, every time. **Non-negotiable.**

Three further rules, all learned from execution:

- **An attractor's evidence list never crosses a boundary.** It holds titles from the source graph, and a
  title can itself be a leak. Rebuild it from what was actually promoted.
- **A promotion may create the attractor it lands on.** Otherwise the first promotion into an empty commons is
  impossible, since evidence cannot cross without an attractor to support.
- **A promoted note is dated by its promotion**, not by the originating note. The source's date is itself an
  engagement fact.
