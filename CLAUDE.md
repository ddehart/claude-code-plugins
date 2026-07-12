# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Claude Code plugin marketplace containing reusable dev workflow agents. The repository distributes plugins that Claude Code can install and use proactively during development sessions.

## Architecture

```
.claude-plugin/marketplace.json     # Marketplace definition (name, owner, plugin list)
plugins/
  dev-workflow/
    .claude-plugin/plugin.json      # Plugin metadata (name, version, keywords)
    agents/
      test-runner.md                # Test execution agent
      branch-creator.md             # Git branch creation agent
      commit-creator.md             # Conventional commits agent
      pr-manager.md                 # Pull request workflow manager
  meta-claude/
    .claude-plugin/plugin.json      # Plugin metadata
    skills/
      session-export/
        SKILL.md                    # Session export skill definition
        scripts/
          export-session.py         # Python export utility
```

**Key concepts:**
- Marketplace definition at root level registers this repo as a plugin source
- Each plugin has its own `.claude-plugin/plugin.json` with metadata
- **Agents** are Markdown files in `agents/` with YAML frontmatter (name, description, tools, model)
- **Skills** are Markdown files in `skills/<skill-name>/SKILL.md` with YAML frontmatter (name, description, allowed-tools)

## Agent Definition Format

Agents use YAML frontmatter followed by Markdown instructions:

```yaml
---
name: agent-name
description: PROACTIVELY... (triggers for when Claude should use this agent)
tools: Bash, Read, etc.
model: haiku
---

# Agent instructions in Markdown
```

The `description` field is critical - it tells Claude when to proactively invoke the agent.

## Skill Definition Format

Skills use YAML frontmatter followed by Markdown instructions:

```yaml
---
name: skill-name
description: What the skill does and when to use it (triggers for activation)
allowed-tools: ["Read", "Write", "Bash", "Glob"]
---

# Skill instructions in Markdown
```

Skills differ from agents:
- Skills have dual invocation: users (`/skill-name`) OR Claude auto-loads based on description
- Agents are delegated via Task tool for isolated context work
- Skills support multi-file structure; agents are single Markdown files
- Both can use subagent execution (`context: fork` or `agent:` field)

## Project Tracking

Ideas and enhancements are tracked in [GitHub Issues](https://github.com/ddehart/claude-code-plugins/issues) with tiered priority labels (tier-1 through tier-4).

## Build System

**No dependencies to install, and no build process.** Plugins are markdown and JSON, and that is still true of
almost everything here.

**One exception: `knowledge-commons` ships an executable and has tests.** Its whole architecture rests on the
plugin *refusing* invalid writes, and a markdown skill cannot refuse anything — it can only be told to. So the
plugin ships a real validator, and the validator has a test suite:

```bash
python3 plugins/knowledge-commons/tests/run.py          # the whole suite
python3 plugins/knowledge-commons/bin/validate.py check --graph <a-graph>
```

Stdlib only, Python 3.9 floor — the plugin must run on a fresh machine with nothing installed. (PyYAML is used
in the tests as a differential oracle when present, and never at runtime.) The suite's load-bearing test is
`test_every_check_is_proven_to_fire`: every check must have a test that breaks a fixture graph and watches it
fire, because **a check with no firing test is indistinguishable from a check that always passes.**

Everything else is validated by ensuring:
1. JSON files are valid (`marketplace.json`, `plugin.json`)
2. Agent and skill Markdown files have valid YAML frontmatter
3. Instructions are clear and actionable

Changes are validated by ensuring:
1. JSON files are valid (`marketplace.json`, `plugin.json`)
2. Agent Markdown files have valid YAML frontmatter
3. Agent instructions are clear and actionable

## Development Workflow

Checklist for adding or updating plugin components (agents, skills, hooks):

### 1. Setup
- [ ] Create feature branch: `feat/<component-name>` or `fix/<issue>`

### 2. Implement
- [ ] Create/update component file(s) in appropriate location
- [ ] Follow format for component type (see sections below)

### 3. Update Metadata
- [ ] `plugins/<plugin>/.claude-plugin/plugin.json` - bump version, update description/keywords
- [ ] `.claude-plugin/marketplace.json` - bump version, update description

### 4. Update Documentation
- [ ] `README.md` - update component tables and usage section

### 5. Commit & PR
- [ ] Commit with conventional format: `feat(<scope>): description`
- [ ] Create PR and watch for review feedback

### 6. Merge & Verify
- [ ] Merge PR after checks pass
- [ ] Test component works as expected

## Adding New Agents

1. Create `plugins/<plugin-name>/agents/<agent-name>.md`
2. Include YAML frontmatter with: name, description, tools, model
3. Write clear instructions for the agent's role and workflow
4. Include escalation criteria (when to ask for help)
5. Include quality assurance checks

## Plugin Installation

Users install via Claude Code slash commands:
```bash
/plugin marketplace add ddehart/claude-code-plugins
/plugin install dev-workflow@ddehart-plugins
```

## Session Chronicle

This project maintains a session chronicle at `docs/chronicle/`.
Claude writes entries capturing decisions, learnings, and reflections.
Read recent entries at the start of sessions for continuity.

## Using the Documentation-Syncing Skill

Run `/documentation-syncing` to sync self-documentation reference files with latest Claude Code releases. The skill orchestrates 4 atomic agents with file-based state handoff for reliable execution.
