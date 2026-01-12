# Undocumented Features

Features mentioned in Claude Code release notes but not yet covered in official documentation. Information is based on release note descriptions and behavioral understanding. Details may be incomplete or subject to change.

**Latest Release**: v2.1.3 (as of 2026-01-09)

---

## Explore Subagent

**What it is**: Built-in Haiku-powered subagent for efficient codebase exploration and searching

**Introduced**: v2.0.17 (2025-02)

**What we know**:
- Automatically invoked when main Claude needs to search through codebase
- Uses Haiku model for speed and context efficiency
- Designed to answer questions like "Where are errors handled?" or "How does authentication work?"
- Has access to Glob, Grep, and Read tools for codebase navigation
- Operates in separate context window to preserve main conversation tokens

**Likely trigger patterns**:
- Questions about code location ("Where is X defined?")
- Architectural questions ("How does Y work?")
- Pattern discovery ("Find all instances of Z")
- Codebase exploration without specific file paths

**Unanswered questions**:
- Exact description/trigger conditions used for automatic invocation
- Full list of available tools
- Whether it can be explicitly invoked or customized

---

## AskUserQuestion Tool

**What it is**: Tool enabling Claude to ask structured multiple-choice questions during conversations

**Introduced**: v2.0.21 (2025-03)

**What we know**:
- Allows Claude to present questions with structured options
- Supports multi-select (choose multiple answers) and single-select modes
- Particularly active in plan mode
- Questions include header (short label), main question text, and 2-4 options
- Each option has label and description explaining implications
- "Other" option automatically provided for custom input

**Typical use cases**:
- Plan mode: "Which approach do you prefer for authentication?"
- Implementation choices: "Which library should we use?"
- User preference gathering: "What features should I prioritize?"
- Clarifying ambiguous requirements before implementation

**Unanswered questions**:
- Full parameter schema and capabilities
- How Claude decides when to ask vs. make assumptions
- Whether users can configure question frequency

---

## Ctrl-G External Editor

**What it is**: Keyboard shortcut to edit prompts in system's configured text editor

**Introduced**: v2.0.10 (2024-12)

**What we know**:
- Press Ctrl-G to open current prompt in external editor
- Useful for composing long or complex prompts
- Likely uses $EDITOR or $VISUAL environment variables

**Expected workflow**:
1. Start typing prompt in Claude Code
2. Press Ctrl-G to open in editor
3. Compose/edit in full editor (Vim, VS Code, nano, etc.)
4. Save and close editor
5. Content returns to Claude Code prompt

---

## @-mention to Toggle MCP Servers

**What it is**: Enable or disable MCP servers by @-mentioning their names

**Introduced**: v2.0.10 (2024-12), refined in v2.0.14

**What we know**:
- @-mention an MCP server name to toggle its enabled/disabled state
- Alternative to using `/mcp` menu for quick server management
- Provides visual confirmation of new state

**Practical uses**:
- Quickly disable expensive MCP servers when not needed
- Enable specialized servers only for specific tasks
- Manage token usage by controlling active tools

---

## Auto-background Long-running Bash Commands

**What it is**: Automatic backgrounding of bash commands that exceed timeout instead of killing them

**Introduced**: v2.0.19 (2025-03)

**What we know**:
- Long-running commands automatically move to background instead of timing out
- Controlled by BASH_DEFAULT_TIMEOUT_MS environment variable
- Complements manual Ctrl-B backgrounding feature

**Behavior change**:
- **Before v2.0.19**: Commands hitting timeout were terminated
- **After v2.0.19**: Commands hitting timeout automatically background
- Claude can continue working while command runs
- Output can be checked later via BashOutput tool

**Configuration**:
- Set `BASH_DEFAULT_TIMEOUT_MS` to control timeout threshold
- Default appears to be 120000ms (2 minutes)
- `BASH_MAX_TIMEOUT_MS` sets maximum allowed timeout

---

## MCP structuredContent Field Support

**What it is**: Support for structured content in MCP tool responses beyond plain text

**Introduced**: v2.0.21 (2025-03)

**What we know**:
- MCP servers can now return `structuredContent` field in tool responses
- Enables richer tool outputs with formatting, hierarchy, or specialized data structures
- Part of Model Context Protocol specification

**Likely capabilities**:
- Structured data formats (JSON, tables, lists)
- Rich formatting (bold, italic, code blocks)
- Hierarchical content organization

---

## MCP headersHelper Configuration

**What it is**: Dynamic header generation for MCP servers via helper script

**Introduced**: v1.0.119 (2025-01)

**What we know**:
- Configure `headersHelper` in MCP server config to run a script that outputs HTTP headers
- Script outputs JSON with header key-value pairs
- Enables OAuth token refresh, short-lived API keys, and dynamic authentication

**Configuration**:
```json
{
  "mcpServers": {
    "my-server": {
      "command": "...",
      "headersHelper": "/path/to/script.sh"
    }
  }
}
```

---

## CLAUDE_BASH_NO_LOGIN Environment Variable

**What it is**: Skip login shell initialization for faster bash command execution

**Introduced**: v1.0.124 (2025-02)

**What we know**:
- Set `CLAUDE_BASH_NO_LOGIN=1` to skip loading .bash_profile, .profile, etc.
- Trade-off: faster execution but may miss custom aliases, functions, PATH entries
- Useful for simple commands, containers, or performance-critical workflows

---

## Auto-Allowed Tools

**What it is**: Pre-approved tools that bypass permission prompts for common, safe operations

**Introduced**: Permission system (v1.0.7+)

**What we know**:
- Certain tool patterns auto-approve in "Ask" permission mode
- Configured in settings.json `permissions.allow` arrays
- Common patterns: WebSearch, safe bash commands (git log, npm test), WebFetch for documentation domains, MCP read operations
- Users can override with explicit Deny rules
- Project settings can add project-specific allowed patterns

---

## Bash Permission Rule Matching

**What it is**: Advanced pattern matching rules for Bash tool permissions including output redirection handling

**Introduced**: Core permission system, enhanced in v1.0.123 (output redirection)

**What we know**:
- Permission rules support sophisticated pattern matching
- System prompt indicates: "Bash permission rules now support output redirections when matching"
- Example: `Bash(python:*)` matches `python script.py > output.txt`

**Pattern matching details**:
- Wildcard support: `Bash(git:*)` matches all git commands
- Output redirection awareness: Rules match command before redirect operators
- Environment variable handling: Inline env vars in commands

**Rule format examples**:
- `Bash(git push:*)` - Allow all git push variations
- `Bash(npm run test:*)` - Allow all test scripts
- `Bash(python:*)` - Allow python commands (including output redirection)

---

## SubagentStart Hook Event

**What it is**: Hook event that fires when a subagent begins execution

**Introduced**: v2.0.43 (2025-11)

**What we know**:
- New hook event type added to the existing hook events
- Complements existing `SubagentStop` hook for complete subagent lifecycle monitoring
- Enables custom automation at subagent initialization

**Expected use cases**:
- Logging/monitoring when specific subagents activate
- Pre-execution validation or setup for subagent tasks
- Custom initialization logic before subagent begins work

---

## Custom Agent permissionMode Field

**What it is**: Configuration field controlling permission behavior for specific custom agents

**Introduced**: v2.0.43 (2025-11)

**What we know**:
- New frontmatter field for custom agent definitions
- Allows per-agent permission policies independent of global settings
- Likely controls auto-approve, ask, or deny behavior for agent's tool usage

**Example configuration**:
```yaml
---
name: trusted-test-runner
description: Run test suites without permission prompts
permissionMode: allow
tools: Bash
---
```

---

## Subagent Skills Frontmatter Field

**What it is**: Configuration to auto-load specific skills when a subagent activates

**Introduced**: v2.0.43 (2025-11)

**What we know**:
- New frontmatter field: `skills: skill-name-1, skill-name-2`
- Skills load when subagent activates, unload when it completes
- Enables specialized expertise per subagent without global loading

**Example**:
```yaml
---
name: code-reviewer
description: Review code changes
skills: code-quality-standards, security-patterns
---
```

---

## Web Background Tasks with & Syntax

**What it is**: Send long-running tasks to Claude Code web by prefixing messages with `&`

**Introduced**: v2.0.45 (2025-11)

**What we know**:
- Start message with `&` in CLI to transfer task to web interface
- Enables continuing CLI work while task runs on web
- Similar to Ctrl-B (background bash) but cross-platform

---

## Opus 4.5 Model

**What it is**: Claude's newest frontier model with enhanced capabilities

**Introduced**: v2.0.51 (2025-11), Pro access added v2.0.58 (2025-12)

**What we know**:
- Model ID: `claude-opus-4-5-20251101`
- Accessible via `/model` selector or `--model opus`
- Thinking mode enabled by default for Opus 4.5 (v2.0.67)
- Pro users have full access included in subscription

**Model selection context**:
- Fits into existing model hierarchy: haiku (fast), sonnet (balanced), opus (complex reasoning)
- `opus` alias now defaults to Opus 4.5
- Works with opusplan mode (opus for planning, sonnet for execution)
- Thinking mode can be toggled with Alt+T (sticky across sessions)

---

## LSP Tool (Language Server Protocol)

**What it is**: Code intelligence tool for go-to-definition, find references, and hover documentation

**Introduced**: v2.0.74 (2025-12)

**What we know**:
- Leverages language servers for semantic code understanding
- Capabilities: go-to-definition, find references, hover documentation/types
- More accurate than grep - understands code structure and types
- Complements Glob and Grep with semantic search

**Likely supported languages**: TypeScript/JavaScript, Python, other LSP-compatible languages

---

## fileSuggestion Setting

**What it is**: Configuration to customize the `@` file search behavior with custom commands

**Introduced**: v2.0.65 (2025-12)

**What we know**:
- New `fileSuggestion` setting in settings.json
- Enables customizing how `@` file suggestions work
- Can use external tools like `fzf`, `fd`, or custom scripts

**Expected configuration**:
```json
{
  "fileSuggestion": {
    "command": "fd --type f"
  }
}
```

---

## CLAUDE_CODE_SHELL Environment Variable

**What it is**: Environment variable to override automatic shell detection

**Introduced**: v2.0.65 (2025-12)

**What we know**:
- Set `CLAUDE_CODE_SHELL` to specify shell executable
- Useful when login shell differs from preferred working shell
- Helps with environments where shell detection fails

**Configuration example**:
```bash
export CLAUDE_CODE_SHELL=/bin/zsh
```

---

## IS_DEMO Environment Variable

**What it is**: Environment variable to indicate demo/streaming mode

**Introduced**: v2.1.0 (2026-01)

**What we know**:
- Set `IS_DEMO=1` when streaming or recording sessions
- Likely affects UI presentation (hide personal info, clean up output)
- Helps with presentation modes for demos and content creation

**Expected configuration**:
```bash
export IS_DEMO=1
claude
```

---

## Teleport and Remote-Env Commands

**What it is**: Resume remote sessions from claude.ai in the CLI

**Introduced**: v2.1.0 (2026-01)

**What we know**:
- `/teleport` - Resume a remote session by ID or open picker
- `/remote-env` - Configure remote session environment
- Claude.ai subscribers can sync sessions between web and CLI
- Enables starting work on web, continuing in CLI seamlessly

**Expected workflow**:
1. Start session on claude.ai
2. Use `/teleport` in CLI to resume that session
3. Work continues with full CLI capabilities
4. Changes sync back to web session

---

## Unreachable Permission Rule Warnings

**What it is**: Warnings for permission rules that can never match due to precedence

**Introduced**: v2.1.3 (2026-01)

**What we know**:
- Claude Code warns when permission rules are unreachable
- Helps debug complex permission configurations
- Indicates when a more specific rule shadows a broader one

**Example warning scenario**:
```json
{
  "permissions": {
    "allow": [
      "Bash(git:*)",
      "Bash(git status:*)"  // Unreachable - already covered by git:*
    ]
  }
}
```

---

## Real-time Thinking in Transcript Mode

**What it is**: Show thinking blocks in real-time when verbose output is enabled

**Introduced**: v2.1.0 (2026-01)

**What we know**:
- Ctrl+O verbose/transcript mode now shows thinking blocks as they stream
- Previously thinking blocks only appeared after completion
- Enables watching Claude's reasoning process in real-time
- Useful for understanding complex decision-making

---

## Claude in Chrome Improvements

**What it is**: Enhanced Chrome extension capabilities for browser control

**Introduced**: Multiple versions (v2.0.72+, ongoing improvements)

**What we know**:
- Chrome extension at https://claude.ai/chrome
- Enables browser automation: navigate, read content, interact with elements, take screenshots
- More powerful than WebFetch - active browser control vs. passive fetching
- Continuous improvements to capabilities and reliability

**Use cases**:
- Web application testing
- Form automation
- Content extraction
- UI verification

---

## VSCode Extension Updates

**What it is**: Ongoing improvements to the VS Code extension

**Introduced**: Various versions (v2.0.74+, ongoing)

**What we know**:
- Regular feature parity improvements with CLI
- Performance enhancements
- UI/UX refinements
- Bug fixes and stability improvements

**Recent improvements** (general pattern):
- Better integration with VS Code features
- Improved session management
- Enhanced diff viewing
- More responsive UI updates

---

## Integration Pattern: Skills + Subagents

**Problem**: You want specialized knowledge available for both user questions AND automation workflows, without duplicating logic.

**Solution**: Create a skill with the expertise, configure subagent to auto-load it.

**Example: npm-update-advisor + package-updater**

```yaml
# Skill: Contains npm diagnostic logic
name: npm-update-advisor
description: Analyzes npm update strategies based on semver, lock files...

# Subagent: Orchestrates package updates, loads skill
name: package-updater
skills: npm-update-advisor
tools: Bash, Read
```

**Result:**
- User asks npm questions → Skill triggers in main conversation
- Security automation runs → Subagent loads skill for smart decisions
- Single source of truth, dual contexts
