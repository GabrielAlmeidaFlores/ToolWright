# Hono Cost A/B Result Set

Run date: 2026-11-16.

- Model: `deepseek/deepseek-flash`
- AI tool under test: OpenCode `2.2.7` (reference adapter only; Claude, Copilot, and Codex were not measured)
- Repository under test: [`honojs/hono`](https://github.com/honojs/hono) at commit `f6fbaf0299c48eea9e656e03e2ffe7ac755e8823`
- Recorded repository commit: `7e44ca6` (the harness and arm changes were uncommitted during the runs and are published with this result set)
- Tasks: 3 (`hono-set-cookie`, `hono-redirect`, `hono-request-id`)
- Arms: `baseline`, `optimized`, `coordinator-slim`, `direct-slim`, `tools-on-demand`
- Repeats: 3
- Runs: 45

Aggregate result: the stock `baseline` arm was the cheapest at $0.0636 total and $0.0071 per verified task. The three new arms cost 20.3% to 44.6% more than baseline; `coordinator-slim` and `direct-slim` were 11.5% and 12.3% cheaper than the current `optimized` arm but still about 20% above baseline. All 45 verification commands passed and all 45 runs changed only expected files. No arm met the pre-registered 15% promotion bar, so nothing was promoted.

Full analysis, per-task medians, correctness, and limitations: [Hono cost A/B results](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/benchmarks/results-hono-cost-ab.md).

Each `r<repeat>-<arm>-<task>/` directory contains `meta.json`, `stats.json`, `run-stats.json`, `session.jsonl`, `export.json`, `verification.log`, `status.txt`, `diff.patch`, `diff-stat.txt`, and `notes.md`. The [aggregate summary](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/benchmarks/results/hono-cost-ab-2026-11-16/summary.json) contains the per-run table used for the published page.
