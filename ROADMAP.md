# Roadmap

ToolWright is a repeatable, safe, provider-neutral development environment for AI coding agents. The current surface is complete for macOS and Linux; the next work is portability, setup ergonomics, and deeper client integration.

## Current

- OpenCode reference adapter, installer, lock file, update check, rollback, and uninstall.
- Installer-generated Claude Code, GitHub Copilot, and OpenAI Codex adapters.
- Agents, commands, skills, profiles, catalog, provenance, and memory.
- Deterministic verification, governance, specs, task board, and evals.
- Optional Ralph orchestration in an isolated clone.
- Minimal code-intelligence guidance: ripgrep, ast-grep, Serena, and optional CodeGraph.

## Next

- `toolwright setup` TUI for project selection, tool selection, plan review, apply, and verification.
- First-class Windows support for the installer and tool detection.
- Native MCP configuration for Claude Code, GitHub Copilot, and OpenAI Codex.
- Continue reducing setup steps without hiding manual or privileged actions.
- Expand tests for adapter discovery and lifecycle behavior on macOS and Linux.

## Explicit non-goals

- A separate model-routing or cost-optimization program.
- A second orchestrator beside Ralph.
- A large agent catalog; the project keeps a focused set of roles.
- A vector database, daemon, A2A hub, or web UI.
- Automatic commits, staging, or merges.
- Self-modifying or self-learning loops without evaluation.

## References

- [`README.md`](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/README.md)
- [`AGENTS.md`](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/AGENTS.md)
- [`docs/validation-checklist.md`](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/validation-checklist.md)
