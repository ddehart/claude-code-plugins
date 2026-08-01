---
genitor: "[[observations]]"
tags: [concurrency, process, silent-failure]
date: 2026-08-01
supports: ["[[concurrent writers are invisible until write time]]"]
---
A spec was handed to a fresh session deliberately, so its author would not implement its own intent. That
session branched before the authoring session's processing run. Both then created the same decision note
under the same filename and superseded the same prior decision, neither able to see the other. Verified with
`git merge-base --is-ancestor`: none of the authoring session's commits were in the branch. Meanwhile three
behavior-changing edits landed on the spec while its header still read the version the other session had
read, one of them reversing an instruction that session may already have executed. The collision surfaced
only when a human asked what to tell the other session. A version bump was minted afterwards to manufacture
the staleness signal that had not existed.

## source
- [[session f64160a1 — the process pipeline correction, specced not built]]
