# `.commons.yml` — configuration schema

> **STATUS: DRAFT (O1).** This schema is being finalized against the first two live instantiations — the
> personal commons and the reference work instance — not in the abstract. Fields marked **provisional**
> below are working defaults chosen to unblock Phase 1; expect them to change once real graphs exercise
> them. Do not treat this as a stable public contract until the plugin is registered (Phase 3).

`.commons.yml` lives **at the graph root**. It is the *data-shaped* specialization of the mechanism: type
declarations per role, directory layout, output classes and sinks, boundary posture, thresholds.

*Procedure-shaped* specialization does not live here — it lives in project-local edge skills (how to resolve
a recording URL, how to write to a tracker). This file only ever **names** them; the orchestrator discovers
them at runtime from the live skill list.

## Full example — the personal-commons shape

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
  - { type: session-chronicle, path: docs/chronicle/, resolve-via: null, ledger: source-note }

outputs:
  claim:     { sink: graph }
  principle: { sink: graph }
  task:      { sink: todoist, via: todoist-dispatch, approval: per-item, defaults: { labels: [next] } }

boundary:
  posture: personal            # personal | professional
  promotion-gate: [mechanical, llm-review, human-approval]

staleness:
  months: 6                    # provisional (O3)
```

## `graph` — required

| Field | Required | Notes |
|---|---|---|
| `root` | yes | Absolute or `~`-relative path to the graph root. `index.md`, `changelog.md`, and `.commons.yml` live here. |
| `types.evidence` | yes | Exactly one evidence type. `requires: attractor-link` is the invariant — it is **not optional**; it is declared here so the write-time check knows the type it applies to. |
| `types.attractors` | yes | One or more. Each needs `name`, `dir`, `lifecycle` (ordered list; first value is the default status on creation). |
| `types.reference` | no | Omit if the graph has no reference tier. Reference notes are exempt from the attractor requirement and never indexed. |
| `types.entity` | no | Lookup-only nouns. Never promotes. Omit for a personal commons. |
| `types.intermediate` | no | Disposable synthesis scaffolding. Omit unless sources are large enough to need it. |

## `sources` — required

A list of source tiers. Each artifact in a tier is enumerable, inert, and carries the ledger stamp.

| Field | Required | Notes |
|---|---|---|
| `type` | yes | Free-form label for the tier (`session-chronicle`, `call-transcript`, `document`). |
| `path` | yes | Where artifacts land, relative to the project or absolute. Globbed at inspect time. |
| `resolve-via` | no | Name of a project-local **edge skill** that turns a raw artifact into readable text (resolve a recording URL, format a transcript). `null` when the artifact is already readable markdown. Discovered at runtime; **never a hardcoded catalog**. |
| `ledger` | yes | Where the `processed:` stamp lives. See below. |

### `ledger` — **provisional (O2)**

Two values, and the choice is per source tier:

- **`source-note`** — the stamp is **additive frontmatter on the source artifact itself**. Preferred: the
  source note *is* the ledger, so the queue is enumerable with no side file to fall out of sync.

  ```yaml
  # appended to the chronicle file's frontmatter by /process
  processed:
    date: 2026-07-12
    claim: ran
    principle: ran
    task: errored          # per output class — partial failures resume cleanly
  ```

- **`sidecar`** — a `.commons-ledger.yml` at the graph root, keyed by source identity, for sources that
  **cannot carry frontmatter** (a transcript from an external service, a read-only export). Same shape,
  keyed by path or transcript ID.

Existing chronicle entries carry no `processed:` field today; the stamp is purely additive, and its absence
means "not yet processed." This is the working default — **confirm it against the live personal instance
before treating it as settled.**

## `outputs` — required

A map of **signal class → routing**. The graph is one sink among several; the orchestrator is a router.

| Field | Required | Notes |
|---|---|---|
| `sink` | yes | `graph`, or the name of an external sink (`todoist`, a tracker). |
| `via` | for non-graph sinks | Name of the project-local edge skill that writes to that sink. Discovered at runtime. |
| `approval` | no | Default `plan` (covered by the single plan approval). `per-item` re-confirms each item interactively. `field-level` re-confirms individual fields. **Heterogeneous approval is by design** — a graph write and a tracker mutation do not deserve the same gate. |
| `defaults` | no | Sink-specific defaults folded into every dispatch (project routing, labels). E.g. `{ labels: [next] }` so a Todoist task never lands unlabelled and invisible. |

**Dispatch classes never become graph notes.** A `task` is extracted, routed to its sink, and recorded in the
stamp — it does not get a file in the graph.

## `boundary` — required

| Field | Required | Notes |
|---|---|---|
| `posture` | yes | `personal` or `professional`. A professional graph's promotions out are gated; a personal graph's are the promotion *target*. |
| `promotion-gate` | yes | Ordered list of layers, all three required for professional promotion: `[mechanical, llm-review, human-approval]`. See `mechanism.md`. Do not shorten this list to move faster. |

## `staleness` — optional

| Field | Required | Notes |
|---|---|---|
| `months` | no | N months without new evidence before an attractor is flagged `stale`. **Default 6 — provisional (O3);** pick empirically after ~6 months of real attractors. |
