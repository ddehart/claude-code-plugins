# Spec: how generated skills reference plugin files

**Status:** Approved 2026-11-08 (two helper skills, chosen over the marketplace-clone path); implemented on `feat/kc-plugin-references`
**Date:** 2026-11-08
**Plugin:** `knowledge-commons` v0.8.2 → v0.9.0
**Related:** [`knowledge-commons-patch-mechanism.md`](./knowledge-commons-patch-mechanism.md) (deltas,
D8 fields, D23 anchors) · [`knowledge-commons-process-pipeline.md`](./knowledge-commons-process-pipeline.md)
("Where the floor scan lives", which this spec supersedes)

## Problem

`graph-init` writes two project-owned skills, `process` and `knowledge-graph`. Both need two files that
belong to the plugin, not the project:

- `references/graph-conventions.md`, the full structural contract. The `knowledge-graph` template cites it
  in `## Conventions` (`{resolved-conventions-path}`); the `process` template cites it by name in
  `## 3. Preserve` (inline-form sources carry material "as `graph-conventions.md` describes").
- `scripts/scan-secrets.sh`, the deterministic floor of the redaction gate, in `## 3. Preserve`
  (`{scan-secrets-path}`), generated only when a source tier's `gate:` is `public` or `shared`.

`graph-init` §6 tells the generator to "stamp the resolved concrete path" for both, because a skill in a
project gets no `${CLAUDE_PLUGIN_ROOT}` substitution. The stamped path is absolute and names one version
on one machine's install layout, e.g.
`/home/derek/.claude/plugins/cache/ddehart-plugins/knowledge-commons/0.6.0/references/graph-conventions.md`.
It rots three ways: the plugin updates and the old cache is pruned; the graph is generated on another
machine (`/Users/derek-personal/...`); or the graph is generated inside a Remote Control session, whose
plugins live under `~/.claude/remote/plugins/<hash>/`.

**The structural condition:** the generator converts a reference that only the plugin can resolve into a
literal resolved at one moment, then hands it to a file that outlives that moment and is never
regenerated. Every per-graph fix so far patched the literal (devbox now runs an `ls … | sort -V` glob,
wellstead a `find`, the commons a GitHub repo path), which moves the rot rather than removing it: the
globs assume one install layout, and the repo path isn't readable from a session.

### Measured on devbox, 2026-11-08

Installed caches: 0.6.0, 0.7.0, 0.8.0, 0.8.1, 0.8.2.

| Graph | Stamped reference | Resolves? |
|---|---|---|
| airbnb-prep, daily-briefing | `…/knowledge-commons/0.5.0/…` (knowledge-graph) | **No** |
| claude-code-plugins | `/Users/derek-personal/…/0.1.7/…` (knowledge-graph) | **No** |
| osu-builder-in-residence | `/Users/derek-personal/…/0.1.8/…` (knowledge-graph) | **No** |
| log-archaeologist, service-health-monitor | `~/.claude/remote/plugins/55abd92600149991/…` (knowledge-graph) | **No** |
| daily-digest, email-triggers, financial-planning | `…/0.6.0/…` (knowledge-graph) | Yes, while 0.6.0 survives |
| claude-usage, persimmon-care | `…/0.6.0/…` (knowledge-graph **and** process `## 3. Preserve`) | Yes, while 0.6.0 survives |
| devbox | `ls` glob over the cache (hand-fixed) | Yes on this layout only |
| wellstead | `find ~/.claude/plugins …` (hand-fixed) | Yes on this layout only |
| commons | GitHub repo path (hand-fixed) | Not readable from a session |

No live graph stamps a `scan-secrets.sh` install path. The one gated graph (this repo) runs the script by
its repo-relative source path, which is a project path and is stable here because this repo *is* the
plugin's source. The template would still stamp an install path into the next gated graph.

## Phase 0: primary research (2026-11-08)

Run on Claude Code 2.1.319 against a throwaway probe plugin loaded with `--plugin-dir` and a scratch
project, using `claude -p --model haiku`. The question was the simplest mechanism that actually works.

| # | Probe | Result |
|---|---|---|
| E1 | `${CLAUDE_PLUGIN_ROOT}` in a **project** skill | **Not substituted**: arrives as the literal `${CLAUDE_PLUGIN_ROOT}`. (`${CLAUDE_SKILL_DIR}` is substituted, but names the project skill's own dir.) A generated skill can't carry a self-resolving plugin path. |
| E2 | `${CLAUDE_PLUGIN_ROOT}` in a **plugin** skill, then Read | Substituted to the loaded plugin's directory; the file read correctly. |
| E3 | Plugin skill with `allowed-tools: ["Bash(${CLAUDE_PLUGIN_ROOT}/…/scan.sh *)"]`, body `… scan.sh $ARGUMENTS`, invoked with args, **no** `--allowedTools` | Ran without a permission prompt. Clean file → exit 0. Planted `ghp_` token → exit 1, finding reported verbatim. |
| E4 | `bin/` executable | On the Bash tool's `PATH`; runs as a bare command. |
| E5 | Discovery at runtime (`claude plugin list --json`, `~/.claude/plugins/installed_plugins.json`) | Not usable: both list **13** knowledge-commons installs at 0.6.0, 0.7.0, and 0.8.2 (project-scoped per project and per worktree), with no filter for "the one this session loaded." Remote Control sessions use `~/.claude/remote/plugins/<hash>/`, and the hash two graphs stamped no longer exists. |
| E6 | `bin/` on claude.ai | Org-sync docs: claude.ai **rejects** a plugin with a top-level `bin/` and says to "keep executables in another directory, such as `scripts/`, and reference them as `${CLAUDE_PLUGIN_ROOT}/scripts/<name>` from your skills." |
| E7 | How often generated skills read the full conventions file (all session transcripts on devbox) | Rarely, and almost only during maintenance. Outside this repo: devbox 11, daily-digest 2 (both inside the graph-init run), financial-planning 1 and log-archaeologist 1 (plugin troubleshooting), service-health-monitor 1. The restatement in the generated skill carries day-to-day work, as designed. |

**What this settles.** E1 and E5 rule out every fix that keeps a path or a lookup in the generated skill.
E2 and E3 confirm the plugin-skill route works, including the gate's exit-code semantics and no-prompt
execution. E4 works but E6 makes it cost claude.ai compatibility, and Anthropic's docs name the
plugin-skill pattern as the alternative to `bin/`. E7 shows the conventions resolver is rarely exercised,
so it should be as small as possible, but it is still needed for the rare read and for the process
stage's citation.

## Prior art (web research, 2026-11-08)

This is a known problem with no platform fix.

- **The exact request was filed and closed unanswered.** anthropics/claude-code#82068 (2026-07-28) asks
  for "a stable path to a plugin's installed version (or @import variable expansion)" because installs
  land at `cache/<marketplace>/<plugin>/<version>/`, old versions are retained, and `${CLAUDE_PLUGIN_ROOT}`
  exists only inside plugin contexts: "A static import pinned to `.../0.2.4/CLAUDE.md` goes silently stale
  on the next bump." Auto-closed for inactivity, no maintainer reply.
- **The same rot shows up across the issue tracker:** stale versioned paths written into `settings.json`
  (#17789, #18517), absolute install paths breaking across machines (#29671), and `${CLAUDE_PLUGIN_ROOT}`
  itself going stale in running sessions after an update prunes the old cache (#46915, #39328, #15642).
- **Workarounds people use:**
  - **The unversioned marketplace clone**, `~/.claude/plugins/marketplaces/<marketplace>/…` (#82068's
    reporter). It exists on devbox (`ddehart-plugins`, at `affcfce`). It's simple, but it's still a path in
    a generated file, it depends on the marketplace's local name, and it tracks the marketplace's latest
    commit rather than the version installed for this project.
  - **A SessionStart hook that maintains a `current` symlink.** #82068's reporter rejected this: a
    disabled plugin or skipped hook leaves a dangling link and the content silently vanishes.
  - **Copying a launcher to a fixed location outside the cache** (a third-party "coach" plugin). This
    freezes the copy.
- **Consistent guidance, official and community:** reference plugin files only from inside plugin
  components via `${CLAUDE_PLUGIN_ROOT}`, and have anything outside the plugin point at the plugin's
  **skill by name**. Anthropic's org-sync page says the same for executables ("reference them as
  `${CLAUDE_PLUGIN_ROOT}/scripts/<name>` from your skills"). The general practice for scaffolders that
  emit user-owned files is the same: refer to generator assets by a logical name the runtime resolves,
  and record the generator version (which `generated:` already does).

## Decisions

**P1. A generated skill never contains a filesystem path into a plugin installation** — not a literal,
not a glob, not a discovery command. Plugin-owned files are reached through **plugin skills**, which
Claude Code loads with `${CLAUDE_PLUGIN_ROOT}` substituted to the currently installed version on the
current machine (documented: skills docs, "In a plugin skill, Claude Code substitutes
`${CLAUDE_PLUGIN_ROOT}` … in the skill's markdown content, and Bash rules in the `allowed-tools`
frontmatter"). The generated skill names the plugin skill; the plugin resolves the path at the moment
it's used. This is the same idiom the templates already use for `/graph-patch` and `promote`
(name the skill, never the path).

*Why skills and not inlining:* inlining the full conventions would freeze a copy that diverges silently
from the plugin's (the same rot in content form), and an executable can't be inlined at all.

**P2. New plugin skill `knowledge-commons:conventions`.** `user-invocable: false` (a helper, not a
slash command; Claude can still invoke it). Its body instructs: read
`${CLAUDE_PLUGIN_ROOT}/references/graph-conventions.md` in full and treat it as the authoritative
contract. Description scoped so it triggers on an explicit invocation from a generated skill or a direct
question about the full graph conventions, not on everyday captures.

**P3. New plugin skill `knowledge-commons:scan-secrets`.** `user-invocable: false`. Takes the rendered
file path(s) as arguments. `allowed-tools: ["Bash(${CLAUDE_PLUGIN_ROOT}/scripts/scan-secrets.sh *)"]`,
so it runs without a permission prompt. Its body: run exactly
`${CLAUDE_PLUGIN_ROOT}/scripts/scan-secrets.sh $ARGUMENTS`, report the exit code and stdout verbatim,
and state that any non-zero exit means *do not archive*. It never judges a hit, never retries with
different arguments, never summarizes a non-zero run as clean. The gate's fail-closed property carries
over unchanged, and gains a case: **if the skill is unavailable** (plugin disabled or uninstalled), the
scan did not run, which is a stop.

*Rejected: a `bin/` executable on PATH.* Documented and simpler to call (`kc-scan-secrets <file>`), but
the plugins reference says claude.ai and Cowork **don't install a plugin that has a `bin/` directory**.
That trades the whole plugin's availability on those surfaces for one helper. The skill wrapper works
everywhere the plugin does. Revisit if a second executable appears.

*Rejected: copying the script into the project at generation time.* Stable, but freezes the scanner,
and scanner improvements have no delta channel (deltas carry prose, not files).

**P4. `graph-init` §6 stops stamping.** Delete both "stamp the resolved concrete path" bullets. State P1
once, in graph-init's skill-wide `## Never` list rather than as a §6 bullet, so it also covers SLOT prose
and the hand-added tail config-only mode suggests. The same one-line rule goes in `/graph-patch` §4c and
the delta log's preamble, since `/graph-patch` now writes prose into every existing graph and has a
resolved plugin path in context while it does.
`graph-init` itself keeps using `${CLAUDE_PLUGIN_ROOT}` for its own reads (it is a plugin skill).

**P5. Template edits.**
- `knowledge-graph.md` `## Conventions`: replace `{resolved-conventions-path}` with: the full contract is
  the plugin's graph conventions, loaded with the `knowledge-commons:conventions` skill when a question
  isn't answered by the restatement here.
- `process.md` `## 3. Preserve`: the inline-form bullet cites "the plugin's graph conventions (load them
  with `knowledge-commons:conventions`)"; the redaction-gate floor becomes "invoke the
  `knowledge-commons:scan-secrets` skill on the rendered material"; the SLOT comment drops "the resolved
  path to the plugin's scripts/scan-secrets.sh"; and the fail-closed paragraph adds "or the skill is
  unavailable."
- `process.md` `## 12. Report`: drop the clause "any plugin path written into this file was resolved at
  generation time and names a version that has since moved on", which files generated from 0.9.0 make
  false. The instruction (don't read the delta log; suggest `/graph-patch`) is unchanged, so this needs no
  delta under the template-deltas rule's no-behavior-change exception.
- Generated text names the helper skills and doesn't explain why paths rot: that reasoning would load on
  every run of a skill that has no path to misuse. The explanation lives here, in graph-init's `## Never`
  rule, and in the delta rationales.

**P6. Two deltas, version 0.9.0.**

| id | file | anchor | satisfied-test (substance) |
|---|---|---|---|
| `kg-conventions-by-skill` | knowledge-graph | `## Conventions` | The section contains no filesystem path, literal or glob or discovery command, into a plugin installation, **and** names the `knowledge-commons:conventions` skill as how to load the full contract. |
| `preserve-plugin-files-by-skill` | process | `["## 3. Preserve", "## 2. Resolve"]`, a fallback list (P9) | The preserve stage contains no filesystem path into a plugin installation, **and** every reference it makes to the plugin's conventions goes through `knowledge-commons:conventions`, **and** a redaction gate's floor scan goes through `knowledge-commons:scan-secrets` (treating the skill being unavailable as a stop). A conventions citation by **bare filename**, with no way to load it, **fails**. A repo-relative path to the scanner's *source* in the plugin's own repo (this repo) is not an install path and passes. A stage that cites neither file, or no preserve stage at all, passes. |

"Plugin installation" in both tests means any directory Claude Code installs plugins into
(`~/.claude/plugins/cache/…`, `~/.claude/plugins/marketplaces/…`, `~/.claude/remote/plugins/…`, or a
macOS/other-home equivalent), versioned or not. The hand-fixed globs in devbox and wellstead and the
commons' repo path **fail** the knowledge-graph test on purpose, so every graph converges on one form.

**P9. A delta's `anchor` may be an ordered fallback list** (found during implementation, corrected in
review). The preserve stage sits in different places across live graphs. Counted 2026-11-08 across the 14
graphs, all of which have one:

| Shape | Graphs |
|---|---|
| Its own `## 3. Preserve` | persimmon-care, email-triggers, log-archaeologist, daily-digest, financial-planning, claude-usage, service-health-monitor |
| Its own stage, other numbering: `## 2a.` / `## 2b.` / unnumbered | wellstead, osu-builder-in-residence (`2a`); devbox, obsidian (`2b`); daily-briefing (none) |
| `### Preserve` subsection inside `## 2. Resolve` | claude-code-plugins |
| `### Preserve` subsection inside `## 3. Find the ledger` | airbnb-prep |

`deltas.md` told authors to anchor preserve deltas on `## 2. Resolve`, but `/graph-patch` judges only the
anchored section, so a Resolve anchor would see none of the stage in the twelve own-section graphs and
report them **falsely satisfied**. Two fixes were wrong. Anchoring on `## 3. Preserve` alone skips
loudly, and stays unstamped forever, wherever the stage is a subsection. A `scope: next-section` field (a
first draft) reached the stage by position, and in devbox and obsidian the section after Resolve is a
different inserted stage (`## 2a. Session inputs`, `## 2a. A company or product`); in devbox that section
holds the out-of-scope meta-claude cache glob, which the delta would have been told to remove.

The fix keys on the stage's name:
- **`anchor` may be a list**, tried in order; the first entry that matches exactly one heading wins, an
  ambiguous entry skips loudly, and none matching is *not found* (`/graph-patch` §4a, `deltas.md` field
  table, template-deltas rule). This one delta uses `["## 3. Preserve", "## 2. Resolve"]`.
- **D23's title matching also drops `2a.`-style numbers, and handles unnumbered headings**, so the first
  entry resolves in all twelve own-section graphs. claude-code-plugins falls back to Resolve and finds its
  subsection there. airbnb-prep falls back to Resolve, which doesn't contain its subsection; it cites
  neither file, so "satisfied" is the correct result there, and the delta's rationale says so.

D23 rejected a list of exact headings, one per numbering, because every author would have to enumerate
numberings. This list is different: its entries are titles, still number-blind, and it lists places a
stage lives, which only a delta aimed at a moved stage needs. `/graph-patch` is a plugin skill, so the
matching change reaches every graph on plugin update with no delta.

**P7. Version 0.9.0 (minor).** Two new skills are new capability, per `plugin-updates.md`, though the
motivating change is a fix. Bump `plugin.json` and `marketplace.json` together; README skill table gains
the two helpers.

**P8. Design history.** Add a dated blockquote under the process-pipeline spec's "Where the floor scan
lives" paragraph pointing here; leave its text unchanged. Note in `deltas.md` nothing beyond the two
entries (the `step10-pending-patches` rationale already documents the hazard and stays as written).

## Out of scope

- Editing any downstream graph. `/graph-patch` does that per graph, with approval.
- devbox's `process` skill locates **meta-claude**'s `export-session.py` with a cache glob. Same hazard,
  different plugin, hand-written rather than templated. Listed as a follow-up, not fixed here.
- `${CLAUDE_PLUGIN_ROOT}` uses inside knowledge-commons' own skills: correct as-is.

## Verification (before the PR is marked ready)

1. `grep -n 'resolved-conventions-path\|scan-secrets-path\|stamp the resolved'` over `graph-init/SKILL.md`
   and both templates returns nothing, and no template contains `plugins/cache`. (`process.md`'s Report
   step mentions `${CLAUDE_PLUGIN_ROOT}` only to say generated skills don't have it.)
2. Load the branch's plugin into a real session in a scratch project
   (`claude --plugin-dir plugins/knowledge-commons -p …`) and invoke:
   - `knowledge-commons:conventions` → it reads the file from the branch path (confirms substitution).
   - `knowledge-commons:scan-secrets` on a clean file → exit 0, and on a file with a planted
     `ghp_`-shaped token → exit 1 reported verbatim (confirms `$ARGUMENTS` and the `allowed-tools` rule,
     and the failure path).
3. Dry-read each delta's `satisfied-test` against the new template section (must pass) and against a
   live graph that still carries a stamped path (must fail), so the test discriminates in both
   directions: `projects/airbnb-prep`'s `knowledge-graph` skill for `kg-conventions-by-skill`, and
   `projects/claude-usage`'s `process` skill for `preserve-plugin-files-by-skill`. (airbnb-prep's
   `process` skill cites neither file, so it passes the process test.)

## Graphs to patch afterward (`/graph-patch`)

- `kg-conventions-by-skill`: commons, devbox, wellstead, osu-builder-in-residence, claude-code-plugins,
  persimmon-care, email-triggers, log-archaeologist, daily-digest, financial-planning, claude-usage,
  daily-briefing, airbnb-prep, service-health-monitor. (obsidian has no `knowledge-graph` skill.)
- `preserve-plugin-files-by-skill`: real edits expected in **6** graphs: claude-usage and persimmon-care
  (a stamped 0.6.0 path), and email-triggers, log-archaeologist, daily-digest, and service-health-monitor
  (cite the conventions by bare filename, which fails the test). Every other graph with a `process`
  skill (devbox, obsidian, wellstead, osu-builder-in-residence, claude-code-plugins, financial-planning,
  daily-briefing, airbnb-prep) should report *already satisfied* and stamp.
