# Real Hono Benchmark Fixtures

> **Status:** Experimental · **Last verified:** 2026-11-16 · **Evidence:** 45-run A/B completed on three of these five fixtures and both new fixtures pass harness `--dry-run`; [results](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/benchmarks/results-hono-cost-ab.md)

These fixtures run against [`honojs/hono`](https://github.com/honojs/hono) at commit `f6fbaf0299c48eea9e656e03e2ffe7ac755e8823`. They are the real-repository tasks for the cost/performance plan and cover bug fixing, security, feature work, multi-file feature work, and read-only investigation.

## Setup

```bash
git clone --no-checkout --filter=blob:none https://github.com/honojs/hono /tmp/toolwright-hono
git -C /tmp/toolwright-hono fetch --depth 1 origin f6fbaf0299c48eea9e656e03e2ffe7ac755e8823
git -C /tmp/toolwright-hono checkout --detach FETCH_HEAD
cd /tmp/toolwright-hono
pnpm install --frozen-lockfile
```

The task files are under `benchmarks/real/hono/tasks/`. Each task has `working_directory: "."`, so the harness must receive `--workspace /tmp/toolwright-hono`.

## Tasks

The table below lists the Hono fixtures used by the real-repository benchmarks. Task is the fixture identifier used in run directories and result tables, What it tests describes the behavior or artifact the agent must produce, and Verification is the command that decides whether the result is correct. All five fixtures run against the same pinned Hono commit, and four use the repository own test suite. Read the verification column before comparing results, because it defines what passed means for each task.

| Task | What it tests | Verification |
|---|---|---|
| `hono-set-cookie` | Preserve cookies from both middleware and a handler when `Context.res` is reassigned | `pnpm exec vp test --run src/context.test.ts` |
| `hono-redirect` | Encode CR/LF in `c.redirect` locations without changing valid redirects | `pnpm exec vp test --run src/context.test.ts` |
| `hono-request-id` | Add `trustIncoming` while preserving default request-id behavior | `pnpm exec vp test --run src/middleware/request-id/index.test.ts` |
| `hono-jwt-typ` | Add expected `typ` verification to the JWT utilities and middleware, including `verifyWithJwks` | JWT utility and middleware suites plus checks for the new `at+jwt` tests |
| `hono-context-investigation` | Investigate `Context.res` header merging and write `INVESTIGATION.md` without modifying tracked source | File, citation, and clean-source checks |

Run a task with:

```bash
OPENCODE_BENCH_MODEL=deepseek/deepseek-flash \
  ./benchmarks/harness/run.sh \
  --arm baseline \
  --task benchmarks/real/hono/tasks/set-cookie.json \
  --workspace /tmp/toolwright-hono
```

For most ToolWright arms (`optimized`, `coordinator-slim`, `direct-slim`, `tools-on-demand`, `slim-uncapped`), install the selected profile into `/tmp/toolwright-hono` first. The harness reads the workspace config at `.opencode/opencode.jsonc` for `optimized` and checks for `.opencode/agents/<agent>.md` for those arms. `scoped-router` is the exception: the harness copies its benchmark-only agent from `benchmarks/agents/` into the workspace, so no installed profile is required. Because the harness overwrites `<workspace>/.opencode/opencode.jsonc` with the selected arm config, use a separate clean checkout for `baseline` and reinstall the profile before switching back to `optimized`.

## Benchmark arms

The benchmark-only arm definitions are in [benchmark arms](https://github.com/GabrielAlmeidaFlores/ToolWright/tree/main/benchmarks/arms). They do not change production defaults. `coordinator-slim` and `direct-slim` share a config derived from `configs/opencode/minimal.jsonc` that declares no MCP servers and caps tool output at 400 lines; they differ in the agent the harness selects. `tools-on-demand` keeps the full MCP surface. `scoped-router` is a benchmark-only coordinator variant that edits a single known file directly and delegates multi-file or ambiguous work; the harness copies its agent file from `benchmarks/agents/` so no installed profile is required. The harness copies the arm config into the disposable workspace before it runs, so the same checkout can be reused between arms.

```bash
OPENCODE_BENCH_MODEL=deepseek/deepseek-flash \
  ./benchmarks/harness/run.sh \
  --arm coordinator-slim \
  --task benchmarks/real/hono/tasks/set-cookie.json \
  --workspace /tmp/toolwright-hono
```

## Related

- [Hono cost A/B results](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/benchmarks/results-hono-cost-ab.md)
- [Hono delegation screen](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/benchmarks/results-hono-delegation-screen.md)
- [Cost and performance plan](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/plans/cost-performance-optimization.md)
- [Benchmark methodology](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/benchmarks/methodology.md)
