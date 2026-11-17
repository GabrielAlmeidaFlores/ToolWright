# ToolWright

<p align="center">
  <img src="assets/logo.svg" alt="ToolWright" width="420">
</p>

<p align="center">
  <img alt="CI green" src="https://img.shields.io/badge/CI-green-22C55E?style=flat-square">
  <img alt="292 tests" src="https://img.shields.io/badge/tests-292-4F46E5?style=flat-square">
  <img alt="12 agents" src="https://img.shields.io/badge/agents-12-06B6D4?style=flat-square">
  <img alt="10 skills" src="https://img.shields.io/badge/skills-10-D97757?style=flat-square">
  <img alt="MIT license" src="https://img.shields.io/badge/license-MIT-0F172A?style=flat-square">
</p>

**A repeatable, safe, provider-neutral development environment for AI coding agents.**

ToolWright does not make the model cheaper or smarter. It makes the workflow around the model consistent, verifiable, and portable across repositories and clients.

## What it is

ToolWright installs and maintains the files an AI coding client needs:

- specialized agents with least-privilege permissions
- reusable commands and skills
- project instructions and memory
- deterministic verification gates
- optional code-intelligence tools
- native adapters for OpenCode, Claude Code, GitHub Copilot, and OpenAI Codex
- a lock file, update path, uninstall path, and backups

The core is plain Markdown and configuration. OpenCode is the reference adapter, but it is optional.

## What it is not

- It is not a model provider and does not include credentials.
- It is not a cost-optimization guarantee.
- It is not a model-routing or performance guarantee.
- It is not a global configuration manager. Setup is project-local by design.

## What you get

- **Agents:** a coordinator and eleven specialists with explicit permissions.
- **Commands:** repeatable entry points such as `/implement`, `/review`, `/debug`, and `/security`.
- **Skills:** sourced workflows for planning, TDD, debugging, review, API design, migrations, authentication, and changelogs.
- **Memory:** project decisions, constraints, conventions, and failures in bounded Markdown.
- **Verification:** tests, lint, typecheck, scope checks, and a single acceptance command per task.
- **Code intelligence:** ripgrep, ast-grep, Serena, and optional CodeGraph.
- **Lifecycle:** plan, install, update, uninstall, backup, and rollback through `toolwright`.
- **Ralph:** optional orchestration loops, isolated from the main checkout.

## Prerequisites

- macOS or Linux. Windows is not yet validated for the full workflow.
- `git`, Node.js 20 or newer, Python 3.11 or newer, and `ripgrep`.
- A supported AI client and its credentials.
- For the reference adapter: OpenCode 2.2.x.

### Platform support

macOS and Linux are supported. Windows is not supported for the full workflow: the shell installer, external tool commands, and client discovery are not validated there. Do not present Windows as a supported platform until a native path is tested.

### MCP support

MCP server configuration is generated only for OpenCode. Claude Code, GitHub Copilot, and OpenAI Codex installations do not write MCP server configuration; use each client's native configuration if you need Serena or CodeGraph there.

## One-time setup per project

Install the CLI once on the machine:

```bash
export TOOLWRIGHT_REPO=/path/to/ToolWright
uv tool install "$TOOLWRIGHT_REPO/packages/toolwright_cli"
```

Then run the setup once in each project folder. The generated files are read when the client opens that folder, so you do not repeat setup per session.

```bash
cd /path/to/project

# OpenCode: configuration, agents, commands, skills, memory plugin, and tools
"$TOOLWRIGHT_REPO/scripts/installation/install.sh" --apply \
  --only opencode,agents,commands,skills,plugin,ast-grep,serena,codegraph --target .

# Optional: Ralph orchestration
# "$TOOLWRIGHT_REPO/scripts/installation/install.sh" --apply --only ralph --target .
touch .toolwright/memory/plugin.enabled
if command -v codegraph >/dev/null; then codegraph init; fi

# Claude Code
toolwright install --platform claude  --profile minimal --target . --apply

# GitHub Copilot
toolwright install --platform copilot --profile minimal --target . --apply

# OpenAI Codex
toolwright install --platform codex   --profile minimal --target . --apply
```

The `TOOLWRIGHT_REPO` export tells the installed CLI where the source artifacts live. Set it in your shell profile if you use the CLI across projects.

The generated files differ by client:

- OpenCode uses `.opencode/` and the memory plugin. Ralph is an optional extra.
- Claude Code uses `CLAUDE.md`, `.claude/agents/`, `.claude/commands/`, and `.claude/skills/`.
- GitHub Copilot uses `.github/copilot-instructions.md`, `.github/instructions/`, `.github/prompts/`, `.github/skills/`, and `AGENTS.md`.
- Codex uses `AGENTS.md` and `.codex/agents/*.toml`.

Commit `toolwright.lock.json` with the project so updates and removals remain safe.

### Setup limits

ToolWright configures MCP servers for OpenCode. It does not currently generate MCP configuration for Claude Code, Copilot, or Codex. Those clients need native MCP configuration if you want Serena or CodeGraph there.

The setup is project-local. Global client configuration is not modified, and model credentials are never stored.

## Interactive setup

Install the optional TUI dependency once:

```bash
uv tool install "$TOOLWRIGHT_REPO/packages/toolwright_cli[tui]"
toolwright setup --target /path/to/project
```

The setup screen selects the project, adapter, and project components, previews the planned files, applies them, and reports the lock path. The TUI does not install client applications or model credentials.

## Daily use

1. Open the project in your AI client.
2. Start with the coordinator or a specialist, depending on the task.
3. Ask for a plan before multi-file work.
4. Use a command such as `/implement`, `/review`, or `/debug` when it fits.
5. Run the acceptance command before accepting the result.
6. Record durable findings in project memory.
7. Leave commits to the human unless you explicitly request one.

The repository’s operating rules are in [`AGENTS.md`](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/AGENTS.md).

## Memory

Memory is plain Markdown under `.toolwright/memory/`:

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

The generated instructions tell Claude, Copilot, and Codex to read the memory catalog. The OpenCode memory plugin injects the bounded preamble automatically after `.toolwright/memory/plugin.enabled` exists.

See the [memory guide](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/memory/README.md).

## Verification

Verification is the core of the workflow. Every task should end with a deterministic command:

```bash
toolwright verify
make ci
```

The repository uses tests, lint, docs checks, catalog drift checks, and a clean Git diff. The same pattern applies to a user project: one acceptance command per task, recorded with the result.

See [verification](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/verification/README.md) and [governance](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/governance/README.md).

## Code intelligence

Start with the smallest useful set:

- **ripgrep** for exact search.
- **LSP or Serena** for symbols, definitions, and references.
- **ast-grep** for structural search and codemods.
- **CodeGraph** only when dependency questions dominate.

Do not enable every MCP server by default. Each server adds schema and context overhead.

See [code intelligence](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/code-intelligence/README.md).

## Ralph orchestration (optional)

Ralph is kept for multi-step loops with research, code-assist, review, and debug hats. Version 2.10.1 commits during landing and has no switch to disable it. Run it only in a separate disposable clone; a linked worktree shares `.git` and is not sufficient.

See the [Ralph guide](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/orchestration/ralph.md).

## Update and remove

Check for drift, then rerun the same install command with `--apply`:

```bash
toolwright update --check --target /path/to/project
```

Remove the managed files with:

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

See [platform compatibility](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/compatibility/README.md).

## Evidence and limits

The repository does not claim a cost or quality win from routing. No production default is based on such a claim.

Other limits:

- MCP configuration is automatic only for OpenCode.
- Client login, billing, and model selection remain outside ToolWright.

## Documentation

- [Installation](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/installation/toolwright-cli.md)
- [Architecture](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/architecture/overview.md)
- [Testing](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/architecture/testing.md)
- [Agents and roles](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/agents/roles.md)
- [Memory](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/memory/README.md)
- [Verification](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/verification/README.md)
- [Profiles](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/profiles/README.md)
- [Catalog and provenance](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/catalog/README.md)
- [Troubleshooting](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/troubleshooting/README.md)

## Contributing

Read [`CONTRIBUTING.md`](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/CONTRIBUTING.md) and [`AGENTS.md`](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/AGENTS.md). Do not stage or commit automatically; leave changes for human review.

## License

MIT. See [`LICENSE`](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/LICENSE).
