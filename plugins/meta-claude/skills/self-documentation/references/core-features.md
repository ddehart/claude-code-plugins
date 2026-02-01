# Core Features

Foundational Claude Code capabilities that enable extensibility and customization.

**Last updated**: 2026-02-01

---

## Claude Code Overview

**What it is**: High-level overview of Claude Code's core capabilities, characteristics, and setup requirements

**Documentation**: https://code.claude.com/docs/en/overview

**Key concepts**:
- **Core capabilities**: Build features (natural language to code), debug and fix issues, codebase navigation, automation (lint fixes, merge conflicts, release notes)
- **Terminal-native**: Integrates into existing developer workflows, not a separate IDE
- **Direct action**: Can edit files, execute commands, create commits directly
- **MCP integration**: Access external resources (Google Drive, Figma, Slack) through Model Context Protocol
- **Unix philosophy**: Composable, scriptable, pipeable for CI/CD integration
- **Enterprise ready**: Available via Claude API, AWS Bedrock, Google Vertex AI with security/privacy/compliance
- **VS Code extension (Beta)**: Graphical IDE alternative without terminal requirements
- **Setup**: Requires Node.js 18+, install via `npm install -g @anthropic-ai/claude-code`

---

## Skills (Unified with Slash Commands)

**What it is**: The extensibility system for Claude Code. Skills are SKILL.md files with YAML frontmatter that extend Claude's capabilities. Custom slash commands have been merged into skills - both `.claude/commands/review.md` and `.claude/skills/review/SKILL.md` create `/review` and work the same way.

**Documentation**: https://code.claude.com/docs/en/skills

**Key concepts**:
- **Dual invocation model**: Skills can be invoked by users (`/skill-name`) OR by Claude automatically when relevant. Both modes enabled by default.
- **User invocation**: Type `/skill-name` to invoke directly; skills appear in slash command autocomplete menu
- **Model invocation**: Claude loads skills automatically when conversation matches the description field
- **Invocation control**: `disable-model-invocation: true` prevents Claude from auto-loading (user-only); `user-invocable: false` hides from menu (Claude-only)
- **Backwards compatibility**: Files in `.claude/commands/` still work with same frontmatter support; if skill and command share a name, skill takes precedence
- **Multi-file structure**: SKILL.md (required) + optional supporting files (references/, scripts/, templates/); manages context efficiently
- **Three scopes**: Personal (`~/.claude/skills/`), Project (`.claude/skills/`, git-shared), Plugin (bundled with Claude Code plugins)
- **Enterprise scope**: Organization-wide skills via managed settings
- **Nested directory discovery**: Skills auto-discovered from nested `.claude/skills/` directories; supports monorepo setups
- **Tool restrictions**: `allowed-tools` frontmatter field limits available tools within skill for security/safety
- **Description field is critical**: Must be specific with trigger terms for discoverability (max 1024 characters); tells Claude when to auto-load
- **Supporting files**: `scripts/` (executable code), `references/` (docs loaded as needed), `assets/` (files used in output)
- **Argument passing**: `$ARGUMENTS` for all args, `$0`/`$1`/`$2` shorthand, `${CLAUDE_SESSION_ID}` for session ID; if `$ARGUMENTS` not in content, args appended automatically
- **Dynamic context**: `!`command`` syntax runs shell commands before skill content is sent to Claude; output replaces placeholder
- **Sharing**: Via plugins (recommended, marketplace distribution) or project repository (`.claude/skills/`, team auto-gets on pull)
- **Subagent pairing**: Skills naturally pair with subagents for context protection. Two patterns:
  - `agent: <agent-name>` spawns subagent with skill loaded into fresh context (ideal for search/research skills using Explore agent)
  - `context: fork` spawns subagent with current conversation context carried over (ideal for parallel operations like memory/summarization that shouldn't pollute main context)
- **Subagent skill loading**: Subagents can auto-load specific skills via `skills` frontmatter field; skills unload when subagent completes
- **Hot-reload**: Skills automatically reloaded when created or modified, no restart required
- **Skill hooks**: Skills can define hooks scoped to their lifecycle using `hooks` frontmatter field; supports `PreToolUse`, `PostToolUse`, and `Stop` events
- **Once hooks**: Hooks with `once: true` run only once per session, then are removed
- **Permission-free skills**: Skills without additional permissions or hooks load without requiring user approval; reduces friction for simple skills
- **Unified Skill tool**: Claude invokes skills programmatically via `Skill` tool; control access via `/permissions` rules like `Skill(name)` or `Skill(name:*)`

---

## MCP (Model Context Protocol) Servers

**What it is**: Open-source standard for AI-tool integrations enabling Claude Code to access external tools, databases, and APIs (hundreds of third-party services)

**Documentation**: https://code.claude.com/docs/en/mcp

**Key concepts**:
- **Core capabilities**: Retrieve features from issue trackers, analyze monitoring data, query databases, access design files, automate workflows
- **Three transport types**: HTTP (recommended for cloud services), SSE (deprecated but functional), Stdio (local processes for custom scripts)
- **Three scopes**: Local (default, personal project configs), Project (team-shared via `.mcp.json` in version control), User (cross-project personal utilities)
- **Scope precedence**: Local overrides project and user when naming conflicts occur
- **Popular integrations**: Sentry, Hugging Face, Jam, Asana, Jira, Linear, Notion, Airtable, HubSpot, PostgreSQL, Stripe, Square, PayPal
- **Management commands**: `claude mcp list/get/remove`, `/mcp` within Claude Code
- **Authentication**: OAuth 2.0 automatic for HTTP servers, tokens stored securely and auto-refreshed
- **Enterprise**: System-wide `managed-mcp.json` for standardization, allowlists/denylists for control
- **Tool naming**: MCP tools use pattern `mcp__<server-name>__<tool-name>`
- **Dynamic updates**: MCP `list_changed` notifications allow servers to dynamically update available tools, prompts, and resources without reconnecting
- **structuredContent support**: MCP servers can return `structuredContent` field in tool responses for richer outputs beyond plain text (formatting, hierarchy, structured data)
- **headersHelper**: Dynamic header generation via helper script in MCP config; script outputs JSON with header key-value pairs; enables OAuth token refresh and short-lived API keys

---

## Plugins

**What it is**: Extensions that add custom functionality (commands, agents, skills, hooks, MCP servers) that can be shared across projects and teams

**Documentation**: https://code.claude.com/docs/en/plugins

**Key concepts**:
- **Components**: Skills (extensibility, includes legacy commands), Agents (specialized AI assistants), Hooks (event handlers), MCP Servers (external integrations)
- **Structure**: `.claude-plugin/plugin.json` (metadata), `skills/`, `agents/`, `hooks/` directories (legacy `commands/` still supported)
- **Installation**: `/plugin` interactive menu (browse/discover), direct commands (`install/enable/disable`)
- **Marketplaces**: Catalogs of plugins, add via `/plugin marketplace add your-org/claude-plugins`
- **Team configuration**: Automatic installation via `.claude/settings.json` in repository
- **Development**: Create plugin.json, add components, test locally, distribute through catalogs
- **Best practices**: Semantic versioning, comprehensive README, local testing, organize by functionality
- **User roles**: Plugin users (discover/install), Developers (create/distribute), Team leaders (governance/catalogs)
- **Search in installed list**: Type to filter plugins by name or description in the Installed tab
- **Auto-updates**: Toggle per marketplace; official marketplaces auto-update by default
- **SHA pinning**: Pin plugins to specific git commit SHAs for exact version control; use `sha` field in marketplace entry for reproducible builds; useful for enterprise audit trails

---

## Agents and Subagents

**What it is**: Specialized AI assistants that Claude Code can delegate tasks to. Each operates with its own separate context window and can be configured with specific system prompts, tools, and models for task-specific problem-solving.

**Documentation**: https://code.claude.com/docs/en/sub-agents

**Key concepts**:
- **Benefits**: Context preservation (separate windows prevent main conversation pollution), specialized expertise (fine-tuned instructions), reusability (work across projects), flexible permissions (different tool access levels)
- **Creation**: `/agents` then Create New Agent then Choose scope then Define/customize then Select tools then Save; or manually create Markdown files with YAML frontmatter
- **File structure**: YAML frontmatter with `name` (required, lowercase-hyphenated), `description` (required, natural language purpose), `tools` (optional, comma-separated), `model` (optional, sonnet/opus/haiku/inherit), `disallowedTools` (optional, explicit tool blocking), `permissionMode` (optional, permission behavior for specific agent)
- **File locations** (priority order): Project (`.claude/agents/`, highest), CLI flag (`--agents`, add subagents dynamically), User (`~/.claude/agents/`, lower), Plugin (`agents/` directory)
- **Usage**: Automatic delegation (Claude proactively identifies based on descriptions; use "PROACTIVELY" or "MUST BE USED" in description), Explicit invocation (direct requests to use specific subagent), @-mention support with typeahead
- **Tool access**: Inherits all tools if not specified; can restrict to specific tools via `tools` field; can explicitly block tools via `disallowedTools` field; includes MCP server tools
- **Skill auto-loading**: `skills` frontmatter field loads specific skills when subagent activates; enables specialized knowledge per subagent; skills unload when subagent completes
- **Built-in subagents**: Explore (Haiku-powered read-only codebase exploration with thoroughness levels: quick/medium/very thorough), Plan (automatic codebase research during plan mode using Read/Glob/Grep/Bash tools with Sonnet model, prevents infinite nesting), General-purpose (complex multi-step tasks with all tools), Helper agents (Bash, statusline-setup, Claude Code Guide)
- **Best practices**: Start with Claude-generated then customize, design focused subagents with single responsibilities, write detailed prompts with constraints, limit tool access to necessary only, version control project subagents
- **Advanced**: Chaining (multiple sequential subagents), dynamic selection (Claude intelligently chooses), model selection ('inherit' for consistency), subagent resumption (Claude can resume previous subagents), dynamic model choice (Claude selects model for subagent tasks)
- **Agent hooks**: Agents can define hooks in frontmatter using `hooks` field; supports `PreToolUse`, `PostToolUse`, and `Stop` events
- **Disable via Task tool**: Use `Task(AgentName)` syntax in permission deny rules to prevent specific agents from being invoked
- **Permission modes**: `permissionMode` field controls permission behavior per agent (`default`, `acceptEdits`, `dontAsk`, `bypassPermissions`, `plan`)
- **Background execution**: Agents can run in foreground (blocking with permission passthrough) or background (concurrent with auto-deny for missing permissions); MCP tools not available in background

---

## Built-in Commands

**What it is**: Claude Code's built-in slash commands for session management, configuration, and common operations. For custom commands, see Skills section above.

**Documentation**: https://code.claude.com/docs/en/interactive-mode#built-in-commands

**Key concepts**:
- **Session commands**: `/clear` (history), `/resume` (resume by name or ID), `/rename` (name session), `/teleport` (resume remote session)
- **Configuration**: `/config` (settings with search), `/model` (selection), `/permissions` (tool access), `/keybindings` (customize shortcuts)
- **Context management**: `/memory` (CLAUDE.md editing), `/compact` (reduce context), `/cost` (token usage), `/stats` (usage statistics)
- **Tools**: `/mcp` (server management), `/sandbox` (sandboxed bash), `/todos` (view task list), `/plan` (enter plan mode)
- **Help**: `/help` (usage), `/context` (view loaded context)
- **Remote**: `/remote-env` (configure remote environment)
- **MCP prompts**: Format `mcp__<server-name>__<prompt-name>` from MCP server prompts
- **Autocomplete**: Works at any position in input, not just at the beginning
- **Note**: Custom slash commands (`.claude/commands/`) have been merged into the Skills system; existing command files continue to work

---

## Hooks

**What it is**: Automated bash scripts that execute in response to specific events during Claude Code sessions, enabling custom automation, validation, and integration workflows

**Documentation**: https://code.claude.com/docs/en/hooks

**Key concepts**:
- **Execution model**: All matching hooks run in parallel with 60-second default timeout; receive JSON via stdin, return structured output to control Claude
- **Configuration locations**: `~/.claude/settings.json` (user), `.claude/settings.json` (project), `.claude/settings.local.json` (local project), enterprise managed policy, skill/agent/command frontmatter
- **11 event types**: PreToolUse (before tool execution, can modify tool inputs), PostToolUse (after completion), UserPromptSubmit (prompt submission), Notification (permission requests with matcher values for event filtering), PermissionRequest (automatically approve/deny tool permissions), Stop (main agent finish, prompt-based matching), SubagentStart (subagent begins), SubagentStop (subagent finish), SessionStart (session begins), SessionEnd (session terminates), PreCompact (before context compacting), Setup (triggered via CLI flags)
- **Setup hook**: Triggered via `--init`, `--init-only`, or `--maintenance` CLI flags; runs setup scripts for repository initialization, dependency installation, or maintenance tasks before the interactive session starts
- **Matcher patterns**: Exact (`Write`), regex (`Edit|Write`), wildcard (`*`), prompt-based (Stop hooks can match against user prompts), Notification and PermissionRequest matcher values for event-specific filtering; case-sensitive
- **Exit codes**: 0 (success, stdout to transcript), 2 (blocking error, stderr to Claude), other (non-blocking error, stderr to user)
- **JSON output**: Advanced control with `continue`, `decision`, `reason`, and hook-specific parameters
- **PreToolUse advanced features**:
  - **updatedInput parameter**: Allows modifying tool input parameters before execution; returned in JSON output to override original tool inputs
  - **ask parameter**: Triggers user confirmation dialog during hook execution; use in JSON output to prompt for approval before tool proceeds
  - **additionalContext parameter**: Adds context string to Claude before tool executes; returned in `hookSpecificOutput.additionalContext` field
- **Hook input fields**: `tool_use_id` field in PreToolUse and PostToolUse hooks enables correlation between pre/post events for same tool call
- **PermissionRequest hook**: Runs when user shown permission dialog; use decision control to allow/deny automatically; recognizes same matcher values as PreToolUse
- **Environment variables**: `CLAUDE_PROJECT_DIR` (project root path), `CLAUDE_ENV_FILE` (SessionStart persistence), `CLAUDE_CODE_REMOTE` (remote/local indicator)
- **Security warning**: Execute arbitrary shell commands automatically - validate/sanitize input, quote variables, use absolute paths, avoid sensitive files, test in safe environments
- **MCP integration**: Works with MCP tools using pattern `mcp__<server>__<tool>`
- **Debugging**: Use `claude --debug` for execution details, matched commands, exit codes, output
- **Component hooks**: Skills, agents, and slash commands can define hooks in frontmatter; scoped to component lifecycle
- **Once hooks**: `once: true` option runs hook only once per session for skills and commands
- **Prompt-based hooks**: `type: "prompt"` uses LLM to evaluate context; supported for Stop, SubagentStop, and other events

---

## Task Tool

**What it is**: Core tool allowing Claude to delegate work to specialized subagents with isolated contexts

**Documentation**: https://code.claude.com/docs/en/sub-agents

**Key concepts**:
- **Purpose**: Invoke subagents for specialized tasks while preserving main conversation context
- **Context isolation**: Each subagent operates with separate context window, preventing pollution of main conversation
- **Automatic selection**: Claude proactively identifies appropriate subagent based on task and descriptions
- **Explicit invocation**: Users can request specific subagent directly
- **Tool inheritance**: Subagents inherit or restrict tool access based on configuration
- **Result integration**: Subagent work summarized and returned to main conversation
- **Chaining support**: Multiple subagents can work sequentially on complex tasks
- **Permission control**: Can be disabled via `/permissions` or blocked with `Task(AgentName)` syntax for specific agents

---

## AskUserQuestion Tool

**What it is**: Interactive tool for asking structured multiple-choice questions during conversations

**Documentation**: https://code.claude.com/docs/en/settings (Tools Available to Claude table)

**Key concepts**:
- **Purpose**: Enables Claude to ask structured questions with multiple-choice options
- **Features**: Single-select or multi-select modes, automatic "Other" option for custom input
- **Use cases**: Gathering preferences, clarifying ambiguous requirements, plan mode decisions
- **Question structure**: Header (short label), question text, 2-4 options with label and description
- **Behavioral constraints**: 60-second timeout, 1-4 questions per call, not available in subagents spawned via Task tool
- **Permission**: No permission required for this tool
- **Ctrl+G support**: External editor (Ctrl+G) now works in AskUserQuestion input field for composing longer responses

---

## LSP Tool

**What it is**: Language Server Protocol integration for semantic code intelligence

**Documentation**: https://code.claude.com/docs/en/settings (Tools Available to Claude table)

**Key concepts**:
- **Introduced**: v2.0.74 (2025-12)
- **Purpose**: Semantic code understanding beyond grep - go-to-definition, find references, hover documentation/types
- **Benefits**: More accurate than grep, understands code structure and types
- **Capabilities**: Navigate code definitions, find all references to symbols, get type information and documentation
- **Use cases**: Codebase exploration, refactoring support, understanding code relationships
- **Likely supported languages**: TypeScript/JavaScript, Python, other LSP-compatible languages

