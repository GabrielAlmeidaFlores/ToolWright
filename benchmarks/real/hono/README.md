# Real Hono Benchmark Fixtures

These tasks run against [`honojs/hono`](https://github.com/honojs/hono) at commit `f6fbaf0299c48eea9e656e03e2ffe7ac755e8823`.

Task prompts and acceptance criteria are derived from the Hono pilot findings in [`docs/pilots/results/code-round-hono.md`](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/pilots/results/code-round-hono.md). The JWT fixture tracks upstream commit `9995a384d90bc5aa42b70d7a761469e278ee5076` and describes the feature rather than copying its implementation.

Fixtures:

- `set-cookie.json` — bug fix that preserves cookies when `Context.res` is reassigned.
- `redirect.json` — security fix that encodes CR/LF in redirect locations.
- `request-id.json` — feature that adds `trustIncoming` to the request-id middleware.
- `jwt-typ.json` — multi-file feature that adds expected `typ` verification to the JWT utilities and middleware.
- `context-investigation.json` — read-only investigation of `Context.res` header merging that must not modify tracked source.

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
