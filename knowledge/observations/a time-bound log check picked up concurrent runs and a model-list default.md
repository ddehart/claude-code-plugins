---
genitor: "[[observations]]"
tags: [concurrency, logs]
date: 2026-11-06
supports: ["[[concurrent writers are invisible until write time]]"]
---
Confirming which model served a pass meant reading log files newer than a mark. With test runs going in parallel, one run's check counted another's log and re-ran the pass. Separately, `agy models` writes a log carrying the tool's default model label, so a mark set before it reports two labels. Binding the check to the run's own workspace path fixed attribution where a time window could not.
