---
name: conventions
description: >
  Load the full knowledge-commons graph conventions (~18 KB). Only when a generated knowledge-graph
  or process skill directs it, or the user asks for the full conventions; not for everyday captures.
user-invocable: false
allowed-tools: ["Read"]
---

# Graph conventions

Read `${CLAUDE_PLUGIN_ROOT}/references/graph-conventions.md` in full. It is the authoritative
structural contract for every knowledge-commons graph, at the version of the plugin installed for this
session.

Where it and a project's generated `knowledge-graph` skill disagree, say so rather than silently picking
one: the project's skill is owned by the project and may have been sharpened deliberately, or may be
stale. `/graph-patch` is how a stale one catches up.

If the file can't be read, say that plainly. Don't go looking for another copy under
`~/.claude/plugins/`: other copies there belong to other versions or other projects, and reading one
returns a contract that may be out of date with no sign that it is.
