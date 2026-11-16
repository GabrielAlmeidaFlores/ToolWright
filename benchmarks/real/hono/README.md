# Real Hono Benchmark Fixtures

These tasks run against [`honojs/hono`](https://github.com/honojs/hono) at commit `f6fbaf0299c48eea9e656e03e2ffe7ac755e8823`.

Task prompts and acceptance criteria are derived from the Hono pilot findings in [`docs/pilots/results/code-round-hono.md`](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/pilots/results/code-round-hono.md).

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

The fixture guide is [`docs/benchmarks/real-hono-fixtures.md`](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/benchmarks/real-hono-fixtures.md). Benchmark arm definitions are in [`benchmarks/arms/README.md`](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/benchmarks/arms/README.md).
