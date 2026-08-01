---
genitor: "[[observations]]"
tags: [testing, verification, silent-failure]
date: 2026-08-01
supports: ["[[an index omission silently disables the check that reads it]]"]
---
A committed regression suite for a secret scanner had nine assertions and was written by the scanner's
author from the three planted secrets already known to work. A reviewer deleted the entire
credential-assignment scan — one of five advertised shapes, and the only one carrying placeholder logic —
and all nine assertions stayed green.

The mechanism was the core assertion: `count -eq 3`. Each of the three plants was *also* caught by a
prefix pattern, so the count held with the path gone entirely. The suite proved three regexes existed; it
did not test the gate. Two defects had already survived it for that reason.

The rebuilt suite is constructed on two stated rules: every code path gets a plant that only that path
can catch, and assertions are per-shape rather than on a finding count. It grew 9 → 45 cases, and each
growth step came from someone other than the author mutating the code in a way the author had not
anticipated.
