# Benchmark Arms

These configurations are benchmark-only. They do not change production profiles or defaults.

The table columns are the arm label, the config loaded by the harness, the primary agent, and the purpose of that arm.

| Arm | Config | Agent | Purpose |
|---|---|---|---|
| `baseline` | `benchmarks/baseline/opencode.json` | `build` | Stock OpenCode |
| `optimized` | workspace `.opencode/opencode.jsonc` | `coordinator` | Current ToolWright profile |
| `coordinator-slim` | `benchmarks/arms/slim.jsonc` | `coordinator` | No MCP, 400-line tool output cap |
| `direct-slim` | `benchmarks/arms/slim.jsonc` | `backend-developer` | No MCP, 400-line tool output cap, no coordinator hop |
| `tools-on-demand` | `benchmarks/arms/tools-on-demand.jsonc` | `coordinator` | Full MCP surface, 400-line tool output cap |

Run one arm:

```bash
OPENCODE_BENCH_MODEL=deepseek/deepseek-flash \
  ./benchmarks/harness/run.sh \
  --arm coordinator-slim \
  --task benchmarks/real/hono/tasks/set-cookie.json \
  --workspace /tmp/toolwright-hono
```

`baseline` requires a clean checkout without a project `.opencode` directory. Other arms require the workspace agents to be installed. The harness copies non-workspace arm configs into the disposable workspace before running; `--dry-run` prints the copy and the command it would execute.

The copy overwrites `<workspace>/.opencode/opencode.jsonc`. Use a fresh checkout per arm, or reinstall the profile before running `optimized` again, otherwise that arm would load the last arm's config.

Every run is bounded by the task's `max_wall_time_seconds` and its process group is terminated afterwards, so MCP servers started by one arm cannot affect the next run.

Each arm config is a copy of its source config with only `tool_output` changed: `slim.jsonc` from `configs/opencode/minimal.jsonc`, `tools-on-demand.jsonc` from `configs/opencode/opencode.jsonc`. `tests/unit/test_benchmark_arms.py` fails when an arm drifts from its source for any other key.

Step budgets stay in the agent frontmatter. A config-level `agents` entry does not override an agent defined by a Markdown file, so the arms do not pretend to change it; step limits are a separate Phase 3 change.

These arms are inputs to the A/B experiment. Do not promote any arm to production before the result is reviewed.
