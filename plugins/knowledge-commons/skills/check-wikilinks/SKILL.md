---
name: check-wikilinks
description: >
  Wrapped-wikilink check for a knowledge-commons graph: fails when a [[wikilink]] is split across a
  line break. Only when a generated process or knowledge-graph skill directs it, or the user asks to
  check a graph for wrapped links.
argument-hint: "<graph-root>"
user-invocable: false
allowed-tools: ["Bash(${CLAUDE_PLUGIN_ROOT}/scripts/check-wikilinks.sh *)"]
---

# Wrapped-wikilink check

Graph root: `$ARGUMENTS`

Run the check once over exactly this graph root, single-quoted (a path may contain spaces). It takes no
options and is read-only:

```bash
${CLAUDE_PLUGIN_ROOT}/scripts/check-wikilinks.sh '<graph-root>'
```

Report the exit code and the full stdout and stderr verbatim. Exit 0 is clean. Exit 1 lists each
finding as `file:line: [[link text]]`. Exit 2 means the check could not run. **Any non-zero exit means
the graph is not known to be clean.** `not read (raw archive…)` lines name directories it skipped on
purpose; relay them with the rest.

Report only. Don't edit a note, don't rerun with a different root, and never call a non-zero run clean:
what to do about a finding belongs to the calling skill. With no graph root in the arguments, report
that the check did not run.
