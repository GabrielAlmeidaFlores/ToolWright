# Hono Delegation Contract Screen

> **Status:** Experimental · **Last verified:** 2026-11-16 · **Evidence:** 90 isolated harness runs on `deepseek/deepseek-flash`; artifacts under [`benchmarks/results/hono-cost-ab-5-repeat-2026-11-16/`](https://github.com/GabrielAlmeidaFlores/ToolWright/tree/main/benchmarks/results/hono-cost-ab-5-repeat-2026-11-16)

This page reports the five-repeat confirmation of the delegation and edit-tool contract that was evaluated after the first Hono cost A/B. The contract was **reverted** after this screen because it fixed delegation but increased cost and wall time. The published runs therefore describe an experimental prompt set, not the current production prompts.

## What this screen tested

The experiment asked whether forcing the coordinator to delegate every file-changing task, and requiring writers to use the `edit` tool instead of shell patching, would reduce cost per verified task. It kept the same three Hono tasks, the same model, and the same verification commands as the earlier A/B, but increased the sample from three to five repeats and added the `slim-uncapped` arm to complete the MCP × output-cap matrix.

The table below lists the six arms and what each was meant to isolate. Read the config and agent columns together: the prompt contract was shared by the coordinator arms, while the baseline stayed untouched. The table is the experimental design, so it should be read before comparing any result row.

| Arm | Config | Agent | Purpose |
|---|---|---|---|
| `baseline` | Stock OpenCode | `build` | Control |
| `optimized` | Current profile plus the experimental contract | `coordinator` | Delegation and edit-tool contract |
| `coordinator-slim` | No MCP, 400-line cap | `coordinator` | Contract without MCP overhead |
| `direct-slim` | No MCP, 400-line cap | `backend-developer` | Direct implementer, no coordinator hop |
| `tools-on-demand` | Full MCP, 400-line cap | `coordinator` | Contract with MCP available |
| `slim-uncapped` | No MCP, default 2,000-line cap | `coordinator` | Contract with the default cap |

## Results

The table below is the headline comparison across 90 runs. Total cost is the sum of fifteen runs per arm; cost per verified task divides by fifteen because every run passed; median wall time is the middle of the fifteen wall times. Read the cost and wall columns together, because a cheaper arm that is much slower is not a practical win.

| Arm | Total cost | Cost per verified task | vs baseline | Median wall |
|---|---|---|---|---|
| `baseline` | **$0.1173** | **$0.0078** | — | **36s** |
| `optimized` | $0.1536 | $0.0102 | +31.0% | 101s |
| `coordinator-slim` | $0.1194 | $0.0080 | +1.8% | 94s |
| `direct-slim` | $0.1337 | $0.0089 | +14.0% | 37s |
| `tools-on-demand` | $0.1504 | $0.0100 | +28.3% | 98s |
| `slim-uncapped` | $0.1537 | $0.0102 | +31.0% | 83s |

The result is negative. The stock agent remains the cheapest configuration, `coordinator-slim` is only 1.8% above it but almost three times slower, and `optimized` is 31% more expensive with a 2.8× wall-time regression. No arm met the promotion rule.

The table below gives the per-task median cost, which is where the aggregate comes from. Read across a row to compare arms on the same task; the largest task, `hono-set-cookie`, dominates the total. A single task win is not enough to offset losses on the other two tasks.

| Task | `baseline` | `optimized` | `coordinator-slim` | `direct-slim` | `tools-on-demand` | `slim-uncapped` |
|---|---|---|---|---|---|---|
| `hono-redirect` | $0.0045 | $0.0083 | $0.0058 | **$0.0043** | $0.0066 | $0.0054 |
| `hono-request-id` | **$0.0034** | $0.0039 | $0.0048 | $0.0045 | $0.0048 | $0.0035 |
| `hono-set-cookie` | $0.0145 | $0.0145 | **$0.0129** | $0.0145 | $0.0180 | $0.0193 |

`coordinator-slim` won `hono-set-cookie` and nearly tied baseline overall, but it lost the two smaller tasks and paid a large wall-time penalty. `direct-slim` matched baseline wall time but cost 14% more.

The table below shows the per-repeat totals that exposed the variance hidden by three repeats. A single cheap or expensive repeat can move the aggregate enough to change the ranking. The table is the evidence for why the earlier three-repeat result was not stable.

| Repeat | `baseline` | `optimized` | `coordinator-slim` | `direct-slim` | `tools-on-demand` | `slim-uncapped` |
|---|---|---|---|---|---|---|
| 1 | $0.0254 | $0.0199 | $0.0211 | $0.0223 | $0.0215 | $0.0546 |
| 2 | $0.0238 | $0.0269 | $0.0304 | $0.0326 | $0.0223 | $0.0363 |
| 3 | $0.0283 | $0.0209 | $0.0285 | $0.0230 | $0.0277 | $0.0107 |
| 4 | $0.0132 | $0.0464 | $0.0198 | $0.0349 | $0.0505 | $0.0226 |
| 5 | $0.0266 | $0.0395 | $0.0195 | $0.0209 | $0.0284 | $0.0295 |

The earlier three-repeat screen reported a 12.5% saving for `optimized`; repeats 4–5 reversed it. This is why the promotion decision uses five repeats and why the screen is published as a negative result rather than a success.

## Correctness and delegation

All 90 runs passed verification and all 90 changed only expected files. There was no correctness difference between stock and any ToolWright arm.

Delegation did occur under the experimental contract: coordinator arms made 19–26 subagent calls across their runs. That fixed the structural defect observed in the first A/B, where the coordinator made zero subagent calls and edited through shell. It did not reduce total cost on these small tasks.

## Decision

The delegation and writer edit-tool contract was **reverted**. Production prompts, profiles, and defaults remain unchanged.

Reasons:

- cost rose about 31% for `optimized` and did not fall for any arm;
- wall time rose about 2.8× for `optimized`;
- the best arm, `coordinator-slim`, only reached +1.8% cost and remained 2.6× slower;
- the original three-repeat win was variance.

The next useful experiment is a **scoped** delegation variant for multi-file or ambiguous work, tested on the five-task matrix. Full delegation on small tasks is not worth its overhead.

## Limitations

- Three small tasks, one repository, one model, one adapter.
- Five repeats per cell; medians are descriptive, not a significance test.
- No blind review and no exercised rework.
- The published runs used the experimental prompt set; current production prompts differ.
- Cost and wall time depend on provider load and pricing at run time.
- Local workspace, repository, and temporary paths in the artifacts are replaced with placeholders.

## Artifacts

Each `r<repeat>-<arm>-<task>/` directory contains `meta.json`, `stats.json`, `run-stats.json`, `session.jsonl`, `export.json`, `verification.log`, `status.txt`, `diff.patch`, `diff-stat.txt`, and `notes.md`. The [aggregate summary](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/benchmarks/results/hono-cost-ab-5-repeat-2026-11-16/summary.json) has one row per run with cost, tokens, cache hit ratio, wall time, scope, and subagent counts.

Related: [Hono cost A/B results](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/benchmarks/results-hono-cost-ab.md), [benchmark methodology](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/benchmarks/methodology.md), [benchmark arms](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/benchmarks/arms/README.md), and the [cost and performance plan](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/plans/cost-performance-optimization.md).
