# Cost-Reduction Tool Candidates

> **Status:** Experimental · **Last verified:** 2026-11-16 · **Evidence:** assessed against the published benchmark results and repository constraints; none of the candidates has been independently benchmarked here

This page records the outside tools that were evaluated for reducing model and agent cost, the verdict for each, and the experiments that would be required before adoption. It exists so the discussion can resume without redoing the research.

## Why this list exists

The repository already measures cost per verified outcome, not raw token count. The published Hono A/B and the earlier result sets show that input tokens are heavily cached, while the measured cost is driven by reasoning and output tokens, shell-based editing, and delegation behaviour. A candidate that only shrinks prompts or cached input is therefore less interesting than one that reduces output, tool noise, or wasted steps without lowering correctness.

The current benchmark evidence is in [Hono cost A/B results](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/benchmarks/results-hono-cost-ab.md), [DeepSeek Flash results](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/benchmarks/results-deepseek-flash.md), and the [benchmark methodology](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/benchmarks/methodology.md). The cost plan is [cost and performance optimization](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/plans/cost-performance-optimization.md).

## Verdict summary

The table below lists every candidate, the layer it operates on, and the current verdict. Read “vendor claim” as a number published by the tool's authors that this repository has not reproduced; read “watchlist” as “study the pattern, do not install it”. The table is a decision aid, not an endorsement: no candidate has been installed or benchmarked here yet.

| Candidate | Layer | Verdict | Evidence status |
|---|---|---|---|
| rtk (Rust Token Killer) | Deterministic shell/test output filtering | Best first experiment | Vendor claim; no local test |
| openslimedit | OpenCode plugin: schemas, reads, line-range edits | Second experiment; high upside and risk | Vendor claim; compatibility unverified |
| caveman skill-only | Output and narration conciseness | Optional guarded experiment | Vendor claim; quality risk |
| context-mode | Local output sandbox and query handles | Defer until output caps are measured | No local test |
| LiteLLM | Gateway, budgets, fallback | Optional deployment integration only | Documented; not benchmarked here |
| RouteLLM | Prompt-complexity model routing | Experiment internally, do not adopt yet | Research/vendor claim |
| LLMLingua | Prompt and KV-cache compression | No | Documented; poor fit for code |
| GPTCache | Semantic response cache | No for code changes | Documented; correctness risk |
| CartoGopher | AST dependency/call graph | No; overlaps existing tools | No local test |
| vLLM | Self-hosted inference | No unless self-hosting becomes strategy | Documented; infrastructure cost |
| TokenEconomizer | Experimental turn control and loop breaking | Watchlist only | Brand new; unverified |

## Deterministic output tools

These tools remove noise without asking a model to make a decision, which fits the repository principle that deterministic tools should handle deterministic work.

### rtk (Rust Token Killer)

rtk is a single-binary CLI proxy that strips ANSI codes, progress output, and passing-test noise before command output enters the agent context. The idea fits because noisy test and lint output can trigger repeated reasoning and unnecessary retries.

The expected saving is uncertain. The harness already caps tool output at 400 lines in the slim arms, and the benchmark tasks run one targeted test file rather than a full noisy suite. The published data does not show output flooding as the dominant cost; reasoning and editing are larger levers.

**Verdict:** run it as an optional benchmark arm before considering installation.

### context-mode

context-mode keeps large command output and fetched documents outside the active conversation, indexing them locally and returning compact handles. That is directionally similar to the existing tool-output cap and compaction settings.

The risk is added infrastructure: a local index, a retrieval path, and new calls to drill into results. It also overlaps with the cap experiment that has not yet been run in isolation.

**Verdict:** defer until the 2×2 output-cap experiment shows that large outputs are still a measured problem.

## Edit and schema tools

These tools change how the agent reads and edits files. They can reduce output tokens directly, but they also change behaviour that verification must catch.

### openslimedit

openslimedit is an OpenCode plugin that shrinks tool schemas, trims boilerplate from file reads, and supports line-range edit expansion. The last point is interesting because edit calls can echo large `oldString` blocks, and output tokens are expensive.

The risks are compatibility and correctness. It changes tool schemas and edit semantics, must be verified against OpenCode 2.2.7, and the claimed 22–45% token reduction is a vendor claim. A bad edit is more expensive than a verbose one because it triggers rework.

**Verdict:** second experiment, with strict verification and scope checks.

## Output-behaviour skills

A Markdown-only skill is cheap to test because it adds no runtime dependency. It is also easy to misuse.

### caveman skill-only

caveman suppresses preamble, step narration, and post-edit explanation while keeping code and commands. The appeal is direct: output tokens are billed, and narrated plans compound into later turns.

The repository requires agents to report commands run, evidence, and residual risks. A blanket “say less” skill would remove exactly the information a reviewer needs. A guarded variant should suppress narration but keep verification evidence.

**Verdict:** optional experiment with an explicit output contract.

## Models, gateways, and routing

These tools operate below the agent and can change cost, latency, privacy, and failure behaviour.

### LiteLLM

LiteLLM provides an OpenAI-compatible gateway with provider fallback, budgets, and cache pass-through. It is a reasonable **optional deployment integration** for an organisation that needs centralized spend control or multiple providers.

It is not a default dependency for this repository. A gateway adds a proxy, credentials, routing configuration, and a new failure point, and it changes latency and caching behaviour, so any benchmark through it must be re-run.

### RouteLLM

RouteLLM routes prompts by complexity to cheap or strong models. The idea overlaps with the static per-agent routing that already exists in [`configs/opencode/model-routing.example.jsonc`](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/configs/opencode/model-routing.example.jsonc), which maps planning, implementation, review, and documentation to configurable model variables.

A dynamic router adds a classification step and a new dependency. Prompt complexity is not the same as task difficulty, and the router has no correctness signal. The better next step is static routing plus escalation on failed verification.

**Verdict:** experiment internally only after static routing is measured.

### LLMLingua

LLMLingua compresses prompts by removing low-information tokens using a small language model. For code, that can remove identifiers, paths, error text, and test evidence that matter. It also adds another model inference step.

The measured input is already about 92% cached. Compressing cached input is optimizing the cheaper side of the bill.

**Verdict:** no.

### GPTCache

GPTCache returns previously answered prompts by semantic similarity. For a coding agent, similar prompts can require different changes because the repository state changed, the branch differs, or the prior answer was wrong.

A semantic cache bypasses verification and can hide regressions. It might fit a documentation Q&A bot with explicit scope and invalidation, not a code-change workflow.

**Verdict:** no for code changes.

### vLLM

vLLM is a high-performance inference engine for self-hosted open-weight models. It is useful only if the organisation owns GPU capacity and deliberately chooses self-hosting.

It moves cost from API bills to infrastructure and operations and weakens the provider-neutral portability this repository is built around. It should be a deployment backend, not a default integration.

**Verdict:** no unless self-hosting becomes a strategic requirement.

## Code navigation

The repository already supports LSP, ripgrep, ast-grep, Serena, CodeGraph, Repomix, and jCodeMunch. The measured runs used Serena sparingly and did not call CodeGraph, Repomix, or jCodeMunch in the A/B.

### CartoGopher

CartoGopher builds an incremental AST dependency and call graph through a Go CLI and MCP. It is deterministic and avoids embeddings, which is attractive in principle.

It also overlaps with the existing graph and symbol tools. Adding it before proving the current tools insufficient would contradict the repository rule against installing overlapping tools.

**Verdict:** no.

## Watchlist

### TokenEconomizer

TokenEconomizer is a new black-box plugin with experimental OpenCode support. Its ideas — turn-based output tiers, tool-result deduplication, KV-cache-safe prompt slots, unused tool pruning, and deterministic loop breaking — are worth studying.

It is too new to be a core dependency, and a loop breaker can hide a retry that is actually needed. The pattern is more valuable than the package right now.

**Verdict:** watchlist only.

## Experiment order

If these candidates are revisited, test one change at a time against the current optimized arm and the stock baseline:

1. **rtk** as an output filter, with raw output preserved for audit.
2. **openslimedit** as a schema/edit plugin, with strict verification.
3. A **guarded output-contract skill**, not blanket silence.
4. **Static per-agent model routing**, using the existing overlay.
5. **LiteLLM** only if budgets or multi-provider fallback become requirements.

Each experiment needs at least five repeats, correctness and scope scoring, wall time, rework, and cost per verified task. A candidate is not adopted because it reduces tokens; it is adopted only if it reduces cost per verified task without a correctness or wall-time regression.

## Adoption gates

Before any candidate becomes a dependency:

- record upstream provenance, license, version, and maintenance status;
- confirm compatibility with OpenCode 2.2.7;
- add an optional benchmark arm, not a default install;
- publish the result with correctness, rework, and limitations;
- obtain explicit human approval;
- keep a rollback path.

## References

- [Hono cost A/B results](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/benchmarks/results-hono-cost-ab.md)
- [DeepSeek Flash results](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/benchmarks/results-deepseek-flash.md)
- [Benchmark methodology](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/benchmarks/methodology.md)
- [Cost and performance optimization plan](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/plans/cost-performance-optimization.md)
- [OpenCode configuration](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/configuration/opencode-v2.md)
- [rtk](https://github.com/rtk-ai/rtk)
- [openslimedit](https://github.com/ASidorenkoCode/openslimedit)
- [context-mode](https://github.com/mksglu/context-mode)
- [caveman](https://github.com/JuliusBrussee/caveman)
- [CartoGopher](https://www.cartogopher.com/)
- [LiteLLM](https://github.com/BerriAI/litellm)
- [RouteLLM](https://github.com/lm-sys/RouteLLM)
- [LLMLingua](https://github.com/microsoft/LLMLingua)
- [GPTCache](https://github.com/zilliztech/GPTCache)
- [vLLM](https://github.com/vllm-project/vllm)
- [TokenEconomizer](https://github.com/microsoft/TokenEconomizer)
