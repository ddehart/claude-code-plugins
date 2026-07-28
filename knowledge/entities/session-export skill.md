---
genitor: "[[entities]]"
tags: [entity, skill, meta-claude]
---

# session-export skill

`meta-claude:session-export`. Renders a session's JSONL transcript into readable UI-style text.

Serves as the resolver for this graph's `session` source tier: raw JSONL is unreadable at transcript size
and burns context for nothing. Since 2026-07-28 the export is rendered to a scratch path outside the repo,
scanned by the preserve stage's redaction gate there, and moved into `knowledge/sources/raw/` — committed —
only once it passes. It is the archived copy of the raw material, not a throwaway derivative.

Until then it landed in `.claude/session-exports/`, gitignored. That is retired: a source note pointing
into an untracked directory is a dangling pointer waiting to happen, and this graph's founding source note
already points at a transcript that went with one.

- **2026-07-22** — resolved `session:5912a7cc` for the first transcript-tier `/process` run. 2 MB JSONL to
  534 KB / 76k words of text.
