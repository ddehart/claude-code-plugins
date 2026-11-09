---
name: scan-secrets
description: >
  Run the knowledge-commons credential scan, the deterministic floor of a generated process skill's
  redaction gate, over rendered material before it is archived. Pass the rendered file path(s) as
  arguments. Use when a generated process skill's preserve stage says to run the scan.
argument-hint: "<rendered-file> [<rendered-file>...]"
user-invocable: false
allowed-tools: ["Bash(${CLAUDE_PLUGIN_ROOT}/scripts/scan-secrets.sh *)"]
---

# Secret scan

Run exactly this command, once, with the arguments you were given:

```bash
${CLAUDE_PLUGIN_ROOT}/scripts/scan-secrets.sh $ARGUMENTS
```

Then report the **exit code** and the **full stdout and stderr verbatim**, nothing paraphrased.

What the exit code means to the caller:

- **0**: clean. No credential shapes found.
- **1**: hits. Each finding is listed in the output.
- **2**: the scan could not run (bad usage, unreadable file, a pattern error).

**Any non-zero exit means do not archive.** Exit 1 and exit 2 mean the same thing to the gate: a scan
that couldn't run is not a scan that passed.

This skill reports; it never judges. Don't resolve, accept, or explain away a hit, don't retry with
different arguments or a narrower file set, and never summarize a non-zero run as clean. Resolving each
hit (redact, withhold, or accept) belongs to the process skill that called this one, with a human.

If no arguments were given, don't guess at a file. Report that the scan did not run, which is a stop.
