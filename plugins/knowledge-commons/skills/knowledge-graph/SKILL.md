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

**Every attractor needs a stated stake** — the thing that makes it an attractor rather than a topic. Refuse to
create one without it. But the *shape* of that stake is per-type, and `note-formats.md` is the authority on
shape:

- A **principle-like** attractor states it as `## so what` — one clause of consequence, what changes because
  this is true. That clause is what the index renders.
- A **question-like** attractor states it as `## why I care` — the stake that makes the question worth
  accumulating answers to — plus `## partial answers`. It has **no** `## so what`; do not demand one, and do
  not refuse to create a question because it lacks one.

For the index, render an attractor's stake clause whatever its type calls it.

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

**Resolve the new status by position, out of the type's own `lifecycle:` list** — never by literal name. The
positions are defined in `mechanism.md`. A `principle` calls position 1 `held`; a `question` calls it
`graduated` and has no `held`. Writing `status: held` onto a question produces a status its type does not
have.

### Graduation that derives a new attractor (`graduates-to:`)

When the graduating type declares `graduates-to: <type>`, graduation is **not** a status flip. Two writes,
one approved transition:

1. **Derive the new attractor.** Write a new note of the target type. Its `## so what` is the stance the
   graduating note arrived at — carried forward as a claim someone stands behind, not as a summary of the
   question.

   **Born at position 1**, not position 0: it inherits the domain count that earned it. (Creating it at
   position 0 would have the next health check immediately re-flag it for the graduation that just made it.)

   **Add** the graduating note's evidence to it, preserving each `(domain)` annotation. **Add — do not move.**
   Each claim now lists *both* attractors in its `supports:`. Stripping the question from those claims would
   leave it with zero evidence and manufacture an orphan on every graduation.
2. **Move the original to position 1** and record what it became: a `## became` section naming the derived
   note as a wikilink, so the trail is not lost. It keeps its evidence and its body.

If you flip the status without deriving the note, the accumulated reasoning is stranded in a note that has
just been marked resolved. That is the exact failure `graduates-to:` exists to prevent — do not do half of
it.

## Step 4: Changelog

Append **one dated bullet per graph-shaping event** to `changelog.md` at the graph root: what changed and
why. This is not a commit log — it is the record of *why the graph looks the way it does*.

**Create `changelog.md` if it is missing.** `commons-init` seeds it, but a graph adopted in place or built by
hand will not have one, and a missing changelog must never be a reason to drop the entry.

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
