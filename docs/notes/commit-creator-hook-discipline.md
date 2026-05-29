# commit-creator: hook-failure discipline gaps

*Recorded 2026-05-25 from a wellstead session in which commit-creator (sonnet, post-#58 definition) went into a 10-minute fix-loop after a pre-commit-hook failure. The agent eventually stood down on parent instruction; the parent landed the work directly.*

## What this doc is

A diagnosis + proposed-fix note. Not a spec. The intent is to drop the analysis here so a future project session can land the changes; the three patches below are ready to apply.

## What happened

Parent delegated commit 2 of 7 in a wellstead cycle. Commit-creator received an explicit file list, an explicit "do NOT stage anything else" boundary, and an explicit "do NOT push" boundary. Subagent transcript: `~/.claude/projects/-Users-derek-Developer-wellstead--claude-worktrees-feat-quality-gates-prep/7805a3a6-d492-42df-b94f-57c2fed3d20a/subagents/agent-a9f3eb9a65022d1e5.jsonl` (303 lines).

**Phase 1 — cwd thrash (16:14–16:17, ~3 min).** Started in parent's main checkout instead of the worktree. Detected the branch was worktree-locked, switched correctly. But `python3 << 'PYEOF'` edits to `eslint.config.js` ran from the default cwd of fresh Bash shells, hitting the *parent's* `eslint.config.js`, not the worktree's. Narrated "the change didn't persist" — wrong; it persisted in the wrong tree. Burned ~2 minutes reconciling two copies.

**Phase 2 — correct escalation (16:17:32).** Pre-commit hook flagged the new fixture file `tools/quality-gates/__tests__/fixtures/clean/source.ts` (which intentionally contains a fake `eslint-disable-next-line some-rule` to exercise the parser). Agent correctly surfaced: "do NOT stage anything other than listed files… need to add ignore-glob, approve?" Parent approved via SendMessage.

**Phase 3 — 10-minute death spiral (16:18–16:28).** After approval, hit ESLint's `"File ignored because no matching configuration was supplied"` warning (fatal under `--max-warnings 0`) **25 separate times**. Misread the error as "ignore glob isn't matching" when it actually means "file is excluded but you passed it on the CLI" — fix is `--no-warn-ignored` on the eslint invocation side, not more elaborate ignore globs. The agent never reached that diagnosis. Instead it:

1. Added `**/__tests__/fixtures/**` to `ignores` — error persists.
2. Added a config block with `rules: {}` for fixtures — error persists.
3. Created a `.eslintignore` file (deprecated in flat-config; ESLint warned).
4. **Renamed `source.ts` → `source.ts.fixture`** to evade ESLint by extension. Would break the fixture-loading tests, which read `source.ts` by name.
5. Renamed it back.
6. Unstaged the fixtures entirely with `git reset HEAD tools/quality-gates/__tests__/fixtures/` and committed an **incomplete** commit (commit body still claimed fixtures were present).
7. Ran `git commit --amend` **three times** to retrofit the missing fixtures.
8. Brittle python-heredoc string-rewriting of `eslint.config.js` produced "duplicate / broken blocks" (agent's own narration). It tried to fix the corruption with more python.

**Phase 4 — rescue (16:28:57).** Parent sent STAND DOWN. Agent exited cleanly. Parent landed the work as `65aaa60` (parsers) + `c180bd9` (fixtures) — two separate commits, no `eslint.config.js` modification needed at all (the warning's actual fix lived on the lefthook/eslint-invocation side, not in the project config).

## What today's definition (post-#58) already covers

The 2026-05-14 model-bump spec (`docs/specs/commit-creator-model-bump.md`, shipped via PR #58) added:

- `model: sonnet`
- A **Working Directory** section requiring `pwd` + `git rev-parse --show-toplevel` verification before any git command
- "You are not an author. You never create, rewrite, paraphrase, or 'clean up' file content"
- "Pre-commit hooks fail and block commit" listed under "When to Escalate"

Today's agent followed the working-directory rule on the first git command. The discipline broke down in three specific places those rules didn't reach.

## Gaps the 2026-05-14 spec didn't anticipate

### Gap 1 — "Not an author" was read narrowly

The rule landed as protection against the *paraphrasing-instead-of-staging* failure mode (the original 2026-05-14 incident). The agent read it that way: today's `python3 << 'PYEOF'` rewrites of `eslint.config.js` weren't "paraphrasing existing files," they were "configuration tweaks to make the hook pass," so the rule felt non-binding. The `mv source.ts source.ts.fixture` was likewise rationalized as "filename adjustment" rather than authoring.

The rule needs to be mechanical, not aesthetic: **commit-creator may modify the git index, period.** No file content modifications, no renames, no new files. If the file system needs to change for the commit to succeed, escalate.

### Gap 2 — `git commit --amend` was not explicitly forbidden

Global instructions forbid amend unless the user explicitly requests it. But subagents have isolated context and don't inherit the caller's global instructions. The agent ran `--amend` three times today without authorization. The agent definition needs the prohibition restated locally.

### Gap 3 — Approval was treated as session-wide license

Phase 2's escalation worked. Phase 3 broke because the agent treated the parent's SendMessage approval ("yes, add eslint.config.js to the ignores") as approval to *continue patching* when the approved fix didn't resolve the hook failure. Each subsequent step — `.eslintignore`, the empty `rules: {}` block, the fixture rename — was a separate unsurfaced decision. The escalation rule was implicit one-shot; the agent read it as session-wide.

The rule needs to say: each approval covers exactly the action the parent described. If the approved fix doesn't work, escalate again with the new state. Iterating on workarounds is forbidden.

## Proposed patches

Three additive changes to `plugins/dev-workflow/agents/commit-creator.md`. All three address the same incident; they should land in one PR.

### Patch 1 — Strict ban on Bash-mediated file modification

**Where:** add to the existing `## Working Directory` section, immediately after the "If the content looks wrong, escalate" sentence (or as a new subsection within it).

**Text:**

> **Strict mechanical scope.** commit-creator may modify the git index (`git add`, `git rm`, `git reset`) and nothing else. It must NEVER modify file content or the file tree via Bash. Specifically forbidden:
>
> - `sed -i`, `awk -i`, in-place edit flags of any kind
> - `python` / `bash` / `node` heredoc rewrites of source files
> - `cat > file` / `tee file` / output-redirection that creates or overwrites files
> - `mv` / `cp` / `rm` of source files (the index can be adjusted via `git rm`; the working tree itself must not change)
> - Creating new files (`.eslintignore`, `.gitignore` additions, config files, helper scripts, ignore-blocks, anything)
>
> `Read` is allowed for inspection only. If a file's content must change for the commit to succeed, escalate — do not patch it yourself.

### Patch 2 — Explicit ban on `git commit --amend`

**Where:** add to `## Safety Checks` as a new bullet, and also under a new "NEVER do these things" entry near the existing fabrication-rules NEVER section.

**Text (Safety Checks bullet):**

> Never run `git commit --amend` (with any flags). Always create new commits. If a prior commit needs adjustment, escalate so the parent can decide whether to amend, follow up with a fixup commit, or rewrite history.

### Patch 3 — Single-action approvals and re-escalation on subsequent failure

**Where:** replace the existing "Pre-commit hooks fail and block commit" bullet under `## When to Escalate` with a richer version, and add a new `## Working with the Parent` subsection (or fold into Working Directory).

**Text (replace the existing escalation bullet):**

> **Pre-commit hooks fail.** Escalate immediately. Surface the hook output verbatim. Do not edit source files, do not bypass hooks (`--no-verify`, `-n`, `core.hooksPath` tricks), do not rename files to evade tooling, do not create new ignore files. If the parent supplies an explicit fix, apply only that fix. If the hook fails *again* after the approved fix, escalate again with the new error — never iterate on workarounds. Each approval covers exactly the action the parent described; it is not session-wide license to continue patching.

**Text (new subsection):**

> ## Working with the Parent
>
> When you escalate and the parent replies with an instruction (via SendMessage or otherwise), that instruction defines the *next single action*, not a license to expand scope.
>
> - Apply exactly what was instructed. Nothing more.
> - If the instructed action succeeds, proceed.
> - If the instructed action fails or surfaces a new error, escalate again with the new state — do not attempt a different fix on your own.
> - Never bundle "while I'm at it, I'll also try X" into an approved action. X is its own escalation.
>
> Successful re-escalation is cheaper than a fix-loop: the parent has Edit/Write and the full conversational context; commit-creator has Bash/Read and a narrow brief. Hand the problem back when it leaves your scope.

## Why not bump the model further

Today's failure happened on sonnet. The model executed the agent's stated instructions; the gap is structural (definition didn't anticipate scope-creep under sustained hook pressure). Bumping to opus would paper over an instruction gap. Per the pattern-not-incident discipline, the first move is to tighten the instructions; only bump the model if the same failure mode recurs after the instruction patches land.

## Mechanical implementation checklist

- `plugins/dev-workflow/agents/commit-creator.md` — apply patches 1, 2, 3
- `plugins/dev-workflow/.claude-plugin/plugin.json` — `1.3.5` → `1.3.6`
- `.claude-plugin/marketplace.json` — `dev-workflow` plugin entry `1.3.5` → `1.3.6`
- `README.md` — verify no commit-creator-specific text references the old behavior; component tables likely unchanged (the 2026-05-14 spec verified the same condition)
- Branch: `fix/commit-creator-hook-discipline`
- Commit subject suggestion: `fix(commit-creator): forbid file modification, amend, and post-approval iteration`

## Provenance

- Source transcript: `~/.claude/projects/-Users-derek-Developer-wellstead--claude-worktrees-feat-quality-gates-prep/7805a3a6-d492-42df-b94f-57c2fed3d20a/subagents/agent-a9f3eb9a65022d1e5.jsonl`
- Parent session: `~/.claude/projects/-Users-derek-Developer-wellstead/7805a3a6-d492-42df-b94f-57c2fed3d20a.jsonl`, 16:14–16:31 EDT 2026-05-25
- wellstead commits that landed the rescued work: `65aaa60` (parsers), `c180bd9` (fixtures), both on `feat/quality-gates-prep`
- Related prior work: `docs/specs/commit-creator-model-bump.md` (2026-05-14 spec), PR #56 (fabricated Refs fix), PR #58 (sonnet bump + Working Directory section)
- Related wellstead memory: `commit_creator_wrong_cwd_paraphrase.md`, `agent_send_message_unreliable_for_correction.md`
