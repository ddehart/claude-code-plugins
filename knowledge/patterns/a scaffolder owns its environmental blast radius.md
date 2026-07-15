---
genitor: "[[patterns]]"
tags: [generator, scaffolding, environment]
---

# a scaffolder owns its environmental blast radius

Generating artifacts into a live repo or machine creates second-order obligations the interview can't
elicit but the tool can flag — the scaffolder owns them even when it doesn't own the fix. Empty type
directories vanish from git without a `.gitkeep`; graph commits trip path-triggered CI unless the graph
root is excluded; a promotion that writes but never commits-and-pushes strands as working-tree changes and
reads from the outside as a no-op. A related duty: *detecting* a gap is the tool's job even when *fixing*
it isn't — a config-only wiring mode that writes a promotion target should grep the existing pipeline for a
trigger and surface its absence, rather than leaving the human to be the detection mechanism. Touching and
checking are different.

*One witness (2026-07-15). Open.*

## evidence
- [[graph commits, empty dirs, and uncommitted promotions were second-order costs of scaffolding into a live repo]]
- [[config-only wiring should surface a missing promotion trigger rather than leave the user to find it]]

## related
- [[the knowledge-commons plugin generates project-owned prose, not a runtime engine]]
- [[graph-init skill]]
