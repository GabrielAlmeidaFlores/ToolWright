# Benchmark Methodology

The full methodology is maintained at [docs/benchmarks/methodology.md](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/benchmarks/methodology.md).

This directory holds the executable side:

- `../tasks/` — task definitions (JSON, no parser dependency)
- `../harness/` — runner
- `../baseline/` — stock configuration arm
- `../results/` — contributed results

The first result set is published in the [DeepSeek Flash results](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/benchmarks/results-deepseek-flash.md). A valid result requires correctness and rework data, not only token counts.
