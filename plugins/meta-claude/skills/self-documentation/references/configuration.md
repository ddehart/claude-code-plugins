# Configuration

Settings, permissions, memory, and customization options for Claude Code.

**Last updated**: 2026-02-01

---

## Memory Management (CLAUDE.md)

**What it is**: System for retaining preferences, coding style, project conventions across sessions via memory files

**Documentation**: https://docs.anthropic.com/en/docs/claude-code/memory

**Key concepts**:
- **Memory hierarchy** (precedence order): Enterprise Policy (org-wide), Project Memory (`./CLAUDE.md` or `./.claude/CLAUDE.md`), User Memory (`~/.claude/CLAUDE.md`), Project Local (deprecated)
- **Auto-loading**: Files loaded automatically on launch; recurses up from cwd to (but not including) root directory
- **File imports**: `@path/to/file` syntax includes external docs; recursive up to 5 hops deep
- **Quick addition**: Start input with `#` to rapidly add memories (prompts for location)
- **Management**: `/memory` (edit in editor), `/init` (bootstrap CLAUDE.md for codebase)
- **Best practices**: Be specific ("2-space indentation"), organize with markdown headings, review periodically as projects evolve

---

## Modular Rules (.claude/rules/)

**What it is**: Organized, topic-specific instruction files that extend project memory with focused guidelines for code style, testing, security, and other conventions

**Documentation**: https://docs.anthropic.com/en/docs/claude-code/memory

**Key concepts**:
- **Directory structure**: Place `.md` files in `.claude/rules/` for automatic loading alongside `CLAUDE.md`
- **Path-specific rules**: Use YAML frontmatter with `paths` field for conditional rules (e.g., `paths: src/api/**/*.ts`)
- **Glob patterns**: Standard glob syntax including `**/*.ts`, `*.md`, braces `{ts,tsx}`, and multiple patterns
- **Subdirectories**: Organize rules hierarchically (e.g., `frontend/`, `backend/`) - all `.md` files discovered recursively
- **User-level rules**: Personal rules at `~/.claude/rules/` apply to all projects (lower priority than project rules)
- **Symlinks supported**: Share common rules across projects via symlinks (circular symlinks handled gracefully)
- **Best practices**: Keep rules focused (one topic per file), use descriptive filenames, use conditional paths sparingly, organize with subdirectories

---

## Model Configuration

**What it is**: Model selection, aliasing, and behavior customization for different tasks and account types

**Documentation**: https://docs.anthropic.com/en/docs/claude-code/model-config

**Key concepts**:
- **Primary aliases**: `sonnet` (4.5, daily coding), `opus` (4.5, complex reasoning), `haiku` (4.5, fast tasks), `default` (recommended for account type)
- **Special aliases**: `opusplan` (opus for plan mode, sonnet for execution), `sonnet[1m]` (million-token extended context)
- **Configuration methods** (priority order): `/model <alias>` (mid-session), `claude --model <alias>` (startup), `ANTHROPIC_MODEL` (environment), settings.json (persistent)
- **Environment variables**: ANTHROPIC_DEFAULT_OPUS_MODEL, ANTHROPIC_DEFAULT_SONNET_MODEL, ANTHROPIC_DEFAULT_HAIKU_MODEL, CLAUDE_CODE_SUBAGENT_MODEL
- **Prompt caching**: DISABLE_PROMPT_CACHING variables (global overrides model-specific)
- **Haiku 4.5**: Auto-uses Sonnet in plan mode (SonnetPlan behavior by default) for Pro users

---

## Permission Management

**What it is**: Tool usage control through allow/ask/deny rules for security and workflow customization

**Documentation**: https://docs.anthropic.com/en/docs/claude-code/settings

**Key concepts**:
- **Three modes**: Allow (auto-approve), Ask (confirmation prompt), Deny (block tool use)
- **Configuration**: settings.json at user (`~/.claude/`), project (`.claude/`, shared), or local (`.claude/settings.local.json`, personal)
- **`/permissions` command**: Manage tool permissions interactively
- **Rule format**: Array of permission rules per mode (e.g., `Bash(git push:*)`, `Read(./.env)`)
- **Wildcard equivalence**: `Bash(*)` is treated as equivalent to `Bash` (matches all commands)
- **Use cases**: Prevent dangerous operations, require confirmation for sensitive actions, enable autonomous work within boundaries
- **MCP integration**: Works with MCP tools using pattern `mcp__<server>__<tool>`
- **Wildcard MCP permissions**: Use `mcp__server__*` syntax to allow/deny all tools from a server
- **Wildcard bash patterns**: Use patterns like `Bash(npm *)` to match commands with any arguments
- **Unreachable rule warnings**: Claude Code warns when permission rules are unreachable due to precedence
- **Task tool permissions**: Use `Task(AgentName)` syntax in deny rules to prevent specific agents from being invoked (cross-reference: core-features.md Agents section for agent configuration)

---

## Configuration Backup

**What it is**: Automatic timestamped backups of configuration files with rotation

**Documentation**: https://code.claude.com/docs/en/settings

**Key concepts**:
- **Automatic backups**: Claude Code automatically creates timestamped backups of configuration files
- **Retention**: Keeps the five most recent backups to prevent data loss
- **Covered files**: settings.json, .claude.json, managed-settings.json
- **Recovery**: Enables recovery from recent config mistakes without manual backup management

---

## Sandboxing

**What it is**: Isolated execution environments using OS-level security primitives to restrict filesystem and network access

**Documentation**: https://docs.anthropic.com/en/docs/claude-code/sandboxing

**Key concepts**:
- **Activation**: `/sandbox` command enables sandboxed bash with default settings
- **Filesystem isolation**: Read/write limited to current working directory; read-only system access excluding denied directories; modifications outside cwd require permission
- **Network isolation**: Access restricted to approved domains via proxy; new domain requests trigger confirmation; restrictions apply to all subprocesses
- **OS-level enforcement**: Linux uses bubblewrap, macOS uses Seatbelt sandbox
- **Security benefits**: Protection against prompt injection, data exfiltration, malicious downloads, unauthorized API calls
- **Policy control**: `allowUnsandboxedCommands` setting disables dangerouslyDisableSandbox escape hatch at policy level for enterprise environments
- **Limitations**: Minimal performance impact; Linux and macOS only; some tools (watchman, docker) require special configuration
- **Autonomous work**: Reduces permission prompts within defined boundaries

---

## Output Styles

**What it is**: Modifications to Claude Code's system prompt that adapt it for different use cases beyond software engineering (educational, collaborative modes)

**Documentation**: https://docs.anthropic.com/en/docs/claude-code/output-styles

**Key concepts**:
- **Built-in styles**: Default (efficient software engineering), Explanatory (educational insights between tasks), Learning (collaborative with TODO(human) labels)
- **How they work**: Directly modify system prompt; exclude code-gen instructions for non-default styles, add custom guidance
- **vs other customizations**: Output styles replace default prompt entirely (vs CLAUDE.md supplements it), affect main loop only (vs Agents handle specific tasks), "stored system prompts" (vs slash commands are "stored prompts")
- **Configuration**: `/output-style` (menu), `/output-style [name]` (direct switch), `/config` menu; stored in `.claude/settings.local.json` (project level)
- **Custom styles**: Create via `/output-style:new I want...`; saved as markdown with frontmatter at `~/.claude/output-styles` (user) or `.claude/output-styles` (project)
- **Frontmatter options**: `keep-coding-instructions: true` to retain default code generation guidance when using custom styles

---

## Status Line Customization

**What it is**: Customizable bottom-of-screen display similar to shell prompts (Oh-my-zsh style), updating with conversation changes

**Documentation**: https://docs.anthropic.com/en/docs/claude-code/statusline

**Key concepts**:
- **Setup**: `/statusline` (interactive), manual configuration via `statusLine` command in settings.json
- **Display**: First line of stdout becomes status line text; supports ANSI color codes; updates max every 300ms
- **Available variables**: Model (id, display_name), Workspace (current_dir, project_dir), Cost metrics (total_cost_usd, duration, lines added/removed), Session (session_id, cwd, version, output_style)
- **Configuration format**: JSON with type ("command"), command path, and padding
- **Implementation tips**: Keep concise (one line), use emojis/colors for scannability, use `jq` for JSON parsing, ensure executable permissions

---

## Cost Tracking & Usage Management

**What it is**: Token consumption monitoring, usage limits, and cost optimization for Claude Code sessions

**Documentation**: https://docs.anthropic.com/en/docs/claude-code/costs

**Key concepts**:
- **Average costs**: $6/developer/day typical; below $12/day for 90% of users
- **`/cost` command**: Session-level token statistics (total cost, API duration, wall-clock time, code changes); not intended for Claude Max/Pro subscribers
- **`/usage` command**: Plan usage limits and rate limit status for subscription plans
- **Budget controls**: `--max-budget-usd` flag sets spending limit per session (SDK/headless mode)
- **Rate limit recommendations**: 200k-300k TPM for small teams (1-5 users), scaling down to 10k-15k TPM for 500+ user organizations
- **Plan management**: Workspace spend limits via Claude Console (Admin role required); historical usage reporting; automatic "Claude Code" workspace creation
- **Cost optimization**: Auto-compaction at 95% capacity, specific queries, task breakdown, clearing history between sessions

---

## Attribution Setting

**What it is**: Configuration to customize commit and PR bylines for Claude-generated content

**Documentation**: https://docs.anthropic.com/en/docs/claude-code/settings

**Key concepts**:
- New `attribution` setting replaces deprecated `includeCoAuthoredBy`
- More flexible control over how Claude's contributions are credited
- Allows customizing or disabling the Co-Authored-By line
- Separate configuration for commits (using git trailers) and pull requests (plain text)

**Configuration**:
```json
{
  "attribution": {
    "commit": "Generated with Claude Code\n\nCo-Authored-By: Claude <noreply@anthropic.com>",
    "pr": "Generated with Claude Code"
  }
}
```

---

## Language Setting

**What it is**: Configure Claude's preferred response language

**Documentation**: https://docs.anthropic.com/en/docs/claude-code/settings

**Key concepts**:
- Set `language` in settings.json to specify preferred response language
- Examples: `"japanese"`, `"spanish"`, `"french"`
- Claude will respond in this language by default
- Useful for international teams or non-English workflows

**Configuration**:
```json
{
  "language": "japanese"
}
```

---

## respectGitignore Setting

**What it is**: Control whether @ file picker respects .gitignore patterns

**Documentation**: https://docs.anthropic.com/en/docs/claude-code/settings

**Key concepts**:
- When `true` (default), files matching `.gitignore` patterns are excluded from `@` file suggestions
- Set to `false` to include all files regardless of gitignore status
- Per-project configuration available

**Configuration**:
```json
{
  "respectGitignore": false
}
```

---

## showTurnDuration Setting

**What it is**: Configuration option to hide turn duration messages

**Documentation**: https://docs.anthropic.com/en/docs/claude-code/settings

**Key concepts**:
- Setting to control display of turn duration messages (e.g., "Cooked for 1m 6s")
- Set to `false` to hide these messages
- Helps reduce visual clutter for users who don't need timing info
- Defaults to `true`

**Configuration**:
```json
{
  "showTurnDuration": false
}
```

---

## plansDirectory Setting

**What it is**: Customize where plan files are stored

**Documentation**: https://docs.anthropic.com/en/docs/claude-code/settings

**Key concepts**:
- Customize the directory where plan files are saved
- Path is relative to project root
- Default: `~/.claude/plans`

**Configuration**:
```json
{
  "plansDirectory": "./plans"
}
```

---

## Auto MCP Tool Search

**What it is**: Automatic threshold-based tool search that activates when MCP tool definitions exceed context budget

**Documentation**: https://code.claude.com/docs/en/mcp#scale-with-mcp-tool-search

**Key concepts**:
- Automatically enables when MCP tool descriptions exceed 10% of context window (default)
- Controlled via `ENABLE_TOOL_SEARCH` environment variable
- Values: `auto` (default 10%), `auto:N` (custom threshold %), `true` (always on), `false` (disabled)
- MCP tools are deferred and loaded on-demand instead of preloaded
- Only works with models supporting `tool_reference` blocks (Sonnet 4+, Opus 4+)
- Can also be disabled via `disallowedTools` setting by denying the MCPSearch tool

**Configuration**:
```bash
ENABLE_TOOL_SEARCH=auto:5 claude  # Custom 5% threshold
```

---

## Ctrl-G External Editor

**What it is**: Keyboard shortcut to edit prompts in system's configured text editor

**Documentation**: https://docs.anthropic.com/en/docs/claude-code/interactive-mode

**Key concepts**:
- Press Ctrl-G to open current prompt in external editor
- Useful for composing long or complex prompts
- Uses $EDITOR or $VISUAL environment variables

**Expected workflow**:
1. Start typing prompt in Claude Code
2. Press Ctrl-G to open in editor
3. Compose/edit in full editor (Vim, VS Code, nano, etc.)
4. Save and close editor
5. Content returns to Claude Code prompt

---

## File Read Token Limit

**What it is**: Override default token limit for file reads

**Documentation**: https://docs.anthropic.com/en/docs/claude-code/settings

**Key concepts**:
- `CLAUDE_CODE_FILE_READ_MAX_OUTPUT_TOKENS` environment variable
- Overrides the default token limit for file reads
- Useful when you need to read larger files in full
- Set before starting Claude Code session

**Configuration**:
```bash
export CLAUDE_CODE_FILE_READ_MAX_OUTPUT_TOKENS=50000
claude
```

---

## Tools Interactive Mode Flag

**What it is**: CLI flag to control tool availability in interactive mode

**Documentation**: https://docs.anthropic.com/en/docs/claude-code/cli-reference

**Key concepts**:
- `--tools` flag controls which tools are available in interactive mode
- Useful for restricting capabilities in specific contexts
- Can be combined with permission settings for fine-grained control

**Configuration**:
```bash
claude --tools Read,Grep,Glob
```

---

## Release Channel Toggle

**What it is**: Configuration option to select update channel (stable vs latest)

**Documentation**: https://docs.anthropic.com/en/docs/claude-code/settings

**Key concepts**:
- `autoUpdatesChannel` setting in settings.json
- `stable` channel (about one week old, skips major regressions) vs `latest` (default, most recent release)
- Toggle via `/config` command or settings.json
- Helps balance new features vs stability

**Configuration**:
```json
{
  "autoUpdatesChannel": "stable"
}
```

---

## Customizable Spinner Verbs

**What it is**: Setting to customize the spinner verb text shown during operations

**Documentation**: https://code.claude.com/docs/en/settings

**Key concepts**:
- **Setting name**: `spinnerVerbs` in settings.json
- **Modes**: `append` (add to default verbs) or `replace` (completely replace defaults)
- **Default verbs**: "Thinking", "Cooking", etc.
- **Customization**: Add personalized verbs for UI feedback during operations

**Configuration**:
```json
{
  "spinnerVerbs": {
    "mode": "append",
    "verbs": ["Pondering", "Contemplating"]
  }
}
```

---

## Thinking Mode

**What it is**: Enable extended thinking for complex reasoning tasks

**Documentation**: https://docs.anthropic.com/en/docs/claude-code/common-workflows

**Key concepts**:
- Enable via Alt+T keyboard shortcut (after running `/terminal-setup`)
- Toggle is sticky across sessions
- Enabled by default for Opus 4.5 model
- Improves performance on complex reasoning and coding tasks
- Impacts prompt caching efficiency
- Can be configured via `alwaysThinkingEnabled` setting
- Token budget controlled by `MAX_THINKING_TOKENS` environment variable

---

## CLAUDE_BASH_NO_LOGIN Environment Variable

**What it is**: Skip login shell initialization for faster bash command execution

**Documentation**: https://docs.anthropic.com/en/docs/claude-code/settings (Environment variables table)

**Key concepts**:
- Set `CLAUDE_BASH_NO_LOGIN=1` to skip loading .bash_profile, .profile, etc.
- Trade-off: faster execution but may miss custom aliases, functions, PATH entries
- Useful for simple commands, containers, or performance-critical workflows

**Configuration**:
```bash
export CLAUDE_BASH_NO_LOGIN=1
claude
```

---

## CLAUDE_CODE_TMPDIR Environment Variable

**What it is**: Override default temporary directory location

**Documentation**: https://docs.anthropic.com/en/docs/claude-code/settings (Environment variables table)

**Key concepts**:
- Introduced in v2.1.5
- Set `CLAUDE_CODE_TMPDIR` to customize where Claude Code stores temporary files
- Useful for systems with limited /tmp space or custom temp directory requirements
- Helps manage disk space in constrained environments

**Configuration**:
```bash
export CLAUDE_CODE_TMPDIR=/custom/tmp/path
claude
```

---

## CLAUDE_CODE_DISABLE_BACKGROUND_TASKS Environment Variable

**What it is**: Disable all background task functionality

**Documentation**: https://docs.anthropic.com/en/docs/claude-code/settings (Environment variables table)

**Key concepts**:
- Set `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1` to disable background tasks
- Disables `run_in_background` parameter on Bash and subagent tools
- Disables auto-backgrounding of long-running commands
- Disables Ctrl+B backgrounding shortcut
- Useful for environments where background execution is problematic

**Configuration**:
```bash
export CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1
claude
```

---

## CLAUDE_CODE_HIDE_ACCOUNT_INFO Environment Variable

**What it is**: Hide personal account information from Claude Code UI

**Documentation**: https://docs.anthropic.com/en/docs/claude-code/settings (Environment variables table)

**Key concepts**:
- Set `CLAUDE_CODE_HIDE_ACCOUNT_INFO=1` to hide email address and organization name
- Replaces IS_DEMO environment variable for broader use cases
- Useful when streaming, recording, or presenting Claude Code sessions
- Helps protect privacy in public demonstrations

**Configuration**:
```bash
export CLAUDE_CODE_HIDE_ACCOUNT_INFO=1
claude
```

---

## CLAUDE_CODE_ENABLE_TASKS Environment Variable

**What it is**: Toggle between the new task management system and the previous TODO list

**Documentation**: https://code.claude.com/docs/en/settings

**Key concepts**:
- Set `CLAUDE_CODE_ENABLE_TASKS=false` to revert to previous TODO list instead of task tracking system
- Default is `true` (new task management system enabled)
- Provides fallback for users experiencing issues with the new task system
- Task system provides dependency tracking, TaskCreate/TaskUpdate/TaskGet/TaskList tools

**Configuration**:
```bash
CLAUDE_CODE_ENABLE_TASKS=false claude
```

---

## --add-dir CLI Flag

**What it is**: Add additional working directories for Claude to access

**Documentation**: https://code.claude.com/docs/en/cli-reference

**Key concepts**:
- Add additional working directories beyond the current working directory
- Validates each path exists as a directory before accepting
- Supports loading CLAUDE.md files from additional directories
- Useful for monorepos or projects with multiple related directories

**Configuration**:
```bash
claude --add-dir ../apps ../lib
```
