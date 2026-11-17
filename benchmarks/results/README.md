# Benchmark Results

The first published result set is [`deepseek-flash-2026-11-13/`](https://github.com/GabrielAlmeidaFlores/ToolWright/tree/main/benchmarks/results/deepseek-flash-2026-11-13), summarized in the [DeepSeek Flash results](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/benchmarks/results-deepseek-flash.md).

The real-repository tool matrix is [`real-hono-tool-matrix-2026-11-13/`](https://github.com/GabrielAlmeidaFlores/ToolWright/tree/main/benchmarks/results/real-hono-tool-matrix-2026-11-13), summarized in the [Real Hono tool matrix](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/benchmarks/real-hono-tool-matrix.md).

The benchmark-arm A/B is [`hono-cost-ab-2026-11-16/`](https://github.com/GabrielAlmeidaFlores/ToolWright/tree/main/benchmarks/results/hono-cost-ab-2026-11-16), summarized in the [Hono cost A/B results](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/benchmarks/results-hono-cost-ab.md).

The five-repeat confirmation is [`hono-cost-ab-5-repeat-2026-11-16/`](https://github.com/GabrielAlmeidaFlores/ToolWright/tree/main/benchmarks/results/hono-cost-ab-5-repeat-2026-11-16), summarized in the [Hono delegation contract screen](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/benchmarks/results-hono-delegation-screen.md).

The scoped-router screen is [`hono-scoped-router-2026-11-17/`](https://github.com/GabrielAlmeidaFlores/ToolWright/tree/main/benchmarks/results/hono-scoped-router-2026-11-17). It is a negative result: the arm was cheaper in total only because two investigation runs failed, and it never delegated the multi-file task.

A result is accepted only if it includes:

- `meta.json` with commit, model ID and variant, arm, and task
- `stats.json` from `opencode stats --json --cost`
- `run-stats.json` derived from `session.jsonl` for per-run cost and tokens
- `session.jsonl` from `opencode run --format json`
- `verification.log` with the acceptance command output
- `status.txt`, `diff.patch`, and `diff-stat.txt` with the changed-file scope
- `notes.md` with correctness, rework, and human interventions

`stats.json` is a raw `opencode stats --project .` snapshot and may aggregate sessions that share a project identity. Use `run-stats.json` for per-run cost and token values. Verification logs and patches are kept byte-faithful: the repository `.gitattributes` disables whitespace-error checks for this tree.

Token counts without correctness and rework outcomes are not a result.

Run the harness:

```bash
OPENCODE_BENCH_MODEL=provider/model ./benchmarks/harness/run.sh --arm baseline  --task benchmarks/tasks/ts-validation.json
OPENCODE_BENCH_MODEL=provider/model ./benchmarks/harness/run.sh --arm optimized --task benchmarks/tasks/ts-validation.json
```
