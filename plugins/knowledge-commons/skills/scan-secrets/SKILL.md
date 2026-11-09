---
name: scan-secrets
description: >
  Credential scan for a generated process skill's redaction gate, run over rendered material before
  it is archived. Only when that gate directs it.
argument-hint: "<rendered-file> [<rendered-file>...]"
user-invocable: false
allowed-tools: ["Bash(${CLAUDE_PLUGIN_ROOT}/scripts/scan-secrets.sh *)"]
---

# Secret scan

Rendered file path(s): `$ARGUMENTS`

Run the scanner once over exactly these paths, each single-quoted (a path may contain spaces or glob
characters):

```bash
${CLAUDE_PLUGIN_ROOT}/scripts/scan-secrets.sh '<path>' ['<path>' ...]
```

Report the exit code and the full stdout and stderr verbatim. **Any non-zero exit means do not
archive**; the script's header documents each code.

Report only. Don't explain away a hit, don't rerun with different arguments, and never call a non-zero
run clean: resolving hits belongs to the calling process skill and a human. With no arguments, report
that the scan did not run, which is a stop.
