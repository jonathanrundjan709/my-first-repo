---
description: Parallel QA sweep of the current project
argument-hint: [target path or URL]
---
Target: $ARGUMENTS (default: whole repo)

Launch these subagents IN PARALLEL in one message:
- `qa-tester` - exercise the app and report bugs
- `code-reviewer` - review recent changes
- `security-auditor` - security audit
- `test-writer` - list missing test coverage (do not write yet)
Then merge their output into one deduplicated report ranked by severity.
