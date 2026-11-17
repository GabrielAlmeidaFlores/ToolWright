# ToolWright

> **Status:** Stable · **Last verified:** 2026-11-17 · **Evidence:** `make ci` green locally with 663 static checks and 302 tests

**A repeatable, safe, provider-neutral development environment for AI coding agents.**

ToolWright does not make the model cheaper or smarter. It makes the workflow around the model consistent, verifiable, and portable.

## Start here

```bash
export TOOLWRIGHT_REPO=/path/to/ToolWright
uv tool install "$TOOLWRIGHT_REPO/packages/toolwright_cli"
toolwright doctor
```

Then run the project setup once per folder:

```bash
cd /path/to/project
"$TOOLWRIGHT_REPO/scripts/installation/install.sh" --apply --all --target .
touch .toolwright/memory/plugin.enabled
toolwright install --platform claude  --profile minimal --target . --apply
toolwright install --platform copilot --profile minimal --target . --apply
toolwright install --platform codex   --profile minimal --target . --apply
```

The generated files are loaded when the client opens the project. No per-session setup is required.

## The four pillars

The table below summarizes the parts of the environment that ToolWright owns. Read it as a map of responsibilities, not a feature comparison.

| Pillar | What it provides |
|---|---|
| **Runtime** | Agents, commands, skills, permissions, OpenCode configuration, native adapters |
| **Context** | Project memory, instructions, specs, code-intelligence guidance |
| **Verification** | Tests, lint, typecheck, scope checks, governance, CI gates |
| **Lifecycle** | Plan, install, update, uninstall, backups, lock file, provenance |

## What is verified

The table below records the strongest evidence label for each capability area. Read the label as a confidence statement: verified means a command or CI run exists, while unverified means the behavior is not proven.

| Area | State |
|---|---|
| Static validation | 663 checks, including provenance, permissions, comments, links, and docs status |
| Test suite | 302 offline tests on Ubuntu and macOS |
| CLI | Wheel build, install lifecycle, profile and catalog checks, verification gates |
| Adapters | OpenCode verified; Claude, Copilot, and Codex installer-generated and partly runtime-verified |

## Design rules

1. Source and attribute every reusable artifact.
2. Never stage or commit automatically.
3. Prefer descriptive names over explanatory comments.
4. Treat deterministic tools as the source of truth for correctness.
5. Keep the default profile minimal and make optional tools explicit.

Full rules: [`AGENTS.md`](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/AGENTS.md).

## Documentation

- [Installation](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/installation/toolwright-cli.md)
- [Architecture](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/architecture/overview.md)
- [Compatibility](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/compatibility/README.md)
- [Memory](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/memory/README.md)
- [Verification](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/verification/README.md)
- [Code intelligence](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/code-intelligence/README.md)
- [CLI reference](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/cli/README.md)
- [Security](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/security/README.md)
