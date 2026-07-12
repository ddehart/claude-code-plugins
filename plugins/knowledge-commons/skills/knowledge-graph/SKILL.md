---
name: knowledge-graph
description: >
  Read and write notes in a knowledge commons graph — claims, principles, questions, evidence, attractors,
  and reference notes — enforcing the evidence-must-point-at-an-attractor invariant at write time. Use when
  writing a note to the graph, adding a claim or principle, linking evidence to an attractor, or answering
  "what do we know about X" by pulling the index. Also used by the /process orchestrator, which delegates
  every graph write to this skill.
allowed-tools: ["Read", "Write", "Edit", "Glob", "Grep"]
---

# Knowledge Graph

The read/write mechanics for a knowledge commons graph. **This is the only skill that writes graph notes.**
`/process` proposes and approves; this skill writes. `commons-check` inspects and flags; it writes only
`index.md`.

Before doing anything, read the two references that define the contract:

- `${CLAUDE_PLUGIN_ROOT}/references/mechanism.md` — roles, the invariant, lifecycles, the boundary
- `${CLAUDE_PLUGIN_ROOT}/references/note-formats.md` — the on-disk format for every note type

Do not reproduce their contents from memory. Read them.

## Step 1: Load the config

Find `.commons.yml` (cwd, then the configured graph root). Resolve **role → type name → directory** from it:
the graph might call its evidence `claim` or `insight`, its attractors `principle` or `opportunity`. Never
assume the personal-commons names — read them.

If `.commons.yml` is absent, stop and point at `/commons-init`. Do not improvise a graph layout.

## Step 2: Enforce the invariant at write time

This is the load-bearing constraint. **One enforced rule is why the graph has edges at all** — unenforced
graphs decay into taxonomies.

### Writing an evidence note

1. The note **MUST** carry ≥1 `supports:` entry.
2. Each `supports:` target **MUST** resolve to an existing attractor file inside the graph root.

If a target does not resolve:

- **Create the attractor only if the approved plan called for it.** `/process` proposes new attractors
  explicitly and they are covered by the plan approval; creating one here is then just execution.
- **Otherwise, refuse the write and report.** Do not create an attractor on the fly to satisfy the check —
  that turns the invariant into a formality. Do not write the evidence note without the link.

**No silent orphan evidence, ever.** An evidence note that points nowhere is the exact failure this whole
mechanism exists to prevent.

### Wikilink containment (boundary layer 1)

Every wikilink written must resolve **inside the graph root**. A link that resolves outside it is a
structural boundary leak — refuse the write and report it.

This catches structure, not prose. It is necessary and **not sufficient** — see `mechanism.md` for the
LLM-review and human-approval layers, which `/process` owns.

### `domain:` is provenance only

Set by the processor, confirmed at plan approval. **Never a link. Never content.** It records where a claim
came from so attractors can count distinct domains for graduation. If the note's substance needs its domain
to make sense, the note has not generalized — say so rather than writing it.

## Step 3: Write

**Filenames are titles.** Evidence gets a `YYYY-MM ` prefix; attractors do not (they are long-lived, stable
link targets). Exact formats are in `note-formats.md`.

**Evidence bodies are one self-contained paragraph.** Not a bullet list, not a section tree. A claim is one
thing someone could stand behind.

**Attractors need a `## so what`** — one clause of consequence, what changes because this is true. It is
what the index renders. An attractor without a "so what" is a topic, not an attractor; refuse to create one.

### Updating an attractor with new evidence

Append a bullet under `## evidence`, annotated with its domain:

```markdown
- [[2026-07 A dry run caught a config error that review missed]]   (homelab)
```

Do not restructure or reword the attractor's existing content while adding evidence. Append.

### Reference notes

`type: reference`, `verified: <date>`, **no `supports:`**, exempt from the attractor requirement, never
indexed. This exemption is what lets reference grow without bound — do not "fix" a reference note by giving
it an attractor link.

### Lifecycle transitions

`commons-check` **flags** transitions; `/process` **applies** them under plan approval. When applying an
approved transition, change `status:` and record it in the changelog. Never flip a status silently as a
side effect of some other write.

## Step 4: Changelog

Append **one dated bullet per graph-shaping event** to `changelog.md` at the graph root: what changed and
why. This is not a commit log — it is the record of *why the graph looks the way it does*.

Creating a claim is not usually graph-shaping. Creating an attractor, graduating one, demoting one,
abandoning a question — those are. When in doubt, ask whether a reader six months out would want to know
why this happened.

At month rollover, archive the prior month to `changelog/YYYY-MM.md` and start `changelog.md` fresh.

## The read path — "what do we know about X"

This is the **pull** side of the design, and it is deliberately unglamorous:

1. Read `index.md` at the graph root. It renders attractors only — the distilled corpus, small enough to
   hold whole.
2. Follow the wikilinks on whatever is relevant to the question.
3. Reference notes are retrieved by **lookup** (grep the reference dir) — you already know what you want.

There is no ambient injection, no embedding search, no MCP server. The index is small and read directly.

## Prohibitions

- **Never write an evidence note without a resolving attractor link.**
- **Never hand-edit `index.md`.** It is generated by `commons-check --index`.
- **Never move a note between graphs.** Promotion *derives* a new self-contained note; it never migrates one.
  See `mechanism.md`.
