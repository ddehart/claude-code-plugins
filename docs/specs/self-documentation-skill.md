# Self-Documentation Skill Specification

## Overview

A skill for the `meta-claude` plugin that enables Claude Code to explain its own features, guide users through capability decisions, and track undocumented observations discovered through usage.

**Supersedes:** User skill at `~/.claude/skills/claude-code-capabilities/`

**Plugin:** `meta-claude` (version bump required)

## Goals

1. **Answer capability questions** - "How do skills work?", "What can you do?", "What's the difference between X and Y?"
2. **Guide feature decisions** - "Should I use a skill or slash command?", "When should I use MCP vs plugins?"
3. **Track release notes** - Maintain index of documented and undocumented features
4. **Record observations** - Capture user-discovered behaviors not in official docs (e.g., "AskUserQuestion can't be delegated to subagents")
5. **Enable community contribution** - Create GitHub issues for observations, support PR workflow

## Non-Goals

- Migration from existing user skill (separate concern)
- Automatic index updates on user machines (updates happen in source repo only)
- Real-time documentation sync (fetch on demand is sufficient)

## Architecture

### Thematic Reference Structure

Split the ~1,700 lines of reference content into focused files optimized for token efficiency. Only load what's needed for the current question.

```
plugins/meta-claude/skills/self-documentation/
├── SKILL.md                           # Main skill definition (~200 lines)
├── references/
│   ├── topic-index.md                 # Lightweight keyword → file mapping
│   ├── decision-guide.md              # "When to use X vs Y" guidance
│   ├── core-features.md               # Skills, agents, slash commands, hooks
│   ├── integrations.md                # MCP servers, plugins, IDE extensions
│   ├── configuration.md               # Settings, permissions, sandboxing, models
│   ├── workflows.md                   # Git automation, parallel execution
│   ├── undocumented.md                # Features from release notes without official docs
│   └── observations.md                # User-discovered behaviors (source of truth for repo)
```

**Granularity rationale:** ~6-8 thematic files at ~150-250 lines each. Fine enough for targeted loading, coarse enough to avoid excessive file lookups.

### Topic Index

A lightweight file (~50-100 lines) mapping keywords/concepts to reference files:

```markdown
## Topic Index

| Keywords | Reference File |
|----------|----------------|
| skill, skills, SKILL.md, allowed-tools | core-features.md |
| mcp, server, protocol, tool | integrations.md |
| permission, sandbox, security | configuration.md |
| git, branch, commit, pr | workflows.md |
| should I use, when to use, vs, difference | decision-guide.md |
| release notes, undocumented, new feature | undocumented.md |
| observation, discovered, tested, behavior | observations.md |
```

### Content Distribution

Each thematic reference file contains three tiers of information for its domain:

1. **Documented features** - Official docs URL, key concepts, last verified date
2. **Undocumented features** - From release notes, what we know, unanswered questions
3. **Observations** - User-discovered behaviors with reproduction context

This keeps related information co-located rather than requiring multiple file loads.

## Workflows

### Answering Questions

```
1. Load topic-index.md
2. Match user question to relevant reference file(s)
3. Load identified file(s) - may load multiple for cross-theme questions
4. If needed, fetch official docs via WebFetch
5. Synthesize conversational response
6. Update reference file with any new information learned
```

**Cross-theme questions:** When a question spans multiple themes (e.g., "How do skills work with MCP servers?"), load both relevant files.

**No proactive suggestions:** Answer the question directly without suggesting related topics.

### Recording Observations

When a user discovers undocumented behavior:

```
1. User reports finding (e.g., "I discovered AskUserQuestion can't be delegated to subagents")
2. Claude confirms this is a new observation worth recording
3. Claude proposes creating a GitHub issue
4. User confirms
5. Claude creates issue via gh CLI in ddehart/claude-code-plugins
6. Claude asks user: "Would you also like me to cache this locally and/or create a PR?"
7. Based on user choice:
   - Cache locally: Write to ~/.claude/plugin-observations/meta-claude.json
   - Create PR: Branch, update observations.md, create PR
   - Neither: Done after issue creation
```

### Observation Issue Format

Minimal format for GitHub issues:

```markdown
Title: [Observation] <brief description>

## Observation
<description of the behavior>

## Reproduction Context
- Discovered: <date>
- Context: <what the user was trying to do>
- Version: <Claude Code version if known>

## Related
- Feature area: <e.g., tools, subagents, skills>

Labels: observation
```

### gh CLI Fallback

If `gh` is unavailable or authentication fails:

```
1. Format the issue content
2. Display to user with instructions:
   "I couldn't create the issue automatically. Here's the formatted content
   you can paste into a new issue at:
   https://github.com/ddehart/claude-code-plugins/issues/new"
3. Still offer local caching option
```

### Release Notes Updates

Updates to the capabilities index happen **only in this source repo**, not on user machines:

```
1. Maintainer runs /release-notes in this repo
2. Skill identifies new releases since last update
3. Skill checks if any undocumented features now have official docs
4. Skill adds new undocumented features from release notes
5. Skill migrates newly-documented features to appropriate thematic files
6. Changes are committed and released via plugin update
```

Users receive updates by running `/plugin update meta-claude@ddehart-plugins`.

## Local Data Persistence

### Observation Cache

Following the pattern from `claude-mem` and other plugins, store user observations in:

```
~/.claude/plugin-observations/meta-claude.json
```

Schema:
```json
{
  "observations": [
    {
      "id": "obs-001",
      "description": "AskUserQuestion tool cannot be delegated to subagents via Task tool",
      "context": "Attempted to create an interactive skill that runs in forked context",
      "discovered": "2025-01-09",
      "feature_area": "tools",
      "issue_url": "https://github.com/ddehart/claude-code-plugins/issues/42",
      "status": "submitted"
    }
  ],
  "last_updated": "2025-01-09"
}
```

**Why this location:**
- `~/.claude/` is the standard user-scoped Claude data directory
- Survives plugin updates (not in plugin cache)
- Follows `claude-mem` pattern of plugin-specific subdirectories
- Simple JSON is sufficient for this use case (no SQLite needed)

## Skill Definition

### YAML Frontmatter

```yaml
---
name: self-documentation
description: >
  Explain Claude Code features, capabilities, and tools. Use for questions like
  "how do skills work?", "what can you do?", "what's the difference between X and Y?",
  "should I use a skill or slash command?". Also handles recording observations
  about undocumented behaviors. Invoke with /self-documentation or ask naturally.
allowed-tools:
  - Read
  - Glob
  - Grep
  - WebFetch
  - Bash
  - Write
---
```

### Description Rationale

- Includes natural trigger phrases users would say
- Mentions the skill name for explicit invocation awareness
- Covers all three concerns: reference, decisions, observations

## Decision Guide

Keep as a separate file (`decision-guide.md`) for questions about choosing between features:

- Skills vs Slash Commands
- Skills vs Subagents
- Skills vs MCP Servers
- When to combine features

**Response pattern:** Make opinionated recommendations based on user's context, not just present options as equal choices.

## Error Handling

| Scenario | Handling |
|----------|----------|
| Reference file not found | Fall back to topic-index, report which file is missing |
| WebFetch fails | Use cached key concepts from reference file |
| gh CLI unavailable | Provide formatted issue for manual creation |
| Cross-theme question unclear | Load topic-index, ask user to clarify if needed |
| Observation already exists | Check local cache, inform user, offer to update |

## File Structure

```
plugins/meta-claude/
├── .claude-plugin/plugin.json          # Bump version
├── skills/
│   ├── session-export/                 # Existing skill
│   │   └── ...
│   └── self-documentation/             # New skill
│       ├── SKILL.md
│       └── references/
│           ├── topic-index.md
│           ├── decision-guide.md
│           ├── core-features.md
│           ├── integrations.md
│           ├── configuration.md
│           ├── workflows.md
│           ├── undocumented.md
│           └── observations.md
```

## Implementation Checklist

### Phase 1: Core Skill
- [ ] Create `skills/self-documentation/SKILL.md` with workflow instructions
- [ ] Create `references/topic-index.md` with keyword mapping
- [ ] Create `references/decision-guide.md` (migrate from existing skill)

### Phase 2: Thematic References
- [ ] Create `references/core-features.md` (skills, agents, slash commands, hooks)
- [ ] Create `references/integrations.md` (MCP, plugins, IDE)
- [ ] Create `references/configuration.md` (settings, permissions, sandbox)
- [ ] Create `references/workflows.md` (git, parallel execution)
- [ ] Create `references/undocumented.md` (release notes features)

### Phase 3: Observations System
- [ ] Create `references/observations.md` (seed with known observations)
- [ ] Implement observation recording workflow in SKILL.md
- [ ] Implement GitHub issue creation via gh CLI
- [ ] Implement local cache at `~/.claude/plugin-observations/meta-claude.json`

### Phase 4: Metadata & Documentation
- [ ] Bump version in `plugins/meta-claude/.claude-plugin/plugin.json`
- [ ] Bump version in `.claude-plugin/marketplace.json`
- [ ] Update `README.md` with new skill documentation

## Open Questions

1. **Observation deduplication** - How to detect if an observation already exists in the repo's observations.md vs just locally cached?
2. **PR automation scope** - Should the skill create full PRs or just prepare the branch/changes?
3. **Reference file size monitoring** - How to ensure thematic files stay under target line counts as content grows?

## Risks

| Risk | Mitigation |
|------|------------|
| Reference files grow too large | Monitor line counts, split further if needed |
| Topic index becomes stale | Include index update as part of reference updates |
| gh CLI auth issues | Graceful fallback with manual instructions |
| Local cache conflicts | Use append-only pattern, include unique IDs |
