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
| `session-export` | Export Claude Code session transcripts from JSONL logs to readable text format |
| `self-documentation` | Explain Claude Code features, capabilities, and tools; record observations about undocumented behaviors |

### pm-workflow

Product management workflow skills for writing PRDs and product one-pagers.

**Skills included:**

| Skill | Description |
|-------|-------------|
| `prd-writing` | Interview users to transform rough product ideas into comprehensive one-pagers for product kick-offs |

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
- Ask to export a session transcript
- Report discovering undocumented behavior

**pm-workflow:**
- Ask to write a PRD or product brief
- Ask to create a one-pager or kick-off doc
- Ask to define product requirements

## Updating

```bash
/plugin update dev-workflow@ddehart-plugins
/plugin update meta-claude@ddehart-plugins
/plugin update pm-workflow@ddehart-plugins
```

## Naming Conventions

**Skills** use action-oriented names that pass the "adept at" test:
- Ask: "Would you say someone is adept at ___?"
- Examples: `spec-writing`, `self-documentation`, `session-export`
- Pattern: Noun-gerund or compound action words representing a craft/expertise

**Agents** use role-oriented names describing their function:
- Examples: `test-runner`, `branch-creator`, `pr-manager`, `chrome-verifier`
- Pattern: Noun-noun compounds representing a specialized role

This distinction reflects their nature: skills teach expertise (something you're "adept at"), while agents perform tasks (roles that "run" or "manage" things).
