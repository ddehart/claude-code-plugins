---
genitor: "[[observations]]"
tags: [testing, regression]
date: 2026-11-06
supports: ["[[each fix round manufactures the next round's defects]]"]
---
The first commit transcribed the old counting rule literally into the new script and added the tests, which failed 19 times, including the core case. Later commits fixed the rule. Copies of the fix were then broken on purpose, by restoring the old rule, flipping a comparison and an off-by-one, and dropping the marker from the template, and each mutation turned the suite red. A rebase merge kept the failing commit in main's history as the record that the test could fail.
