# SDK Behavioral Bridges

Last updated: 2026-01-11
Source: Agent SDK Documentation (platform.claude.com/docs/en/agent-sdk/)

Information from the Agent SDK documentation that explains Claude Code CLI behavior. This file bridges SDK documentation with CLI usage, extracting behavioral constraints that affect how Claude Code works.

---

## AskUserQuestion Tool

**Source**: /docs/en/agent-sdk/user-input

**Behavioral Constraints**:
- 60-second timeout for responses
- 1-4 questions per call
- 2-4 options per question
- **Not available in subagents** spawned via Task tool

**Implication**: Interactive skills must run in main context, not forked. Use `context: fork` only for non-interactive workflows.

---

## Permission Evaluation Flow

**Source**: /docs/en/agent-sdk/permissions

**Order of evaluation**:
1. Hooks (can allow, deny, or continue)
2. Permission rules (deny → allow → ask)
3. Permission mode (bypassPermissions, acceptEdits, dontAsk, default)
4. canUseTool callback (if not resolved above)

**Key insight**: Deny rules are checked first - any match results in immediate denial, regardless of allow rules.

---

## Subagent Constraints

**Source**: /docs/en/agent-sdk/subagents

**Behavioral Constraints**:
- Cannot spawn their own subagents (no Task tool in subagent tools)
- Cannot use AskUserQuestion
- Messages include `parent_tool_use_id` field for tracking

**Implication**: Subagent depth is limited to 1 level. Design workflows that don't require nested delegation.

---

## MCP Tool Naming

**Source**: /docs/en/agent-sdk/mcp

**Convention**: `mcp__<server_name>__<tool_name>`

**Examples**:
- Server "playwright" → `mcp__playwright__browser_click`
- Server "linear" → `mcp__linear__create_issue`

The server name comes from the key used in MCP server configuration.

---

## File Checkpointing Scope

**Source**: /docs/en/agent-sdk/file-checkpointing

**What's tracked** (can be reverted):
- Write tool
- Edit tool
- NotebookEdit tool

**What's NOT tracked** (permanent changes):
- Bash commands (echo, sed, cat, etc.)
- Directory operations
- Remote files

**Implication**: For revertible file operations, use Write/Edit tools. Changes made via Bash are permanent and cannot be rewound using checkpoints.

---

## Skills Tool Restrictions

**Source**: /docs/en/agent-sdk/skills

**Important difference between CLI and SDK**:
- `allowed-tools` frontmatter in SKILL.md only works in CLI
- SDK ignores skill-level tool restrictions
- SDK controls tools via `allowedTools` option in query configuration

**Implication**: Skills designed with tool restrictions work as expected in CLI but may have broader tool access in SDK applications.

---

## Session Fork Behavior

**Source**: /docs/en/agent-sdk/sessions

**Fork vs Continue**:

| Behavior | `forkSession: false` (default) | `forkSession: true` |
|----------|-------------------------------|---------------------|
| Session ID | Same as original | New ID generated |
| History | Appends to original | Creates new branch |
| Original session | Modified | Preserved unchanged |
| Use case | Continue linear conversation | Explore alternatives |

**Implication**: Use fork when you want to try different approaches from the same starting point without modifying the original session.

---

## Hook Availability

**Source**: /docs/en/agent-sdk/hooks

**TypeScript-only hooks** (not available in Python SDK):
- SessionStart
- SessionEnd
- Notification
- SubagentStart
- PostToolUseFailure
- PermissionRequest

**Hook execution order** (when multiple hooks match):
1. Deny decisions checked first (any match = immediate denial)
2. Ask rules checked second
3. Allow rules checked third
4. Default to Ask if nothing matches

---

## Streaming Input Requirements

**Source**: /docs/en/agent-sdk/streaming-vs-single-mode

**Features requiring streaming input mode**:
- Image attachments in messages
- Dynamic message queueing
- Real-time interruption
- Hook integration
- MCP server connections

**Single message mode limitations**:
- No image attachments
- No hooks
- No MCP tools
- Stateless operation only

**Implication**: For full Claude Code functionality, streaming mode is preferred.

---

## Built-in Tools Reference

**Source**: /docs/en/agent-sdk/overview

**Standard tools available**:

| Tool | Purpose |
|------|---------|
| Read | Read files from filesystem |
| Write | Create new files |
| Edit | Modify existing files |
| Bash | Run terminal commands |
| Glob | Find files by pattern |
| Grep | Search file contents with regex |
| WebSearch | Search the web |
| WebFetch | Fetch and parse web content |
| AskUserQuestion | Ask user questions (constraints above) |
| Task | Invoke subagents |
| Skill | Invoke skills |
| TodoWrite | Manage task lists |
| NotebookEdit | Edit Jupyter notebooks |

---

## How to Use This File

This reference is for understanding behavioral constraints that come from SDK documentation but affect CLI usage. When you encounter unexpected behavior related to:

- Tool availability in subagents
- Permission handling
- File tracking and rewind
- Session management

Check this file for authoritative documentation from the Agent SDK.
