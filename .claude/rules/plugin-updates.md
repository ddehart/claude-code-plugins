---
paths: plugins/**/*.{md,json}
---

# Plugin Update Rule

When modifying any plugin component (agents, skills, hooks), you MUST also update:

1. **Plugin version** in `plugins/<plugin>/.claude-plugin/plugin.json`
2. **Marketplace version** in `.claude-plugin/marketplace.json`

Both files must have matching versions for the updated plugin.

This is not optional. Include these updates in your implementation plan before starting work.
