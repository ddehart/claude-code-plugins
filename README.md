# Claude Code Plugins

Personal Claude Code plugin marketplace with reusable dev workflow agents.

## Installation

```bash
# Add the marketplace (once per machine)
/plugin marketplace add ddehart/claude-code-plugins

# Install the dev-workflow plugin
/plugin install dev-workflow@ddehart-plugins
```

## Available Plugins

### dev-workflow

Dev workflow agents and skills for test running, branch creation, conventional commits, pull request management, Linear issue management, browser verification, and spec writing.

**Agents included:**

| Agent | Description |
|-------|-------------|
| `test-runner` | Execute test suites (unit, E2E, or all) and analyze results |
| `branch-creator` | Create properly named Git branches following conventions |
| `commit-creator` | Create commits following Conventional Commits standard |
| `pr-manager` | Manage pull request workflows (create, monitor checks, review feedback, merge) |
| `linear-issues` | Manage Linear issues (create, update, view, search, status transitions) |
| `chrome-verifier` | Verify deployed features via browser automation, returning concise summaries |

**Skills included:**

| Skill | Description |
|-------|-------------|
| `spec-writing` | Interview users to refine rough ideas into comprehensive, implementation-ready specifications |

## Usage

Once installed, the agents and skills are automatically available. Claude will proactively use them when you:

- Ask to run tests
- Ask to create a branch
- Ask to commit changes
- Ask to create, monitor, or merge pull requests
- Ask to manage Linear issues
- Ask to verify a deployment or check a live site
- Ask to write, create, or refine a spec

## Updating

```bash
/plugin update dev-workflow@ddehart-plugins
```
