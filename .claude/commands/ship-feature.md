---
description: Full pipeline for a feature - plan, implement, test, QA, review, security, docs
argument-hint: <feature description>
---
Feature: $ARGUMENTS

Run this pipeline using subagents, passing each one only the context it needs:
1. `planner` - produce the plan.
2. `researcher` - only if the plan lists unknowns.
3. `implementer` - one invocation per plan step (parallel where the plan says independent).
4. `test-writer` - tests for the new behavior.
5. `qa-tester` - exercise it for real.
6. In parallel: `code-reviewer` and `security-auditor`.
7. `debugger` for any failure found; loop back to step 5.
8. `doc-writer` - update docs.
Finish with a short summary: what was built, test results, open issues.
