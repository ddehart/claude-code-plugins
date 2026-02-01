# Integrations

IDE extensions, platform integrations, and deployment options for Claude Code.

**Last updated**: 2026-02-01

---

## VS Code Extension

**What it is**: Native IDE integration providing graphical sidebar interface as alternative to terminal usage

**Documentation**: https://code.claude.com/docs/en/vs-code

**Key concepts**:
- **Native IDE experience**: Dedicated Claude Code sidebar panel accessed via Spark icon in Editor Toolbar
- **Core features**: Plan review mode, auto-accept edits mode, @-mention file management with line ranges, MCP server support, conversation history, multiple simultaneous sessions (tabs and windows), keyboard shortcuts, slash commands
- **Requirements**: VS Code 1.98.0+; install from Visual Studio Code Extension Marketplace
- **Prompt box features**: Permission mode indicator, command menu (`/`), context usage indicator, extended thinking toggle, multi-line input (Shift+Enter)
- **@-mentions**: Fuzzy matching for files/folders, automatic selection visibility, `Option+K`/`Alt+K` to insert file reference with line numbers
- **Removable attachments**: File suggestions display as attachment chips; click X to remove unwanted files before sending prompt
- **Session management**: Resume past conversations via dropdown, search by keyword or browse by time
- **Remote sessions**: OAuth users can resume sessions from claude.ai via Remote tab in Past Conversations dialog
- **Plugin management**: Type `/plugins` to browse, install, and manage plugins with graphical interface; supports user, project, and local scopes
- **Multiple conversations**: Open in New Tab or New Window from Command Palette; colored dots indicate status (blue=permission pending, orange=completed while hidden)
- **Git integration**: Create commits and PRs, works with git worktrees for parallel tasks
- **Third-party providers**: Support for Amazon Bedrock, Google Vertex AI, Microsoft Foundry via environment configuration
- **Unavailable features**: MCP server configuration (must use CLI), `!` bash shortcut, tab completion, checkpoints (coming soon)
- **Security considerations**: Auto-edit permissions may modify IDE configs with auto-execution risks; use Restricted Mode and manual approval for untrusted workspaces

**Extension settings**:
- `selectedModel` - Model for new conversations
- `useTerminal` - Launch in terminal mode instead of graphical panel
- `initialPermissionMode` - Default approval behavior (default, plan, acceptEdits, bypassPermissions)
- `preferredLocation` - Where Claude opens (sidebar or panel)
- `autosave` - Auto-save files before Claude reads/writes
- `useCtrlEnterToSend` - Use Ctrl/Cmd+Enter instead of Enter to send
- `respectGitIgnore` - Exclude .gitignore patterns from file searches

---

## Azure AI Foundry

**What it is**: Third-party model provider integration enabling Claude Code access through Microsoft's Azure AI Foundry platform

**Documentation**: https://code.claude.com/docs/en/microsoft-foundry

**Key concepts**:
- **Prerequisites**: Azure subscription with Azure AI Foundry access, RBAC permissions, optional Azure CLI for credential management
- **Resource provisioning**: Create Claude resource in Azure AI Foundry, deploy three model variants (Opus, Sonnet, Haiku)
- **Authentication options**: API key method (`ANTHROPIC_FOUNDRY_API_KEY`) or Microsoft Entra ID (automatic via Azure SDK default credential chain)
- **Essential environment variables**: `CLAUDE_CODE_USE_FOUNDRY=1` (activation), `ANTHROPIC_FOUNDRY_RESOURCE={resource}` (resource name), model-specific deployment mappings
- **Permissions**: "Azure AI User" and "Cognitive Services User" roles sufficient, custom roles require `Microsoft.CognitiveServices/accounts/providers/*` dataAction
- **Limitations**: `/login` and `/logout` commands unavailable when using AI Foundry
- **Common issues**: Authentication errors typically from unconfigured Entra ID (configure or set API key)

---

## Claude Code for Desktop

**What it is**: Native desktop application providing graphical interface without terminal requirement

**Documentation**: https://code.claude.com/docs/en/desktop

**Key concepts**:
- Available at https://claude.com/download
- Third deployment option alongside CLI and VS Code extension
- Native desktop experience without terminal familiarity required

**Deployment options**:
- **CLI**: Terminal-native, scriptable, keyboard-driven
- **VS Code Extension**: IDE sidebar integration
- **Desktop App**: Standalone native application

---

## Claude in Chrome (Beta)

**What it is**: Chrome extension for browser control directly from Claude Code

**Documentation**: https://code.claude.com/docs/en/chrome

**Key concepts**:
- **Prerequisites**: Google Chrome, Claude in Chrome extension (v1.0.36+), Claude Code CLI (v2.0.73+), paid Claude plan
- **How it works**: Extension uses Chrome's Native Messaging API to receive commands from Claude Code; Claude opens new tabs (shares login state); requires visible browser window (no headless mode)
- **Setup**: Run `claude --chrome` to enable, use `/chrome` command to manage connection
- **Enable by default**: Select "Enabled by default" in `/chrome` menu (increases context usage)
- **Login handling**: Claude pauses at login pages, CAPTCHAs, or blockers; handles manually then tell Claude to continue

**Capabilities**:
- Navigate pages, click and type, fill forms, scroll
- Read console logs and network requests
- Manage tabs, resize windows
- Record browser interactions as GIFs
- Interact with authenticated apps (Google Docs, Gmail, Notion, etc.)

**Use cases**:
- Live debugging with console error reading
- Design verification against mocks
- Web app testing (forms, user flows)
- Data extraction from web pages
- Task automation (data entry, form filling)
- Multi-site workflows
- Session recording as GIFs

**Best practices**:
- Modal dialogs can interrupt flow - dismiss manually and tell Claude to continue
- Use fresh tabs if a tab becomes unresponsive
- Filter console output by specifying patterns rather than requesting all output

---

## JetBrains IDEs

**What it is**: Integration with IntelliJ IDEA, PyCharm, WebStorm, and other JetBrains IDEs

**Documentation**: https://code.claude.com/docs/en/jetbrains

**Key concepts**:
- IDE integration for JetBrains family of IDEs
- Similar functionality to VS Code extension
- Access Claude Code within IDE environment
