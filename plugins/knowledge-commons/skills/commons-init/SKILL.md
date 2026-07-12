---
name: commons-init
description: >
  Set up a knowledge commons: interview for the graph's types, sources, sinks, and boundary posture, then
  write .commons.yml, scaffold the directories, and stub any missing project-edge skills. Use when asked to
  initialize a knowledge commons or knowledge graph, set up a commons in a project, create .commons.yml, or
  add a knowledge tier to a repo. Generates config and scaffolding — never copies of the mechanism.
argument-hint: "[graph-root]"
allowed-tools: ["Read", "Write", "Edit", "Glob", "Bash", "AskUserQuestion"]
---

# Commons Init

Stand up a new knowledge commons, or adopt an existing directory as one.

Read the contract first:

- `${CLAUDE_PLUGIN_ROOT}/references/commons-yml.md` — the config schema and every field's meaning
- `${CLAUDE_PLUGIN_ROOT}/references/mechanism.md` — roles, so the interview's questions make sense

## The prohibition — read this before anything else

**Never copy `process`, `knowledge-graph`, or `commons-check` into the target project.**

This skill generates **config and scaffolding**. A generated copy of the orchestrator would be a fork: it
stops receiving mechanism updates the moment it is written, and the graph it serves quietly diverges from
every other graph. The mechanism lives in the plugin. Full stop.

Generated **edge-skill stubs are fine and expected** — they are owned by the project, they encode
project-specific procedure, and they are *supposed* to specialize and drift. That is the whole split:
data-shaped specialization goes in `.commons.yml`, procedure-shaped specialization goes in project-local
edge skills, and the invariant mechanism stays in the plugin.

## Step 1: Preflight

- **Existing `.commons.yml`?** Do not clobber it. Offer to *augment* it (add a source tier, a new sink, a
  missing stub) or abort. Show what is already configured.
- **Existing graph or vault at the target root?** Adopt it in place. An existing Obsidian vault with notes
  in it is a graph that has not been configured yet, not an obstacle — scaffold *around* what is there and
  never overwrite an existing note.
- Confirm the graph root before writing anything to it.

## Step 2: Interview

Use `AskUserQuestion`. **Batch the questions** — this should be a short conversation, not an interrogation.

Default to the **personal-commons shape** (below) and let the user diverge from it. Most instantiations are
near-minimal, and offering a filled-in default is faster than asking six open questions.

```yaml
graph:
  root: <asked>
  name: <asked>              # the domain: this graph stamps on notes it promotes elsewhere
  types:
    evidence:   { name: claim,     dir: claims/,     requires: attractor-link }
    attractors:
      - { name: principle, dir: principles/, lifecycle: [provisional, held, stale] }
      - { name: question,  dir: questions/,  lifecycle: [open, graduated, abandoned], graduates-to: principle }
    reference:  { name: reference, dir: reference/ }
sources:
  - type: session-chronicle
    domain: <asked>            # required — the provenance stamped on every claim from this tier
    path: docs/chronicle/
    glob: "20*.md"             # keeps reflective-practice.md out of the source queue
    resolve-via: null
    ledger: source-note
outputs:
  claim:     { sink: graph }
  principle: { sink: graph }
  reference: { sink: graph }
boundary:
  posture: personal
  promotion-gate: [mechanical, llm-review, human-approval]
staleness:
  months: 6
```

What to ask:

1. **Graph root, and the graph's name** — where the notes live, and what this graph is called. The name is
   not cosmetic: it becomes the `domain:` on any note this graph promotes into another one.
2. **Boundary posture** — `personal` or `professional`. This is the consequential one: a professional graph's
   promotions *out* are gated by all three layers; a personal graph is usually the promotion *target*.
   Explain that when asking.
3. **Types per role** — evidence (exactly one), attractors (one or more, each with a lifecycle), and
   optionally reference. Offer the defaults; ask what this graph actually calls these things. A work graph's
   `opportunity` is not a personal commons' `principle`, and forcing shared names would make the graph worse
   to make the model tidier.

   **Do not offer `entity` or `intermediate`.** Both are defined in `mechanism.md` for Phase 2, and neither
   is wired: there is no on-disk format for an entity and no skill that can write one. Configuring a type
   nothing can produce would leave the first `/process` run with an output class it has no instructions for.
   If the user asks for one, say plainly that it is not implemented yet.

   Each attractor's `lifecycle:` is an ordered `[proposed, earned, retired]` — the names are the graph's to
   choose, and the skills resolve them by position. If a type *becomes* another type when it earns its keep
   (a `question` answered across two domains has become a stance, i.e. a `principle`), set
   `graduates-to: <type>` — otherwise graduation is a bare status flip and the reasoning gets stranded in a
   note marked resolved.
4. **Source tiers** — what artifacts arrive on their own, where they land, **what domain each carries**, and
   whether each needs an edge skill to become readable text (a recording URL to resolve, a transcript to
   format) or is already markdown. Set each tier's `glob:` if its directory holds anything that is not a
   source (`docs/chronicle/` also contains `reflective-practice.md`, which is not a session record).

   **Warn if the config ends up with only one domain.** Graduation requires evidence from ≥2 distinct
   domains, so a single-domain graph has an inert lifecycle: nothing ever reaches position 1, and nothing
   ever demotes. That is a legitimate configuration — a project knowledge tier is single-domain by
   definition — but the user should choose it knowingly rather
   than discover it months later when nothing has ever graduated. Say it plainly, and offer to add a second
   tier.
5. **Output classes → sinks → approval** — the graph is one sink; a task manager or tracker may be others.
   For each non-graph sink, get the edge skill's name and its approval mode (`per-item` for a task manager).
   Note any sink defaults that must always apply — e.g. Todoist tasks that land without a `next` label fall
   out of every GTD filter and become invisible, so `defaults: { labels: [next] }` belongs in config, not in
   the user's memory.

## Step 3: Write the config and scaffold

- Write `.commons.yml` at the graph root.
- Create the directories the type config declares (`claims/`, `principles/`, …).
- Seed `index.md` with the generated-file header (see `note-formats.md`) and a note that
  `commons-check --index` owns it.
- Seed an empty `changelog.md` for the current month.

Do not create example notes. A graph seeded with fake claims starts with content nobody stands behind, and
the first real `/process` run then has to argue with it.

## Step 4: Stub the missing edge skills

For every `resolve-via:` and `via:` name in the config, check the **live skill list** — the skills enumerated
in your own session context, which already covers plugin, project, and personal skills. Do not scan
`.claude/skills/` instead; that holds project skills only, and you would stub over an edge skill that already
exists at another level. For each name genuinely absent, write a stub to the *target project's*
`.claude/skills/<name>/SKILL.md`.

A stub is a **contract, not an implementation**: valid frontmatter, and a body stating what it receives,
what it must return, and its approval mode — with the procedure left as a clearly-marked TODO.

```markdown
---
name: todoist-dispatch
description: >
  Write a dispatch item from /process to Todoist. Called by the knowledge-commons orchestrator; not
  usually invoked directly.
allowed-tools: ["Bash"]
---

# Todoist Dispatch  (STUB — implement me)

**Receives:** one dispatch item — title, optional due date, optional project — plus the `defaults` from
`.commons.yml` (`labels: [next]`).

**Must:** create the task, and return the created task's id, or a clear error. Confirm each item before
creating it (`approval: per-item`).

**TODO:** implement. Until this is done, `/process` will report the `task` class as skipped-with-reason
and continue with everything else.
```

An unimplemented stub is not a failure state — `/process` degrades cleanly around it, skipping that class
with a reason and continuing. Say so in the report so the user knows the graph still works.

## Step 5: Report

- What was created (config, directories, seeded files) and what was adopted in place.
- **Which stubs need implementing before their output class will run.**
- The next step: run `/process` to refine the first sources into the graph.
