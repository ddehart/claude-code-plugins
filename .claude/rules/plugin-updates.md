---
paths: plugins/**/*.{md,json}
---

# Plugin Update Rule

When modifying any plugin component (agents, skills, hooks), you MUST also update:

1. **Plugin version** in `plugins/<plugin>/.claude-plugin/plugin.json`
2. **Marketplace version** in `.claude-plugin/marketplace.json`

Both files must have matching versions for the updated plugin.

This is not optional. Include these updates in your implementation plan before starting work.

## Choosing patch vs. minor

Bumping *something* is mandatory; bumping the **right** component is the part that's easy to get wrong.

- **Patch** (`0.1.8` → `0.1.9`) — bug fixes and corrections only. Nothing a user could newly *do*.
- **Minor** (`0.1.9` → `0.2.0`) — any new capability. A new skill, agent, or hook always qualifies. So
  does new *behavior* in an existing component, even when it ships alongside a pile of fixes and even
  when the diff is mostly fix.

The trap is a PR that is predominantly bug fixes but quietly adds one new behavior. The fixes dominate
the diff and the commit reads `fix(...)`, so a patch bump feels right — but a user of that plugin gains
something they didn't have, and the version should say so. **Size the bump by what the plugin can now do,
not by what the diff mostly contains.**

Validated 2026-07-21: two parallel agents each defaulted to a patch bump — one for a PR adding an entire
new skill, one for a PR adding proactive entity recommendation. The prior version of this rule mandated
the bump but was silent on choosing its size, so both complied with it and both were wrong.

When a change is genuinely ambiguous, round up. An over-stated minor costs nothing; an under-stated patch
hides a capability from anyone reading the changelog to decide whether to upgrade.

## Exception: unregistered plugins

A plugin that is not yet listed in `.claude-plugin/marketplace.json` has no marketplace entry to bump — only
step 1 applies. This is the normal state for a plugin still being built: the marketplace should never
advertise an installable that installs nothing. Register it, at the version it has reached, when it is ready
to install.
