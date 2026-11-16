# Hono Delegation Contract Screen

Run date: 2026-11-16.

- Model: `deepseek/deepseek-flash`
- Runtime: OpenCode `2.2.7`
- Repository: `honojs/hono` at commit `f6fbaf0299c48eea9e656e03e2ffe7ac755e8823`
- Tasks: `hono-set-cookie`, `hono-redirect`, `hono-request-id`
- Arms: `baseline`, `optimized`, `coordinator-slim`, `direct-slim`, `tools-on-demand`, `slim-uncapped`
- Repeats: 5
- Runs: 90
- Recorded repository commit: `caf4089` plus the uncommitted delegation contract that was evaluated and later reverted

Aggregate result: the stock baseline was cheapest at $0.1173 total and $0.0078 per verified task. The experimental `optimized` arm cost 31.0% more and took 2.8× as long; `coordinator-slim` came closest at +1.8% but was still 2.6× slower. All 90 runs verified and all 90 stayed within expected files. No arm was promoted, and the delegation contract was reverted.

The published artifacts describe the experimental prompt set, not the current production prompts. Full analysis, per-task medians, variance, and limitations: [Hono delegation contract screen](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/benchmarks/results-hono-delegation-screen.md).

Each `r<repeat>-<arm>-<task>/` directory contains `meta.json`, `stats.json`, `run-stats.json`, `session.jsonl`, `export.json`, `verification.log`, `status.txt`, `diff.patch`, `diff-stat.txt`, and `notes.md`. The [aggregate summary](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/benchmarks/results/hono-cost-ab-5-repeat-2026-11-16/summary.json) contains the per-run table used for the result page. Machine-specific paths are replaced with placeholders.
