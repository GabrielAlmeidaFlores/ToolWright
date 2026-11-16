# Hono Cost A/B Results

> **Status:** Experimental · **Last verified:** 2026-11-16 · **Evidence:** 45 isolated harness runs on `deepseek/deepseek-flash`; artifacts under [`benchmarks/results/hono-cost-ab-2026-11-16/`](https://github.com/GabrielAlmeidaFlores/ToolWright/tree/main/benchmarks/results/hono-cost-ab-2026-11-16)

## The short answer

**No arm was promoted.** The stock OpenCode `build` agent was the cheapest configuration, and none of the three new benchmark arms beat it. Every arm passed every verification command, so this is a cost negative result rather than a correctness problem.

| Arm | Config | Agent | Total cost | Cost per verified task | Median wall |
|---|---|---|---|---|---|
| `baseline` | stock OpenCode | `build` | $0.0636 | $0.0071 | 39s |
| `optimized` | current ToolWright profile | `coordinator` | $0.0872 | $0.0097 | 72s |
| `coordinator-slim` | no MCP, 400-line output cap | `coordinator` | $0.0772 | $0.0086 | 59s |
| `direct-slim` | no MCP, 400-line output cap | `backend-developer` | $0.0765 | $0.0085 | 46s |
| `tools-on-demand` | full MCP, 400-line output cap | `coordinator` | $0.0919 | $0.0102 | 55s |

Relative to `baseline`, the arms cost **20.3% to 44.6% more**. Relative to the current `optimized` arm, `coordinator-slim` was 11.5% cheaper and `direct-slim` was 12.3% cheaper, but both remain about 20% more expensive than stock. `tools-on-demand` was 5.4% more expensive than `optimized`.

The pre-registered promotion bar was a cost reduction of at least **15% versus both `baseline` and `optimized`**. No arm met it. The decision is to keep production profiles, agents, and defaults unchanged and document the negative result.

> **Verdict:** on these three Hono tasks and this model, removing MCP and capping tool output did not reduce total cost. The coordinator hop and shell-based editing remained more expensive than the stock agent.

## Method

- Repository: [`honojs/hono`](https://github.com/honojs/hono) at commit `f6fbaf0299c48eea9e656e03e2ffe7ac755e8823`, installed with `pnpm install --frozen-lockfile`.
- Tasks: `hono-set-cookie`, `hono-redirect`, `hono-request-id`; prompts and verification commands are in [`benchmarks/real/hono/tasks/`](https://github.com/GabrielAlmeidaFlores/ToolWright/tree/main/benchmarks/real/hono/tasks).
- Model: `deepseek/deepseek-flash`; OpenCode `2.2.7` as the reference adapter.
- Repeats: 3 per task and arm; 5 arms; 45 runs total.
- Isolation: one disposable clone per run, temporary `XDG_CONFIG_HOME`, `opencode --standalone`, and process-group termination after each run so MCP servers cannot leak into the next run.
- Bounds: each run enforced the task's `max_wall_time_seconds`; no run timed out.
- Scoring: the verification command decides correctness, and the changed-file set is compared with the expected files for the task. Score 4 means verification passed with only expected files changed.

Each arm config is a copy of a production config with only `tool_output` changed. `coordinator-slim` and `direct-slim` share [`benchmarks/arms/slim.jsonc`](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/benchmarks/arms/slim.jsonc) and differ only in the agent the harness selects. See [benchmark arms](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/benchmarks/arms/README.md).

## Cost by task

Median cost per task over three repeats:

| Task | `baseline` | `optimized` | `coordinator-slim` | `direct-slim` | `tools-on-demand` |
|---|---|---|---|---|---|
| `hono-redirect` | $0.0051 | $0.0089 | $0.0086 | **$0.0045** | $0.0074 |
| `hono-request-id` | **$0.0036** | $0.0043 | $0.0040 | $0.0044 | $0.0049 |
| `hono-set-cookie` | **$0.0089** | $0.0164 | $0.0111 | $0.0185 | $0.0205 |

The result is not uniform. `direct-slim` was the cheapest arm on `hono-redirect`, and `coordinator-slim` was cheaper than `optimized` on all three tasks. But `hono-set-cookie`, the largest task, dominated the total: every ToolWright arm cost more than baseline there, and the two full-surface arms cost roughly twice as much.

## Tokens and tool use

Totals across nine runs per arm:

| Arm | Input | Output | Reasoning | Cache read | Tool calls |
|---|---|---|---|---|---|
| `baseline` | 196,786 | 22,066 | 22,194 | 2,502,528 | 153 |
| `optimized` | 201,434 | 29,535 | 44,930 | 4,116,096 | 176 |
| `coordinator-slim` | 170,004 | 32,191 | 37,532 | 3,280,768 | 201 |
| `direct-slim` | 182,578 | 27,634 | 35,599 | 3,718,400 | 196 |
| `tools-on-demand` | 203,406 | 33,434 | 45,329 | 4,719,616 | 194 |

Two tool patterns explain part of the gap:

- The coordinator arms have no `edit`/`write` permission and edit through `shell`, which requires more commands and more output. `direct-slim`, which may use `edit`, still spent more than `baseline` because it issued 116 shell commands against the baseline's 64.
- MCP tools were used only in the arms that load them: Serena `execute` was called 8 times in `optimized` and 9 times in `tools-on-demand`. CodeGraph, Repomix, and jCodeMunch were never called, so the full MCP surface added schema and startup weight without measured benefit on these tasks.

## Correctness and scope

- 45 of 45 runs passed their verification command.
- 45 of 45 runs scored 4: only the expected source and test files changed.
- No run timed out; the slowest run was 229s against a 900s limit.
- Cost ranges overlap heavily: `baseline` $0.0031–$0.0211, `optimized` $0.0033–$0.0227, `direct-slim` $0.0041–$0.0207. The three-repeat medians are not a significance test.

## Limitations

- Three tasks, one small part of one repository, one model.
- Three repeats per task; the spread is large enough that task-level wins should not be generalized.
- Correctness is the task's test command plus an automated changed-path check. There was no independent blind review, and rework was not exercised.
- Provider pricing changes over time; the numbers use DeepSeek Flash prices at run time.
- This is an OpenCode reference-adapter result. It does not measure Claude, Copilot, or Codex.
- Each run records `commit: 7e44ca6`, the repository HEAD while the arm and harness changes were still uncommitted. The arm configs and harness are published in the same change as this result set, so the exact revisions are recoverable from the repository.

## What would change the conclusion

1. **Remove the coordinator hop for small tasks.** `direct-slim` was competitive on wall time and on `hono-redirect`, but its shell usage and reasoning were still high. A benchmark variant that lets the implementer use `edit` without a coordinator is the next useful comparison.
2. **Fix editing through `shell`.** Coordinator arms spent 114–132 shell calls per nine runs and never called `edit`. Giving the coordinator a narrow edit permission, or routing edits to a specialist, is a prerequisite for cost parity.
3. **Run the five-task, five-repeat set.** The plan's Phase 5 matrix is the right size to decide production changes; this three-task run is a screen.
4. **Keep the MCP-off config available, not default.** The no-MCP variant was cheaper than the full MCP surface on these tasks, but still more expensive than stock. Do not promote it without a wider win.

## Artifacts

Each `r<repeat>-<arm>-<task>/` directory contains `meta.json`, `stats.json`, `run-stats.json`, `session.jsonl`, `export.json`, `verification.log`, `status.txt`, `diff.patch`, `diff-stat.txt`, and `notes.md`. The [aggregate summary](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/benchmarks/results/hono-cost-ab-2026-11-16/summary.json) contains the per-run table used for this page.

Related: [benchmark methodology](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/benchmarks/methodology.md), [real Hono fixtures](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/benchmarks/real-hono-fixtures.md), and the [cost and performance plan](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/plans/cost-performance-optimization.md).
