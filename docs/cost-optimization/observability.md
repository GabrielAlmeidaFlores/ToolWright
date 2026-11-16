# Observability and Cost Reporting

> **Status:** Stable · **Last verified:** 2026-11-16 · **Evidence:** `toolwright usage` tests and `make ci` pass locally

The harness stores raw artifacts under `benchmarks/results/<run-id>/`. The cost report aggregates those artifacts without calling a model.

## Ongoing project usage

Benchmark artifacts are not the only source of cost data. `toolwright usage` records ordinary sessions under `.toolwright/usage/<run-id>/` with the same `meta.json` and `session.jsonl` shape used by the benchmark harness. It can record a captured session or run a wrapper command and capture its JSON output, then report cost, tokens, verification, and rework by task, agent, and model.

The ledger is local, gitignored, and telemetry-free. Prune old entries with `toolwright usage prune --older-than-days <n> --apply --yes`. See the [CLI reference](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/cli/README.md).

## Generate a report

```bash
toolwright stats
toolwright stats --results /path/to/results
toolwright stats --format json
toolwright stats --format csv
toolwright stats --budget 5.00
```

The legacy wrapper still works:

```bash
python3 scripts/benchmarking/report_costs.py
```

`--budget` fails with exit code 1 when the total recorded cost exceeds the ceiling. It is a
post-run guard; it cannot stop a model that is already running.

The report reads:

- `meta.json` for arm, task, model, agent, working directory, wall time, and verification exit.
- `session.jsonl` for cost, input tokens, output tokens, reasoning tokens, cache tokens, steps, tool calls, and tool errors.

It also aggregates by agent, model, and tool, and compares baseline and optimized runs that
share a task. When a task has multiple runs per arm, the comparison averages cost and tokens
and reports the verification pass rate for each arm. A comparison is emitted only when both
arms exist. CSV output is generated with the standard `csv` module, so commas are quoted.

`session.jsonl` is the primary source because `opencode stats` can return zero for ephemeral projects.

## Example local smoke observation

The following numbers came from one task on a disposable TypeScript fixture. They are **not** a published benchmark result. It has 3 rows and 9 columns: Run, Arm, Cost, Input, Output, Steps, Tools, Wall, and Verify. Each row is one run, and the other columns record Arm, Cost, Input, Output, Steps, Tools, Wall, and Verify. Read it to compare rows or to find a specific run.

| Run | Arm | Cost | Input | Output | Steps | Tools | Wall | Verify |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline | build | $0.012315 | 24240 | 5283 | 15 | 27 | 70 s | 0 |
| baseline | build | $0.010319 | 24869 | 4895 | 14 | 28 | 59 s | 0 |
| optimized | coordinator | $0.005190 | 15815 | 2060 | 7 | 10 | 34 s | 0 |

The optimized run used fewer steps and fewer tools on this single task. This is a smoke observation, not evidence that the optimized profile is cheaper in general.

## Metrics

- cost per run
- input, output, reasoning, cache-read, and cache-write tokens
- model steps, tool calls, and tool errors
- wall time
- verification exit code
- baseline/optimized cost and token ratios

The report intentionally excludes correctness scoring and rework, so it must not be used as a standalone quality claim. See [benchmark methodology](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/benchmarks/methodology.md).

## Budget control

`toolwright stats --budget` reports an exceeded ceiling with exit code 1 after the artifacts exist. The
harness does not enforce a live budget. For paid runs, set a provider-side budget or stop after a
fixed number of runs. Do not add a paid budget service for this repository.
