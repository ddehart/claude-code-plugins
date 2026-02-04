# Undocumented Features

Features mentioned in Claude Code release notes but not yet covered in official documentation. Information is based on release note descriptions and observed behavior. Details may be incomplete or subject to change.

**Latest Release**: v2.1.31

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

## Bash Timeout Duration Display

**What it is**: Display of timeout duration alongside elapsed time for Bash commands

**Introduced**: v2.1.23

**What we know**:
- Bash commands now display timeout duration alongside elapsed time
- Provides visibility into how long until a command times out
- Helps users understand command execution constraints

---

## /debug command

**What it is**: Added /debug for Claude to help troubleshoot the current session

**Introduced**: v2.1.30

**What we know**:
- Available in interactive mode for session troubleshooting
- Helps Claude analyze current session state
- Useful for debugging complex issues or session state problems

---

## Token count, tool uses, and duration metrics to Task tool results

**What it is**: Added token count, tool uses, and duration metrics to Task tool results

**Introduced**: v2.1.30

**What we know**:
- Task tool results now include token usage statistics
- Shows number of tool invocations during task execution
- Displays duration of task execution
- Enables cost and performance analysis of background tasks

**Use cases**:
- Monitor subagent efficiency and resource usage
- Understand performance characteristics of tasks
- Track token consumption for cost management

---

## Reduced motion mode

**What it is**: Added reduced motion mode to the config

**Introduced**: v2.1.30

**What we know**:
- New configuration setting to reduce animations and visual motion
- Improves accessibility for users sensitive to motion
- Follows system accessibility preferences
- Reduces visual strain during extended sessions

---

## TaskStop tool result improvement

**What it is**: Improved TaskStop tool to display the stopped command/task description in the result line instead of a generic 'Task stopped' message

**Introduced**: v2.1.30

**What we know**:
- TaskStop results now show the specific task that was stopped
- Provides better feedback about which background task was terminated
- Clearer output when managing multiple background tasks

