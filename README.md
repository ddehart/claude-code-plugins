# Claude Code Plugins

Personal Claude Code plugin marketplace with reusable dev workflow agents.

## Installation

```bash
# Add the marketplace (once per machine)
/plugin marketplace add ddehart/claude-code-plugins

# Install the dev-workflow plugin
/plugin install dev-workflow@ddehart-plugins
```

## Available Plugins

### dev-workflow

Dev workflow agents and skills for test running, branch creation, conventional commits, pull request management, Linear issue management, browser verification, and spec writing.

**Agents included:**

| Agent | Description |
|-------|-------------|
| `test-runner` | Execute test suites (unit, E2E, or all) and analyze results |
| `branch-creator` | Create properly named Git branches following conventions |
| `commit-creator` | Create commits following Conventional Commits standard |
| `pr-manager` | Manage pull request workflows (create, monitor checks, review feedback, merge) |
| `linear-issues` | Manage Linear issues (create, update, view, search, status transitions) |
| `chrome-verifier` | Verify deployed features via browser automation, returning concise summaries |

**Skills included:**

| Skill | Description |
|-------|-------------|
| `spec-writing` | Interview users to refine rough ideas into comprehensive, implementation-ready specifications |

### meta-claude

Claude Code productivity skills for session management, self-documentation, and self-reflection.

**Skills included:**

| Skill | Description |
|-------|-------------|
| `session-chronicle` | Two-layered session journal: functional chronicle (decisions, learnings, failed approaches) and open-ended reflection on functional states. Auto-triggers deep practice review after 10+ entries without evolution. Manual `/session-chronicle reflect` now reviews all entries since last evolution (capped at 20). |
| `session-export` | Export Claude Code session transcripts from JSONL logs to readable text format |
| `self-documentation` | Explain Claude Code features, capabilities, and tools; record observations about undocumented behaviors |

### pm-workflow

Product management workflow skills for writing and evaluating PRDs and product one-pagers.

**Skills included:**

| Skill | Description |
|-------|-------------|
| `prd-writing` | Interview users to transform rough product ideas into comprehensive one-pagers for product kick-offs |
| `prd-evaluation` | Evaluate PRDs from a product leader's perspective, surfacing gaps in reasoning and unstated assumptions |

### knowledge-commons

Generator for per-project knowledge graphs with cross-domain promotion. Scaffolds a graph (atlas, maps, type directories), a ledgered `/process` pipeline, and project-owned skills from a config-driven interview; portable claims promote into a personal commons, and steering-grade principles graduate into always-loaded rules. No validators or enforcement machinery — plan approval is the gate.

**Skills included:**

| Skill | Description |
|-------|-------------|
| `graph-init` | Interview → `.commons.yml` + graph scaffold + generated project-owned `process` and `knowledge-graph` skills; `--config-only` wires an existing hand-built graph into promotion |
| `promote` | Derive a portable claim into a target graph (or a rule into the instruction tier) with association against the target's maps and per-promotion approval |

## Usage

Once installed, the agents and skills are automatically available. Claude will proactively use them when you:

**dev-workflow:**
- Ask to run tests
- Ask to create a branch
- Ask to commit changes
- Ask to create, monitor, or merge pull requests
- Ask to manage Linear issues
- Ask to verify a deployment or check a live site
- Ask to write, create, or refine a spec

**meta-claude:**
- Ask about Claude Code features ("How do skills work?", "What can you do?")
- Ask decision questions ("Should I use a skill or slash command?")
- Ask to chronicle a session, write a journal entry, or reflect on what was accomplished
- Ask to export a session transcript
- Report discovering undocumented behavior

**pm-workflow:**
- Ask to write a PRD or product brief
- Ask to create a one-pager or kick-off doc
- Ask to define product requirements
- Ask to evaluate, review, or critique a PRD

## Updating

```bash
/plugin update dev-workflow@ddehart-plugins
/plugin update meta-claude@ddehart-plugins
/plugin update pm-workflow@ddehart-plugins
/plugin update knowledge-commons@ddehart-plugins
```

## Naming Conventions

**Skills** use specific, intention-revealing names:
- Ask: "Reading this name in a `/` menu, would I know what it does?"
- Examples: `spec-writing`, `self-documentation`, `session-export`, `graph-init`, `promote`
- Gerunds read well and are common here, but they're a house preference, not a requirement — a
  skill's slash command comes from its directory name and auto-invocation is driven by its
  `description`, so the name's real job is menu discoverability. Plugin namespacing
  (`knowledge-commons:promote`) supplies disambiguation for otherwise-generic names.

**Agents** use role-oriented names describing their function:
- Examples: `test-runner`, `branch-creator`, `pr-manager`, `chrome-verifier`
- Pattern: Noun-noun compounds representing a specialized role

This distinction reflects their nature: skills teach expertise (something you're "adept at"), while agents perform tasks (roles that "run" or "manage" things).
