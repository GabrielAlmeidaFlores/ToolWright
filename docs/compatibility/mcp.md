# MCP by Client

> **Status:** Experimental · **Last verified:** 2026-11-17 · **Evidence:** OpenCode config inspection, Claude `mcp list`, Copilot `mcp --help`, and Codex `mcp --help`

MCP support is not identical across clients. ToolWright generates MCP server configuration only for OpenCode. The other clients own their MCP configuration and may store it at user scope, which ToolWright does not modify.

The table below records where each client expects MCP configuration and whether ToolWright generates it. Read the scope column before expecting a project-local setup.

| Client | MCP scope | ToolWright behavior |
|---|---|---|
| OpenCode | Project `.opencode/opencode.jsonc` | Generates Serena and CodeGraph server entries |
| Claude Code | Project `.mcp.json` or user scope | Does not generate; Claude reads `.mcp.json` but requires approval |
| GitHub Copilot CLI | User scope | Does not generate; `copilot mcp add` writes user configuration |
| OpenAI Codex | User scope | Does not generate; `codex mcp add` writes user configuration |

Claude Code supports project-local MCP through `.mcp.json`. Add it manually when needed:

```json
{
  "mcpServers": {
    "serena": {
      "command": "serena",
      "args": ["start-mcp-server", "--context", "ide", "--project-from-cwd"]
    },
    "codegraph": {
      "command": "codegraph",
      "args": ["serve", "--mcp"]
    }
  }
}
```

Copilot and Codex currently expose MCP management at user scope in their non-interactive CLIs. ToolWright does not change user-global configuration; run their native `mcp add` command if you want those servers available.

This is an intentional limit, not a silent fallback. The project files still install normally; only MCP configuration is client-specific.
