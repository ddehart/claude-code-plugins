# Spec: Documentation Syncing

Atomic agent architecture for keeping self-documentation reference files current with Claude Code releases.

## Problem Statement

The current `documentation-updater` agent is unreliable. In testing, it:

1. **Added documented features to undocumented.md** - fetched docs, confirmed features exist, then followed the wrong code path
2. **Silently deleted features** without migration or audit trail
3. **Created inconsistent topic-index.md** entries pointing to wrong files

### Root Cause: Cognitive Overload

The agent performs 7 complex steps in a single execution with similar but opposite logic paths:
- Step 3: If feature has docs → REMOVE from undocumented.md
- Step 4: If feature has docs → ADD to thematic file (NOT undocumented.md)

Single-purpose agents that performed audits consistently caught issues the multi-purpose agent missed.

## Proposed Solution

Split into 4 atomic agents coordinated by a skill, using file-based state handoff.

### Architecture

```
/documentation-syncing skill (orchestrates agents)
         │
         │  ┌─────────────────────────────────────┐
         │  │  .claude/cache/doc-sync-state.json  │
         │  │  (shared state between agents)      │
         │  └─────────────────────────────────────┘
         │
         ├─→ doc-release-parser        → parses releases + SDK docs
         │
         ├─→ doc-migration-checker     → checks existing features
         │
         ├─→ doc-content-writer        → writes all changes
         │
         └─→ doc-consistency-auditor   → PASS/FAIL gate
                    │
                    ▼ (if FAIL)
              skill iterates: fix → re-audit until PASS or unfixable
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Data flow | File-based handoff | Token efficient, debuggable, resumable |
| Shared config | Skill passes mappings in prompts | Centralized, no config drift |
| SDK docs | Part of release-parser | Fewer agents, related to "what's new" |
| Failure recovery | Iterate until pass | Autonomous, only escalates unfixable errors |
| Dry-run mode | Not included | Auditor + git provide safety |
| Context forking | No (fresh context) | File-based agents don't need conversation history |

### Constraint

Subagents cannot spawn subagents (Task tool unavailable). The skill runs on the main thread and invokes agents via Task tool.

## State File Schema

Location: `.claude/cache/doc-sync-state.json`

The state file is designed to **prevent the specific failures** we observed:
- **Problem 1** (documented features in undocumented.md): Require evidence of doc checks
- **Problem 2** (silent deletions): Cross-reference removals with additions
- **Problem 3** (wrong topic-index): Track all index changes with rationale

```json
{
  "workflow_id": "uuid",
  "started_at": "ISO timestamp",
  "current_step": "parsing | checking | writing | auditing | complete",

  "versions": {
    "tracked": "v2.1.20",
    "latest": "v2.1.29"
  },

  "parser_output": {
    "new_features": [
      {
        "name": "Customizable Spinner Verbs",
        "version": "v2.1.23",
        "description": "...",
        "doc_check": {
          "pages_fetched": ["settings.md", "interactive-mode.md"],
          "found_in": "settings.md",
          "search_terms": ["spinnerVerbs", "spinner"],
          "excerpt": "The spinnerVerbs setting allows...",
          "decision": "documented",
          "target_file": "configuration.md"
        }
      },
      {
        "name": "Per-User Temp Directory",
        "version": "v2.1.23",
        "description": "...",
        "doc_check": {
          "pages_fetched": ["settings.md"],
          "found_in": null,
          "search_terms": ["temp directory", "TMPDIR", "isolation"],
          "excerpt": null,
          "decision": "undocumented",
          "target_file": "undocumented.md"
        }
      }
    ],
    "sdk_features": [...]
  },

  "checker_output": {
    "to_migrate": [
      {
        "name": "PR Review Status Indicator",
        "current_location": "undocumented.md",
        "doc_check": {
          "pages_fetched": ["interactive-mode.md"],
          "found_in": "interactive-mode.md",
          "search_terms": ["PR review", "status indicator", "prompt footer"],
          "excerpt": "The prompt footer shows PR review status..."
        },
        "target_file": "workflows.md",
        "doc_url": "https://code.claude.com/docs/en/interactive-mode"
      }
    ],
    "to_keep": [
      {
        "name": "Permission Prompt Feedback",
        "doc_check": {
          "pages_fetched": ["settings.md", "interactive-mode.md"],
          "found_in": null,
          "search_terms": ["permission", "feedback", "prompt"]
        },
        "reason": "Not found in any candidate doc page"
      }
    ]
  },

  "writer_output": {
    "files_modified": ["undocumented.md", "workflows.md", "topic-index.md"],

    "entries_added": [
      {"feature": "Customizable Spinner Verbs", "file": "configuration.md", "source": "new_documented"},
      {"feature": "Per-User Temp Directory", "file": "undocumented.md", "source": "new_undocumented"},
      {"feature": "PR Review Status Indicator", "file": "workflows.md", "source": "migrated"}
    ],

    "entries_removed": [
      {"feature": "PR Review Status Indicator", "file": "undocumented.md", "reason": "migrated", "migrated_to": "workflows.md"}
    ],

    "topic_index_changes": [
      {
        "keywords": "spinnerVerbs, spinner verbs, customize spinner",
        "action": "add",
        "target_file": "configuration.md",
        "rationale": "New documented feature added to configuration.md"
      },
      {
        "keywords": "PR review status, prompt footer",
        "action": "update",
        "old_target": "undocumented.md",
        "new_target": "workflows.md",
        "rationale": "Feature migrated from undocumented.md"
      }
    ],

    "version_updated_to": "v2.1.29"
  },

  "audit_history": [
    {
      "attempt": 1,
      "status": "FAIL",
      "checks": {
        "no_documented_in_undocumented": {
          "status": "FAIL",
          "errors": [
            {"feature": "Spinner Verbs", "found_doc": "settings.md", "fixable": true}
          ]
        },
        "topic_index_correct": {
          "status": "PASS"
        },
        "removals_accounted_for": {
          "status": "PASS",
          "verified": ["PR Review Status Indicator -> workflows.md"]
        },
        "version_header_correct": {
          "status": "PASS"
        }
      }
    }
  ]
}
```

### Audit Invariants

The auditor MUST verify these invariants using the state file:

1. **No documented features in undocumented.md**
   - For each entry in undocumented.md, verify no `doc_check.found_in` exists
   - Cross-reference with `parser_output` and `checker_output`

2. **Every removal is accounted for**
   - For each `entries_removed`, verify a corresponding `entries_added` with `source: "migrated"`
   - Flag any removal without a destination

3. **Topic-index matches actual file locations**
   - For each `topic_index_changes`, verify the `target_file` matches where the feature was actually written
   - For existing mappings, spot-check that features still exist in pointed files

4. **Doc check evidence is present**
   - Every feature decision must have `pages_fetched` and `search_terms`
   - Reject decisions without evidence

### Required Evidence by Decision Type

| Decision | Required Evidence | Auditor Rejects If Missing |
|----------|-------------------|---------------------------|
| Feature is **documented** | `pages_fetched[]`, `found_in`, `excerpt`, `target_file` | Yes - unfixable |
| Feature is **undocumented** | `pages_fetched[]`, `found_in: null`, `search_terms[]` | Yes - unfixable |
| Feature should **migrate** | `pages_fetched[]`, `found_in`, `excerpt`, `doc_url`, `target_file` | Yes - unfixable |
| Feature should **stay** undocumented | `pages_fetched[]`, `found_in: null` | Yes - unfixable |
| Entry **removed** | `reason`, `migrated_to` (if migrated) | Yes - unfixable |
| Topic-index **changed** | `target_file`, `rationale` | Yes - fixable (re-derive from entries_added) |

**Key insight:** The original agent made correct observations (fetched docs, found features) but wrong decisions. By requiring evidence to be recorded, we can audit the decision-making process, not just the outcomes.

### How State File Prevents Each Failure Mode

| Original Problem | How State File Prevents It |
|------------------|---------------------------|
| **Documented features added to undocumented.md** | Every feature has `doc_check.pages_fetched` and `doc_check.found_in`. Auditor cross-references this evidence. If `found_in` is set but feature is in undocumented.md, auditor fails. |
| **Silent deletions** | `entries_removed` requires `migrated_to` field. Auditor verifies every removal has a corresponding addition. Removal without destination = unfixable error. |
| **Wrong topic-index mappings** | `topic_index_changes` records `target_file`. Auditor verifies this matches actual `entries_added` destination. Mismatch = fixable error, triggers re-write. |

**Lifecycle:**
1. Skill creates fresh state file at workflow start
2. Each agent reads state, adds its output section, writes back
3. On audit failure, skill updates `audit_history` and re-invokes writer/auditor
4. On success, skill archives state file for debugging (don't delete)

## Agent Specifications

### 1. doc-release-parser

**Purpose:** Identify new features (including SDK docs) since last tracked version

**Workflow:**
1. Read "Latest Release" header from undocumented.md
2. Fetch release notes from GitHub
3. Parse features introduced after tracked version
4. For features involving subagents/permissions/tools, check Agent SDK docs
5. Write results to state file

**Tools:** WebFetch, Read, Write
**Model:** haiku

**Critical requirement:** For EVERY new feature, the parser MUST:
1. Identify candidate doc pages using feature-to-page mapping
2. Fetch each candidate page
3. Search for the feature
4. Record the evidence (pages fetched, search terms, excerpt if found)
5. Make a decision with recorded rationale

This evidence chain prevents the "checked docs but wrong decision" failure mode.

### 2. doc-migration-checker

**Purpose:** Check if existing undocumented features now have official docs

**Workflow:**
1. Read state file for context
2. Read all features from undocumented.md
3. For each feature, fetch candidate doc pages and search for coverage
4. Write migration recommendations to state file

**Tools:** WebFetch, Read, Write
**Model:** sonnet (needs judgment on doc matching)

**Skill provides in prompt:** Feature-to-page mapping table

**Critical requirement:** For EVERY existing undocumented feature, the checker MUST:
1. Record which pages were fetched
2. Record what search terms were used
3. If found: record excerpt proving the feature is documented
4. If not found: record that no match was found in any candidate page

A migration recommendation without evidence should be rejected by the auditor.

### 3. doc-content-writer

**Purpose:** Write feature entries to correct files and update version header

**Workflow:**
1. Read state file for all inputs
2. For migrated features: remove from undocumented.md, add to thematic file
3. For new documented features: add to thematic file
4. For new undocumented features: add to undocumented.md
5. For SDK features: add to sdk-behavioral-bridges.md
6. Update "Latest Release" header
7. Update topic-index.md with new keywords
8. Write summary to state file

**Tools:** Read, Write
**Model:** haiku (mechanical task)

**Skill provides in prompt:**
- Entry format templates (undocumented, thematic, SDK)
- Categorization logic (content signals → target file)

**Critical requirement:** The writer MUST:
1. Record every entry added with its source (new_documented, new_undocumented, migrated)
2. Record every entry removed with reason and destination
3. Record every topic-index change with rationale linking to actual file written
4. Cross-check: if removing from undocumented.md, verify it's being added elsewhere

The writer should REFUSE to remove an entry without a recorded destination.

### 4. doc-consistency-auditor

**Purpose:** Verify reference files are consistent

**Checks:**
1. No documented features in undocumented.md
2. All topic-index.md keywords point to correct files
3. All thematic file entries have valid doc URLs (spot check)
4. Version header matches expected latest version
5. No orphaned entries (in thematic files but removed from source)

**Tools:** Read, WebFetch, Glob, Write
**Model:** sonnet (needs verification judgment)

**Critical requirement:** The auditor MUST verify using the state file evidence:

1. **no_documented_in_undocumented**: For each feature in undocumented.md, cross-reference with `parser_output` and `checker_output` to ensure no `found_in` exists

2. **removals_accounted_for**: Every `entries_removed` must have a corresponding `entries_added` with matching feature name

3. **topic_index_correct**: Every `topic_index_changes` entry's `target_file` must match where the feature was actually written (per `entries_added`)

4. **evidence_present**: Reject any feature decision that lacks `pages_fetched` and `search_terms`

The auditor should flag missing evidence as an unfixable error - it indicates the parser or checker skipped verification.

## Skill Specification

### Frontmatter

```yaml
---
name: documentation-syncing
description: Sync self-documentation reference files with latest Claude Code releases. Use when maintaining the meta-claude plugin to update feature documentation.
allowed-tools: [Task, Read, Write, Glob]
---
```

### Workflow

```markdown
## Workflow

1. **Initialize**
   - Create fresh state file at `.claude/cache/doc-sync-state.json`
   - Set workflow_id and started_at

2. **Parse releases**
   - Invoke doc-release-parser via Task tool
   - Include feature-to-page mapping in prompt
   - If no new releases, check if migrations needed; if neither, report "Already up to date"

3. **Check migrations**
   - Invoke doc-migration-checker via Task tool
   - Include feature-to-page mapping in prompt

4. **Write content**
   - Invoke doc-content-writer via Task tool
   - Include entry format templates and categorization logic in prompt

5. **Audit and iterate**
   - Invoke doc-consistency-auditor via Task tool
   - If PASS: proceed to step 6
   - If FAIL with fixable errors:
     - Re-invoke doc-content-writer with fix instructions
     - Re-invoke auditor
     - Repeat until PASS or unfixable error
   - If FAIL with unfixable errors: report to user, do NOT bump version

6. **Finalize** (only if audit passed)
   - Bump version in plugins/meta-claude/.claude-plugin/plugin.json
   - Bump version in .claude-plugin/marketplace.json
   - Delete or archive state file
   - Report summary of all changes
```

### Shared Configuration (Passed in Prompts)

**Feature-to-Page Mapping:**
```
| Feature keywords | Candidate doc pages |
|------------------|---------------------|
| subagent, agent, Task tool, Explore, Plan | sub-agents.md |
| keyboard, shortcut, Ctrl, background, vim | interactive-mode.md |
| setting, config, permission, environment | settings.md |
| MCP, server, tool, protocol | mcp.md |
| skill, slash command, /command | skills.md |
| hook, PreToolUse, PostToolUse | hooks.md |
| plugin, marketplace | plugins.md, plugin-marketplaces.md |
| VS Code, IDE, extension | vs-code.md, jetbrains.md |
| checkpoint, rewind | checkpointing.md |
| memory, CLAUDE.md | memory.md |
| CLI, flag, --option | cli-reference.md |
| session, resume, --from-pr | common-workflows.md |
```

**Categorization Logic:**
```
| Content Signals | Target File |
|-----------------|-------------|
| Skills, agents, MCP, plugins, hooks, Task tool | core-features.md |
| Settings, permissions, CLAUDE.md, sandboxing | configuration.md |
| VS Code, IDE, extensions, Azure, Foundry | integrations.md |
| Keyboard, shortcuts, git, sessions, checkpoints | workflows.md |
| SDK behavioral constraints, limitations | sdk-behavioral-bridges.md |
```

**Entry Format Templates:**
(Include the format templates from the old agent definition)

## Version Tracking

The "Latest Release" header in undocumented.md serves as the version checkpoint:

```markdown
**Latest Release**: v2.1.29
```

- **Parser reads** this to determine which releases are new
- **Writer updates** this after processing all new releases
- **Auditor verifies** this matches expected latest version

## Error Handling

| Error | Handling |
|-------|----------|
| WebFetch fails for release notes | Abort workflow, report error |
| WebFetch fails for doc check | Treat feature as undocumented, continue |
| Auditor returns fixable errors | Iterate: fix → re-audit |
| Auditor returns unfixable errors | Stop iteration, report to user |
| Agent times out | Report which agent failed, state file preserved for retry |
| State file corrupted | Abort, suggest deleting state file and restarting |

## Migration from Old Agent

1. Add deprecation notice to `.claude/agents/documentation-updater.md`:
   ```markdown
   > **DEPRECATED**: Use `/documentation-syncing` skill instead.
   > This agent is unreliable and will be removed in a future version.
   ```
2. Remove old agent after new workflow is proven reliable (2-3 successful runs)

## Files to Create

| File | Purpose |
|------|---------|
| `.claude/agents/doc-release-parser.md` | Parse releases + SDK docs |
| `.claude/agents/doc-migration-checker.md` | Check migrations |
| `.claude/agents/doc-content-writer.md` | Write content |
| `.claude/agents/doc-consistency-auditor.md` | Final audit |
| `.claude/skills/documentation-syncing/SKILL.md` | Orchestration |

## Implementation Order

1. Create state file schema and skill skeleton
2. Implement doc-release-parser (can test independently)
3. Implement doc-migration-checker (can test independently)
4. Implement doc-content-writer
5. Implement doc-consistency-auditor
6. Wire up skill orchestration and iteration logic
7. Test full workflow on a small version delta
8. Add deprecation notice to old agent

## Success Criteria

1. Skill completes autonomously without user intervention (unless unfixable error)
2. No documented features end up in undocumented.md
3. topic-index.md mappings are always correct
4. State file enables debugging and resumption
5. Iteration loop converges (doesn't loop forever)
