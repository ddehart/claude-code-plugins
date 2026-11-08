---
genitor: "[[observations]]"
tags: [review, testing]
date: 2026-11-06
supports: ["[[execution against real data catches what authoring and review miss]]"]
---
The PR said older note shapes were "recognized strictly." A code review that fed the script edge-case files found ten issues, two of them wrong-behavior bugs: a qualifier before the marker hid a real review, and notes saying no review ran still counted as one. The review's own summary noted the second "contradicts the strict matching I described in the PR." Each fix then got a failing test first.
