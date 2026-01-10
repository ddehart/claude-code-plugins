# Integrations

IDE extensions, platform integrations, and deployment options for Claude Code.

**Last updated**: 2025-01-09

---

## VS Code Extension

**What it is**: Beta native IDE integration providing graphical sidebar interface as alternative to terminal usage

**Documentation**: https://docs.anthropic.com/en/docs/claude-code/vs-code

**Key concepts**:
- **Native IDE experience**: Dedicated Claude Code sidebar panel accessed via Spark icon
- **Core features**: Plan review mode, auto-accept edits mode, @-mention file management, MCP server support, conversation history, multiple simultaneous sessions, keyboard shortcuts, slash commands
- **Requirements**: VS Code 1.98.0+; install from Visual Studio Code Extension Marketplace
- **Third-party providers**: Configure environment variables in VS Code settings for Bedrock/Vertex AI
- **Unavailable features**: MCP server configuration (must use CLI), subagents setup, checkpoints, advanced shortcuts (#, !, tab completion)
- **Security considerations**: Auto-edit permissions may modify IDE configs with auto-execution risks; use Restricted Mode and manual approval for untrusted workspaces
- **Legacy CLI integration**: Terminal-based integration offers selection context sharing, IDE diff viewing, automatic diagnostic sharing

---

## Azure AI Foundry

**What it is**: Third-party model provider integration enabling Claude Code access through Microsoft's Azure AI Foundry platform

**Documentation**: https://docs.anthropic.com/en/docs/claude-code/azure-ai-foundry

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

**Introduced**: v2.0.51 (2025-11)

**What we know**:
- Available at https://claude.com/download
- Third deployment option alongside CLI and VS Code extension
- Native desktop experience without terminal familiarity required

**Deployment options**:
- **CLI**: Terminal-native, scriptable, keyboard-driven
- **VS Code Extension**: IDE sidebar integration
- **Desktop App**: Standalone native application

**Unanswered questions**:
- Full feature parity with CLI
- Supported operating systems
- MCP server and custom agent support

---

## Claude in Chrome (Beta)

**What it is**: Chrome extension for browser control directly from Claude Code

**Introduced**: v2.0.72 (2025-12)

**What we know**:
- Chrome extension at https://claude.ai/chrome
- Enables browser automation: navigate, read content, interact with elements, take screenshots
- More powerful than WebFetch - active browser control vs. passive fetching

**Use cases**:
- Web application testing
- Form automation
- Content extraction
- UI verification

**Unanswered questions**:
- Full list of available browser actions
- Security model and authentication handling
- Cross-browser support
