# The Mechanism

The invariant shared by every knowledge commons instantiation. Types differ per graph; **this does not.**

Read this before writing to or checking a graph. The authoritative design is
`docs/specs/knowledge-commons-plugin.md` (D1, D4); this file is the operational statement of it.

## The invariant, stated once

> Evidence must point at ≥1 attractor. Attractors accumulate evidence and carry a lifecycle whose statuses
> each graph names for itself: **proposed → earned → retired**. Reference is lookup-only. Dispatch classes
> route to external sinks under per-sink approval semantics and are exempt from graph constraints. A health
> check enforces the structure. A changelog records why the graph looks the way it does. An index renders
> attractors for consultation. Promotion *derives* portable notes upward; it never moves them.

Note what that sentence does **not** say: it does not name the statuses. `provisional`/`held`/`stale` are one
graph's names for the three positions; a `question` calls them `open`/`graduated`/`abandoned`. Everything
below is stated **by position**, and so is every rule in every skill. See § Lifecycles.

## Roles

What generalizes is not a type list but a set of **roles**. Each instantiation declares its own type names
per role in `.commons.yml`. A work graph's `opportunity` and a personal commons' `principle` are both
attractors; forcing them to share a name would make working graphs worse to make the model tidier.

| Role | Behavior | Work-graph example | Personal-commons example |
|---|---|---|---|
| **Source** | raw, inert, arrives on its own, carries the ledger stamp | call transcript | session chronicle / transcript |
| **Intermediate** † | bounded-event synthesis; disposable scaffolding | call synthesis | — |
| **Evidence** | atomic, provenanced, **must point at ≥1 attractor** | insight | claim |
| **Attractor** | accumulates evidence; has a "so what"; has a lifecycle | opportunity, decision | principle, question |
| **Entity** † | the nouns; lookup-only; **never promotes** | account, person | — |
| **Reference** | lookup-retrieved facts; unbounded; never indexed | integration notes | tool facts |
| **Dispatch** | extracted but routed *out* of the graph to an external sink | task, tracker update | task |

† **`Intermediate` and `Entity` are defined but not yet wired.** Both are retained here because the reference
work instance uses them — an intermediate call synthesis between transcript and insights; entities for
accounts and people — and Phase 2 will need them. Neither is available machinery yet:

- **`Intermediate`** — no skill produces or consumes one. `/process` handles long sources by fanning out
  subagents by signal class instead.
- **`Entity`** — `note-formats.md` defines no on-disk format for one, and `knowledge-graph` (the only skill
  that writes notes) has no path to write one. **`commons-init` must not offer it** until both exist.

Do not treat either as available. A type a graph can declare but no skill can write is a trap: the config
accepts it, and the first `/process` run that tries to produce one has nothing to follow.

## Lifecycles

**This section is the single definition of the lifecycle rules.** `commons-check` applies them and
`/process` executes the flags; neither restates them. Change them here.

Attractor lifecycles are declared **per type** in config, as an ordered list. Every type's list is a
different name for the same three positions — so **the rules below are stated by position, never by literal
status name.** A rule that says "flag it `held`" is wrong: a `question` has no `held`.

| Position | Meaning | `principle` | `question` |
|---|---|---|---|
| **0 — proposed** | created; has not yet earned its keep | `provisional` | `open` |
| **1 — earned** | evidence from ≥2 distinct domains | `held` | `graduated` |
| **2 — retired** | no longer live | `stale` | `abandoned` |

Read the target status out of the type's own `lifecycle:` list at position 0/1/2. A type may declare a
2-position lifecycle (no retired state); then staleness has nowhere to go and is reported without a
transition.

**Transitions are flagged, never applied silently.** `commons-check` flags them; they are applied during the
next `/process` run under plan approval. The rules:

| Flag | Condition | Transition |
|---|---|---|
| **Graduation** | an attractor at **position 0** with evidence from ≥2 distinct `domain:` values | → **position 1** |
| **Demotion** | an attractor at **position 1** whose evidence is all from a single domain — it was promoted early | → **position 0** |
| **Staleness** | no new evidence in N months (config `staleness.months`) | → **position 2** |
| **Orphan** | an attractor **at position 0** with zero evidence | none — report only |

The orphan check applies **only at position 0**. An attractor that has been graduated or retired is not an
orphan — it is finished, and its evidence may legitimately have moved on. Checking it would flag every
graduated note forever.

### Graduation may derive a new attractor

Some attractor types graduate *into another type* rather than merely changing status. A `question` that has
accumulated answers from two domains has stopped being a question — it has become a stance, and the stance
belongs in a `principle`.

A type declares this with `graduates-to: <type>` in config. When it is set, reaching **position 1** means
two things happen together, both under the same plan approval:

1. A **new attractor of the target type is derived** from the graduating one — carrying its substance
   forward as a `## so what`. The graduating note's evidence is **added to** the new note, preserving each
   `(domain)` annotation.
2. The original moves to **position 1** and records what it became (a `## became` wikilink).

Without `graduates-to:`, position 1 is a status change and nothing more. **If a type declares
`graduates-to:` and only the status flips, the accumulated reasoning is stranded in a note now marked
resolved** — which is the failure this field exists to prevent.

Two rules that fall out of this, and that are easy to get wrong in opposite directions:

- **The graduating note keeps its evidence.** Its claims now support *both* it and the derived note. A
  question is the record of what was asked and how it came to be answered; stripping its evidence to "move"
  it to the principle would leave an attractor with zero evidence — which the orphan check would then flag,
  **manufacturing an orphan on every single graduation.** Add; do not move.
- **The derived note is born at position 1, not position 0.** It inherits the domain count that earned it —
  that is the entire premise of graduating it. Creating it at position 0 would have the next health check
  immediately flag it for graduation: a redundant transition on a note that graduation just produced.

## Retrieval model

Two modes, two tiers — this is *why* the structure above exists:

- **Reference** is retrieved by **lookup** — you already know what you want. It can grow without bound
  precisely because it never enters the index.
- **Reasoning** (evidence → attractors) is retrieved by **association** — at `/process` time, when new
  claims meet the full distilled corpus, and on demand when a session pulls the index for a judgment-heavy
  task.

You could never *look up* a principle you don't know applies. That connection has to be **made**, and the
design fixes where: in the refinement loop, by the session whose job it is to look.

## The boundary — defense in depth

A domain note **never moves** to a more general graph. Promotion writes a **new, self-contained note**
carrying only the portable substance, with provenance as a non-resolving field (`domain: <name>`) — never a
path, never a link. *If a derived note needs its source to make sense, it has not generalized.*

**The promoted note's `domain:` is the originating graph's name** (`graph.name` in its config) — not a source
tier of the receiving graph, because it never passed through one. This is load-bearing: a promoted note is
evidence in the graph it lands in, and its domain is what that graph counts toward the ≥2-domain bar. A
promotion arriving with no domain silently under-counts.

Note the consequence for a professional graph: **its name travels with every note it promotes.** A graph
named for a client or an employer discloses that by existing in someone else's `domain:` field. Name
professional graphs for their *kind of work*, not their party.

For any promotion out of a professional domain, three layers — **none sufficient alone**:

1. **Mechanical.** No wikilink in the target graph may resolve outside it. Catches structure. (Entity names
   in free prose cannot be mechanically excluded — a denylist would import the very names it protects — so
   this layer is necessary, not sufficient.)
2. **LLM review gate.** Before writing, three questions. **Every answer must be "no."** Any single "yes"
   refuses the promotion.
   - Does this name or identify any person, organization, or client?
   - Does it disclose any fact specific to one engagement — a figure, a date, a timeline, a contract term,
     a headcount?
   - **Would it stop being true or useful if every party involved vanished?** (Phrased for a "no": a
     genuinely portable note survives the disappearance of everyone concerned. If erasing the parties would
     gut it, its substance *is* the engagement.)

   Catches prose.

   **Run all three against the `domain:` value too, not only the body.** The promoted note's `domain:` is the
   originating graph's `graph.name`, and the promotion mechanism writes it into the target's frontmatter
   automatically. A graph named for its client would sail through every prose check and stamp that client's
   name into every note it ever promotes — the one field none of the three layers would otherwise read. If
   the name fails, **refuse the promotion and fix the name**; do not quietly substitute a different one, which
   would leave the graph's own config still carrying it.
3. **Human approval.** Every cross-boundary promotion is approved explicitly. **Non-negotiable.**

## Steering-grade principles graduate outward

The few principles that ought to change how sessions *behave* are promoted — deliberately, at `/process`
time, under approval — into whatever always-loaded instruction tier the user already operates (e.g.
`~/.claude/rules/`).

The graph is the **epistemic** tier, where stances accumulate evidence. The instruction tier is the
**behavioral** view of the few that earned it. Rules are the graduation *target*, not a parallel store —
which is what keeps the two tiers from drifting apart.

## Discovery is pull, not push

Cross-domain connections are made **at refinement time**, by the processing session — which holds both the
new material and the full index in context simultaneously. That is the ideal condition for association:
distilled claim against distilled corpus.

Consuming sessions **pull** (read the index, follow links). There is no ambient injection into every
session: the per-session cost is paid forever and the value event is rare.
