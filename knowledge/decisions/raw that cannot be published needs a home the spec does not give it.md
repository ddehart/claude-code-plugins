---
genitor: "[[decisions]]"
tags: [knowledge-commons, process, preservation, privacy]
---

# raw that cannot be published needs a home the spec does not give it

The pipeline spec has two rules about raw material and a gap between them.

**D2** — raw is committed in-repo, under the graph — and its rationale explicitly rejects the alternative:
*"a durable location outside the repo reintroduces the dangling pointer through a different door."*
**D5–D7** build a redaction gate whose job is to make material *safe* to commit, with D7 offering
**redact**, **withhold**, or **accept** per finding.

Neither anticipated a third state: raw that must be **kept** and cannot be **published**. D7 defines
withholding as *"this material is not archived at all"* — which reads as discarded, and is correct only for
material nobody needs. D2 forbids the one other place it could go.

That state is not hypothetical. The first time the gate ran against material the pipeline had not produced
itself — this graph's founding transcript — the deterministic floor passed and the read-through failed it on
third-party confidential content. Scrubbing was considered and declined: substituting entities makes the
artifact derived rather than raw, and a scrub is only as good as the enumeration behind it, which is the
failure mode that put the material at risk in the first place.

**So: a second raw location, outside the publishable repo, private, and durable in its own right.** Here
that is `~/Developer/session-archive/` with a private git remote. It is not a staging area awaiting
migration and not a dangling pointer — it is version-controlled and off-machine, which is exactly what D2
wanted and assumed only an in-repo archive could provide.

Two consequences for the generic template. A graph whose archive destination is public needs the gate *and*
a withheld-raw destination; declaring only the first leaves the second to be improvised at the moment it is
needed, under time pressure, by whoever hits it. And the source note has to record the withholding and where
the material went — a withheld source that says nothing is indistinguishable from one that was never
preserved.

*Decided 2026-08-02, from the gate's first real failure.*

## related
- [[processing preserves the raw and synthesizes for a human, and extracts from the raw]]
- [[the generated process skill]]
