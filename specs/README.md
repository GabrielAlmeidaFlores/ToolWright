# Specs

Spec-driven development artifacts managed by `toolwright spec`. Each feature gets a directory with four files. It has 4 rows and 2 columns: File and Purpose. Each row is one file, and the other column records Purpose. Read it to compare rows or to find a specific file.

| File | Purpose |
|---|---|
| `requirements.md` | Goals, testable acceptance criteria, non-goals |
| `design.md` | Components, interfaces, decisions, risks |
| `tasks.md` | Small tasks, each mapped to a criterion |
| `evidence.md` | Command or artifact proving each criterion |

## Workflow

```bash
toolwright spec new "Add user authentication" --criterion "A rejected password returns 401" --criterion "A valid login returns a session"
toolwright spec plan user-authentication
toolwright spec list
toolwright spec verify user-authentication
```

`plan` fails until every criterion has at least one task and every task names a valid criterion. `verify` additionally requires evidence for every criterion.

## Format

Criteria and tasks use checkbox lines:

```markdown
- [ ] AC-1: A rejected password returns 401
- [ ] T-1: Implement credential check (criterion: AC-1)
- AC-1: `npm test -- auth` passes
```

Checked boxes (`- [x]`) are accepted. Angle-bracket placeholders from the template are ignored, so a freshly created spec fails verification until it is filled in.

## Ownership

The table below describes Ownership. It has 4 rows and 2 columns: Agent and Responsibility. Each row is one agent, and the other column records Responsibility. Read it to compare rows or to find a specific agent.
|---|---|
| `planner` | Requirements and tasks |
| `architect` | Design and decisions |
| `test-engineer` | Evidence commands and results |
| `code-reviewer` | Checks that evidence matches the criterion |

See [`docs/specs/README.md`](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/specs/README.md) for the full workflow.
