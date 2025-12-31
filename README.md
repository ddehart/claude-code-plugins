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

Dev workflow agents for test running, branch creation, conventional commits, and pull request management.

**Agents included:**

| Agent | Description |
|-------|-------------|
| `test-runner` | Execute test suites (unit, E2E, or all) and analyze results |
| `branch-creator` | Create properly named Git branches following conventions |
| `commit-creator` | Create commits following Conventional Commits standard |
| `pr-manager` | Manage pull request workflows (create, monitor checks, review feedback, merge) |

## Usage

Once installed, the agents are automatically available. Claude will proactively use them when you:

- Ask to run tests
- Ask to create a branch
- Ask to commit changes
- Ask to create, monitor, or merge pull requests

## Updating

```bash
/plugin update dev-workflow@ddehart-plugins
```
