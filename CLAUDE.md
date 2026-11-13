# Multi-agent workspace

The main session is the **orchestrator**: plan, delegate, merge results. Specialists live in `.claude/agents/`.

## Roster
| Agent | Job | Writes code? |
|---|---|---|
| planner | break goal into steps | no |
| researcher | find answers in code/web | no |
| implementer | make one scoped change | yes |
| test-writer | write automated tests | yes |
| qa-tester | use the app, file bugs | no |
| code-reviewer | review diffs | no |
| security-auditor | defensive audit | no |
| debugger | root-cause + fix | yes |
| refactorer | restructure safely | yes |
| doc-writer | docs/README | yes |
| data-analyst | analyze data files | scripts only |

## Delegation rules
- Independent tasks -> launch agents in parallel in a single message.
- Give each agent a self-contained prompt; they don't see this conversation.
- Read-only agents for judging, writing agents for changing. Never let the same agent write and approve its own work.
- Agents report outcomes faithfully; failing tests are reported, not hidden.

## Slash commands
- `/ship-feature <desc>` - full pipeline
- `/qa-sweep [target]` - parallel QA
- `/investigate <question>` - parallel research
