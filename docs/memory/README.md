# Project Memory

> **Status:** Stable · **Last verified:** 2026-11-17 · **Evidence:** `make ci` and adapter tests pass locally

Memory is plain Markdown under `.toolwright/memory/`. There are no embeddings, no vector database, and no background service.

## Layout

```text
.toolwright/memory/
├── catalog.md      generated index
├── project/        repository decisions and constraints (tracked)
├── shared/         published knowledge (tracked)
└── user/           local preferences (gitignored)
```

Precedence for the generated preamble is `project > user > shared`.

## Entry format

```markdown
---
type: decision
title: Use expand-and-contract migrations
created: 2026-11-12
source: docs/decisions/ADR-001.md
confidence: 0.9
expires: 2026-12-12
links: [docs/decisions/ADR-001.md]
---

Replace columns in expand and contract steps so old and new code can run
against the same schema during a rolling deploy.
```

Allowed types: `decision`, `constraint`, `convention`, `failure`, `question`.

## Commands

```bash
toolwright memory add "Use expand-and-contract migrations" --type constraint --source docs/decisions/ADR-001.md
toolwright memory add "Flaky auth test" --type failure --ttl-days 7
toolwright memory search migrations
toolwright memory search --type constraint access
toolwright memory prune
toolwright memory prune --apply --yes
toolwright memory export
toolwright memory export --format json
toolwright memory preamble --budget 1500
```

The table below describes Commands. It has 5 rows and 2 columns: Command and Behavior. Each row is one command, and the other column records Behavior. Read it to compare rows or to find a specific command.

| Command | Behavior |
|---|---|
| `add` | Writes one entry, rejects duplicate titles per scope, and refuses credential patterns |
| `search` | Lexical match over title, body, source, and type; optional type and scope filters |
| `prune` | Lists expired entries; `--apply --yes` deletes them and regenerates the catalog |
| `export` | Markdown or JSON snapshot |
| `preamble` | Deterministic, token-bounded summary ordered by scope precedence |

## Guarantees

- **No embeddings.** Search is lexical and deterministic.
- **Bounded context.** The preamble stops at the configured token budget (estimated at four characters per token).
- **Expiry.** Entries expire after `ttl_days` and are excluded from the preamble. Default: 30 days.
- **Secrets.** Candidate AWS keys, GitHub tokens, OpenAI keys, private keys, and generic `api_key`/`token`/`password` assignments are rejected before writing.
- **Deduplication.** A normalized title match in the same scope is refused unless `--force` is used.
- **Git.** `project/` and `shared/` are tracked; `user/` is ignored. `catalog.md` is generated.

## Configuration

```toml
[memory]
token_budget = 2000
ttl_days = 30
```

## Automatic use by client

The project [`AGENTS.md`](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/AGENTS.md) now contains a binding memory protocol: read `.toolwright/memory/catalog.md` before exploring code, verify any claim against its cited source, and record durable findings. The Claude, GitHub Copilot, and Codex adapters copy that file. No plugin or CLI invocation is required for those clients to receive the instruction.

OpenCode adds a stronger path: the opt-in plugin runs `toolwright memory preamble` and injects the bounded summary into each request, so the memory content is already in context. The CLI remains the stable interface for recording and searching entries:

```bash
toolwright memory preamble
```

The protocol asks an agent to read the memory files with its file tools; it does not copy memory content into generated instruction files. That keeps one source of truth and avoids stale duplicated snapshots. If a client cannot read repository files, memory is not available to it.

## Design reference

The three-partition Markdown-first model follows `aerovato/operator-memory` (BSD-3-Clause): deterministic loading, catalog routing, and no retrieval by similarity. The implementation is original Python; see [`docs/provenance/registry.yml`](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/provenance/registry.yml) entry `memory-and-specs`.

## References

- [`docs/specs/README.md`](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/specs/README.md)
- [`docs/decisions/ADR-007-memory-without-rag.md`](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/decisions/ADR-007-memory-without-rag.md)
- [`.toolwright/memory/README.md`](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/.toolwright/memory/README.md)
