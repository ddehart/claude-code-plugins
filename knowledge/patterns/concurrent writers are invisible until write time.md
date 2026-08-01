---
genitor: "[[patterns]]"
tags: [process, concurrency, silent-failure]
---

# concurrent writers are invisible until write time

The pipeline assumes one writer at every stage — plan, approve, write, stamp. Nothing detects a second.
Graph notes are files and creating one looks idempotent; there is no lock, no lease, no writer identity, and
no field distinguishing two runs over overlapping material.

So divergence accumulates silently and surfaces at a merge, or by accident. A redundancy screen run minutes
before a write can be reading a state that no longer exists — and `git fetch` reporting "already up to
date" is not evidence, since a sibling session's commit can be local.

The sibling-session case has no guard at all: the existing double-counting guard covers overlapping *tiers*,
not two sessions describing one event. Two runs will land the same incident as a note from each side, and it
reads as two witnesses.

*Two witnesses (2026-07-28, 2026-08-01). Open.*

## evidence
- [[the promotion target moved between the redundancy screen and the write]]
- [[two sessions independently wrote the same decision note]]

## related
- [[naming a failure shape confers no immunity to it]]
- [[a claim restated into several artifacts starts reading as corroborated]]
