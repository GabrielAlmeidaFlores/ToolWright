Repository: https://github.com/GabrielAlmeidaFlores/ToolWright

# Install Ralph Orchestrator

> **Status:** Stable · **Last verified:** 2026-11-17 · **Evidence:** verified locally

## Prerequisites

- Node >= 18
- OpenCode V2 installed and authenticated
- Optional: Rust toolchain only for `ralph web`

## Install

```bash
npm install -g @ralph-orchestrator/ralph-cli
ralph --version
```

Expected: `2.10.x`.

## Initialize

```bash
ralph init --backend opencode
```

This writes a `ralph.yml` in the current directory. The repository's configuration is under `configs/ralph/`; use it directly rather than accepting defaults.

## Verify the backend

```bash
opencode run --agent coordinator "Reply with OK"
ralph preflight --format human
```

`ralph preflight` checks config, hooks, backend, git, paths, tools, and specs. Treat warnings as actionable, not decorative.

## Auto-commit warning

Ralph 2.10.1 runs a git commit during landing even when `features.auto_merge` is `false`. Do not point it at a repository that must remain uncommitted, regardless of whether the tree is clean before the run. Use [`scripts/maintenance/run-ralph-isolated.sh`](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/scripts/maintenance/run-ralph-isolated.sh) (not a linked worktree, which shares `.git`), or use the native OpenCode agents instead.

## First run

Run this only inside a separate disposable clone:

```bash
# Inside /tmp/toolwright-ralph or another disposable clone
ralph run \
  -c configs/ralph/ralph.yml \
  -H configs/ralph/hats/code-assist.yml \
  -p "Add input validation to the example TypeScript endpoint and verify with tests"
```

## Configuration options that matter

The table below describes Configuration options that matter. It has 5 rows and 3 columns: Option, Value, and Why. Each row is one option, and the other columns record Value and Why. Read it to compare rows or to find a specific option.
| --- | --- | --- |
| `cli.backend` | `opencode` | Use OpenCode as the runtime |
| `adapters.opencode.timeout` | `900` | MCP and language-server startup |
| `event_loop.max_iterations` | `40` | Cost ceiling |
| `memories.budget` | `2000` | Bound injected context |
| `features.parallel` | `false` | Avoid index and file conflicts |

## Common problems

The table below describes Common problems. It has 5 rows and 2 columns: Symptom and Fix. Each row is one symptom, and the other column records Fix. Read it to compare rows or to find a specific symptom.
| --- | --- |
| Backend not found | `which opencode`; it must be on `PATH` |
| Auth failure | Run OpenCode directly once |
| Hangs on first iteration | Raise `adapters.opencode.timeout` |
| Never completes | Check that the collection emitted its completion promise |
| Gate passes incorrectly | The critic must run the verification commands itself |

## Uninstall

```bash
npm uninstall -g @ralph-orchestrator/ralph-cli
```

State under `.ralph/` is project-local; remove it separately if desired.

## References

- https://github.com/mikeyobrien/ralph-orchestrator
- https://mikeyobrien.github.io/ralph-orchestrator/guide/backends/
- https://mikeyobrien.github.io/ralph-orchestrator/guide/configuration/
