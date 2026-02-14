# Undocumented Features

Features mentioned in Claude Code release notes but not yet covered in official documentation. Information is based on release note descriptions and observed behavior. Details may be incomplete or subject to change.

**Latest Release**: v2.1.42

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

## Per-User Temp Directory Isolation

**What it is**: Isolated temporary directories for each user to prevent permission conflicts

**Introduced**: v2.1.23

**What we know**:
- Fixed per-user temp directory isolation preventing permission conflicts on shared systems
- Each user gets their own isolated temp directory
- Prevents conflicts when multiple users run Claude Code on same system

---

## TaskStop tool result improvement

**What it is**: Improved TaskStop tool to display the stopped command/task description in the result line instead of a generic 'Task stopped' message

**Introduced**: v2.1.30

**What we know**:
- TaskStop results now show the specific task that was stopped
- Provides better feedback about which background task was terminated
- Clearer output when managing multiple background tasks

---

## Summarize from Here Feature

**What it is**: Added 'Summarize from here' option to the message selector for creating summaries from selected points

**Introduced**: v2.1.32

**What we know**:
- Available in interactive mode message selector
- Allows creating summaries from specific conversation points
- Useful for extracting relevant context from long conversations

---

## Extended Thinking Interruption Handling

**What it is**: Improved handling for extended thinking interruption

**Introduced**: v2.1.33

**What we know**:
- Improved robustness when extended thinking is interrupted
- Better error handling during thinking phase
- More graceful fallback to standard reasoning

---

## Heredoc Delimiter Parsing Security Improvement

**What it is**: Improved heredoc delimiter parsing to prevent command smuggling

**Introduced**: v2.1.38

**What we know**:
- Enhanced security in bash command parsing
- Prevents potential command injection via heredoc delimiters
- Protects against sophisticated shell command attacks

---

## Blocked Writes to .claude/skills in Sandbox Mode

**What it is**: Blocked writes to .claude/skills directory in sandbox mode for security

**Introduced**: v2.1.38

**What we know**:
- Sandbox mode now prevents writing to .claude/skills directory
- Prevents potential skill injection attacks from sandboxed code
- Improves security isolation in sandboxed environments

---

## Claude Auth Login/Status/Logout CLI Subcommands

**What it is**: New CLI subcommands for authentication: claude auth login, claude auth status, and claude auth logout

**Introduced**: v2.1.41

**What we know**:
- Three new authentication-related commands added to CLI
- Allows authentication management from terminal directly
- Provides status checking and explicit logout capability

**Available commands**:
- `claude auth login` - Authenticate with Claude Code
- `claude auth status` - Check current authentication status
- `claude auth logout` - Logout from current session

---

## File Resolution for @-mentions with Anchor Fragments

**What it is**: Improvements to file resolution for @-mentions with anchor fragments

**Introduced**: v2.1.41

**What we know**:
- Enhanced resolution of @-mentions when using anchor fragments
- Allows more precise file and location references
- Improves file suggestion accuracy

---

## Windows ARM64 Native Binary Support

**What it is**: Added Windows ARM64 (win32-arm64) native binary support

**Introduced**: v2.1.41

**What we know**:
- Native binary support for Windows running on ARM64 processors
- Previously required emulation on ARM-based Windows systems
- Improves performance on modern ARM-based Windows devices

---

## Startup Performance Improvements

**What it is**: Improved startup performance by deferring Zod schema construction

**Introduced**: v2.1.42

**What we know**:
- Startup process optimized with deferred schema validation
- Reduces initialization time for sessions
- Particularly beneficial for frequently-started sessions

---

## Prompt Cache Hit Rate Optimization

**What it is**: Improved prompt cache hit rates by moving date out of system prompt

**Introduced**: v2.1.42

**What we know**:
- System prompt refactored to improve cache efficiency
- Date moved to user context instead of system prompt
- Increases cache hit rates and reduces API costs
- Results in better token usage for sessions

---

## One-time Opus 4.6 Callout for Eligible Users

**What it is**: One-time Opus 4.6 callout for eligible users

**Introduced**: v2.1.42

**What we know**:
- One-time notification for users eligible to use Opus 4.6
- Appears in Claude Code when user qualifies
- Informs users about new model availability

---

## Guard Against Launching Claude Code Inside Another Session

**What it is**: Added guard against launching Claude Code inside another Claude Code session

**Introduced**: v2.1.41

**What we know**:
- Detects when Claude Code is launched from within another Claude Code session
- Prevents accidental nested session launch
- Shows warning or error to prevent user confusion
