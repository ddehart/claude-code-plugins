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
- Skills are model-invoked (Claude decides when to activate based on description)
- Agents are explicitly delegated via the Task tool
- Skills can include supporting scripts in a `scripts/` subdirectory

## No Build System

This is a documentation-only repository. There are:
- No dependencies to install
- No build process
- No tests to run
- No linting configured

Changes are validated by ensuring:
1. JSON files are valid (`marketplace.json`, `plugin.json`)
2. Agent Markdown files have valid YAML frontmatter
3. Agent instructions are clear and actionable

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
