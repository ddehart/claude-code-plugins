---
genitor: "[[observations]]"
tags: [testing, controls]
date: 2026-11-06
supports: ["[[execution against real data catches what authoring and review miss]]"]
---
The end-to-end harness ran the previous skill version, 1.8.3, on the same due-path fixture the new version had passed, as a gate: if it passed too, the harness proved nothing and testing stopped. It failed the marker, anchor, count, and re-run checks. Its own report said "one entry since the last note, so no deep review ran," with 12 unreviewed entries, reproducing the original bug live.
