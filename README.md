# ToolWright

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/logo-dark.svg">
    <img src="assets/logo.svg" alt="ToolWright" width="420">
  </picture>
</p>

<p align="center">
  <a href="https://github.com/GabrielAlmeidaFlores/ToolWright/actions/workflows/validate.yml"><img alt="CI green" src="https://img.shields.io/badge/CI-green-22C55E?style=flat-square"></a>
  <a href="https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/architecture/testing.md"><img alt="293 tests" src="https://img.shields.io/badge/tests-293-4F46E5?style=flat-square"></a>
  <a href="https://github.com/GabrielAlmeidaFlores/ToolWright/tree/main/agents"><img alt="12 agents" src="https://img.shields.io/badge/agents-12-06B6D4?style=flat-square"></a>
  <a href="https://github.com/GabrielAlmeidaFlores/ToolWright/tree/main/skills"><img alt="10 skills" src="https://img.shields.io/badge/skills-10-D97757?style=flat-square"></a>
  <a href="https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/LICENSE"><img alt="MIT license" src="https://img.shields.io/badge/license-MIT-0F172A?style=flat-square"></a>
</p>

<p align="center">
  <strong>A repeatable, safe, provider-neutral development environment for AI coding agents.</strong>
</p>

<p align="center">
  <a href="#quick-start">Quick start</a> ·
  <a href="#what-you-get">What you get</a> ·
  <a href="#daily-workflow">Daily workflow</a> ·
  <a href="#compatibility">Compatibility</a> ·
  <a href="#documentation">Documentation</a>
</p>

> **ToolWright does not make the model cheaper or smarter.**<br>
> It makes the workflow around the model consistent, verifiable, and portable across repositories and clients.

## Why ToolWright

AI coding setups tend to drift: every project gets different instructions, different tools, and different rules. ToolWright turns that into a managed project environment.

The table below contrasts the usual ad hoc setup with the ToolWright approach. Read the rows as workflow outcomes, not benchmark claims.

| Without a shared environment | With ToolWright |
|---|---|
| Rules live in someone’s head or a chat history | Instructions, agents, commands, and skills live in the repository |
| Each client needs a different setup | Native adapters for OpenCode, Claude Code, GitHub Copilot, and OpenAI Codex |
| Verification depends on memory | Deterministic tests, lint, typecheck, and acceptance commands |
| Context is rediscovered every session | Project memory records durable decisions and constraints |
| Tool sprawl and MCP overhead | A minimal default set with optional advanced tools |
| Installations are hard to update or remove | Lock file, update check, rollback, and uninstall |

## What you get

The table below summarizes the main building blocks. Each row links to the directory or guide that owns it.

| Building block | What it gives you |
|---|---|
| **[Agents](https://github.com/GabrielAlmeidaFlores/ToolWright/tree/main/agents)** | A coordinator and eleven specialists with explicit permissions |
| **[Commands](https://github.com/GabrielAlmeidaFlores/ToolWright/tree/main/commands)** | Repeatable entry points such as `/implement`, `/review`, `/debug`, and `/security` |
| **[Skills](https://github.com/GabrielAlmeidaFlores/ToolWright/tree/main/skills)** | Sourced workflows for planning, TDD, debugging, review, API design, migrations, auth, and changelogs |
| **[Memory](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/memory/README.md)** | Project decisions, constraints, conventions, and failures in bounded Markdown |
| **[Verification](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/verification/README.md)** | Tests, lint, typecheck, scope checks, and one acceptance command per task |
| **[Code intelligence](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/code-intelligence/README.md)** | ripgrep, ast-grep, Serena, and optional CodeGraph |
| **[Lifecycle](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/cli/README.md)** | Plan, install, update, uninstall, backup, and rollback through `toolwright` |
| **[Ralph](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/orchestration/ralph.md)** | Optional orchestration loops, isolated from the main checkout |

## Quick start

### 1. Install the CLI

```bash
export TOOLWRIGHT_REPO=/path/to/ToolWright
uv tool install "$TOOLWRIGHT_REPO/packages/toolwright_cli[tui]"
```

The optional `tui` extra enables the interactive setup screen. The CLI works without it.

### 2. Set up a project

**Recommended:** open the setup screen.

```bash
toolwright setup --target /path/to/project
```

The screen selects the project, adapter, and project components, previews the planned files, applies them, and writes the lock. It does not install client applications, credentials, or native MCP configuration.

**Or run the commands directly.** Expand the client you use:

<details>
<summary><strong>OpenCode</strong> — reference adapter</summary>

```bash
cd /path/to/project
"$TOOLWRIGHT_REPO/scripts/installation/install.sh" --apply \
  --only opencode,agents,commands,skills,plugin,ast-grep,serena,codegraph --target .
touch .toolwright/memory/plugin.enabled
if command -v codegraph >/dev/null; then codegraph init; fi
```

Add Ralph only when you want isolated orchestration loops:

```bash
"$TOOLWRIGHT_REPO/scripts/installation/install.sh" --apply --only ralph --target .
```

</details>

<details>
<summary><strong>Claude Code</strong></summary>

```bash
cd /path/to/project
toolwright install --platform claude --profile minimal --target . --apply
```

</details>

<details>
<summary><strong>GitHub Copilot</strong></summary>

```bash
cd /path/to/project
toolwright install --platform copilot --profile minimal --target . --apply
```

</details>

<details>
<summary><strong>OpenAI Codex</strong></summary>

```bash
cd /path/to/project
toolwright install --platform codex --profile minimal --target . --apply
```

</details>

Commit `toolwright.lock.json` with the project. It records what ToolWright owns and makes updates and removals safe.

### 3. Verify

```bash
toolwright doctor
```

For the repository itself, run the full local gate:

```bash
make ci
```

## Daily workflow

1. Open the project in your AI client.
2. Ask for a plan before multi-file work.
3. Use a command such as `/implement`, `/review`, or `/debug` when it fits.
4. Run the acceptance command before accepting the result.
5. Record durable findings in project memory.
6. Leave commits to the human unless you explicitly request one.

The repository’s operating rules are in [`AGENTS.md`](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/AGENTS.md).

## Core concepts

### Memory

Memory is plain Markdown under `.toolwright/memory/`. It uses lexical search, expiry, and a bounded preamble instead of embeddings or a vector database.

```text
.toolwright/memory/
├── project/   tracked decisions, constraints, conventions
├── shared/    tracked published knowledge
├── user/      local preferences
└── catalog.md generated index
```

Use it when a decision or failure should not be rediscovered:

```bash
toolwright memory add "Set-Cookie merge keeps the old cookie and drops the new one" \
  --type constraint --source src/context.ts
toolwright memory search set-cookie
toolwright memory preamble --budget 1500
```

The generated instructions tell Claude, Copilot, and Codex to read the memory catalog. The OpenCode plugin injects the bounded preamble after `.toolwright/memory/plugin.enabled` exists.

### Verification

Verification is the core of the workflow. Every task should end with a deterministic command:

```bash
toolwright verify
```

The repository applies the same idea to itself through `make ci`: tests, lint, documentation checks, catalog drift, and a clean Git diff.

### Code intelligence

Start with the smallest useful set:

- **ripgrep** for exact search.
- **LSP or Serena** for symbols, definitions, and references.
- **ast-grep** for structural search and codemods.
- **CodeGraph** only when dependency questions dominate.

Do not enable every MCP server by default. Each server adds schema and context overhead.

### Ralph orchestration

Ralph is optional. It is useful for long multi-step loops, but version 2.10.1 commits during landing and has no switch to disable it. Run it only in a separate disposable clone; a linked worktree shares `.git` and is not sufficient.

## Update and remove

Check for drift, then rerun the same install command with `--apply`:

```bash
toolwright update --check --target /path/to/project
```

Remove managed files with:

```bash
toolwright uninstall --target /path/to/project --dry-run
toolwright uninstall --target /path/to/project --apply --yes
```

`--force` removes modified managed files. `--purge` also deletes `.toolwright/`, including project memory, so export anything you want to keep first. The full lifecycle is in the [CLI reference](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/cli/README.md).

## Compatibility

The table below summarizes the supported adapters and their verification state. Read the support column as an evidence label, not a guarantee of every client feature.

| Client | Support | Generated files |
|---|---|---|
| OpenCode 2.2.x | Verified reference adapter | `.opencode/`, memory plugin; Ralph optional |
| Claude Code | Installer-generated, runtime discovery partly verified | `CLAUDE.md`, `.claude/agents/`, commands, skills |
| GitHub Copilot | Installer-generated, CLI discovery verified | `.github/copilot-instructions.md`, instructions, prompts, skills, `AGENTS.md` |
| OpenAI Codex | Installer-generated, [`AGENTS.md`](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/AGENTS.md) loading verified | `AGENTS.md`, `.codex/agents/*.toml` |

## Limits

- macOS and Linux are supported. Windows is not supported or validated for the full workflow.
- MCP configuration is generated only for OpenCode. Claude Code, Copilot, and Codex require native MCP configuration.
- Client login, billing, and model selection remain outside ToolWright.
- ToolWright does not claim a cost, quality, or routing win.

## Documentation

The table below groups the detailed guides by task. Start with installation or compatibility, then follow the area you need.

| I want to… | Read |
|---|---|
| Install and update the CLI | [Installation](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/installation/toolwright-cli.md) · [CLI reference](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/cli/README.md) |
| Use a specific client | [Compatibility](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/compatibility/README.md) |
| Understand the design | [Architecture](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/architecture/overview.md) · [Agents](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/agents/roles.md) |
| Keep context across sessions | [Memory](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/memory/README.md) |
| Add deterministic checks | [Verification](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/verification/README.md) · [Governance](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/governance/README.md) |
| Choose tools | [Code intelligence](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/code-intelligence/README.md) · [Profiles](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/profiles/README.md) |
| Fix a problem | [Troubleshooting](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/troubleshooting/README.md) |
| Contribute | [Contributing](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/CONTRIBUTING.md) · [`AGENTS.md`](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/AGENTS.md) · [Provenance](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/provenance/README.md) |

## License

MIT. See [`LICENSE`](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/LICENSE).
