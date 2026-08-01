---
genitor: "[[observations]]"
tags: [agents, review, automation]
date: 2026-08-01
supports: ["[[a check inherits the frame of whoever briefed it]]"]
---
A patch tool requires per-item approval — `y` / `edit` / `skip` for each change — and explicitly forbids
batch approval, on the grounds that batching hides exactly what needs judgment. Run unattended, that gate
does not protect anything: it stalls indefinitely, and the only ways past it are to auto-approve through
it or to drop it.

The session took a third option: give each change its own commit, so the pull request presents them as
separately reviewable diffs. The reviewable surface the gate exists to buy was relocated to where a human
could actually use it, and the deviation was stated in the PR rather than quietly taken.

The general shape: a control designed around a human at a prompt has to be re-sited, not deleted, when
the prompt is gone. Deleting it loses the review; auto-approving keeps its form and none of its function.
