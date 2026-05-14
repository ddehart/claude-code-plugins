# commit-creator: bump model haiku → sonnet + add working-directory discipline

> **Status: READY** — drafted 2026-05-14 from wellstead-session evidence; fleshed out 2026-05-14 after scope decisions (see Decisions). Ready for an implementation plan.

## Problem

`plugins/dev-workflow/agents/commit-creator.md` pins `model: haiku`. Three distinct failure modes have surfaced in real use (all in the `wellstead` project), which together suggest haiku is under-powered for the task:

1. **Fabricated issue reference** — injected `Refs: WEL-D3` (a synthesized, non-existent Linear ID) into a commit on a no-Linear branch. Fixed upstream in dev-workflow 1.3.3 via PR #56 by tightening the agent definition's "detectable" wording.
2. **Inconsistent trailer application** (2026-05-14) — added a `Co-Authored-By: Claude` trailer to one of three commits in the same session, picking up a global instruction that conflicts with the target project's commit standard. Applied inconsistently even within a single session.
3. **Wrong working directory + silent content paraphrasing** (2026-05-14) — given an explicit git worktree path to operate in, ran git in the shared checkout instead; and rather than committing the existing files, spent ~32 tool-uses re-creating its own paraphrased, abbreviated versions of the content and committed *those* — then reported confident success with hashes. Caught only by an external `git log` check.

The common thread is haiku-class: losing the thread on multi-step instructions, not reliably tracking the working directory, and "helpfully" reconstructing content instead of performing the literal mechanical `git add` / `git commit`. commit-creator's job is mechanical but touches git history — a botched commit is expensive to recover, and the paraphrasing failure mode produces *plausible-looking wrong content* that only output verification catches. The cost asymmetry (haiku's marginal speed/cost saving vs. recovery cost plus the risk of silent bad commits) argues for a more capable model.

Failure mode 3 has a second root cause beyond model capability: the agent definition contains **no working-directory guidance at all** and **no explicit instruction that commit-creator's job is mechanical** (stage what exists, do not author content). A model bump lowers the probability of the failure; an instruction fix removes the gap the failure exploited. This spec does both.

## Decisions

Three judgment calls were settled with Derek on 2026-05-14:

- **D1 — Scope: commit-creator only.** This spec bumps only `commit-creator`. It is the one dev-workflow agent that mutates git history, making its cost asymmetry uniquely sharp. `branch-creator`, `test-runner`, and `pr-manager` stay on `haiku`; a broader audit is deferred (see Non-Goals).
- **D2 — Pin `sonnet` explicitly.** Frontmatter becomes `model: sonnet`, not a removed `model:` line. An explicit pin is deterministic and reproducible regardless of the invoking session's model; removing the line would make behavior depend on caller context and could silently regress if commit-creator were ever invoked from a haiku session.
- **D3 — Bundle the cwd/worktree instruction fix.** This spec also adds a working-directory + mechanical-discipline section to `commit-creator.md`, because failure mode 3 was partly an instruction gap, not purely a model-capability gap. Fixing both in one change closes the gap completely rather than relying on the model bump alone.

## Goals

- Bump `commit-creator`'s pinned model from `haiku` to `sonnet` (explicit pin, per D2).
- Add an explicit **Working Directory** section to `commit-creator.md` that (a) tells the agent to operate in the directory it was given and verify it before any git operation, and (b) states that commit-creator's job is mechanical — stage and commit the files that already exist, never Read-then-rewrite or paraphrase content.
- Bump `dev-workflow` plugin and marketplace versions per `.claude/rules/plugin-updates.md`.

## Non-Goals

- **Bumping the other three dev-workflow agents.** Per D1, `branch-creator`, `test-runner`, and `pr-manager` are out of scope. If a future audit shows they warrant the same treatment, that is a separate spec/PR.
- **Rewriting commit-creator's instructions wholesale.** The change is additive: one frontmatter line plus one new section. The existing Role, Commit Types, Issue Reference Detection, Examples, Workflow, Safety Checks, Escalation, and QA sections are unchanged.
- **Changing the agent's `tools` list.** `Bash, Read` stays as-is. (`Read` is retained — the agent legitimately reads files to determine commit type; the new section constrains *how* it may use what it reads, not whether it may read.)
- **Generalizing worktree/cwd guidance to other agents or to a shared include.** Even though `branch-creator` and `pr-manager` also run git, this spec scopes the instruction fix to `commit-creator.md` only, consistent with D1.

## Design

### Change 1 — Model bump

In `plugins/dev-workflow/agents/commit-creator.md` frontmatter:

```diff
-model: haiku
+model: sonnet
```

No other frontmatter changes.

### Change 2 — Working Directory section

Insert a new `## Working Directory` section into `commit-creator.md`, placed immediately after the `## Your Role` section (before `## Commit Types`) so it is read before any workflow step. Use the section text below **as-is** — it is the agreed wording, not a draft to paraphrase. (Only the outer ```markdown fence is a delimiter; everything inside it is the literal section content.)

```markdown
## Working Directory

commit-creator's job is **mechanical**: stage and commit the files that already
exist on disk. You are not an author. You never create, rewrite, paraphrase, or
"clean up" file content — not even if you think you could improve it. If the
content looks wrong, escalate (see "When to Escalate"); do not fix it yourself.

Before any git command:

1. **Establish the working directory.** If the invoking context gave you an
   explicit path (a worktree path, a repo path, a "commit in X" instruction),
   that path is where you operate. If no path was given, operate in the current
   working directory.
2. **Verify it.** Run `pwd` and `git rev-parse --show-toplevel`. Confirm the
   resolved repository root matches the directory you were told to use. If they
   disagree, or the directory is not inside a git repository, stop and escalate
   — do not guess.
3. **Run every git command in that directory.** Use `git -C <path> ...` or `cd`
   into the directory first. Do not run git in a sibling checkout, a parent
   repo, or the shared working tree when you were given a worktree path.

When you verify the commit afterward (`git log -1`), verify it in the **same**
directory, and confirm the committed files are the ones that already existed —
not regenerated copies.
```

### Change 3 — Reinforce in Safety Checks and Escalation

To make the new discipline load-bearing at the points the agent actually checks itself, add:

- To `## Safety Checks`, a new bullet: `Confirm you are in the working directory you were given (see "Working Directory") before staging or committing.`
- To `## Quality Assurance`, a new bullet: `Confirm committed content is the pre-existing files, not regenerated or paraphrased copies.`

The existing `## When to Escalate` already lists `Working directory state is ambiguous` — that line stays and is now backed by the explicit `## Working Directory` procedure.

## Changes Required

- **`plugins/dev-workflow/agents/commit-creator.md`**
  - Frontmatter: `model: haiku` → `model: sonnet`.
  - Insert `## Working Directory` section after `## Your Role`.
  - Add one bullet to `## Safety Checks` and one to `## Quality Assurance` (Change 3).
- **`plugins/dev-workflow/.claude-plugin/plugin.json`** — version `1.3.4` → `1.3.5`.
- **`.claude-plugin/marketplace.json`** — `dev-workflow` plugin entry version `1.3.4` → `1.3.5`.
- **`README.md`** — **no change.** Verified 2026-05-14: `README.md` contains no per-agent model references, so the component tables do not need updating. (The stub flagged this as "verify"; it is now verified.)

## Edge Cases

- **commit-creator invoked from a haiku session.** The explicit `model: sonnet` pin (D2) overrides the caller's model, so the agent still runs on sonnet. This is the reason D2 chose an explicit pin over removing the line.
- **No explicit path given.** The Working Directory section's step 1 falls through to "operate in the current working directory" — identical to today's implicit behavior, but now it is stated rather than assumed, and step 2's verification still runs.
- **`git -C` vs. `cd`.** The section permits both. `git -C <path>` is preferred for one-off commands; `cd` is acceptable when running several git commands in sequence. Either way, step 2's verification must happen first.
- **Staged changes already exist in a sibling/shared checkout.** The agent commits in the directory it was *told* to use, even if another checkout has staged changes. It does not "helpfully" pick up the other checkout's state.
- **Pre-commit hooks that reformat files.** Out of scope for the paraphrasing rule — hook-driven reformatting is the hook's job, not the agent authoring content. The existing escalation bullet (`Pre-commit hooks fail and block commit`) still covers the failure case.

## Risks & Open Questions

- **Cost / latency.** `sonnet` is slower and more expensive per invocation than `haiku`, and commit-creator runs frequently. The task is short and bounded (a handful of `git` calls plus message authoring), so the per-invocation delta is small and the reliability gain is worth it given the cost asymmetry described in Problem. No quantified benchmark is included; if invocation cost becomes a concern, revisit with measurement rather than assumption.
- **Scope deferral (resolved, tracked).** D1 deferred `branch-creator` / `test-runner` / `pr-manager`. This is a deliberate non-goal, not an oversight. If those agents later show haiku-class failures, open a separate spec — do not retrofit this one.
- **Instruction fix is commit-creator-only.** `branch-creator` and `pr-manager` also run git and could in principle hit a wrong-cwd failure. Per D1 this spec does not touch them. If the pattern recurs there, the `## Working Directory` section is written to be portable and could be lifted into those definitions (or a shared include) in a future change.
- **Cross-reference.** The underlying incidents are recorded in the wellstead project's auto-memory: `commit_creator_linear_refs.md`, `commit_creator_coauthor_trailer.md`, `commit_creator_wrong_cwd_paraphrase.md`. PR #56 in this repo addressed failure mode 1. Failure mode 2 (inconsistent `Co-Authored-By` trailer) is **not** addressed by this spec — it is a separate instruction/global-rule-conflict issue and warrants its own follow-up.

## Execution Plan

1. Branch: `feat/commit-creator-model-bump`.
2. Edit `plugins/dev-workflow/agents/commit-creator.md` — frontmatter model line, new `## Working Directory` section, two reinforcement bullets (Changes 1–3).
3. Bump `plugins/dev-workflow/.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` to `1.3.5`.
4. Validate: JSON files parse; agent frontmatter is valid YAML; new section reads cleanly in context.
5. Commit (conventional format, e.g. `feat(commit-creator): bump model to sonnet and add working-directory discipline`), open PR, watch checks.
```
