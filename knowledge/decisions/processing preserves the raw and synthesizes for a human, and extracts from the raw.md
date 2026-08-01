---
genitor: "[[decisions]]"
tags: [knowledge-commons, process, sources, synthesis]
---

# processing preserves the raw and synthesizes for a human, and extracts from the raw

Processing one source has four stages, not two. Take it in; **preserve** the raw material durably;
**synthesize** it into something a human reads; **extract** the graph's atomic notes from the raw.

Stages three and four are siblings, both fed by the raw material. Neither is upstream of the other. That is
the whole point: a synthesis compresses away the corrections, dead ends, and exact wording that atomic
evidence needs, so evidence comes from the raw *because* you do not want it coming from the distillation.

Two consequences for this graph. The chronicle is the **synthesis tier**, not a source tier — it is what a
run produces, at `docs/chronicle/`, outside the graph root. And preservation is a named, unconditional
stage: a stage generated only sometimes is how the last one went missing.

Preservation commits raw material in-repo. Because this repo is public, that needs a gate — a deterministic
credential scan that always runs and fails closed, plus an agent read-through for what patterns cannot
catch, both required to pass. The deterministic floor was added after a first choice of agent-only: a
judgment-based gate cannot be shown to work, and a planted-secret test that passes proves it caught *that*
secret, not that it catches secrets.

Where a synthesis exists but its raw source is gone, extraction falls back to the synthesis and the source
note is marked `raw: unavailable`. That is a permanent named path, not a migration step — transcripts will
keep being pruned.

**The bar for that path is "verifiably absent", and this graph has already failed it once.** The founding
source note was marked `raw: unavailable` on the strength of a project-scoped glob that returned nothing;
the transcript was 2.8 MB and intact, under another project's slug. So the path fires on a UUID search
across every slug coming back empty — never on a scoped miss, and never because the raw material is merely
large or the synthesis an easier read. Extracting from a synthesis whose raw source is alive is the one
thing this model exists to prevent, and the degraded path must not become its loophole.

*Decided 2026-07-26. Specced in `docs/specs/knowledge-commons-process-pipeline.md` (v1.3); implemented in
knowledge-commons 0.6.0.*

## related
- [[session transcripts are primary and the chronicle is the lossy fallback]] (superseded by this)
- [[a workaround written up as a decision stops reading as a workaround]]
- [[the generated process skill]]
