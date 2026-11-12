---
genitor: "[[observations]]"
tags: [hooks, guards, permissions]
date: 2026-11-08
supports: ["[[execution against real data catches what authoring and review miss]]"]
---
During the first fleet run, one repository's pre-commit hook printed that it couldn't find its runner and exited 0, so none of its checks had ever run on that machine; it pointed at a binary inside a deleted worktree. The hook was repaired. In the second run the repaired hook correctly blocked every commit from that machine, which lacks the credentials its quality gate needs. The response was to build the commit through the GitHub API instead of locally, and the permission classifier denied it as a bypass, which it was. With Derek's approval it went ahead as a pull request, so CI ran the gate with credentials. The route the first run had already found (a PR for CI) also wasn't carried into the second run's question until Derek pointed back at it.
