---
name: graph-patch
description: >
  Propagate template fixes into a project's already-generated, hand-sharpened process and
  knowledge-graph skills, without regenerating them. Reads the plugin's delta log, applies each
  pending semantic change by judgment against the project's own prose, verifies it landed, and
  records what was applied in .commons.yml. Use when the user wants to "apply pending patches",
  says "graph-patch", asks to "patch my process skill", "patch my generated skills", "what
  template fixes am I missing", "update my generated skills", "are there pending patches", or
  when a /process run reports pending patches and the user asks to apply them.
argument-hint: "[delta id to apply, or blank for all pending]"
allowed-tools:
  - Read
  - Edit
  - Glob
  - Grep
  - Bash
  - AskUserQuestion
---

# graph-patch

This is the maintainer. `graph-init` generates two project-owned skills — `process/SKILL.md` and
`knowledge-graph/SKILL.md` — and then tells the project it owns them and should sharpen them from
real runs. Projects do, heavily: measured across three live graphs, bodies diverge by up to 78%
while every `## N. Title` heading survives byte-identical. That asymmetry is the whole design.

**You apply semantic instructions by judgment, anchored on exact heading text. You never apply a
textual diff, and you never regenerate a file.** The same fix reads differently in each graph
because each graph wrote its own prose; your job is to make the change *true* in this project's
voice, not to paste the template's words into it.

Run this from inside the target project — the project that owns the graph, not the plugin repo.
That is where the domain context lives, which is where the approval judgment belongs.

**Every write in this skill is a surgical `Edit`.** `Write` is deliberately absent from this
skill's tools: it is the one tool that makes whole-file replacement reachable, and whole-file
replacement is this skill's first prohibition. You never create a file and you never replace one.

## 1. Orient

Read `.commons.yml` at the project root. If there isn't one, this project has no
knowledge-commons graph — say so and stop; there is nothing to patch.

Locate the two patchable files:

- `<project>/.claude/skills/process/SKILL.md`
- `<project>/.claude/skills/knowledge-graph/SKILL.md`

Either may legitimately be absent. A graph with no `sources:` (the commons) gets no `process`
skill at all. A missing file is not an error — it means every delta targeting that file is
**out of scope** for this project. Note which file is missing and carry it to the report (step 7);
those deltas are neither applied nor pending, so nothing else will surface them.

Read the delta log at `${CLAUDE_PLUGIN_ROOT}/references/deltas.md`. If it is missing or empty,
report that and stop.

## 2. Establish applied-patch state

State lives in a `generated:` block in `.commons.yml`:

```yaml
generated:
  process:
    template-version: 0.2.0
    applied: [step4-explicit-negative, step9-stamp-gate, step11-pull-target]
  knowledge-graph:
    template-version: 0.2.0
    applied: [entity-proactive-recommend]
```

**If the block is absent, bootstrap it.** Every graph generated before this mechanism existed came
from templates at plugin version `0.1.8` — assume that, add the block with
`template-version: 0.1.8` and an empty `applied: []` for each generated file that actually exists,
and proceed. Do not probe file contents to guess a version; the population of graphs older than
0.1.8 is zero. Say plainly in the report that you bootstrapped.

Add the bootstrap block before applying anything, so a run that fails partway still leaves the
project with honest state.

**If the block exists but a file's sub-key is missing, treat that sub-key as empty** — every delta
targeting that file is pending. This is reachable in normal operation: bootstrap writes a sub-key
only for each generated file that existed *at bootstrap time*, so any project that gains its second
generated skill afterward lands here. A missing sub-key means "nothing applied yet," never "skip
this file."

### Amend `.commons.yml` surgically — never re-serialize it

`.commons.yml` is a file the project wrote by hand, and it carries hand-written comments — the
reference config has six comment-bearing lines explaining what `domain:` means, which attractors are
open versus settled, which sources have no queue.

**Use `Edit` to append or replace the `generated:` block, and nothing else.** Every other key, its
values, its ordering, its inline comments, and the file's whitespace must survive **byte-identical**.

Specifically: do **not** parse the YAML into a data structure, insert a key, and re-emit the file. A
round-trip through any YAML serializer strips every comment and reflows the formatting — destroying
hand-written explanation on a config the project owns, in a single silent step. That is the same
failure this whole skill exists to prevent, committed against a different file. It also violates the
`Never` below: a re-serialization touches every key's formatting even when the values survive.

Append `generated:` at the end of the file if it isn't there. If it is, edit within it.

## 3. Select what's pending

**Select by set membership on `id`, never by version arithmetic.** A delta is pending if its `id`
does not appear in the `applied:` list for its `file`. That is the only test.

This matters: D15 stamps only what actually applied, so `applied:` can legitimately have holes
below `template-version`. Comparing versions would silently skip a delta that failed on a previous
run — which is precisely the silent-loss shape this mechanism exists to prevent.

Filter out deltas whose `file` doesn't exist in this project (step 1) — those are **out of scope**
for this project, not pending. Track them for the report; they are neither applied nor pending, and
must not silently vanish.

**If an argument named a specific delta id**, resolve it against the **whole log**, not the pending
set, and report which of three cases it hit:

- **Found and pending** → apply only that one.
- **Found but already in `applied:`** → say so and stop. Nothing to do; do not re-apply.
- **Not in the log at all** → say *"no delta with that id exists"* and stop. **Never fall through to
  "nothing pending" and report a clean run** — a typo'd or newer-than-this-plugin id would then look
  like a patch that was considered and found unnecessary, when it was never found at all. Name the
  id you looked for, and suggest the plugin may need updating if the id came from a newer version.

**With no argument**, take every pending delta, in log order.

If nothing is pending, say so and stop. That is a clean, common outcome — but state it as "no
pending deltas," and still report anything out of scope.

## 4. Apply each delta

Each log entry carries seven fields: `id`, `file`, `anchor`, `version`, `instruction`,
`rationale`, `satisfied-test`. Work one delta at a time, through the whole of this section, before
starting the next.

### 4a. Locate the anchor

Find the `anchor` string as an **exact heading match** in the target file.

- **Not found → skip it, loudly.** Report the delta id, the anchor text, and the file. **Never
  stamp it.** **Never relocate it semantically** — do not look for "where that section moved to,"
  do not pick the nearest plausible heading, do not apply the instruction somewhere else. Guessing
  where content went is where a patcher does real damage to hand-written prose. A delta that
  can't find its target does nothing, loudly, rather than landing somewhere convincing.
- **Matches more than once → skip it, loudly, the same way.** An ambiguous anchor is a missing
  anchor.

There are real, legitimate reasons an anchor is absent — a project renamed a heading, or the
heading was templated at generation time and resolved differently here. Skipping is the correct
behavior in every one of those cases, not a failure to work around.

### 4b. Judge redundancy first

Read the anchored section in full, then answer the `satisfied-test` against what is actually
written there. **If the test already passes, propose no edit.** The project hand-fixed this
defect already, or wrote it correctly from the start. Report *already satisfied*, **note it for
stamping in step 5**, and move to the next one. Don't write to `.commons.yml` here — step 5 is the
single point where state reaches disk.

Do not propose a cosmetic rewrite to make the section resemble the template. The test is the
contract; matching prose is not.

### 4c. Propose, with the concrete diff

Show, for this delta:

1. The delta's `instruction` and `rationale`, so the reader knows what is being asked and why.
2. **The concrete before-and-after against the project's actual current prose** — the real text in
   the file today, and the exact text you propose replacing it with. Never propose an edit without
   showing this. A summary of the change is not a diff, and this is hand-written prose: the diff is
   the reader's only defense against a locally-plausible edit that contradicts a nearby paragraph.

Write the replacement **in the project's own voice and vocabulary**, using this graph's type names,
signal classes, and terminology. Some deltas edit the template's generic spine, which usually
survives nearly verbatim and can be edited near-literally. Others must weave into diverged body
prose — *"add an entity signal class alongside this graph's existing classes in step 4"*. Both go
through this same flow. For a weave, the `rationale` is what tells you what the change must
accomplish; write the sentences this project would have written, not the template's.

Then ask for approval: **`y` / `edit` / `skip`**, per delta. Wait for it. "Skip" and "edit" are
both ordinary answers, not failures.

- **`y`** — apply as shown.
- **`edit`** — take the reader's revision and apply that. Then still run 4d against it.
- **`skip`** — apply nothing, **stamp nothing**, and note it for the report. A skipped delta stays
  pending and will be offered again on the next run.

### 4d. Verify — re-run the `satisfied-test`

After writing the edit, re-read the section and answer the `satisfied-test` again. The same test
that answered *"is this already here?"* before the edit answers *"did it land?"* after.

- **Passes** → the delta applied. It is now eligible to be stamped.
- **Fails** → the edit did not accomplish what the delta asked. Do not stamp it. Do not retry
  silently. Report it as a failure with the anchor, what you wrote, and how the test failed, so it
  can be retried by hand.

This step is not optional and does not get skipped for a delta that "obviously" worked. This batch
of fixes is entirely about failures that are indistinguishable from success; the patcher must not
have that failure mode itself.

### 4e. Continue and collect

A delta that fails — missing anchor, failed post-condition, anything else — does not stop the run.
Skip it, keep going with the remaining deltas, and report every failure together at the end with
enough detail to retry. This mirrors `process`'s continue-and-collect; the plugin has one idiom for
this and the patcher should not invent a second.

## 5. Stamp only what applied

Update the `generated:` block in `.commons.yml`:

- Append to `applied:` the ids of deltas that **actually applied and verified in 4d**, plus the ids
  found *already satisfied* in 4b. Nothing else.
- **Never stamp** a delta that was skipped, whose anchor was missing or ambiguous, or whose
  post-condition failed.
- Set `template-version` to the highest `version` among the deltas you stamped for that file. If
  you stamped nothing for a file, leave its `template-version` alone.

A partly-applied run leaves partly-stamped state, and that is correct. The `applied:` list is the
truth; `template-version` is a convenience. Set-membership selection (step 3) is what keeps the
holes honest on the next run.

## 6. Re-read for coherence

After all deltas are applied, **read each touched file start to finish, whole.** A per-delta
post-condition proves the edit says the right thing locally; it cannot see that the new sentence
contradicts a paragraph three sections down that the project wrote by hand.

Report anything that reads wrong — a duplicated instruction, a contradiction, a now-dangling
cross-reference, a paragraph the edit made redundant — **as a concern, for the human to decide.**
Do not fix it. Do not fold an unapproved edit into an approved run. Every write in this skill goes
through 4c's diff and approval; a coherence fix is a new proposal, and it belongs to the next run
or to the human's own hand.

## 7. Report

State, plainly:

- Which deltas **applied**, per file.
- Which were **already satisfied** (stamped, no edit made).
- Which were **skipped by the reader**, and which **failed** — for each failure, the id, the
  anchor, the file, and why, in enough detail to retry.
- Which were **out of scope** because their target file doesn't exist in this project — name them
  and name the missing file. These are neither applied nor pending, and without their own line they
  disappear from the report entirely. A commons graph has no `process` skill, so every `process`
  delta lands here on every run; say so rather than leaving the reader to wonder where they went.
- Whether the `generated:` block was **bootstrapped** this run.
- Any **coherence concerns** from step 6.
- What remains **pending** after this run.

Failures and skips get the same prominence as successes. An unpropagated fix that nobody notices
is the exact condition this mechanism exists to end.

## 8. Commit, never push

If the project is a git repository and anything changed, commit — **naming every path explicitly,
never blanket-staging.** The paths are the touched `SKILL.md` files and `.commons.yml`, nothing
else.

Conventional-commit message citing the applied delta ids:

```
chore(graph): apply template deltas step4-explicit-negative, step9-stamp-gate
```

**Do not push.** This deliberately differs from `promote`, which commits *and* pushes. A promotion
is a contribution other machines are waiting on; a patch run is local maintenance that just edited
prose the project wrote by hand, in a repo with its own PR conventions. The push decision stays
with the human — say so in the report so they know the commit is sitting local.

## Never

- **Never regenerate a file.** Regeneration destroys the local prose that makes the skill useful;
  that is the entire reason this skill exists instead of a re-run of `graph-init`.
- **Never apply a textual diff from the template.** Deltas are semantic instructions applied by
  judgment. The target has diverged; the template's words are not the target's words.
- **Never touch anything outside the two generated skills.** Notes, maps, the atlas, changelog,
  type directories, and scaffold structure are entirely out of scope. The `.commons.yml`
  `generated:` block is bookkeeping you write — it is not itself a patch target, and no other key
  in that file gets edited.
- **Never re-serialize `.commons.yml`.** Amend the `generated:` block with `Edit`; every other key,
  its ordering, its whitespace, and its hand-written comments survive byte-identical. A YAML
  round-trip silently destroys all of them.
- **Never write an edit without showing the concrete before-and-after first** and getting explicit
  per-delta approval. Batch approval hides exactly what needs judgment.
- **Never stamp a delta that didn't verify.** Skipped, missing-anchor, ambiguous-anchor, and
  failed-post-condition deltas all stay unstamped and stay pending.
- **Never relocate a missing anchor.** Skip and report; do not find it a new home.
- **Never blanket-stage, and never push.**
