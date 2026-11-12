---
genitor: "[[entities]]"
tags: [plugin, knowledge-commons]
---

# knowledge-commons plugin

A generator plugin that scaffolds per-project, project-owned knowledge-graph tooling from a config file
plus an interview. Ships two skills — [[graph-init skill]] and [[promote skill]] — and zero verification
machinery: no validator, no write-transactions, no lifecycle or upgrade machinery. The only gate on graph
health is plan-approval by a human plus prose judgment by the LLM. Designed at the weight of the year-old
reference it generalizes; see [[knowledge-commons ships at the weight of the system it generalizes]].

## interaction log
- 2026-07-15 — designed and shipped across releases 0.1.0 → 0.1.7 in one day, each bump from a real
  defect surfaced by actual use.
- 2026-11-08 — 0.7.0 added the [[graduate skill]] and promote's graduation check; 0.8.2 fixed promote's rules branch for chezmoi-managed rules.
- 2026-11-08 → 11-11 — 0.8.0 corrected the entity-type route and changed delta anchors and supersession; 0.8.1 restated a too-literal satisfied-test; 0.9.0 (separate session) reached plugin files through skills, not stamped paths; 0.9.1 removed private per-graph details from a delta rationale.
