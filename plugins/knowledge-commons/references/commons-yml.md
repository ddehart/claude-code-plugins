# `.commons.yml`

The **data-shaped** half of a graph: type names, directories, controlled vocabularies, required and forbidden
fields, growth thresholds, source tiers, sink routing, the boundary posture. It lives at the graph root, and
`bin/validate.py` reads it before it reads a single note.

What it deliberately **cannot** hold is the *procedure-shaped* half — how this domain turns its sources into
its notes, the promote-vs-skip bar and its error asymmetry, the debiasing rules, the propagation
choreography. Those are prose, they live in the project's generated extraction skill, and no YAML key can hold
them. A generic engine reading a config file could never reproduce the system this design generalizes.

**This file documents what the validator actually reads.** Keys it does not read (and the skills do) are
marked as such, so nobody mistakes a passing `validate.py schema` run for more than it is.

Parsed by the vendored YAML subset (`bin/_miniyaml.py`): block maps, block sequences, inline flow maps and
lists, quoted scalars, comments. **Block scalars, anchors, aliases, merge keys, tags and duplicate keys are
errors with a line number.** A duplicate key in particular — which PyYAML silently resolves last-wins — is
refused, because a silently discarded key is a dead config entry, and a dead config entry is indistinguishable
from a passing check.

Two shapes exist: a **feeder** and the **commons**. **The switch is the presence of a `graduation:` block.**
That single fact decides whether the lifecycle, graduation and `domain:` mechanisms exist in this graph at
all.

---

## A FEEDER graph

Single-domain by construction: one project, one body of work. Its attractors accumulate evidence and that is
all they do. **It declares no lifecycle, nothing graduates in it, and its notes carry no `domain:`.**

This is `tests/fixtures/orchard/.commons.yml` — a community orchard. It is real, and it passes.

```yaml
graph:
  root: .
  name: orchard                 # becomes `domain:` on notes this graph promotes UPWARD.
                                # Notes in THIS graph carry no `domain:`.
  atlas: grove.md               # the one note with no genitor
  maps-dir: maps/
  parent-field: genitor
  growth: { new-map-at: 5, promote-heading-at: 7, split-note-at-lines: 200 }
  promotes-to: { kind: graph, path: ../commons }   # a leaf omits it
  expected-orphans: []

types:
  # `type:` in frontmatter is AUTHORITATIVE. The directory is a default, not a rule —
  # a folderless graph still validates. That is why `map` and `atlas` are declared types:
  # in a folderless graph, nothing else identifies the navigation tier.
  # Every content type declares the `map:` it is entered in — the down-link's target.
  atlas:     { name: atlas, map: null }
  map:       { name: map, heading-level: 2 }
  source:    { name: logbook, dir: logbook/, map: logbook, preserve-verbatim: true }
  evidence:  { name: observation, dir: observations/, map: observations,
               attractor-field: supports, min-attractors: 1 }
  attractors:
    # NO lifecycle. Single-domain; nothing graduates.
    - { name: pattern, dir: patterns/, map: patterns,
        stake-section: "## so what", evidence-section: "## evidence" }
    - { name: practice, dir: practices/, map: practices,
        stake-section: "## so what", evidence-section: "## evidence" }
  hubs:                         # optional
    # `field:` is the frontmatter key ON THE ATTRACTOR that names this hub.
    - { name: plot, dir: plots/, map: plots, bidir-with: pattern,
        section: "## patterns", field: plots }
  reference: { name: varietal, dir: varietals/, map: varietals }

schema:
  atlas:    { required: [type] }
  map:      { required: [type] }
  logbook:  { required: [type, genitor, source] }
  observation:
    required:  [type, genitor, date, source, supports]
    forbidden: [domain, status]     # both are commons-tier mechanisms
  pattern:  { required: [type, genitor], forbidden: [domain, status] }
  practice: { required: [type, genitor], forbidden: [domain, status] }
  plot:     { required: [type, genitor], forbidden: [plots, date] }
  varietal: { required: [type, genitor, verified] }
  controlled-values:
    season: [spring, summer, autumn, winter]

sources:
  - type: orchard-logbook
    path: logbook-source/          # ENUMERATED: /process with no argument globs here
    glob: "20*.md"                 # required with `path:` — a permissive default queues non-sources
    event-delimiter: "^## \\d{2}:\\d{2}"   # one FILE is a day; one EVENT is a session
    extract-via: extract-logbook   # the hook the whole generator exists for
    ledger: source-note            # declared, never discovered

outputs:
  observation: { sink: graph }

boundary:
  posture: personal               # personal | professional
  promotion-gate: [mechanical, llm-review, human-approval]
```

---

## The COMMONS

Genuinely different, and the differences are the ones that matter. This is
`tests/fixtures/commons/.commons.yml`. It also passes.

```yaml
graph:
  root: .
  name: commons
  atlas: principium.md
  maps-dir: maps/
  parent-field: genitor
  # The instruction tier is NOT a graph, and `kind:` says so explicitly rather than making
  # /process infer it from the path. Promotion into it writes a rule file, not a note.
  promotes-to: { kind: instruction-tier, path: ~/.claude/rules/ }

types:
  atlas:    { name: atlas }
  map:      { name: map, heading-level: 2 }
  evidence: { name: claim, dir: claims/, map: claims,
              attractor-field: supports, min-attractors: 1 }
  attractors:
    # ONLY the commons has these.
    - { name: principle, dir: principles/, map: principles,
        lifecycle: [provisional, held, stale],
        stake-section: "## so what", evidence-section: "## evidence" }
    - { name: question, dir: questions/, map: questions,
        lifecycle: [open, graduated, abandoned], graduates-to: principle,
        stake-section: "## why I care", evidence-section: "## partial answers" }
  reference: { name: reference, dir: reference/, map: reference }

schema:
  atlas:     { required: [type] }
  map:       { required: [type] }
  claim:     { required: [type, genitor, date, domain, supports] }   # `domain:` here, and nowhere else
  principle: { required: [type, genitor, status] }
  question:  { required: [type, genitor, status] }
  reference: { required: [type, genitor] }

# NO `sources:` block. Nothing is processed into the commons; everything arrives by
# promotion from a feeder. The commons is the distillate, never the inbox.

graduation:
  bar: 2                          # distinct `domain:` values, i.e. distinct feeder graphs
  staleness-months: 6

feeders:                          # the registry; commons-init appends on each wiring
  - { name: orchard,  root: ../orchard,  posture: personal }
  - { name: workshop, root: ../workshop, posture: personal }

boundary:
  posture: personal
  promotion-gate: [mechanical, llm-review, human-approval]
```

**What differs, precisely:**

| | Feeder | Commons |
|---|---|---|
| `graduation:` | absent | **present — this is the switch** |
| `lifecycle:` on attractors | pointless (KC104 warns) | **required** (KC104 errors without it) |
| `status:` on notes | refused (KC024) | required, drawn from the lifecycle by position |
| `domain:` on notes | forbidden by schema (KC015) | required on evidence |
| `sources:` | present — this is where material enters | **absent** — nothing is processed in |
| `feeders:` | absent | present — the sweep's registry |
| `promotes-to.kind` | `graph` | `instruction-tier` |

---

## Key reference

### `graph:`

The **only** keys permitted here. Anything else is **KC109** — the typo detector, and the reason a dead config
key surfaces instead of silently never firing.

| Key | Read by the validator | Meaning |
|---|---|---|
| `root` | no | The graph root. The validator takes it from `--graph`. |
| `name` | no | This graph's name. Becomes `domain:` on every note it promotes upward — so **name a professional graph for its kind of work, not its party.** |
| `atlas` | **yes** | Filename of the one note with no `genitor`. **Required** (KC103); if it does not exist, KC006. |
| `maps-dir` | no | Where maps live. A convention for the skills; the validator identifies maps by `type:`. |
| `parent-field` | **yes** | The up-link field. Defaults to `genitor`. |
| `growth.new-map-at` | **yes** | KC030 fires when this many notes name a map that does not exist. |
| `growth.promote-heading-at` | no | Threshold for splitting a map heading into a sub-map. Applied by `knowledge-graph`. |
| `growth.split-note-at-lines` | no | **Lines.** The name says so on purpose. Applied by the skills. |
| `promotes-to` | **yes (shape)** | `{kind: graph\|instruction-tier, path: <path>}` — an **object**, never a bare path, because the two kinds take different code paths (KC107). Omit it and the graph is a leaf, deliberately. |
| `ordering-exempt` | **yes** | Map titles excused from the alphabetical-ordering warnings (KC008 / KC031). |
| `expected-orphans` | **yes** | Note titles excused from the lateral-orphan warning (KC020). |

### `types:`

Five single roles (`atlas`, `map`, `source`, `evidence`, `reference`) and two list roles (`attractors`,
`hubs`). **Every check loops over this table, built from the config** — there is no hardcoded lookup table a
declared type can be missing from, and therefore no declared type can silently escape validation.

| Key | Where | Read | Meaning |
|---|---|---|---|
| `name` | every type | **yes** | The value that appears in a note's `type:`. Authoritative. |
| `dir` | every type but `atlas`/`map` | **yes** | A **default**, not a rule. A note elsewhere is KC032, a *warning* — reported, never acted on. |
| `map` | **every content type** | **yes** | The map this type is entered in: the down-link's target, and the only note `genitor` may resolve to (KC005). **Required**, or the reachability invariant quietly becomes a no-op (KC103). `atlas` and `map` are exempt. |
| `heading-level` | `map` | **yes** | Depth of the category headings *inside* a map. `2` in both fixtures, so `##`. |
| `preserve-verbatim` | `source` | no | The material is kept exactly as received. Honoured by the skills. |
| `attractor-field` | `evidence` | **yes** | The frontmatter field naming the attractors this evidence supports. **Required** (KC102). |
| `min-attractors` | `evidence` | **yes** | Floor of **1**. **A config value below the invariant is a config error, not an override** (KC102). |
| `stake-section` | attractors | **yes** | The "so what" heading, e.g. `"## so what"`. Absent from a note: KC034 (warning). Also the source of the index's one-clause summary. |
| `evidence-section` | attractors | **yes** | The heading whose bullets cache the supporting evidence. Absent, or drifted from the evidence notes' frontmatter in either direction: KC035 (**error**). |
| `lifecycle` | attractors | **yes** | Ordered list, resolved **by position**. **Commons only** — KC104 warns on a feeder, and errors if the commons omits it. |
| `graduates-to` | attractors | no | Reaching position 1 derives a new attractor of the named type rather than merely flipping a status. Applied by `/process`. |
| `bidir-with` | hubs | **yes** | The attractor type this hub is bound to. Present ⇒ `section:` and `field:` are required (KC105). |
| `section` | hubs | **yes** | The hub's half of the bidirectional pair — the heading whose links must be answered. Absent from a note: KC033 (**error**), never a silent skip. |
| `field` | hubs | **yes** | The attractor's half — the frontmatter key **on the attractor** that names this hub. **Declared, never guessed by pluralizing the hub's type name**, which breaks on the first type that doesn't pluralize. |

### `schema:`

Keyed by **type name**. A key that names no declared type is **KC110**, an error — that block would never
fire, and a dead config key is indistinguishable from a passing check. A declared type with no `schema:` entry
is KC110, a warning: nothing is required of it.

| Key | Read | Meaning |
|---|---|---|
| `<type>.required` | **yes** | Fields that must be present and non-empty. **KC014, an error.** |
| `<type>.forbidden` | **yes** | Fields that must be absent. **KC015, an error.** This is how a feeder forbids `domain:` and `status:`, and how a hub is stopped from referencing itself. |
| `<type>.filename` | no | `{case: natural\|lower, date-prefix: true\|false}`. **Per-type — the date prefix is never universal.** A convention; the validator does not check filenames. |
| `controlled-values.<field>` | **yes** | The allowed set for a field, **checked on every note carrying that field**, whatever its type. **KC016, an error.** |

Required and forbidden are **errors, not warnings** — deliberately, and this diverges from the reference
implementation, which warns. `knowledge-graph` *refuses* a missing required field at write time; a health
check that merely warned about what the writer refuses would be incoherent.

### `sources:`

A list of tiers. **Absent from the commons entirely.** A tier may be handed an input, enumerate a queue, or
both.

| Key | Read | Meaning |
|---|---|---|
| `type` | **yes** (as a label) | The tier's name. |
| `path` | **yes** | Enumerated mode: `/process` with no argument globs here. **The trigger is a thing existing, not a person remembering.** |
| `glob` | **yes** | **Required whenever `path:` is set** (KC106) — a permissive default queues non-sources. |
| `event-delimiter` | **yes** (`--source-scan`) | A heading regex. One artifact may hold several events; the identity of each is `<artifact-path>#<verbatim-heading>`. Two identical headings in one artifact collide on one identity, and the second would be silently treated as already processed — **KC028, an error**, precisely because it is silent. An uncompilable regex is KC028 too. |
| `resolve-via` | no | Skill that turns this source's identifier into text (a URL → a transcript). |
| `extract-via` | no | The domain's extraction skill. **The hook the generator exists for.** |
| `inspect-classes` | no | Signal classes `/process` fans one subagent out per, above ~1,500 words. |
| `ledger` | **yes** | `source-note` — a note **in the graph** carries the `source:` identity and the `processed:` stamp — or `none`, for a tier that deliberately produces no note and is therefore treated as new on every pass. **Required: it must be declared, not discovered** (KC108). A tier that produces no note and does not say so would have `/process` search for a ledger note forever, find nothing, and silently re-propose that source on every run, compounding. |

### `outputs:`, `boundary:`, `feeders:`, `graduation:`

| Key | Read | Meaning |
|---|---|---|
| `outputs.<class>` | no | Sink routing: `{sink, via, approval, after, defaults}`. Consumed by `/process`. **Approval is heterogeneous, and fine-grained subsumes coarse-grained** — a per-item task gate needs no separate batch gate. Never stack both. |
| `boundary.posture` | no | `personal` \| `professional`. |
| `boundary.promotion-gate` | no | The three layers, in order. **Human approval is non-negotiable.** |
| `feeders[]` | no | The commons' registry of the graphs that feed it. Without it, the scheduled cross-graph sweep has no input and the safety net is imaginary. |
| `graduation` | **yes (presence)** | **The presence of this block is what makes a graph the commons.** |
| `graduation.bar` | **yes** | Distinct `domain:` values required to earn position 1. Default 2. Counted **off the evidence notes' `domain:` fields, never off the bullets in an attractor's evidence section** — the two can drift, and a stale annotation would graduate an attractor that had not earned it. |
| `graduation.staleness-months` | **yes** | Months without new evidence before an attractor is flagged stale (KC023). Measured against `--today`, which is injectable and is **recorded in the baseline** — a time-dependent check that is not pinned to the same instant on both sides of a diff invents findings marked NEW that no edit caused. |

Anything else at the top level is **KC109**, a warning. The known set is exactly: `graph`, `types`, `schema`,
`sources`, `outputs`, `boundary`, `graduation`, `feeders`.

---

## The checks

```
validate.py check --graph ROOT [--scope REL ...] [--baseline FILE] [--format json] [--source-scan]
```

**Config checks run first, and an error among them stops the graph checks** — a wrong config makes every graph
finding meaningless.

**Exit codes:** `0` clean · `1` **the validator could not run — never mistake this for clean** · `2` errors ·
`3` new errors against a `--baseline`.

`--scope` narrows **reporting, never analysis**: every run parses the whole graph, because every invariant
that matters is cross-file. It filters findings by their **fix set** — the files whose content would have to
change to fix the finding, which is not the same as the file the problem was discovered in. A note absent from
its map is a finding about *both* the note and the map, and a transaction that touched only one of them must
still see it.

### Graph checks

| Code | Checks | Severity | Config it reads |
|---|---|---|---|
| **KC001** | Frontmatter is present and parses | error | — |
| **KC002** | `type:` is present and declared | error | `types.*` |
| **KC003** | The up-link field is present | error | `graph.parent-field` |
| **KC004** | The up-link resolves | error | `graph.parent-field` |
| **KC005** | The up-link names the type's declared map — *`genitor` answers "where do I file this," never "what is this about"* | error | `types.<t>.map` |
| **KC006** | Exactly one root; it is the atlas; it has no up-link; it exists | error | `graph.atlas`, `types.atlas.name` |
| **KC007** | **The down-link.** Every note is an entry in its parent map; every map is an entry in the atlas | **error** | `types.<t>.map`, `graph.atlas` |
| **KC008** | Map entries are alphabetical within their heading | warning | `graph.ordering-exempt` |
| **KC009** | No duplicate entry in a map — ambiguity, not untidiness | error | — |
| **KC010** | Evidence names ≥ `min-attractors` attractors | error | `types.evidence.attractor-field`, `.min-attractors` |
| **KC011** | Each attractor link resolves, and resolves *to an attractor* | error | `types.attractors[].name` |
| **KC012** | **Hub → attractor.** Every attractor a hub lists names that hub back | error | `types.hubs[].section`, `.field`, `.bidir-with` |
| **KC013** | **Attractor → hub.** Every hub an attractor names links back to it | error | same |
| **KC014** | Required fields present | error | `schema.<t>.required` |
| **KC015** | Forbidden fields absent | error | `schema.<t>.forbidden` |
| **KC016** | Controlled values drawn from their set, on **every** note carrying the field | error | `schema.controlled-values` |
| **KC017** | Body wikilinks resolve (**alias-aware**) — *stub before linking* | error | note `aliases:` |
| **KC018** | **No wikilink reaches outside the graph.** The boundary's first layer, and the only one that does not depend on an LLM reading prose. Promotion *derives* a self-contained note; it never links across | error | — |
| **KC019** | No ambiguous target: no title or alias resolves to two notes | error | note `aliases:` |
| **KC020** | **Lateral** orphan — no inbound association from another note's body or frontmatter. The dead-vault detector | warning | `graph.expected-orphans` |
| **KC021** | **Commons only.** At position 0 with evidence from ≥ `bar` domains: has earned position 1 | warning | `graduation.bar` |
| **KC022** | **Commons only.** At position 1 below the bar: promoted early | warning | `graduation.bar` |
| **KC023** | **Commons only.** No new evidence in `staleness-months`. Measured against an injectable `--today`, because a check whose result depends on the wall clock is one nobody can prove fires | warning | `graduation.staleness-months` |
| **KC024** | `status:` is drawn from the type's lifecycle — **and a `status:` on a type with no lifecycle is an error**, because the lifecycle is a commons-tier mechanism and nothing graduates in a feeder | error | `types.attractors[].lifecycle` |
| **KC025** | An attractor with no evidence is a topic | warning | `types.evidence.attractor-field` |
| **KC027** | The `processed:` ledger stamp is well-formed: a list, of mappings, each with an ISO `date:` and list-valued `ran:` / `skipped:` / `errored:` | error | — |
| **KC028** | *(`--source-scan`)* Two identical event headings in one artifact collide on one canonical identity, and the second would be silently treated as processed | error | `sources[].path`, `.glob`, `.event-delimiter` |
| **KC030** | ≥ `new-map-at` notes name a map that does not exist — a map is **needed**. Flags; never creates | warning | `graph.growth.new-map-at` |
| **KC031** | Map headings are alphabetical | warning | `graph.ordering-exempt` |
| **KC032** | A note sits outside its type's declared `dir:` — reported, **never acted on**, because `type:` is authoritative | warning | `types.<t>.dir` |
| **KC033** | A hub has its declared `section:` — **renaming or dropping it must fail, never silently disable the check that depends on it** | error | `types.hubs[].section` |
| **KC034** | An attractor has its `stake-section:` — one without a "so what" is a topic | warning | `types.attractors[].stake-section` |
| **KC035** | An attractor's `evidence-section:` exists and agrees with the evidence notes' frontmatter **in both directions** — the frontmatter is authoritative, the section is a cache | error | `types.attractors[].evidence-section` |

### Config checks

| Code | Checks | Severity | Key |
|---|---|---|---|
| **KC102** | `min-attractors` is an integer ≥ 1; `evidence` declares an `attractor-field` | error | `types.evidence` |
| **KC103** | `graph.atlas` is set; every content type declares a `map:` | error | `graph.atlas`, `types.<t>.map` |
| **KC104** | A feeder attractor declares a lifecycle (**warning** — nothing graduates in a single-domain graph); a commons attractor declares none (**error**) | warning / error | `types.attractors[].lifecycle`, `graduation` |
| **KC105** | A hub with `bidir-with:` also declares `section:` and `field:` | error | `types.hubs[]` |
| **KC106** | A source tier with `path:` also declares `glob:` | error | `sources[]` |
| **KC107** | `promotes-to` is `{kind: graph\|instruction-tier, path: …}` | error | `graph.promotes-to` |
| **KC108** | Every source tier declares a `ledger:` | error | `sources[]` |
| **KC109** | Unknown top-level key, or unknown key under `graph:` — **the typo detector** | warning | — |
| **KC110** | A `schema:` key names a declared type (**error** — otherwise the block never fires); every declared type has a `schema:` entry (**warning**) | error / warning | `schema` |

*(Nothing else in the KC001–KC110 range is emitted. A config that cannot be parsed at all is fatal rather
than a finding — the validator exits 1 and says so, because a finding list built from a config it could not
read would be worthless. **Never mistake exit 1 for a clean run.**)*

**Every code in this table has a test that breaks a fixture graph and watches it fire.** That is enforced
mechanically by `test_every_check_is_proven_to_fire`, which greps the whole validator — docstrings included —
and fails if any code is *mentioned* without a test that fires it. This is not ceremony: the first version of
that test only looked at codes in quoted strings, so it could not see a check that was named and never
implemented. Three were hiding — `KC018`, `KC022`, `KC023`, one of them already being rendered into the
index's flag vocabulary. **A check that is documented but unimplemented is worse than a missing one, because
the clean run tells you it passed.**

### The other entrypoints

| Command | Does |
|---|---|
| `validate.py schema --graph ROOT` | Config checks only. |
| `validate.py baseline --graph ROOT --out FILE` | Writes the whole-graph fingerprint set. A real graph has pre-existing findings, and **a write must not be refused for a violation it did not cause.** The fingerprint deliberately excludes line numbers and message prose, so an unrelated edit does not make every pre-existing finding in the file look brand new. |
| `validate.py check --baseline FILE` | Marks findings absent from the baseline as **new**, and exits `3` if any new *error* appeared. This is what `knowledge-graph` runs after a transaction, scoped to the touched files, to decide whether to revert the whole set. |
| `validate.py index --graph ROOT [--write]` | Renders `index.md`: attractors only, one line each — **bold title** — the "so what" — `[domains]` — flags. The flag vocabulary is closed and maps 1:1 onto the checks, which is exactly why the index lives inside the validator: **the flags and the checks must not be able to disagree.** |
