# Undocumented Features

Features mentioned in Claude Code release notes but not yet covered in official documentation. Information is based on release notes descriptions and behavioral understanding. Details may be incomplete or subject to change.

**Latest Release**: v2.1.12 (as of 2026-01-19)

---

## Real-time Thinking in Transcript Mode

**What it is**: Show thinking blocks in real-time when verbose output is enabled

**Introduced**: v2.1.0

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

## Auto MCP Tool Search

**What it is**: Automatic threshold-based tool search that activates when MCP tool definitions exceed context budget

**Introduced**: v2.1.9

**What we know**:
- `auto:N` syntax for configuring threshold (e.g., `auto:5` for 5%)
- Default is `auto` which activates at 10% of context window
- Can be configured via `ENABLE_TOOL_SEARCH` environment variable
- Values: `auto` (default 10%), `auto:N` (custom %), `true` (always on), `false` (disabled)

**Expected configuration**:
```bash
ENABLE_TOOL_SEARCH=auto:5 claude  # Custom 5% threshold
```

---

## Permission Prompt Feedback

**What it is**: Ability to provide feedback when accepting permission prompts

**Introduced**: v2.1.7

**What we know**:
- Users can now provide feedback when accepting permission prompts
- Helps improve permission system based on user experience
- Likely integrated into permission dialog UI

**Use cases**:
- Report overly restrictive permissions
- Suggest better permission defaults
- Help Anthropic improve permission UX

---

## Agent Final Response in Task Notifications

**What it is**: Display of agent's final response inline in task completion notifications

**Introduced**: v2.1.7

**What we know**:
- Task notifications now show the agent's final response inline
- Provides context without needing to check task details separately
- Improves visibility into what agents accomplished

**Expected behavior**:
- Background task completes
- Notification shows both completion status and agent's summary
- Reduces need to navigate to task details

---

## OAuth/API Console URL Update

**What it is**: URL change for OAuth and API Console from anthropic.com to platform.claude.com

**Introduced**: v2.1.7

**What we know**:
- OAuth and API Console URLs now point to platform.claude.com
- Previously used anthropic.com domain
- Likely part of infrastructure consolidation

**Updated URLs**:
- OAuth: platform.claude.com/oauth
- API Console: platform.claude.com/console

---

## External Editor in AskUserQuestion

**What it is**: Ctrl+G external editor support when responding to AskUserQuestion input prompts

**Introduced**: v2.1.9

**What we know**:
- External editor (Ctrl+G) now works in AskUserQuestion input field
- Enables composing longer responses in your preferred editor
- Consistent with main prompt external editor support

**Expected workflow**:
1. Claude asks question via AskUserQuestion
2. Press Ctrl+G to open response in external editor
3. Compose answer in editor, save and close
4. Response returns to Claude Code

---

## Session URL Attribution in Git

**What it is**: Automatic attribution of session URLs to commits and PRs from web sessions

**Introduced**: v2.1.9

**What we know**:
- Web sessions now add session URL attribution to commits and PRs
- Helps trace git activity back to originating web session
- Improves audit trail for web-based workflows

**Expected format**:
- Commit/PR includes URL to originating claude.ai session
- Enables jumping from git history to conversation context

---

## PreToolUse Hooks with additionalContext

**What it is**: PreToolUse hooks can now return `additionalContext` field to inject context before tool execution

**Introduced**: v2.1.9

**What we know**:
- `hookSpecificOutput.additionalContext` adds string to Claude's context before tool runs
- Enables hooks to provide dynamic context based on tool inputs
- Useful for environment info, warnings, or situational guidance

**Example use case**:
- Hook detects production database command
- Returns `additionalContext: "CAUTION: You are targeting PRODUCTION database"`
- Claude sees this context before executing the tool

---

## ${CLAUDE_SESSION_ID} Substitution in Skills

**What it is**: String substitution variable for current session ID in Skill files

**Introduced**: v2.1.9

**What we know**:
- Skills can use `${CLAUDE_SESSION_ID}` for session-specific operations
- Useful for logging, session-specific files, or correlation
- Substituted at runtime with actual session ID

**Example**:
```markdown
---
name: session-logger
description: Log activity for this session
---

Log the following to logs/${CLAUDE_SESSION_ID}.log:
$ARGUMENTS
```

---

## Copy OAuth URL Keyboard Shortcut

**What it is**: Keyboard shortcut 'c' to copy OAuth URL when browser doesn't open during login

**Introduced**: v2.1.10

**What we know**:
- Press 'c' to copy OAuth URL to clipboard during login
- Useful when browser auto-open fails
- Improves login experience in restricted environments

**Expected workflow**:
1. Start login process
2. Browser fails to open automatically
3. Press 'c' to copy URL to clipboard
4. Paste URL manually in browser

---

## Install Count Display in VSCode Plugin Listings

**What it is**: Display of installation counts for plugins in VS Code extension

**Introduced**: v2.1.10

**What we know**:
- Plugin listings in VSCode extension now show install counts
- Helps users assess plugin popularity and community adoption
- Provides social proof for plugin discovery

---

## Trust Warning for Plugin Installation in VSCode

**What it is**: Warning dialog when installing plugins via VSCode extension

**Introduced**: v2.1.10

**What we know**:
- VSCode extension shows trust warning before plugin installation
- Improves security awareness when adding third-party plugins
- Aligns with VSCode security best practices

---

## Startup Keystroke Capture Improvement

**What it is**: Enhanced startup to capture keystrokes before REPL is fully ready

**Introduced**: v2.1.10

**What we know**:
- Startup improved to capture keystrokes earlier
- Prevents lost input during Claude Code initialization
- Improves responsiveness during startup phase

**Benefits**:
- No need to wait for full REPL readiness before typing
- Faster perceived startup time
- Better user experience for quick commands

---

## File Suggestions as Removable Attachments

**What it is**: Enhanced display of file suggestions as removable attachments in the UI

**Introduced**: v2.1.10

**What we know**:
- File suggestions now display as removable attachments
- Improves clarity of which files are included in context
- Allows easy removal before sending prompt

**Expected behavior**:
- Suggest files with @-mention
- Files appear as attachment chips
- Click to remove unwanted suggestions before submit

---

## JavaScript Template Literals in Heredocs Fix

**What it is**: Fix for crash when running bash commands with heredocs containing JavaScript template literals

**Introduced**: v2.1.10

**What we know**:
- Previously crashed when heredocs contained JavaScript template literals (backticks with ${})
- Now handles these correctly without crashing
- Improves reliability for complex bash scripts

**Example scenario**:
```bash
cat << 'EOF' > script.js
const message = `Hello ${name}`;
EOF
```

---

## Excessive MCP Connection Requests Fix

**What it is**: Fix for excessive MCP connection requests for HTTP/SSE transports

**Introduced**: v2.1.11

**What we know**:
- Previously made too many connection requests to HTTP/SSE MCP servers
- Fixed to reduce connection overhead
- Improves performance and reduces server load

---

## Message Rendering Bug Fix

**What it is**: Fix for message rendering issues

**Introduced**: v2.1.12

**What we know**:
- Fixed bug affecting message rendering
- Details not specified in release notes
- Likely visual or formatting issue in conversation display
