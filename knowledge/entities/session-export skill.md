---
genitor: "[[entities]]"
tags: [entity, skill, meta-claude]
---

# session-export skill

`meta-claude:session-export`. Renders a session's JSONL transcript into readable UI-style text.

Serves as the resolver for this graph's `session` source tier: raw JSONL is unreadable at transcript size
and burns context for nothing. Exports land in `.claude/session-exports/`, gitignored — a derived artifact,
since the transcript under `~/.claude/projects/` is the real source.

- **2026-07-22** — resolved `session:5912a7cc` for the first transcript-tier `/process` run. 2 MB JSONL to
  534 KB / 76k words of text.
