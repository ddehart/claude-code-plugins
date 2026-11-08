---
genitor: "[[observations]]"
tags: [permissions, testing, claude-code]
date: 2026-11-06
supports: ["[[execution against real data catches what authoring and review miss]]"]
---
A test plan scoped each headless run with a project `.claude/settings.json` allowlist. Claude Code ignored it, printing "Ignoring 29 permissions.allow entries" to stderr, because an untrusted workspace's allowlist doesn't load. Only stderr showed it; most runs still worked on other permissions. Trusting the folder meant editing global config, so the rerun passed the same list through `--allowedTools=` instead.
