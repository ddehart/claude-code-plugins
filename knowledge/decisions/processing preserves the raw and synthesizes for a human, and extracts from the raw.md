---
genitor: "[[decisions]]"
tags: [knowledge-commons, process, sources, synthesis]
---

# processing preserves the raw and synthesizes for a human, and extracts from the raw

A `/process` run does four things to a source, and their arrangement is the substance of the design:

1. **Take it in** — resolve the input to a canonical identity.
2. **Preserve it** — write the source note and keep the raw material durably.
3. **Synthesize it** — produce the document a human reads.
4. **Extract from it** — write the graph's atomic notes, **from the raw material**.

Stages 3 and 4 are **siblings**, both fed by the raw material. Neither is upstream of the other.

**Extraction reads the raw because a synthesis is written for a reader.** A distillation compresses away
the corrections, the dead ends, and the exact wording that an observation is made of. Evidence pulled
from it inherits every omission and cannot detect any of them — the first real run of this pipeline
found three divergences between a session's own account of itself and what its transcript showed, none
of which a reader of the account would have seen. The synthesis may orient; it may not source a finding.

**Preservation is a named stage in every generated pipeline, unconditionally.** Its form varies — small
sources inline into the source note, large ones go to a committed archive with a pointer — but its
presence does not. A stage generated only where config asks for it reproduces the defect: a missing
stage is one nobody notices is missing. Which is exactly what happened here. The pipeline had a step
that *searched* for a source note and a step that *stamped* one, and nothing that *wrote* one, and for
sessions that gap degraded preservation to a pointer into a gitignored directory. This graph's founding
source note points at a transcript that no longer exists.

**The archive is committed, in-repo.** A durable location outside the repo reintroduces the dangling
pointer through a different door. The accepted cost is that the material is as public as the repo, which
is what puts a redaction gate on the preserve stage where the destination is public or shared: a
deterministic floor that fails closed on its own failure as well as on a hit, plus a subagent
read-through, both required, with each hit resolved individually.

**A synthesis may be an existing project artifact adopted into the tier.** Here the chronicle entries in
`docs/chronicle/` *are* the synthesis notes, at the path they already occupy — outside the graph root
and without its frontmatter conventions. The alternative, a note inside `knowledge/` whose only content
is a link to the chronicle, is a second artifact per session whose sole job is to point at the first.

**Where the raw material is verifiably gone**, extraction reads the synthesis and the source note
carries `raw: unavailable` with the reason. This is a permanent, named path — transcripts will keep
being pruned — and it is deliberately not a convenience for raw material that is merely large.

*Decided 2026-07-28. Shipped in knowledge-commons v0.6.0.*

## related
- [[session transcripts are primary and the chronicle is the lossy fallback]]
- [[a generator reproduces its template's flaws]]
- [[the knowledge-commons plugin generates project-owned prose, not a runtime engine]]
- [[patches are semantic instructions anchored on headings, never diffs]]
