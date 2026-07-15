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
