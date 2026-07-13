# Note Formats

The on-disk contract for every file in a knowledge commons graph. `knowledge-graph` writes to it,
`commons-check` validates against it, `process` proposes plans in its terms — and `bin/validate.py` is what
actually enforces it. Where this file and the validator could disagree, the validator wins; every rule below
that is *checked* names the check code that checks it, and every rule that is *convention only* says so.

Notes are markdown files with YAML frontmatter, parsed by a vendored YAML subset (`bin/_miniyaml.py`): block
maps, block sequences, inline flow maps and lists, quoted scalars, comments. **Block scalars (`|`, `>`),
anchors, aliases, merge keys, tags, and duplicate keys are refused with a line number** — a parser that
silently mis-parses would make the validator confidently wrong.

Links are wikilinks (`[[Note title]]`), resolved **by filename or alias, never by path**, case-insensitively,
within the graph root.

**All examples below are drawn from `tests/fixtures/` — a community orchard (a feeder) and the commons it
promotes into. They are fresh-authored, neutral, and they pass the validator.**

## The frontmatter contract

| Field | Who carries it | Meaning |
|---|---|---|
| `type:` | **every note** | **Authoritative.** Names a type declared in `.commons.yml`. The directory is a default, not a rule. Missing or undeclared: **KC002**. Note outside its declared `dir:`: **KC032** (warning — reported, never acted on). |
| `genitor:` | every note **except the atlas** | The navigation parent, as a wikilink. Field name is `graph.parent-field`. Missing: **KC003**. Unresolved: **KC004**. Names anything but the type's declared `map:`: **KC005**. Present on the atlas: **KC006**. |
| `aliases:` | any note | A list of display synonyms. **The validator resolves wikilinks through them.** An alias that collides with another note's title or alias is **KC019** — ambiguity is silently-wrong rather than loudly-broken. |
| `tags:` | any note, by schema | Free-form list. **The discriminator, and it is invariant:** *every level of a tag hierarchy must be independently useful for retrieval. If searching the parent tag alone wouldn't return a useful set, it's a field, not a tag.* That is what keeps a tag namespace from rotting. |
| `source:` | source notes; evidence | The **canonical identity** of the material this came from — a plain string, **not a wikilink**. For a multi-event artifact it is `<artifact-path>#<verbatim-heading>`. |
| `processed:` | the source (ledger) note | The ledger stamp. Shape checked by **KC027**. |
| `<attractor-field>:` | evidence | The attractor(s) this evidence supports. ≥`min-attractors`, each resolving to an attractor. **KC010** / **KC011**. Named by `types.evidence.attractor-field` (`supports:` in both fixtures). |
| `<hub-field>:` | attractors, where hubs exist | The hub(s) this attractor belongs to. Named by `hubs[].field` (`plots:` in the orchard). **KC013**. |
| `status:` | **commons attractors only** | A value drawn from the type's `lifecycle:`, by position. On a type with no lifecycle it is **KC024**, an error — the lifecycle is a commons-tier mechanism. |
| `domain:` | **commons notes only** | The originating graph's `graph.name`, set by promotion. **Never** carried in a feeder graph, where provenance is `source:`. A feeder forbids it and **KC015** refuses it. |

Any other frontmatter field is a schema matter: `schema.<type>.required` (**KC014**),
`schema.<type>.forbidden` (**KC015**), `schema.controlled-values` (**KC016**). **All three are errors** —
`knowledge-graph` refuses a missing required field at write time, and a health check that merely warned about
what the writer refuses would be incoherent.

**Careful with wikilinks in frontmatter.** Every frontmatter field *except* `genitor` is scanned for
wikilinks, and each one found counts as a **lateral** (association) edge. That is deliberate — the reasoning
tier's edges are exactly what the dead vault lacked — but it means a field you did not intend as an
association should not contain `[[…]]`.

## Filenames

- **The filename is the note title, and the title is the link target.**
  `patterns/Cold air pools at the low end of the slope.md` is linked as
  `[[Cold air pools at the low end of the slope]]`.
- **Titles must be filesystem-safe, so write them that way in the first place.** A title cannot contain `/`
  or `:`, cannot begin with `.`, and should stay well under the filesystem's length limit. Do **not** write a
  title and then mangle it into a filename — the filename *is* the link target, so a mangled filename is a
  broken wikilink. Phrase the title so the question never arises, and keep any exact literal in the body,
  where it belongs.
- **Case.** Content notes take the natural title, spaces and all — it is the display name. Maps and the atlas
  take lowercase concept names (`observations.md`, `principium.md`).
- **Date prefixes are per-type, not universal.** A type declares `filename: { date-prefix: true }` only when
  the note *is* a dated event. In the orchard the `logbook` source notes are dated
  (`2026-03-14 Spring walkthrough`) and nothing else is; an attractor never is, because it is long-lived and
  its title is a stable link target. *(Convention. The validator does not check filenames.)*
- **The date is the source's, not the processor's.** `date:` records when the thing happened, not the day
  `/process` got around to reading it. Otherwise working through a two-year backlog in an afternoon would make
  every attractor look freshly exercised. **Exception — a promoted note is dated by its promotion**: it passed
  through no source, and the originating note's date is itself an engagement fact.
- Directories come from `.commons.yml`, not from this file, and they are a default rather than a rule.

## Atlas

The one note with no `genitor`. Every map is entered here. Its filename is `graph.atlas`; it may carry an
`aliases:` list, and links resolve through it.

```markdown
<!-- grove.md  —  graph.atlas: grove.md -->
---
type: atlas
aliases:
  - The Grove
---
# The Grove

The one note with no genitor. Every map is entered here; every note is entered in a map.

## maps
- [[logbook]]
- [[observations]]
- [[patterns]]
- [[plots]]
- [[practices]]
- [[varietals]]
```

A map absent from this list is unreachable by browsing: **KC007**. A second rootless note, or a `genitor:` on
the atlas itself: **KC006**.

## Map

The **complete** index of one type. Category headings sit at `types.map.heading-level` (`2` in both fixtures,
so `##`). **An entry is the *first* wikilink on a bullet line** — any further wikilinks on that line are
annotations, not entries.

```markdown
<!-- maps/observations.md -->
---
type: map
genitor: "[[The Grove]]"
---
# observations

## entries
- [[Blossom damage clusters at the bottom of the slope]]
- [[Mulching before the first hard freeze cut winter loss]]
- [[Row four leafs out ten days before row nine]]
```

- Entries are **alphabetical within their heading**, and headings are alphabetical among themselves —
  **inserted in position, never appended**. **KC008** / **KC031**, warnings; a map may be excused with
  `graph.ordering-exempt`.
- A duplicate entry is ambiguity, not untidiness: **KC009**, error.
- Every note of a type whose `map:` names this file must appear here: **KC007**, error. *A resolving `genitor`
  alone does not make a note reachable* — a human navigates by reading the bullet list.
- The map is **complete**. The index is **editorial**. They are not interchangeable, and a hub is neither.

## Source — e.g. `logbook`

Raw material, preserved exactly as received, and **the ledger**. The source note lives **in the graph, never
in the source repository** — so `/process` leaves no trace in a tree someone is actively working in, and the
stamp can never match the file it describes.

```markdown
<!-- logbook/2026-03-14 Spring walkthrough.md -->
---
type: logbook
genitor: "[[logbook]]"
source: "logbook-source/2026-03-14.md### 09:20 Spring walkthrough"
processed:
  - date: 2026-03-15
    ran: [extract-logbook]
    skipped: []
    errored: []
---
# 2026-03-14 Spring walkthrough

The material, verbatim.
```

**`source:` is the canonical identity of one *event*, not one file.** An artifact holding several events (a
chronicle file is a *day*, holding two or three sessions) declares an `event-delimiter:` in config; `/process`
splits on it, and the identity of each block is `<artifact-path>#<verbatim-heading>`. The heading is copied
**verbatim** — it exists to be *found again*, and a heading you normalized is a heading you cannot match. Two
identical headings in one artifact collide on one identity and the second would be silently treated as already
processed; that silence is why **KC028** (with `--source-scan`) is an error.

**`processed:` is a list, so it keeps a history**, keyed by skill. `/process` reads it to enter augment mode:
do only what is not yet done, and *say* what already exists rather than recreating it. **KC027** checks the
shape — a list, of mappings, each with an ISO `date:` and list-valued `ran:` / `skipped:` / `errored:`.

A source tier that deliberately produces no note has nothing to carry the stamp; it declares `ledger: none`
and is treated as new on every pass. **It must be declared, not discovered** (**KC108**) — otherwise
`/process` searches for a ledger note forever, finds nothing, and silently re-proposes that source on every
run, compounding.

## Evidence — e.g. `observation`, `claim`

Atomic, provenanced, **must point at ≥1 attractor**.

```markdown
<!-- observations/Row four leafs out ten days before row nine.md -->
---
type: observation
genitor: "[[observations]]"       # the MAP — never the pattern it supports
date: 2026-03-14
season: spring                    # a controlled value; KC016 checks it against the set
source: "logbook-source/2026-03-14.md### 09:20 Spring walkthrough"
supports:                         # ≥1 REQUIRED — KC010; each must resolve to an attractor — KC011
  - "[[Cold air pools at the low end of the slope]]"
---
Row four sits at the top of the slope and row nine at the bottom. Bud break in row four ran roughly ten
days ahead of row nine across the whole walkthrough, and the gap widened toward the fence line rather than
tracking sun exposure, which runs the other way.
```

The body is **one self-contained paragraph**. Not a bulleted list, not a section tree — evidence is one thing
someone could stand behind.

In the **commons**, and only there, an evidence note also carries `domain:` — the originating graph's name,
written by the promotion, and the field the graduation bar counts:

```markdown
<!-- claims/Executing a config caught an error five reviews had missed.md -->
---
type: claim
genitor: "[[claims]]"
date: 2026-07-12
domain: orchard                   # REQUIRED here; FORBIDDEN in a feeder graph (KC015)
supports:
  - "[[Execution beats review for validating a guard]]"
---
Five passes of careful reading over a configuration file found nothing. Running it found a malformed entry
on the first attempt, in seconds. The reading was not careless; the artifact simply does not reveal that
class of defect to reading.
```

## Attractor — e.g. `pattern`, `principle`

Accumulates evidence. Has a "so what." **In the commons — and only there — has a lifecycle.**

```markdown
<!-- patterns/Cold air pools at the low end of the slope.md   (a FEEDER attractor) -->
---
type: pattern
genitor: "[[patterns]]"
plots:                            # the hub field — the attractor's half of the bidirectional pair
  - "[[North Plot]]"
---
# Cold air pools at the low end of the slope

## so what
Site frost-tender varietals uphill, and read the contour line rather than the sun map when deciding what to
plant where.

## evidence
- [[Blossom damage clusters at the bottom of the slope]]
- [[Row four leafs out ten days before row nine]]
```

- **`## so what` is one clause of consequence** — what changes because this is true. It is what the index
  renders. An attractor without a "so what" is a topic, not an attractor: **KC034**, warning, when the type
  declares a `stake-section:`.
- **`## evidence` is a cache; the evidence note's frontmatter is authoritative.** The validator reconciles the
  two in **both** directions and reports any drift as **KC035** (error): evidence naming this attractor but
  absent from the section means the propagation is half-done; a bullet here whose note does not name this
  attractor back means the cache is stale. **Do not put a wikilink in an annotation inside this section** —
  every wikilink under the heading is read as a listed entry. Plain-text annotation is fine.
- An attractor nothing points at is a topic: **KC025**, warning.
- **No `status:` in a feeder graph.** **KC024** refuses it, and the orchard's schema forbids it outright.

The commons attractor is the same shape plus the lifecycle:

```markdown
<!-- principles/Execution beats review for validating a guard.md   (a COMMONS attractor) -->
---
type: principle
genitor: "[[principles]]"
status: provisional               # position 0 of lifecycle: [provisional, held, stale]
---
# Execution beats review for validating a guard

## so what
Run the artifact against a deliberately-broken input before trusting any textual audit of it.

## evidence
- [[A dry run surfaced a broken gate that reading it had not]]
- [[Executing a config caught an error five reviews had missed]]
```

Those two claims carry `domain: workshop` and `domain: orchard` — two distinct domains, so this principle has
met the bar and `commons-check` flags **KC021**, `graduation-pending`. **The count is taken off the claims'
`domain:` fields, never off these bullets.** The two can drift, and a stale annotation would otherwise
graduate an attractor that had not earned it.

## Attractor — e.g. `question`

Same role, different section names, and the sections are declared per type (`stake-section:`,
`evidence-section:`), never assumed.

```markdown
<!-- questions/When is a checklist better than automation.md -->
---
type: question
genitor: "[[questions]]"
status: open                      # open | graduated | abandoned  (positions 0 | 1 | 2)
---
# When is a checklist better than automation

## why I care
Automating a step can remove the judgment that made it work, and those failures are quiet.

## partial answers
- [[A dry run surfaced a broken gate that reading it had not]]
```

**`## why I care` is written by the processor** — the stake the source material shows, not a blank left for a
human to fill. It is proposed in the plan like everything else and confirmed at approval. A question with an
empty stake section is a topic, and topics do not accumulate evidence.

A type may declare `graduates-to: <type>`, and then reaching position 1 does **not** merely flip a status — it
**derives a new attractor of the target type**, carrying the stance forward as its "so what," and the question
records what it became (`## became`, a wikilink). Two rules fall out, easy to get wrong in opposite
directions:

- **The graduating note keeps its evidence.** Add to the derived note; do not move. Stripping the question's
  evidence to "move" it would leave an attractor with zero evidence — manufacturing a KC025 orphan on every
  graduation.
- **The derived note is born at position 1.** It inherits the domain count that earned it; creating it at
  position 0 would have the next check immediately flag it for a graduation that just happened.

*(`graduates-to:` is declared in config and applied by `/process` under plan approval. The validator does not
check it.)*

## Hub — e.g. `plot`

**Optional.** A curated entry point for an entity: *the most important things to know about this right now.*
**Editorial, not exhaustive** — the *map* is the exhaustive index, and losing that distinction turns hubs into
duplicate maps.

```markdown
<!-- plots/North Plot.md -->
---
type: plot
genitor: "[[plots]]"
aliases:
  - Lower Orchard
---
# North Plot

The oldest planting, running downhill from the gate to the fence line.

## patterns
- [[Cold air pools at the low end of the slope]]
```

The section name is `hubs[].section` and the attractor's answering field is `hubs[].field` — **both are
declared, never guessed by pluralizing the hub's type name.** The obligation is bidirectional and checked in
both directions: the hub lists the attractor here (**KC012**) *and* the attractor names the hub in `plots:`
(**KC013**). **Half a pair is not a smaller violation than none; it is a worse one.** Renaming or dropping the
section is **KC033**, an error — it must fail loudly rather than silently disabling the check that depends on
it.

## Reference — e.g. `varietal`

Lookup-retrieved facts. **Unbounded, never indexed, exempt from the attractor requirement, and exempt from the
orphan check** — that is exactly what lets them grow without bound.

```markdown
<!-- varietals/Bramley cooking apple.md -->
---
type: varietal
genitor: "[[varietals]]"
verified: 2026-03-14
---
# Bramley cooking apple

Triploid, so it will not pollinate its neighbours and needs two other varietals nearby to set fruit itself.
Lookup-only: this is a fact to retrieve, not a claim to accumulate.
```

No attractor field, no lifecycle. `verified:` is a schema field, not a mechanism: a fact you cannot trace to
when you last checked it is a fact you cannot re-verify when it goes stale — and tool facts go stale
constantly.

**Reference and hub notes never promote across a boundary.**

## `index.md` — graph root

**Generated by `commons-check --index` (i.e. `validate.py index --write`). Committed. Never hand-edited.**
It is excluded from the graph walk, so it carries no frontmatter and is never itself validated.

One line per attractor: **bold title** — the "so what" in one clause — `[domains]`. Evidence and reference
**never appear**. The "so what" is the first prose line under the type's `stake-section:`; the domains are
read off the supporting evidence notes' `domain:` fields, so in a feeder graph — which has none — the bracket
is simply absent.

```markdown
# Index

_Generated by `commons-check --index`. Do not hand-edit._

## principles
- **Execution beats review for validating a guard** — Run the artifact against a deliberately-broken input before trusting any textual audit of it. `[orchard, workshop]` ⚠️ graduation-pending

## questions
- **When is a checklist better than automation** — Automating a step can remove the judgment that made it work, and those failures are quiet. `[workshop]`
```

*When is a checklist better than automation* carries **no flag**: it is at position 0 on one domain, which is
simply unearned, not defective — the normal, healthy state of most attractors. *Execution beats review* has
met the ≥2-domain bar and awaits the next `/process` run to apply the transition; `graduation-pending` exists
because that state is real and lasts a whole cycle.

**The flag vocabulary is closed.** A generated file whose vocabulary each run improvises is not a stable
artifact, so do not invent new ones. The flags are rendered by the validator itself, from its own findings —
which is precisely why the index lives inside the validator: the flags and the checks must not be able to
disagree.

| Flag | Check | Meaning |
|---|---|---|
| `⚠️ graduation-pending` | KC021 | at **position 0** with evidence from ≥`bar` domains — has earned promotion, not yet applied |
| `⚠️ single-domain` | KC022 | at **position 1** on evidence from fewer — was promoted early; flagged for demotion |
| `⚠️ stale` | KC023 | no new evidence in `graduation.staleness-months` months |
| `⚠️ orphan` | KC025 | an attractor with zero evidence |

Note `⚠️ single-domain` is a **position 1** condition. A position-0 attractor with single-domain evidence is
not flagged at all.

Two honest notes about the current validator, so nobody reads a passing run as more than it is: **KC023 is in
the flag vocabulary and KC023 emits it** — staleness is implemented, measured against an injectable `--today`, and
`graduation.staleness-months` is read by nothing. And **KC020**, the *lateral*-orphan warning (a note with no
inbound association from any other note's body or frontmatter — the dead-vault detector), is a distinct
finding from KC025 and is **not** rendered in the index.

Index size is a smoke alarm, not a wall: growth is controlled epistemically (graduation requires ≥2 domains),
not budgetarily.

## `changelog.md` — graph root

One dated bullet per **graph-shaping event**: what changed and why. Not a commit log — a record of why the
graph looks the way it does. Appended by `knowledge-graph`. Excluded from the graph walk, so no frontmatter.

```markdown
# Changelog

## 2026-07
- **2026-07-12** — Promoted *Execution beats review for validating a guard* toward `held`: a second domain
  (orchard) produced supporting evidence, meeting the ≥2-domain graduation bar.
- **2026-07-08** — Opened *When is a checklist better than automation* after two claims pulled in opposite
  directions on the same question.
```

The current month lives in `changelog.md`. At month rollover the prior month is archived to
`changelog/YYYY-MM.md` and `changelog.md` starts fresh. Both `changelog.md` and everything under `changelog/`
are excluded from validation.
