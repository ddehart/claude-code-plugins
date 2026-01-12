# Observation Persistence Spec

Implementation blueprint for persisting user observations in the self-documentation skill.

## Problem

The self-documentation skill allows users to record undocumented behaviors they discover. Currently, `observations.md` lives in the plugin directory and gets overwritten on plugin updates—losing all recorded observations.

## Solution

Store observations in a user-local JSON file outside the plugin directory, following XDG Base Directory conventions.

## Storage Location

```
$XDG_DATA_HOME/claude-plugins/self-documentation/observations.json
```

Falls back to `~/.local/share/claude-plugins/self-documentation/observations.json` if `XDG_DATA_HOME` is unset.

**Rationale:** XDG compliance ensures data survives plugin updates, follows platform conventions, and integrates with standard backup strategies.

## Data Schema

```json
{
  "version": 1,
  "observations": [
    {
      "id": "obs-20260111-001",
      "description": "AskUserQuestion tool cannot be delegated to subagents",
      "context": "Discovered while building spec-writing skill that needs interactive prompts",
      "feature_area": "tools",
      "discovered": "2026-01-11",
      "status": "submitted",
      "issue_url": "https://github.com/ddehart/claude-code-plugins/issues/42"
    }
  ],
  "last_updated": "2026-01-11"
}
```

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | yes | Unique identifier: `obs-YYYYMMDD-NNN` |
| `description` | string | yes | What was observed |
| `context` | string | no | How/when it was discovered |
| `feature_area` | string | yes | Category: `tools`, `skills`, `agents`, `mcp`, `config`, `other` |
| `discovered` | string | yes | ISO date when discovered |
| `status` | enum | yes | `new`, `submitted`, `documented` |
| `issue_url` | string | no | GitHub issue URL if submitted |

## Workflows

### Recording an Observation

1. User describes undocumented behavior
2. Agent checks for similar existing observations (warn if found)
3. Agent writes observation to JSON with status `new`
4. Agent optionally creates GitHub issue → updates status to `submitted`

### Referencing an Observation

When the agent references a stored observation:
1. Check if the behavior is now documented (in reference files or official docs)
2. If documented → delete the observation (lazy cleanup)
3. If not → use the observation to help the user

### Duplicate Detection

Before adding a new observation:
1. Search existing observations by description similarity and feature area
2. If similar observation exists → warn user, ask if they want to add anyway
3. Do not block—user decides

### Issue Creation

Follow existing skill pattern:
- Create issue in `ddehart/claude-code-plugins`
- Apply label `observation`
- Update observation status to `submitted`
- Store issue URL in observation record

## Bootstrap

On first observation:
1. Check if storage directory exists
2. Create directory path if missing: `mkdir -p $XDG_DATA_HOME/claude-plugins/self-documentation/`
3. Create `observations.json` with empty observations array

No explicit setup command required—silent auto-creation.

## Error Handling

### Corrupted/Missing Storage

If `observations.json` is missing, corrupted, or unparseable:
1. Warn user: "Observation storage was corrupted or missing. Starting fresh."
2. Create new empty storage file
3. Continue with operation

### Schema Migration

**Out of scope for v1.** No prior versions exist to migrate from. When a v2 schema is needed, add migration logic to the helper script at that time.

## Implementation Checklist

- [x] Remove `references/observations.md` from plugin
- [x] Add storage path resolution (XDG with fallback)
- [x] Implement JSON read/write with error handling
- [x] Add observation CRUD operations to skill workflow
- [x] Implement duplicate detection (description similarity)
- [x] Implement lazy cleanup on reference
- [x] Update SKILL.md workflow documentation

**Implemented via:** `scripts/observations.py` helper script with `list`, `add`, `remove`, `get` commands.

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| User has no `~/.local/share` (Windows) | Fall back to `~/.claude/self-documentation/` on non-Unix |
| Concurrent access from parallel sessions | JSON is small; use atomic write (write to temp, rename) |
| Storage grows unbounded | Lazy cleanup removes documented observations; consider periodic prune |

## Open Questions

- Should observations sync across machines? (Current answer: No, out of scope)
- Should there be an export/import mechanism? (Defer until needed)
