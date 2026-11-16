# Code Intelligence

> **Status:** Stable · **Last verified:** 2026-11-12 · **Evidence:** verified locally

The default stack answers different questions with the cheapest sufficient tool.

| Question | Tool |
| --- | --- |
| Where is this string, error, or config key? | `grep` / `rg` |
| Which files match this name? | `glob` / `rg --files` |
| Which code has this structure? | ast-grep |
| Where is this symbol defined or referenced? | Serena |
| What calls this / what breaks if I change it? | CodeGraph |

## Defaults

- ripgrep — installed, no MCP.
- ast-grep — CLI, no MCP.
- Serena — MCP, `--context ide`.
- CodeGraph — MCP, per-project index.

## Optional

Repomix, jCodeMunch, Universal Ctags, Graphify, and Aider repository maps are documented in [optional-tools.md](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/code-intelligence/optional-tools.md). They are not installed by default.

## Overhead rules

1. One MCP server per concern. Do not add a second symbol server.
2. Use Code Mode and permission filtering instead of exposing every tool.
3. Index once; do not re-index on every prompt.
4. Disable the stack on small repositories; use the minimal config.
5. Measure startup time before enabling a server in an interactive loop.

## Pages

- [ripgrep](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/code-intelligence/ripgrep.md)
- [ast-grep](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/code-intelligence/ast-grep.md)
- [Serena](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/code-intelligence/serena.md)
- [CodeGraph](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/code-intelligence/codegraph.md)
- [Optional tools](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/code-intelligence/optional-tools.md)
- [MCP overhead](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/code-intelligence/overhead.md)
