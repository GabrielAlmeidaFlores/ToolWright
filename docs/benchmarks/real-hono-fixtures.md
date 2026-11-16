# Real Hono Benchmark Fixtures

> **Status:** Experimental · **Last verified:** 2026-11-16 · **Evidence:** fixtures exercised by one baseline smoke run and a dry-run harness check; full A/B pending

These fixtures run against [`honojs/hono`](https://github.com/honojs/hono) at commit `f6fbaf0299c48eea9e656e03e2ffe7ac755e8823`. They are the first real-repository tasks for the cost/performance plan.

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

The next table lists the fixtures. **Task** is the fixture id; **What it tests** is the behavior under change; **Verification** is the command that decides whether the run passed.

| Task | What it tests | Verification |
|---|---|---|
| `hono-set-cookie` | Preserve cookies from both middleware and a handler when `Context.res` is reassigned | `pnpm exec vp test --run src/context.test.ts` |
| `hono-redirect` | Encode CR/LF in `c.redirect` locations without changing valid redirects | `pnpm exec vp test --run src/context.test.ts` |
| `hono-request-id` | Add `trustIncoming` while preserving default request-id behavior | `pnpm exec vp test --run src/middleware/request-id/index.test.ts` |

Run a task with:

```bash
OPENCODE_BENCH_MODEL=deepseek/deepseek-flash \
  ./benchmarks/harness/run.sh \
  --arm baseline \
  --task benchmarks/real/hono/tasks/set-cookie.json \
  --workspace /tmp/toolwright-hono
```

For an optimized arm, install the selected ToolWright profile into `/tmp/toolwright-hono` first. The harness reads the workspace config at `.opencode/opencode.jsonc` and checks for `.opencode/agents/coordinator.md`.

## Related

- [Cost and performance plan](../plans/cost-performance-optimization.md)
- [Benchmark methodology](methodology.md)
