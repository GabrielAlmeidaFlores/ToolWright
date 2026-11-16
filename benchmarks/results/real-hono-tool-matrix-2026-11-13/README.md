# Real Hono Tool Matrix Result Set

Run date: 2026-11-13 to 2026-11-14.

- Repository: `honojs/hono`
- Commit: `f6fbaf0299c48eea9e656e03e2ffe7ac755e8823`
- Tool under test: OpenCode `2.2.7`
- Model: `deepseek/deepseek-flash`
- Matrix: 3 tasks × 3 arms × 3 repeats = 27 runs
- Probes: 9 capability runs
- Ralph: 1 isolated research run

Results:

- baseline: $0.078202, 9/9 score 4;
- optimized: $0.092539 (+18.3%), 9/9 score 4;
- full-forced: $0.140033 (+79.1%), 9/9 score 4.

Full analysis, task prompts, tool coverage, and limitations: [Real Hono Tool Matrix](../../../docs/benchmarks/real-hono-tool-matrix.md).

Each matrix run contains `meta.json`, `session.jsonl`, `run-stats.json`, `verification.log`, `status.txt`, and `diff.patch`. Probe runs contain their session and verification artifacts. Ralph artifacts contain the loop log, event stream, handoff, summary, and git log.

Limitations:

- OpenCode only; Claude, Copilot, and Codex were not measured.
- One model and one real repository.
- Slash-command expansion through `opencode run` is unverified.
- The coordinator has no `edit` or `write` tool in these runs; it edits through `shell`.
- Ralph ran a research workflow only, not a code-change workflow.
