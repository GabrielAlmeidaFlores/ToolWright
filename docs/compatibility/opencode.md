# OpenCode

> **Status:** Stable · **Last verified:** 2026-11-13 · **Evidence:** verified locally and in CI

OpenCode is the fully verified reference adapter and remains optional. ToolWright installs an OpenCode configuration, a custom primary agent, specialized subagents, commands, skills, and optional MCP servers. The same core artifacts install as native files for Claude, GitHub Copilot, and ChatGPT/Codex.

## Install

```bash
git clone https://github.com/GabrielAlmeidaFlores/ToolWright.git
cd ToolWright
uv tool install ./packages/toolwright_cli

toolwright doctor
toolwright install --profile minimal --target /path/to/project --apply
```

Profiles. It has 3 rows and 2 columns: Profile and Components. Each row is one profile, and the other column records Components. Read it to compare rows or to find a specific profile.

| Profile | Components |
|---|---|
| `minimal` | OpenCode configuration, agents, commands, skills, Ralph |
| `standard` | Minimal plus ast-grep |
| `full` | Standard plus Serena, CodeGraph, and the memory plugin |

## Files installed

The table below describes Files installed. It has 6 rows and 2 columns: Path and Purpose. Each row is one path, and the other column records Purpose. Read it to compare rows or to find a specific path.
|---|---|
| `.opencode/opencode.jsonc` | OpenCode configuration |
| `.opencode/agents/*.md` | Primary and subagent definitions |
| `.opencode/commands/*.md` | Slash commands |
| `.opencode/skills/*/SKILL.md` | Reusable skills |
| `.opencode/plugins/toolwright-memory.js` | Opt-in memory plugin |
| `toolwright.lock.json` | Installed file digests and source metadata |

## Verify

```bash
opencode debug agents
opencode run --agent coordinator "Reply with exactly: OK"
toolwright doctor --json --no-mcp
```

The compatibility matrix in `toolwright compat` describes the supported OpenCode V2 surface.

## Agent model

The coordinator is primary and delegates. The planner, researcher, architect, developers, reviewers, test engineer, security reviewer, performance analyst, and documentation engineer are subagents. Permissions are least-privilege: read-only roles cannot edit, and shell access is restricted.

## Ralph

Ralph Orchestrator is optional and uses its OpenCode backend. Read the auto-commit limitation before running it in a repository where automatic commits are unacceptable.

## References

- [OpenCode agents](https://opencode.ai/docs/agents)
- [OpenCode configuration](https://opencode.ai/docs/config)
- [Installation guide](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/installation/opencode.md)
- [CLI reference](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/cli/README.md)
