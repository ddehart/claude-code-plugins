---
genitor: "[[observations]]"
tags: [graph-patch, anchors]
date: 2026-11-08
supports: ["[[a check keyed to the template's literal surface fails copies that diverged on purpose]]", "[[a fail-safe argument holds only if a miss happens once]]"]
---
The patch mechanism anchors each delta on an exact heading, on the measured premise that headings survive generation byte-identical. Version 0.6.0 broke that premise by its own operation: the template inserted two stages and renumbered, while deltas insert relative to existing headings and never renumber. So graphs generated at 0.6.0 titled the report section `## 12. Report` and patched graphs kept `## 10. Report`. A check of the live graphs before choosing an anchor found them split about evenly. A single-string anchor would have skipped loudly in about half of them, and with no declined state the skip would recur on every run. Derek chose a list of exact headings from a menu of three; the same day it was replaced by matching on the title with the generated number dropped.
