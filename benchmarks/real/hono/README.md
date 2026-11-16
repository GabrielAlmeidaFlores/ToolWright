# Real Hono Benchmark Fixtures

These tasks run against `honojs/hono` at `f6fbaf0299c48eea9e656e03e2ffe7ac755e8823`.

Setup:

```bash
git clone --no-checkout --filter=blob:none https://github.com/honojs/hono /tmp/toolwright-hono
git -C /tmp/toolwright-hono fetch --depth 1 origin f6fbaf0299c48eea9e656e03e2ffe7ac755e8823
git -C /tmp/toolwright-hono checkout --detach FETCH_HEAD
cd /tmp/toolwright-hono
pnpm install --frozen-lockfile
```

Run with the benchmark harness:

```bash
OPENCODE_BENCH_MODEL=deepseek/deepseek-flash \
  ./benchmarks/harness/run.sh \
  --arm baseline \
  --task benchmarks/real/hono/tasks/set-cookie.json \
  --workspace /tmp/toolwright-hono
```

The harness accepts `--workspace`; do not install ToolWright into the Hono checkout for the baseline arm. Install the selected profile into the checkout before running an optimized arm.

Task prompts and acceptance criteria are derived from the Hono pilot findings in `docs/pilots/results/code-round-hono.md`. The published fixture guide is [`docs/benchmarks/real-hono-fixtures.md`](../../../docs/benchmarks/real-hono-fixtures.md).
