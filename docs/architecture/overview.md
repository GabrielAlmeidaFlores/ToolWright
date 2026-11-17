# Architecture Overview

> **Status:** Stable · **Last verified:** 2026-11-17 · **Evidence:** local validation and CLI lifecycle tests

ToolWright is a provider-neutral environment layer around an AI coding client. The client owns model access, tools, and conversation. ToolWright owns the project files that make the workflow consistent: instructions, agents, commands, skills, memory, verification, and lifecycle metadata.

## Layers

```text
┌──────────────────────────────────────────────────────────────┐
│ Human                                                        │
│ TUI or native client UI                                      │
└───────────────────────────┬──────────────────────────────────┘
                            │
┌───────────────────────────▼──────────────────────────────────┐
│ AI coding client                                             │
│ OpenCode · Claude Code · GitHub Copilot · OpenAI Codex       │
└───────────────────────────┬──────────────────────────────────┘
                            │ loads project files
┌───────────────────────────▼──────────────────────────────────┐
│ ToolWright environment                                       │
│ AGENTS.md · agents · commands · skills · memory · lock file  │
└───────┬───────────────────────────┬──────────────────────────┘
        │                           │
┌───────▼──────────────┐  ┌─────────▼───────────────────────────┐
│ Deterministic tools  │  │ Code intelligence                   │
│ tests, lint, tsc,    │  │ ripgrep · ast-grep · Serena MCP     │
│ formatters, git      │  │ CodeGraph MCP                       │
└──────────────────────┘  └─────────────────────────────────────┘
```

## Responsibilities

The table below describes each layer. Read the owns and does-not-own columns together so a failure is assigned to the right layer.

| Layer | Owns | Does not own |
|---|---|---|
| AI coding client | Model access, tool execution, context window | Project conventions |
| ToolWright environment | Project instructions, agents, commands, skills, memory, lock file | Model credentials or billing |
| Deterministic tools | Correctness evidence | Reasoning about intent |
| Code intelligence | Retrieval precision | Deciding what to change |
| Ralph (optional) | Multi-step loops, gates, iteration limits | Tool permissions or model access |

## Request flow

1. A human opens the project in a supported client.
2. The client loads `AGENTS.md`, native adapter files, and project memory.
3. The agent chooses a command or a specialist role.
4. The agent uses native tools, ripgrep, ast-grep, Serena, or CodeGraph as needed.
5. The agent runs the task’s deterministic verification command.
6. Durable findings are recorded in project memory.
7. The human reviews the diff and decides whether to commit.

Ralph is an optional path for long multi-step loops. It runs only in a separate disposable clone because Ralph 2.10.1 commits during landing.

## Data and state

The table below lists the persistent state owned by each component. Read the owner column before deleting or moving a directory.

| State | Location | Owner |
|---|---|---|
| ToolWright lock and state | `toolwright.lock.json`, `.toolwright/state.json` | ToolWright CLI |
| Project memory | `.toolwright/memory/` | ToolWright memory |
| Capacity and usage state | `.toolwright/board/`, `.toolwright/config.toml` | ToolWright board and verification |
| OpenCode sessions | OpenCode data directory | OpenCode |
| Claude, Copilot, Codex files | `.claude/`, `.github/`, `.codex/`, `AGENTS.md` | The selected adapter |
| CodeGraph index | `.codegraph/` | CodeGraph |
| Serena project config | Serena project directory | Serena |
| Ralph state (optional) | `.agent/` or configured `.ralph/agent/` | Ralph |

## Design constraints

- The core is Markdown and configuration; the CLI owns lifecycle and validation.
- OpenCode is the reference adapter, not a requirement.
- MCP configuration is automatic only for OpenCode.
- No component stages, commits, or merges automatically.
- A failed external tool install leaves project files intact and reports a manual step.
