---
paths: plugins/knowledge-commons/references/templates/*.md
---

# Template Delta Rule

When you edit any template under `plugins/knowledge-commons/references/templates/`, you MUST also
write a delta entry for that change in `plugins/knowledge-commons/references/deltas.md`, in the
same commit.

This is not optional. Include the delta entry in your implementation plan before starting work.

## Why

`graph-init` generates project-owned `process` and `knowledge-graph` skills from these templates,
and then tells each project it owns those files and should sharpen them from real runs. Projects
do — bodies diverge by up to 78% — so a template fix reaches **nothing** that was already
generated. Without a delta, `/graph-patch` has no way to propagate the fix.

The failure shape is what makes this mandatory: a forgotten delta leaves the plugin looking
correct while every downstream graph stays silently broken, with no mechanism that surfaces the
gap. That is the exact failure the patch mechanism was built to prevent, reproduced by the person
maintaining it.

## What a delta entry needs

Seven fields, per the spec's D8:

| Field | Purpose |
|---|---|
| `id` | Stable kebab-case identifier, globally unique, recorded in a project's `applied:` list |
| `file` | `process` or `knowledge-graph` |
| `anchor` | The **exact `##` heading text** the change targets — not a pattern, not a number |
| `version` | The plugin version that introduces it |
| `instruction` | The semantic change, in domain-neutral terms |
| `rationale` | *Why* — this is what lets the patcher adapt the edit to prose that has diverged, instead of pasting |
| `satisfied-test` | An explicit test for "does the target already say this?" — used both to detect redundancy before the edit and to verify the edit landed after |

Write the `satisfied-test` sharply. It is load-bearing twice over, and a vague one makes both
redundancy detection and post-condition verification unreliable.

## Exception

A template edit that changes no instruction — a typo fix, a link correction, reflowed whitespace,
a clarification that leaves the meaning identical — needs no delta. The test is whether an
already-generated skill would behave differently if it had this change. If yes, it needs a delta.

## Related

- `plugin-updates.md` — the version-bump rule this one sits next to. Both are enforced by
  discipline, not by tooling, and both are stated as non-optional for the same reason.
- `docs/specs/knowledge-commons-patch-mechanism.md` — D8 (delta fields), D17 (this rule).
