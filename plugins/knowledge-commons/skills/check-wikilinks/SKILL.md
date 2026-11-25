---
name: check-wikilinks
description: >
  Wrapped-wikilink check for a knowledge-commons graph: fails when a [[wikilink]] is split across a
  line break. Only when a generated process or knowledge-graph skill directs it, or the user asks to
  check a graph for wrapped links.
argument-hint: "[--fix] <graph-root>"
user-invocable: false
allowed-tools: ["Bash(${CLAUDE_PLUGIN_ROOT}/scripts/check-wikilinks.sh *)"]
---

# Wrapped-wikilink check

Arguments: `$ARGUMENTS`

Run the check once over exactly this graph root, single-quoted (a path may contain spaces), with
`--fix` only if the arguments include it:

```bash
${CLAUDE_PLUGIN_ROOT}/scripts/check-wikilinks.sh [--fix] '<graph-root>'
```

Report the exit code and the full stdout and stderr verbatim. Exit 0 is clean. Exit 1 lists each
finding as `file:line: [[link text]]`. Exit 2 means the check could not run. **Any non-zero exit means
the graph is not known to be clean**; the script's header documents each code and what it skips.

The check does not read the graph's raw archives: the directories the project's `.commons.yml` names
under a source tier's `archive:`. It finds them itself and prints a `not read (raw archive…)` line for
each. Pass nothing extra for them, and relay those lines with the rest.

`--fix` rejoins what is safe to rejoin (the line break and the indentation after it become one space,
nothing else changes) and then re-runs the check, so its exit code and remaining findings describe the
graph as it now stands. What it lists after a fix it declined to touch, with a `left alone (reason)`
line for each; those are a hand decision for the calling skill.

Report only. Don't edit a note yourself, don't add `--fix` when it wasn't asked for, don't rerun with a
different root, and never call a non-zero run clean: repairing what is left belongs to the calling
skill. With no graph root in the arguments, report that the check did not run.
