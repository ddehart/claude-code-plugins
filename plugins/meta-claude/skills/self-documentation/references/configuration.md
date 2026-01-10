# Configuration

Settings, permissions, memory, and customization options for Claude Code.

**Last updated**: 2025-01-09

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
- **`/permissions` command**: Manage tool permissions interactively (v1.0.7+)
- **Rule format**: Array of permission rules per mode (e.g., `Bash(git push:*)`, `Read(./.env)`)
- **Use cases**: Prevent dangerous operations, require confirmation for sensitive actions, enable autonomous work within boundaries
- **MCP integration**: Works with MCP tools using pattern `mcp__<server>__<tool>`
- **Wildcard MCP permissions** (v2.0.70): Use `mcp__server__*` syntax to allow/deny all tools from a server

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

**Introduced**: v2.0.62 (2025-12)

**What we know**:
- New `attribution` setting replaces deprecated `includeCoAuthoredBy`
- More flexible control over how Claude's contributions are credited
- Allows customizing or disabling the Co-Authored-By line

**Configuration**:
```json
{
  "attribution": {
    "enabled": true,
    "format": "co-author"
  }
}
```
