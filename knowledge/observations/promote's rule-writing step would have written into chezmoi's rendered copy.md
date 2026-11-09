---
genitor: "[[observations]]"
tags: [chezmoi, promote, environment]
date: 2026-11-08
supports: ["[[a scaffolder owns its environmental blast radius]]"]
---
Asked how a principle becomes steering, the session traced promote's instruction-tier branch. It writes the rule file into the rules directory, then commits only if that directory is a git repository. On a machine where chezmoi manages `~/.claude/rules/`, the directory is a rendered copy, not a repository: the rule would land there uncommitted and be overwritten by the next `chezmoi apply`. The fix runs `chezmoi source-path` first, writes into the source, then applies, verifies, and commits it as one unit. It shipped as 0.8.2, untested end to end because no promotion to rules had run yet.
