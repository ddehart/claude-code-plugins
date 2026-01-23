# Undocumented Features

Features mentioned in Claude Code release notes but not yet covered in official documentation. Information is based on release note descriptions and observed behavior. Details may be incomplete or subject to change.

**Latest Release**: v2.1.17

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

## Plugin Pinning to Git Commit SHAs

**What it is**: Support for pinning plugins to specific git commit SHAs for exact version control

**Introduced**: v2.1.14

**What we know**:
- Marketplace entries can specify exact commit SHAs
- Enables reproducible builds and dependency locking
- Useful for enterprise environments requiring audit trails
- Allows teams to control exact plugin versions across installs

**Expected configuration**:
- Marketplace entry includes commit SHA in source specification
- Plugin installation uses exact commit rather than branch head
- Updates require explicit SHA changes in marketplace definition

---

## Search in Installed Plugins List

**What it is**: Filter installed plugins by name or description

**Introduced**: v2.1.14

**What we know**:
- Type to filter plugins in the installed plugins interface
- Searches both plugin names and descriptions
- Improves navigation in environments with many installed plugins
- Accessible from `/plugins` command in the installed tab

**Expected behavior**:
1. Open `/plugins` command
2. Navigate to installed tab
3. Type search query
4. List filters to matching plugins in real-time

---

## Native VSCode Plugin Management

**What it is**: Built-in plugin management interface in VSCode extension

**Introduced**: v2.1.16

**What we know**:
- Browse, install, and manage plugins directly from VSCode UI
- No need to use CLI commands for plugin operations
- Integrates with VSCode extension marketplace patterns
- Provides same functionality as CLI `/plugin` command

**Expected features**:
- Browse available plugins from marketplaces
- Install/uninstall plugins with UI confirmation
- Enable/disable installed plugins
- View plugin details and documentation

---

## OAuth Session Browsing and Resume in VSCode

**What it is**: Browse and resume remote Claude sessions from VSCode extension

**Introduced**: v2.1.16

**What we know**:
- OAuth users can view their remote sessions from Sessions dialog
- Resume web sessions directly from VSCode
- Provides continuity between web and desktop workflows
- Requires OAuth authentication (not API key auth)

**Expected workflow**:
1. Open Sessions dialog in VSCode extension
2. Browse remote sessions from claude.ai
3. Select session to resume
4. Session loads in VSCode with full conversation history
