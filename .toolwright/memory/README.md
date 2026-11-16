# Project Memory

This directory holds plain Markdown memory managed by `toolwright memory`. There are no embeddings and no background service.

## Scopes

The table below describes Scopes. It has 3 rows and 3 columns: Scope, Tracked in Git, and Purpose. Each row is one scope, and the other columns record Tracked in Git and Purpose. Read it to compare rows or to find a specific scope.
|---|---|---|
| `project/` | Yes | Repository decisions, constraints, conventions, failures, open questions |
| `shared/` | Yes | Knowledge published with the repository |
| `user/` | No | Local preferences; ignored by [`.gitignore`](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/.gitignore) |

Precedence for the generated preamble is `project > user > shared`.

## Entry format

```markdown
---
type: decision
title: Short title
created: 2026-11-12
source: docs/adr-or-commit
confidence: 0.9
expires: 2026-12-12
links: [docs/decisions/ADR-001.md]
---

Explain the decision, constraint, convention, failure, or question.
```

Types: `decision`, `constraint`, `convention`, `failure`, `question`.

## Commands

```bash
toolwright memory add "Use expand-and-contract migrations" --type constraint --source docs/decisions/ADR-001.md
toolwright memory search migrations
toolwright memory prune
toolwright memory prune --apply --yes
toolwright memory export --format json
toolwright memory preamble --budget 1500
```

`add` rejects duplicate titles in the same scope and refuses text that matches a credential pattern. Expired entries are never injected into the preamble.

`catalog.md` is generated from the entries; do not edit it by hand.

## Configuration

[`.toolwright/config.toml`](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/.toolwright/config.toml):

```toml
[memory]
token_budget = 2000
ttl_days = 30
```

## Using memory with OpenCode

Reference this directory from the project [`AGENTS.md`](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/AGENTS.md), or load the preamble on demand:

```bash
toolwright memory preamble
```

Session-start injection through a plugin is deferred to a later phase. See [`docs/memory/README.md`](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/memory/README.md).
