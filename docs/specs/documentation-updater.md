# Spec: Documentation Updater Agent

Local maintenance agent for keeping the self-documentation skill's reference files current with Claude Code releases.

## Problem Statement

The `self-documentation` skill (in `plugins/meta-claude/`) includes reference files that track Claude Code features—both documented and undocumented. These files become stale as new releases ship and previously undocumented features gain official documentation.

Currently, the skill contains a "Release Notes Updates" workflow that describes updating these files, but:
1. The skill is distributed via the plugin marketplace
2. User-side updates are overwritten on plugin updates
3. The skill's purpose is answering questions, not maintenance

## Solution

Create a **local maintenance agent** in `.claude/agents/` that:
- Lives in the project repo, not distributed with the plugin
- Updates reference files based on release notes
- Migrates features when official docs become available
- Produces changes that get committed and released as plugin updates

## Scope

### In Scope
- Fetching and parsing release notes via `/release-notes` command
- Adding new undocumented features to `undocumented.md`
- Adding documented features to appropriate thematic reference files
- Migrating previously undocumented features when docs appear
- Updating version tracking headers
- Removing the "Release Notes Updates" workflow from the skill

### Out of Scope
- Automatic git commits or PR creation (user handles git workflow)
- Updating `observations.md` (user-submitted, handled by skill)
- Modifying the skill's question-answering logic

## Technical Approach

### Agent Location

```
.claude/agents/documentation-updater.md
```

This location:
- Is local to the project (not distributed)
- Follows Claude Code's agent discovery conventions
- Keeps maintenance tooling separate from distributed plugins

### Data Sources

**Release Notes:**
- Use the `/release-notes` slash command (via Skill tool)
- This is the canonical source within Claude Code

**Official Documentation:**
- Index: `https://code.claude.com/docs/llms.txt` (LLM-friendly documentation index)
- URL pattern: `https://code.claude.com/docs/en/<page>.md`
- Discovery: Fetch `llms.txt` once per run, search cached index for feature names

### Reference Files (Update Targets)

| File | Content | Update Action |
|------|---------|---------------|
| `references/undocumented.md` | Features without official docs | Add new undocumented features |
| `references/core-features.md` | Skills, agents, MCP, plugins, hooks | Add documented features (core) |
| `references/configuration.md` | Settings, permissions, sandboxing | Add documented features (config) |
| `references/integrations.md` | VS Code, IDE extensions | Add documented features (integrations) |
| `references/workflows.md` | Shortcuts, git automation | Add documented features (workflows) |
| `references/topic-index.md` | Keyword-to-file mapping | Add keywords for new features |

### Workflow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. FETCH RELEASE NOTES                                      │
│    - Invoke /release-notes via Skill tool                   │
│    - Parse releases newer than "Latest Release" header      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. CHECK FOR DOC MIGRATIONS                                 │
│    - For each feature in undocumented.md:                   │
│      - WebFetch official docs to check if docs now exist    │
│      - If documented: Mark for migration                    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. PROCESS NEW FEATURES                                     │
│    - For each new feature from release notes:               │
│      - Check if official docs exist                         │
│      - If documented: Categorize by content → thematic file │
│      - If undocumented: Add to undocumented.md              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. WRITE CHANGES                                            │
│    - Update reference files directly                        │
│    - Update "Latest Release" header                         │
│    - Update topic-index.md with new keywords                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. SUMMARIZE                                                │
│    - Output summary of changes made                         │
│    - List: added features, migrated features, updated files │
└─────────────────────────────────────────────────────────────┘
```

### Categorization Logic

When a feature has official documentation, the agent infers the appropriate thematic file by reading the doc content:

| Doc Content Signals | Target File |
|---------------------|-------------|
| Skills, agents, MCP, plugins, hooks, Task tool | core-features.md |
| Settings, permissions, CLAUDE.md, sandboxing | configuration.md |
| VS Code, IDE, extensions, Azure | integrations.md |
| Keyboard, shortcuts, git, sessions, checkpoints | workflows.md |

The agent reads the official doc page and matches against these content patterns. If ambiguous, it uses `core-features.md` as the default.

### Feature Entry Format

**For undocumented.md:**
```markdown
## Feature Name

**What it is**: Brief description

**Introduced**: vX.X.X (YYYY-MM)

**What we know**:
- Bullet points of known behavior
- Based on release notes

**Unanswered questions**:
- What remains unclear
```

**For thematic files:**
```markdown
## Feature Name

Brief description with key concepts.

**Documentation**: [Official Docs](url)

**Key concepts**:
- Important points from official docs
- Last updated: YYYY-MM-DD
```

### Edge Cases

**No new releases:**
- Still run doc migration check
- Output: "No new releases since vX.X.X. Checked N undocumented features for doc availability."

**Feature already exists:**
- Skip if feature name matches existing entry
- Update existing entry if significant new info

**Docs unavailable (WebFetch fails):**
- Treat as undocumented
- Note in entry: "Official docs check failed; may have documentation"

**Category unclear:**
- Default to `core-features.md`
- Add note: "Categorization may need review"

## Agent Definition

### Frontmatter

```yaml
---
name: documentation-updater
description: Update self-documentation skill reference files with new Claude Code releases. Run when maintaining the plugin to sync with latest features.
tools: Skill, WebFetch, Read, Write, Glob, Grep
model: sonnet
---
```

### Required Tools

| Tool | Purpose |
|------|---------|
| Skill | Invoke `/release-notes` command |
| WebFetch | Check official documentation URLs |
| Read | Read current reference files |
| Write | Update reference files |
| Glob | Find reference files |
| Grep | Search for existing feature entries |

## Skill Modification

### Remove from SKILL.md

Delete the entire "Workflow: Release Notes Updates" section (lines 183-197):

```markdown
## Workflow: Release Notes Updates

**Important:** Index updates happen only in the source repo, not on user machines.

When maintaining the reference files (as repo maintainer):

1. Run `/release-notes` to get latest Claude Code releases
2. Identify releases newer than the "Latest Release" in `undocumented.md`
3. For each new feature:
   - Check if official docs exist (fetch docs map)
   - If documented: Add to appropriate thematic file
   - If undocumented: Add to `undocumented.md`
4. Check if any previously undocumented features now have docs (migrate them)
5. Update "Latest Release" header
6. Commit and release via plugin update
```

### Rationale

- The workflow describes maintainer-only behavior
- It belongs in the maintenance agent, not the distributed skill
- The agent in `.claude/agents/` is discoverable by maintainers
- Removes confusion about where updates happen

## Implementation Tasks

1. Create `.claude/agents/documentation-updater.md` with agent definition
2. Remove "Workflow: Release Notes Updates" section from skill's SKILL.md
3. Update plugin version in `plugins/meta-claude/.claude-plugin/plugin.json`
4. Update marketplace version in `.claude-plugin/marketplace.json`
5. Test agent with a dry run

## Risks & Open Questions

### Risks

| Risk | Mitigation |
|------|------------|
| `/release-notes` output format may change | Agent should handle format variations gracefully |
| Docs URL structure may change | Dynamic discovery avoids hardcoded paths |
| Categorization errors | Default to core-features.md; maintainer can adjust |

### Open Questions

- ~~**Rate limiting**: Should the agent batch WebFetch calls to avoid hitting rate limits?~~ **Resolved:** Yes, fetch `llms.txt` once and cache.
- **Caching**: Should doc availability checks be cached locally between runs? **Deferred:** Not implemented; can be added if needed.
- **Partial runs**: Should the agent support updating only specific sections (e.g., just migrations)? **Deferred:** Not implemented; full run is simple enough.

---

## Implementation Notes

*Added post-implementation to document deviations from the original spec.*

### Spec vs Implementation Deviations

| Spec | Implementation | Rationale |
|------|----------------|-----------|
| Version bump to 1.3.0 | Version bump to 1.2.1 | Removing a workflow section is maintenance, not a feature. Patch version is more appropriate. |
| Docs URL: `docs.anthropic.com/en/docs/claude-code/` | Docs URL: `code.claude.com/docs/llms.txt` | Anthropic provides an LLM-friendly index at `llms.txt`. This is the correct discovery mechanism. |
| "Dynamic discovery via sitemap" | Fetch `llms.txt` once, cache, search index | The `llms.txt` file is specifically designed for agent access. More reliable than sitemap parsing. |
| No release notes format specified | Added explicit format reference with examples | Critical for agent reliability. Without knowing the format, parsing is guesswork. |
| No rate limiting guidance | Added "Efficiency Guidelines" section | Prevents excessive WebFetch calls; fetch index once, batch searches. |
| Workflow step 2: "Check for doc migrations" | Implementation adds explicit step 2: "Determine version delta" | Clearer separation of concerns. Must know what's new before checking migrations. |

### Additions Beyond Spec

| Addition | Rationale |
|----------|-----------|
| **Escalation section** | Standard practice for agent definitions. Tells agent when to ask for help. |
| **Quality Checks section** | Provides completion criteria. Helps agent self-verify before finishing. |
| **topic-index.md entry format** | Spec mentioned updating topic-index but didn't specify format. |
| **Expanded categorization signals** | Added "subagents", "model config", "Foundry", "cost" based on actual Claude Code features. |
| **"Skip trivial entries" guidance** | Bug fixes and platform-specific fixes clutter documentation. Agent should filter. |

### Not Implemented from Spec

| Spec Item | Status | Notes |
|-----------|--------|-------|
| SKILL.md cleanup instruction in agent | Not needed | Already performed during implementation. Agent doesn't need to know about this. |
| Version update reminders | Not needed | One-time task, not ongoing agent responsibility. |
| Partial run support | Deferred | Full runs are simple; partial runs add complexity without clear benefit. |
| Cross-run caching | Deferred | Can be added if WebFetch becomes a bottleneck. |

### Implementation Date

2025-01-09
