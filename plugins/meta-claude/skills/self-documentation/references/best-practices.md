# Best Practices

Meta-level guidance for using Claude Code effectively: when/why, not just what/how.

**Documentation**: https://code.claude.com/docs/en/best-practices

**Last updated**: 2026-01-22

---

## The Verification Principle (Most Important)

**What it is**: Always give Claude a way to verify its work

**Key concepts**:
- Without verification criteria, Claude produces plausible-looking but incomplete code
- Provide tests, screenshots, expected outputs, or scripts
- Example: "write validateEmail function. test cases: test@example.com→true, invalid→false. run tests after"

---

## Workflow Strategy: Explore → Plan → Code

**What it is**: Phased approach separating research from implementation

**Key concepts**:
- **Explore**: Enter Plan Mode, read files without changes
- **Plan**: Create detailed implementation plan
- **Implement**: Switch to Normal Mode, code with verification
- **Commit**: Have Claude commit and create PRs
- **When to skip**: Small, scoped tasks describable in one sentence

---

## Prompt Crafting

**What it is**: Techniques for effective Claude Code prompts

**Key concepts**:
- **Scope precisely**: File, scenario, testing approach
- **Point to sources**: Git history, existing patterns
- **Describe symptoms**: Location and success criteria
- **Provide rich content**: `@` files, screenshots, URLs, piped data

---

## CLAUDE.md Authoring

**What it is**: Guidelines for effective persistent context

**Key concepts**:
- **Include**: Commands Claude can't guess, non-standard style rules, testing instructions, repo etiquette, env quirks, architectural decisions
- **Exclude**: Standard conventions, detailed API docs (link instead), frequently-changing info, self-evident practices
- **Import files**: Use `@README.md` syntax for references

---

## Session Management Strategy

**What it is**: When to clear, correct, or accumulate context

**Key concepts**:
- **Course-correct early**: Esc (stop), Esc+Esc or /rewind (restore), "Undo that", /clear (reset)
- **The two-correction rule**: After correcting twice on same issue, /clear and rewrite prompt
- **Subagent delegation**: Use subagents for investigation to avoid cluttering main context
- **/clear between tasks**: Prevents "kitchen sink sessions"

---

## Common Failure Patterns

**What it is**: Anti-patterns to recognize and avoid

**Key concepts**:
1. **Kitchen sink session**: Mixing unrelated tasks → /clear between tasks
2. **Correction loop**: Multiple failed fixes → /clear after 2 failures, better initial prompt
3. **Over-specified CLAUDE.md**: Too many rules get ignored → prune ruthlessly, convert to hooks
4. **Trust-then-verify gap**: Plausible code with edge case bugs → always provide verification
5. **Infinite exploration**: Unbounded investigation → scope or use subagents

---

## Developing Intuition

**What it is**: When to break the rules

**Key concepts**:
- Sometimes accumulate context for deep problems
- Sometimes skip planning and let Claude explore
- Sometimes vague prompts reveal how Claude interprets
- Pay attention to what produces great output, replicate those conditions
