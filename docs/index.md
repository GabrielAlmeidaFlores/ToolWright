# ToolWright

> **Status:** Stable · **Last verified:** 2026-11-16 · **Evidence:** `make ci` green locally with 676 static checks and 321 tests

A provider-neutral multi-agent development toolkit with a fully verified OpenCode adapter and installer-generated adapters for GitHub Copilot, Claude Code, and OpenAI GPT/Codex. OpenCode is optional. It is built around four pillars:

| Pillar | What it provides |
|---|---|
| Environment | OpenCode V2 configuration, agents, commands, skills, Ralph hats, installer, `toolwright` CLI, and installer-generated adapters for Copilot, Claude, and GPT |
| Orchestration | Ralph as the loop owner, coordinator delegation, risk-based gates |
| Intelligence | ripgrep, ast-grep, Serena, CodeGraph, Markdown memory, spec artifacts |
| Optimization | Deterministic verification, governance budgets, cost/token reporting, evals |

## Start here

The core agents, commands, skills, and rules are provider-neutral. The commands below install the OpenCode reference adapter; choose Claude, GitHub Copilot, or ChatGPT/Codex from the compatibility pages if you use a different platform.

```bash
git clone https://github.com/GabrielAlmeidaFlores/ToolWright.git
cd ToolWright
uv tool install ./packages/toolwright_cli
toolwright doctor
toolwright install --profile minimal --target /path/to/project --apply
```

- [Compatibility overview](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/compatibility/README.md)
- [OpenCode installation](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/installation/opencode.md)
- [GitHub Copilot](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/compatibility/github-copilot.md)
- [Claude Code](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/compatibility/claude.md)
- [OpenAI GPT / Codex](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/compatibility/openai-gpt.md)
- [Install the CLI](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/installation/toolwright-cli.md)
- [CLI reference](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/cli/README.md)
- [Profiles](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/profiles/README.md)

## What is verified

| Area | State |
|---|---|
| Static validation | 676 checks, including provenance, permissions, comments, absolute links, and docs status |
| Test suite | 321 offline tests on Ubuntu and macOS |
| CLI | Wheel build, install lifecycle, profile/catalog verification, verification gates |
| Catalog | 34 generated artifacts with drift enforcement |
| Benchmarks | Three published result sets; the Hono cost A/B found no arm cheaper than stock |
| Pilots | Discovery 15/15; Hono 5/5, CleanArchitecture 5/5, turborepo 4/5 reviewed |

Claims link to local evidence or a CI run. Vendor claims are labelled; no benchmark result is published without correctness and rework data.

## Design rules

1. Source and attribute every reusable artifact; do not invent agents, skills, or commands.
2. Never stage or commit automatically; the human decides.
3. Prefer descriptive names over comments; document only contracts.
4. Treat deterministic tools as the source of truth for correctness.
5. Keep the default profile minimal; enable optional tools explicitly.

Full rules: [AGENTS.md](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/AGENTS.md).

## Project

- [Architecture](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/architecture/overview.md)
- [Security](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/security/README.md)
- [Compatibility policy](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/compatibility/policy.md)
- [Provenance](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/provenance/README.md)
- [Release process](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/release/README.md)
- [Troubleshooting](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/troubleshooting/README.md)
