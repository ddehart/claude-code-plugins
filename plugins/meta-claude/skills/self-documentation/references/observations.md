# Observations

User-discovered behaviors and findings not documented in official Claude Code documentation. These observations come from hands-on testing and community contributions.

**How to contribute**: When you discover undocumented behavior, use this skill to record it. The skill will create a GitHub issue and optionally cache locally.

---

## AskUserQuestion Cannot Be Delegated to Subagents

**Observation**: The AskUserQuestion tool cannot be used when running in a forked/subagent context via the Task tool.

**Discovered**: 2025-01-09

**Context**: Attempted to create an interactive skill that runs in forked context (`context: fork`) to ask users questions during execution.

**Behavior**: When a subagent attempts to use AskUserQuestion, the tool is not available or fails. Interactive questioning only works in the main conversation context.

**Implication**: Skills that need to ask users questions must run in the main context, not as forked subagents. Use `context: fork` only for non-interactive workflows.

**Feature area**: Tools, Subagents

**Status**: Confirmed through testing

---

## How to Add Observations

When you discover something undocumented about Claude Code:

1. Describe the observation clearly
2. Note when and how you discovered it
3. Explain the practical implication
4. Identify the feature area (Tools, Subagents, Skills, Hooks, etc.)

The skill will help you format and submit this as a GitHub issue for tracking.
