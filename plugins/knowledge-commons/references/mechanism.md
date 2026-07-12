# The Mechanism

The invariant shared by every knowledge commons instantiation. Types differ per graph; **this does not.**

Read this before writing to or checking a graph. The authoritative design is
`docs/specs/knowledge-commons-plugin.md` (D1, D4); this file is the operational statement of it.

## The invariant, stated once

> Evidence must point at ≥1 attractor. Attractors accumulate evidence and carry a lifecycle
> (`provisional` → `held` → `stale`). Entities and reference are lookup-only. Dispatch classes route to
> external sinks under per-sink approval semantics and are exempt from graph constraints. A health check
> enforces the structure. A changelog records why the graph looks the way it does. An index renders
> attractors for consultation. Promotion *derives* portable notes upward; it never moves them.

## Roles

What generalizes is not a type list but a set of **roles**. Each instantiation declares its own type names
per role in `.commons.yml`. A work graph's `opportunity` and a personal commons' `principle` are both
attractors; forcing them to share a name would make working graphs worse to make the model tidier.

| Role | Behavior | Work-graph example | Personal-commons example |
|---|---|---|---|
| **Source** | raw, inert, arrives on its own, carries the ledger stamp | call transcript | session chronicle / transcript |
| **Intermediate** | bounded-event synthesis; disposable scaffolding | call synthesis | — |
| **Evidence** | atomic, provenanced, **must point at ≥1 attractor** | insight | claim |
| **Attractor** | accumulates evidence; has a "so what"; has a lifecycle | opportunity, decision | principle, question |
| **Entity** | the nouns; lookup-only; **never promotes** | account, person | — |
| **Reference** | lookup-retrieved facts; unbounded; never indexed | integration notes | tool facts |
| **Dispatch** | extracted but routed *out* of the graph to an external sink | task, tracker update | task |

## Lifecycles

Attractor lifecycles are declared per type in config. The common shapes:

- **principle-like:** `provisional` → `held` → `stale`
- **question-like:** `open` → `graduated` | `abandoned`

**Transitions are flagged, never applied silently.** `commons-check` flags them; they are applied during the
next `/process` run under plan approval. The rules:

| Flag | Condition |
|---|---|
| **Graduation** | a `provisional` attractor with evidence from ≥2 distinct `domain:` values → promote to `held` |
| **Demotion** | a `held` attractor whose evidence is all from a single domain → it was promoted early |
| **Staleness** | no new evidence in N months (config `staleness.months`) → flag for review |
| **Orphan** | an attractor with zero evidence |

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

For any promotion out of a professional domain, three layers — **none sufficient alone**:

1. **Mechanical.** No wikilink in the target graph may resolve outside it. Catches structure. (Entity names
   in free prose cannot be mechanically excluded — a denylist would import the very names it protects — so
   this layer is necessary, not sufficient.)
2. **LLM review gate.** Before writing, three questions, **three noes required**:
   - Does this name or identify any person, organization, or client?
   - Does it disclose any fact specific to one engagement?
   - Would it remain true and useful if every party involved vanished?

   Catches prose.
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
