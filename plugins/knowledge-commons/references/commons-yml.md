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
  name: commons                          # the domain: stamped on notes this graph promotes elsewhere
  types:
    evidence:   { name: claim,     dir: claims/,     requires: attractor-link }
    attractors:
      - { name: principle, dir: principles/, lifecycle: [provisional, held, stale] }
      - { name: question,  dir: questions/,  lifecycle: [open, graduated, abandoned], graduates-to: principle }
    reference:  { name: reference, dir: reference/ }

sources:
  - type: session-chronicle
    domain: devbox                       # the provenance stamped onto every claim from this tier
    path: docs/chronicle/
    glob: "20*.md"                       # tier membership — excludes reflective-practice.md et al.
    resolve-via: null
    ledger: source-note

outputs:
  claim:     { sink: graph }
  principle: { sink: graph }
  reference: { sink: graph }
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
| `name` | no | This graph's name, used as the `domain:` on notes it promotes *into another graph*. Defaults to the root directory's name. A promoting graph should set it deliberately — it becomes provenance in someone else's graph, and a professional graph's name is itself disclosure (see `mechanism.md` § the boundary). |
| `types.evidence` | yes | Exactly one evidence type. `requires: attractor-link` is the invariant — it is **not optional**; it is declared here so the write-time check knows the type it applies to. |
| `types.attractors` | yes | One or more. Each needs `name`, `dir`, and `lifecycle` — an **ordered** list whose positions are `[proposed, earned, retired]` (see `mechanism.md` § Lifecycles). Position 0 is the status on creation. Skills resolve statuses **by position**, so the names are yours to choose. |
| `types.attractors[].graduates-to` | no | Name of another attractor type. When set, reaching **position 1** derives a new attractor of that type rather than merely flipping status — e.g. `question` sets `graduates-to: principle`, because a question answered from two domains has become a stance. Omit it and graduation is a status change only. |
| `types.reference` | no | Omit if the graph has no reference tier. Reference notes are exempt from the attractor requirement and never indexed. |
| `types.entity` | no | Lookup-only nouns. Never promotes. Omit for a personal commons. |
| `types.intermediate` | no | Disposable synthesis scaffolding. Omit unless sources are large enough to need it. |

## `sources` — required

A list of source tiers. Each artifact in a tier is enumerable, inert, and carries the ledger stamp.

| Field | Required | Notes |
|---|---|---|
| `type` | yes | Free-form label for the tier (`session-chronicle`, `call-transcript`, `document`). |
| **`domain`** | **yes** | **The provenance value stamped onto every evidence note derived from this tier.** See below — this is load-bearing. |
| `path` | yes | Where artifacts land, relative to the project or absolute. |
| **`glob`** | **yes** | Which files in `path` are actually of this tier. **Required, with no default** — a permissive default (`*.md`) is what puts non-sources in the queue: `docs/chronicle/` also contains `reflective-practice.md`, which is a practice file, not a session record. Make the author name the shape (`20*.md`) rather than inheriting a glob that matches everything in the directory. |
| `resolve-via` | no | Name of a project-local **edge skill** that turns a raw artifact into readable text (resolve a recording URL, format a transcript). `null` when the artifact is already readable markdown. Discovered at runtime; **never a hardcoded catalog**. |
| `ledger` | yes | Where the `processed:` stamp lives. See below. |

### `domain` — the currency of the whole mechanism

Every evidence note carries `domain:`. It is **not decoration**: it is what attractors count to decide
graduation (evidence from ≥2 distinct domains → `held`), what triggers demotion, and what the index renders
in `[domains]`.

It comes from **the source tier**, declared here. The processor stamps it onto every claim derived from that
tier and confirms it at plan approval. It is never inferred from the artifact's contents, and never a link.

**A note that arrives by promotion has no source tier** — it was derived in another graph and written into
this one. Its `domain:` is **the name of the originating graph**, as declared in that graph's config
(`graph.name`, defaulting to its root directory's name). This is the one case where `domain:` does not come
from `sources[]`, and it has to work: a promoted note is evidence in the receiving graph, and its domain is
what that graph counts toward graduation. A promotion that arrives with no domain cannot be counted, and the
≥2-domain bar silently under-counts.

It remains **provenance, not a link**: the originating graph's *name*, never a path into it.

**A graph with only one source tier has only one domain — so nothing in it can ever graduate.** That is a
coherent configuration (a project knowledge tier is legitimately single-domain), but it means the lifecycle
machinery is inert: every attractor sits at `provisional` forever, flagged `⚠️ single-domain`, and the
demotion counterweight never fires. If you want graduation to *mean* something, the graph needs source tiers
from genuinely different domains. `commons-init` warns when it is about to write a single-tier config.

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

#### A stamp is not "done" — it is "done as of a point in time"

**Sources get appended to.** A chronicle file holds one *day*, not one *session*: a second session that
evening appends a new block to the same file, under the same frontmatter. A stamp that means "this file is
processed" would cause `/process` to skip that file forever, **silently dropping every session appended
after the stamp** — the exact silent evaporation the ledger exists to prevent.

So the stamp records **what was seen**, and inspect re-queues anything that has changed since:

```yaml
processed:
  date: 2026-07-12
  through: "2026-07-12 14:01"   # the last source unit covered — the final session block's heading
  digest: sha256:1a2b3c…        # OR, for sources with no internal unit structure, a content digest
  claim: ran
  principle: ran
  task: errored
```

At inspect time, a source is **re-queued** if it contains any unit after `through:` (or if its digest no
longer matches). It is skipped only when the stamp covers the file *as it currently stands*. Re-queued
sources are processed in `--augment` mode automatically — propose only what is new — rather than requiring
the user to remember the flag.

**Never treat the presence of a stamp as sufficient to skip.** Compare it against the source.

#### The digest must exclude the stamp — or it invalidates itself

With `ledger: source-note`, the stamp is written **into the file it describes**. So a digest taken over the
whole file is guaranteed to be wrong the moment it is stored: writing `processed:` changes the bytes the
digest covers, the next run sees a mismatch, and the source is re-queued — **on every run, forever.**

**The digest covers the source's content with the `processed:` block excluded.** Compute it over the body
plus any frontmatter *other than* `processed:`. Then stamping does not perturb it, and a mismatch means what
it is supposed to mean: the source itself actually changed.

This does not arise for `ledger: sidecar`, where the stamp lives outside the file it hashes — a reason to
prefer the sidecar for sources with no internal unit structure, which are exactly the ones that need a
digest.

**Prefer `through:` to `digest:` whenever the source has units at all.** It is cheaper, it says *what* was
covered rather than merely *that something changed*, and it cannot self-invalidate.

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
