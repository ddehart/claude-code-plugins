---
name: promote
description: "Derive a portable claim from a source graph into a target graph or the instruction tier, with association and human approval. Use when the user asks to promote a note or insight to the commons, wants to know whether something generalizes, invokes /promote, asks to derive a claim into the commons, or asks to graduate a principle into a rule. Triggers: promote this to the commons, does this generalize, /promote, derive this into the commons, graduate this principle to a rule."
argument-hint: "[note or claim to promote]"
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
---

# Promote

One uniform mechanism for moving a claim out of the graph that produced it and into whatever it feeds:
any graph into the commons, or the commons into the instruction tier (`~/.claude/rules/`). Same flow
every time — there is no mode switch by domain, and no separate machinery for the instruction-tier case
beyond the one branch in §4.

You may be invoked at the tail of a `/process` run with one or more candidates already identified, mid-session
because something noticed looked commons-worthy, or directly ("/promote this insight to the commons"). All
three enter the same flow below.

## 1. Load two configs — don't confuse them

Read the **source** graph's `.commons.yml` for exactly one value: `graph.name`. That string becomes the
`domain:` field on the note you write. Nothing else about the source config matters here.

The target is named by the source's `promotes-to:` field, unless the caller named a different target
explicitly (e.g. promoting from the commons into `~/.claude/rules/`, which is a directory, not a graph — see
§4).

**Refresh the target before reading any of it.** Once you know which target, and before you read its
config, its maps, or its notes: if it's a git repository with a remote, fetch and fast-forward — then say
plainly what came in, including new attractors, new claims, new questions, and which domains they arrived
from. The order is the substance here, not tidiness. §3 associates against the target's maps and checks
redundancy against its existing claims, and both read whatever happens to be on disk; a refresh that runs
after those reads changes nothing, because nothing re-reads. A clone a few commits behind can have gained
principles, graduated the very question you were about to attach to, and already hold a near-duplicate of
the claim you're deriving — none of which surfaces until the push in §6 is rejected, by which point the
note is written and the association is already wrong.

**A fetch that succeeds is not the same as a target that is current.** Treat it as a failed refresh
whenever the local copy did not actually end up at the remote's tip: no remote, no network, no git, a
fetch error — and also a fetch that returns cleanly while the fast-forward is refused, because the local
copy has diverged or the tree is dirty. That last case is the dangerous one: `git fetch` exits 0, `HEAD`
doesn't move, and "refreshed, nothing new" is exactly what a clone missing nine commits looks like. Check
that the fast-forward actually happened, not merely that the fetch returned.

On any of those, continue — but say so. A skipped, failed, or refused refresh must never read as "the
target is current." State that the association and the redundancy check ran against a possibly-stale
copy, so the human weighing the proposal knows what it was weighed against. An unreported gap that looks
exactly like a clean result is the failure this whole flow is built to avoid.

Then read the **target**'s `.commons.yml` for everything else: type names, directories, where the atlas
and maps live.

Getting the two configs backwards is the other way this goes wrong. You are about to write into the
**target**'s world, using the target's type names and the target's directory layout. The source config
exists only to answer "whose domain is this."

## 2. Derive the candidate

Write the note you would write if you were authoring fresh in the target graph — never move or modify the
source note. The test that defines the operation: **would this stay true and useful if its source domain
vanished?** Read the candidate material, strip anything specific to entities, people, tools, or events in
the source domain, and check what's left. If no claim survives that strip, it doesn't promote — say so and
stop, rather than force a note that needs its origin to make sense.

A few things that trip this up:

- **Never carry an attractor's evidence list across.** If the candidate is itself an attractor being
  promoted (rare — usually it's a single evidence note), its title and evidence entries are artifacts of the
  source graph and can themselves be domain-specific. Rebuild the evidence section from what is actually
  being promoted in this operation, not by copying the source's list.
- **A promoted note is dated by its promotion**, not by whatever date the source material carried. Check
  the target's frontmatter contract for this note type (the generated knowledge-graph skill states it;
  the commons requires `date:` on claims) and set the promotion date — don't skip the field because the
  source note happened not to show one.
- **All wikilinks must resolve inside the target graph.** A promoted note that still links back into its
  source graph hasn't generalized — cut the link or replace it with a target-side equivalent.
- **`domain:` is a plain string, never a link or a path.** It's `orchard`, not `[[orchard]]` and not
  `~/orchard/graph.name`.

Follow the target's frontmatter and note-shape conventions exactly
(`${CLAUDE_PLUGIN_ROOT}/references/graph-conventions.md`): `genitor`, `tags`, the right note-type sections.

## 3. Associate

Read the target's attractor maps — the annotated entries are the distilled corpus, and reading them is the
fastest way to see what the claim might connect to. Three outcomes, in order of preference:

1. **Supports an existing attractor.** Name the attractor in the *claim's* `supports:` frontmatter
   (attractors never carry `supports:` — they're what gets supported), and add a line to that
   attractor's `## evidence` section, with the `(domain)` annotation. If this is the attractor's first
   evidence from a second domain, say so explicitly in the proposal — under the commons' convention that's
   the line between a provisional stance and a held one, and it's worth the reader's attention.
2. **Attaches to an open question.** No forcing required — questions exist to absorb claims that don't yet
   support a principle. **Confirm the question is still open before attaching to it.** A question that has
   already graduated is not a valid target: the claim belongs under the attractor it became, as evidence,
   which is outcome 1. Check this by reading the note itself — whether it still carries `## question` or
   now carries `## so what` — never by where a map happens to list it. Questions graduate in place, so a
   map can still file one under a "questions" heading long after it stopped being one.
3. **Nothing fits.** Propose a new question, not a new attractor. Attractors earn their name from
   accumulated evidence; a promotion may create one when the material genuinely warrants it (a fresh commons
   with nothing to attach to yet), but the default for a first-of-its-kind claim is a question.

**Never hold a first-domain claim back to wait for corroboration.** Association reads the *target's* maps —
a claim left in its home graph is invisible to every other domain's promote run, so the planted question is
the only hook by which a second domain's recurrence can ever be recognized. Single-domain questions are the
designed intermediate state of a receiving graph, not dilution: a question asserts nothing beyond "worth
watching," and the graduation bar — not entry — is what protects the graph's authority.

**Route by type.** A portable *lookup* fact — tool behavior, a platform gotcha, something you'd search for
by name — derives into the target's reference tier, not as a claim. Reference notes need no attractor and
no question; the promote-vs-hold tension doesn't apply to them.

## 4. The instruction-tier branch

When the target is a rules directory (e.g. `~/.claude/rules/`) rather than a graph — the commons graduating
a principle — the write is a **rule file**, not a note. Everything above still applies (derive, don't
migrate; portability test; association is "does an existing rule already cover this") with one addition:

- **Read the existing rules first.** A graph built from sessions that those rules already steered will keep
  re-deriving the same principle. If a rule already says this, the answer is "already steering" — report
  that and stop, don't propose a duplicate.
- **Extra screen question:** is this steering-grade? Should it change how a session *behaves*, not just what
  it *knows*? A principle can be true and interesting without being worth encoding as behavior.
- The proposed rule file states the principle, states why — citing the principle's evidence domains in
  prose (rules directories don't resolve wikilinks, so no `[[links]]` here) — and states how to apply it.
  Same shape a human-authored rule would take.

## 5. Propose

Show the full derived note (or rule file), the map updates it implies, any attractor or question created or
updated, and the reasoning behind the association choice. This is the gate — there is no separate boundary
apparatus, no screening machinery beyond this proposal. The reader sees exactly what will land and decides.

Lean toward proposing. A declined candidate costs the reader one "skip"; a claim that never got proposed is
invisible loss. When genuinely uncertain whether something generalizes, propose it and let the human sort it
— that judgment call belongs to the reader, not to this skill.

Wait for explicit approval before writing anything. "Skip," "edit," and "not yet" are all valid answers.

## 6. Write

On approval: write the note (or rule file) per the target's conventions, enter it in its map at the correct
alphabetical position (genitor), and append one line to the target's `changelog.md` recording the
promotion — what came in, from where, and what it now supports.

**Then commit.** If the target graph is a git repository, commit the promotion (the note, map updates,
changelog line — name the paths, don't blanket-stage) and push if a remote exists. An uncommitted
promotion is invisible to every other machine and session — the cross-domain chain this skill exists for
dies in a working tree. If the push is blocked (no network, permission rule), say so plainly so the
human knows the promotion hasn't left this clone.

**A rejected push means the target moved while you were writing.** Pull and rebase, then push again — but
read what came in before resolving anything. If the incoming commits touch what the association rests on
— the question you attached to, the attractor you added evidence to, the map line you inserted — stop and
re-derive rather than resolving mechanically. A conflict in a map is rarely a merge chore; it usually
means the association is now wrong: the question graduated, an attractor absorbed the claim, or someone
else's promotion already said this. Take it back through §3 and re-propose. Resolving by hand and pushing
produces a promotion that is well-formed and pointed at the wrong thing, which is far harder to find
later than the conflict was.

A promoted note must stand alone. That's the whole test, at every step of this flow.
