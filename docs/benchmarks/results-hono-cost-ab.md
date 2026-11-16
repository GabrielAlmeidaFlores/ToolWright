# Hono Cost A/B Results

> **Status:** Experimental · **Last verified:** 2026-11-16 · **Evidence:** 45 isolated harness runs on `deepseek/deepseek-flash`; artifacts under [`benchmarks/results/hono-cost-ab-2026-11-16/`](https://github.com/GabrielAlmeidaFlores/ToolWright/tree/main/benchmarks/results/hono-cost-ab-2026-11-16)

## What this page answers

ToolWright exists to make AI-assisted development cheaper **without making it worse**. That claim needs a measurement, not intuition. This page reports one such measurement.

> When several ToolWright configurations and the stock OpenCode configuration attempt the same real repository tasks, with the same model and the same verification, which one completes them correctly for the lowest total cost?

The experiment is an A/B test:

- **A** is the comparison point. It is the stock OpenCode `build` agent with no ToolWright instructions, tools, or MCP servers.
- **B** is a set of ToolWright configurations, each changing one dimension: orchestration, MCP surface, or tool-output limits.
- Every arm receives the same prompt, the same checkout, and the same verification command.
- Each combination of arm and task runs three times so one lucky or unlucky run does not decide the result.

This page covers one model (`deepseek/deepseek-flash`), one AI tool (OpenCode `2.2.7`), one repository ([`honojs/hono`](https://github.com/honojs/hono)), and three tasks. It is a **screen**, not a final verdict on every repository or every AI tool. The result is negative, and negative results are published here on purpose.

## Result at a glance

The table below is the headline comparison. Each row is one arm: what it is (configuration and agent), what it cost across nine runs, what it cost per verified task, and how long a typical run took. Read total cost as the batch price, cost per verified task as the comparable unit, and median wall time as the typical latency; bold values mark the best result in each column. The table is the fastest way to see the main finding: the stock agent is the cheapest row.

| Arm | Configuration | Agent | Total cost | Cost per verified task | Median wall time |
|---|---|---|---|---|---|
| `baseline` | stock OpenCode | `build` | **$0.0663** | **$0.0074** | **39s** |
| `optimized` | current ToolWright profile | `coordinator` | $0.0872 | $0.0097 | 72s |
| `coordinator-slim` | no MCP, 400-line output cap | `coordinator` | $0.0772 | $0.0086 | 59s |
| `direct-slim` | no MCP, 400-line output cap | `backend-developer` | $0.0833 | $0.0093 | 46s |
| `tools-on-demand` | full MCP, 400-line output cap | `coordinator` | $0.0783 | $0.0087 | 55s |

Read the table this way:

- **Total cost** is the sum of the nine runs for that arm (three tasks × three repeats). It answers "what would this arm cost for this batch of work?"
- **Cost per verified task** divides that total by the number of runs that passed verification. All 45 runs passed, so it is the mean cost of a passing run.
- **Median wall time** is the middle value of the nine wall times. It answers "how long does a typical run take?" and is less sensitive to one slow outlier than a mean.

The comparison table below restates the main differences against the stock baseline. Each row is an arm, and the columns give its total cost change and, for the current profile, its median wall-time change. Positive percentages mean the arm spent more than baseline; a negative value would mean a saving. Read it as a quick sanity check before the detailed tables, not as a substitute for the per-task evidence.

| Comparison | Result |
|---|---|
| `optimized` vs `baseline` | +31.6% cost, +85% median wall time |
| `coordinator-slim` vs `baseline` | +16.4% cost |
| `direct-slim` vs `baseline` | +25.7% cost |
| `tools-on-demand` vs `baseline` | +18.2% cost |

Against the current `optimized` arm, every new arm was cheaper: `coordinator-slim` by 11.5%, `tools-on-demand` by 10.2%, and `direct-slim` by 4.5%. That is real but not enough: all three remain 16–26% more expensive than stock.

The decision rule applied in this evaluation was: an arm had to be at least **15% cheaper than both `baseline` and `optimized`**, with equal correctness and no wall-time regression. The 15% threshold comes from the [plan](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/plans/cost-performance-optimization.md); the baseline condition keeps a cheaper-than-ToolWright configuration from being labeled a win. No arm met it. The decision is to keep production profiles, agents, and defaults unchanged.

> **Verdict:** on these three Hono tasks and this model, reducing the MCP surface and capping tool output lowered cost relative to the current ToolWright profile, but not enough to beat the stock agent. The coordinator path stayed more expensive than stock because it edited through `shell` and never delegated to a specialist.

## The experiment in detail

### The hypothesis

The starting hypothesis came from the [cost and performance plan](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/plans/cost-performance-optimization.md): a meaningful share of cost comes from (a) MCP server startup and tool schemas, (b) large tool outputs flooding the context, and (c) an orchestration hop that adds tokens before any code is written. If that were true, an arm without MCP, with a smaller output cap, and with a direct implementer should be cheaper than the current coordinated profile.

The experiment tests that hypothesis directly, one variable per arm.

### What each arm is

All arms share the same checkout, model, prompts, verification commands, and repeat count; only the differences listed below change. The table makes the experimental design auditable: it names the config file and agent for each arm, states whether MCP servers are loaded and what tool-output cap applies, and explains which hypothesis the arm tests. If a result surprises you, this table shows which variable could have caused it.

| Arm | Configuration file | Agent | MCP servers | Tool output cap | What it tests |
|---|---|---|---|---|---|
| `baseline` | stock OpenCode | `build` | none | OpenCode default | The control: no ToolWright layer |
| `optimized` | workspace `.opencode/opencode.jsonc` | `coordinator` | full surface | production setting | The current ToolWright profile |
| `coordinator-slim` | [`slim.jsonc`](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/benchmarks/arms/slim.jsonc) | `coordinator` | none | 400 lines / 16 KB | Removing MCP and shrinking outputs while keeping orchestration |
| `direct-slim` | [`slim.jsonc`](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/benchmarks/arms/slim.jsonc) | `backend-developer` | none | 400 lines / 16 KB | Removing MCP and the coordinator hop |
| `tools-on-demand` | [`tools-on-demand.jsonc`](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/benchmarks/arms/tools-on-demand.jsonc) | `coordinator` | full surface | 400 lines / 16 KB | Keeping MCP available but shrinking outputs |

The arm configs are **benchmark-only**. They are copies of production configs with exactly one key changed, `tool_output`; `tests/unit/test_benchmark_arms.py` fails if they drift from their source for any other key. `coordinator-slim` and `direct-slim` deliberately share one config and differ only in the agent the harness selects. Step budgets are **not** changed: a config-level `agents` entry does not override an agent defined by a Markdown file, so the arms do not pretend to change it.

`direct-slim` uses `backend-developer`, which has `edit` permission. The coordinator does not: [`agents/coordinator/AGENT.md`](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/agents/coordinator/AGENT.md) denies `edit` for `*`, so the coordinator path writes files through `shell`.

### What was held constant

- One checkout at commit `f6fbaf0299c48eea9e656e03e2ffe7ac755e8823`, with dependencies installed once per template and copied per run.
- One model and one provider price list.
- The same prompt text, working directory, and verification command per task.
- Three repeats per task and arm.
- An isolated `XDG_CONFIG_HOME`, `opencode --standalone`, one disposable clone per run, and process-group termination after each run. The last point matters: without it, an MCP server started by one arm can keep running and consume resources during the next arm. Three cells reviewed after the first pass were re-run in workspaces whose parent contained no harness files; see Limitations.
- A wall-clock limit from the task definition. No run hit it.

## The tasks

Each task is a real change to Hono with a failing behavior, a requested fix, and a test command that decides success. The table lists the three tasks, summarizes what the agent had to do, and gives the exact verification command used to score it. The full prompts and acceptance criteria live in the task files linked below; the table is the short map from task name to expected behavior.

| Task | What the agent had to do | Verification command |
|---|---|---|
| `hono-set-cookie` | Fix the `Context.res` setter so cookies from middleware and from a handler both survive when the response is reassigned; add a regression test | `pnpm exec vp test --run src/context.test.ts` |
| `hono-redirect` | Percent-encode CR and LF in `c.redirect` locations without breaking valid redirects; add regression tests | `pnpm exec vp test --run src/context.test.ts` |
| `hono-request-id` | Add a `trustIncoming` option that defaults to `true`; when `false`, ignore incoming request IDs and always use the generator; add tests for both modes | `pnpm exec vp test --run src/middleware/request-id/index.test.ts` |

The full prompts and acceptance criteria are in [`benchmarks/real/hono/tasks/`](https://github.com/GabrielAlmeidaFlores/ToolWright/tree/main/benchmarks/real/hono/tasks). `hono-set-cookie` is the largest task and, as shown below, dominates the cost result.

## Metrics

The table below defines every measurement used on this page, so later numbers can be read without guessing. Each row gives the metric, how it is calculated, and the artifact that holds the underlying value. Two definitions matter most: a run is verified when the task test command exits 0, and cost per verified task divides an arm total by its number of passing runs. Cost and tokens are recomputed from the session log rather than taken from a cumulative stats snapshot.

| Metric | Definition | Source |
|---|---|---|
| Cost | USD charged by the provider for one run | `run-stats.json`, derived from the run's session events |
| Cost per verified task | Total cost of an arm divided by its number of passing runs | Computed from `summary.json` |
| Verified | The task's verification command exited `0` | `meta.json` → `verification_exit` |
| Scope score | 4 = verification passed and only expected files changed; 3 = passed with unexpected or missing changes; 1 = verification failed; 0 = run failed | `status.txt` compared with the task's allowed files |
| Wall time | Seconds from process start to process exit | `meta.json` → `wall_time_seconds` |
| Input tokens | Fresh prompt tokens billed at the input rate | `run-stats.json` |
| Output tokens | Visible response tokens | `run-stats.json` |
| Reasoning tokens | Billed reasoning tokens | `run-stats.json` |
| Cache read | Prompt tokens served from the provider cache | `run-stats.json` |
| Tool calls | Number of tool invocations in the session | `run-stats.json` |

Cost and tokens are recomputed from each run's `session.jsonl`. The raw `opencode stats --project .` snapshot is retained as `stats.json` but is **not** used for any number on this page, because it can aggregate sessions that share a project identity.

## Results by arm

The table adds per-run medians to the totals. **Total cost** answers what the batch cost; **cost per verified** normalizes for correctness; **median cost**, **median steps**, and **median tools** describe a typical run; **median wall** describes typical latency. Read medians when one expensive run could distort the total, and read totals when budget is the question. Both are shown because they can disagree: `direct-slim` has the lowest median run cost but a higher total than baseline.

| Arm | Runs | Verified | Scope 4 | Total cost | Cost per verified | Median cost | Median wall | Median steps | Median tools |
|---|---|---|---|---|---|---|---|---|---|
| `baseline` | 9 | 9 | 9 | $0.0663 | $0.0074 | $0.0051 | 39s | 12 | 15 |
| `optimized` | 9 | 9 | 9 | $0.0872 | $0.0097 | $0.0089 | 72s | 16 | 18 |
| `coordinator-slim` | 9 | 9 | 9 | $0.0772 | $0.0086 | $0.0081 | 59s | 16 | 26 |
| `direct-slim` | 9 | 9 | 9 | $0.0833 | $0.0093 | $0.0045 | 46s | 15 | 18 |
| `tools-on-demand` | 9 | 9 | 9 | $0.0783 | $0.0087 | $0.0074 | 55s | 15 | 19 |

Two medians are worth reading carefully:

- `direct-slim` has the **lowest median run cost** ($0.0045) but a **higher total** than baseline. Most of its runs are cheap; three expensive `hono-set-cookie` runs raise the total. That is why total and median are both reported.
- `tools-on-demand` has a higher total than `coordinator-slim` despite using fewer shell calls, and it carries 3.48M cache-read tokens. Keeping MCP available was not free even when its tools were rarely used.

## Results by task

Median cost per task over three repeats, grouped so each task can be compared across arms. The table shows where an arm wins and where it loses; it is the evidence behind the claim that the aggregate is not uniform. Read across a row to compare arms on the same task, and down a column to see whether an arm is consistently cheap or expensive. The largest task, `hono-set-cookie`, dominates the total.

| Task | `baseline` | `optimized` | `coordinator-slim` | `direct-slim` | `tools-on-demand` |
|---|---|---|---|---|---|
| `hono-redirect` | $0.0051 | $0.0089 | $0.0086 | **$0.0045** | $0.0074 |
| `hono-request-id` | **$0.0036** | $0.0043 | $0.0040 | $0.0044 | $0.0049 |
| `hono-set-cookie` | **$0.0102** | $0.0164 | $0.0111 | $0.0185 | $0.0121 |

The result is not uniform:

- `direct-slim` was the cheapest arm on `hono-redirect`, and `coordinator-slim` was cheaper than `optimized` on all three tasks.
- `baseline` was cheapest on the other two tasks and on the total.
- `hono-set-cookie` dominates the aggregate. Every ToolWright arm cost more than baseline there: `optimized` and `direct-slim` were about 1.6–1.8× baseline, while `tools-on-demand` came closest. A configuration that helps small edits but scales badly on a larger change will still lose on total cost.

## Tokens and tool use

Totals across the nine runs of each arm, split into the token categories the provider bills and the tool categories that explain behavior. Input and output are visible prompt and response tokens; reasoning is billed separately; cache read is prompt text served from the provider cache; shell and edit calls show how the agent changed files. Read this table with the cost table: reasoning growth and shell-based editing are the two largest behavioral differences between the arms.

| Arm | Input | Output | Reasoning | Cache read | Tool calls | Shell calls | `edit` calls |
|---|---|---|---|---|---|---|---|
| `baseline` | 197,154 | 21,694 | 26,683 | 2,559,872 | 158 | 71 | 28 |
| `optimized` | 201,434 | 29,535 | 44,930 | 4,116,096 | 176 | 114 | 0 |
| `coordinator-slim` | 170,004 | 32,191 | 37,532 | 3,280,768 | 201 | 132 | 0 |
| `direct-slim` | 185,341 | 29,135 | 42,938 | 4,095,360 | 203 | 111 | 30 |
| `tools-on-demand` | 174,910 | 31,163 | 38,287 | 3,477,120 | 177 | 109 | 0 |

Three patterns explain part of the gap:

1. **Reasoning tokens rose sharply.** The baseline produced 26,683 reasoning tokens; the ToolWright arms produced 37,532–44,930. Reasoning is billed, so a more deliberate workflow has a direct cost.
2. **The coordinator edits through `shell`.** Coordinator arms made 109–132 shell calls and **zero** `edit` calls across nine runs. `direct-slim`, which may use `edit`, made 30 `edit` calls and one `write`, but still issued 111 shell calls; its shell overhead kept it above baseline.
3. **The coordinator did not delegate.** No session contains a subagent invocation. The coordinator solved the tasks directly, so the "hop" in this experiment is really a coordinator doing implementer work without the implementer's `edit` permission. That is a concrete, fixable defect, not an inherent cost of orchestration.

MCP observations:

- Serena's `execute` tool was called 8 times in `optimized` and 9 times in `tools-on-demand`. Those are the only MCP tools observed.
- CodeGraph, Repomix, and jCodeMunch were never called. Any schema or startup cost they added was paid without an observed benefit on these tasks.
- The two no-MCP arms still used `shell`, `read`, `grep`, and `glob`, which is expected: native tools remain available.

## Correctness and scope

Every run is scored with the same rubric before cost is considered, so a cheap but wrong run cannot look like a win. The table defines the four scores: 4 is a verified change limited to expected files, 3 is a verified change with a scope problem, 1 is a failed verification, and 0 is a failed run. The score is derived from the verification exit code and the changed-file set recorded after the agent finished.

| Score | Meaning |
|---|---|
| 4 | Verification passed; only expected files changed |
| 3 | Verification passed, but the change set was missing expected files or touched unexpected ones |
| 1 | Verification failed |
| 0 | The run itself failed (process error or timeout) |

Outcome:

- **45 of 45 runs verified** and **45 of 45 scored 4**.
- No run timed out; the slowest run was 229s against a 900s limit.
- No run edited files outside the task's expected set.

Cost ranges show the spread behind each median, because a single number can hide large run-to-run variation. The table lists the cheapest and most expensive run for each arm; overlapping ranges mean the medians should be read as descriptive rather than decisive. The spread also explains why this screen uses three repeats and why the full plan calls for more.

| Arm | Cheapest run | Most expensive run |
|---|---|---|
| `baseline` | $0.0031 | $0.0211 |
| `optimized` | $0.0033 | $0.0227 |
| `coordinator-slim` | $0.0038 | $0.0224 |
| `direct-slim` | $0.0041 | $0.0276 |
| `tools-on-demand` | $0.0039 | $0.0205 |

## Decision

The decision rule was:

- at least **15% lower cost than both `baseline` and `optimized`**;
- equal verification results;
- no worse scope score;
- no wall-time regression;
- no increase in rework.

**No arm met the bar.** Therefore:

- production profiles, agents, and defaults are unchanged;
- the benchmark arms remain benchmark-only;
- the negative result is published rather than reframed as a win.

## What would change the conclusion

1. **Give the coordinator an `edit` route and discourage shell-based edits.** The coordinator path made zero `edit` calls and edited through `shell`. Even `direct-slim`, which may use `edit`, made 111 shell calls, so the instruction set must prefer the edit tool for file changes. A narrow `edit` permission or routing implementation to a specialist is the most likely way to close the gap.
2. **Make delegation actually happen.** The coordinator did not invoke any subagent. If orchestration is meant to reduce context, the coordinator must delegate instead of doing the work itself.
3. **Re-run the three-task screen after that change.** It is cheap and informative. Only a result that closes the gap to baseline should justify the full five-task, five-repeat matrix in the plan.
4. **Keep the no-MCP config available but not default.** It was cheaper than the full MCP surface here, but still more expensive than stock. Availability is not promotion.

## Limitations

- **One model, one tool, one repository, three tasks.** This is a screen, not a universal result.
- **Three repeats per cell.** The cost spread inside one arm is large; medians are descriptive, not a significance test.
- **Correctness is a test command plus a changed-path check.** There was no independent blind review, and no second human review of the diffs.
- **Rework was not exercised.** No follow-up prompts were issued after a passing verification, so rework is zero by construction, not by measurement.
- **Provider pricing is a moving target.** The numbers use DeepSeek Flash prices at run time.
- **MCP tools were scarcely used.** The result says more about MCP overhead than about MCP capability. A task that needs symbol navigation could change that.
- **The `tool_output` cap was not isolated.** The two slim arms change both the MCP surface and the output cap; this run cannot attribute their difference to one of those factors alone.
- **The round was not the full plan.** Phase 5 specifies five tasks and five repeats per cell. This run is the smaller screen described in the plan.
- **Three cells were re-executed.** A review of the first pass found that the agent in three `hono-set-cookie` runs could inspect the harness directory (one read the runner script). Those cells were re-run in fresh workspaces whose parent contained no harness files, and the published artifacts are the clean re-runs. The other 42 sessions contain no harness file contents.
- **Recorded commit varies.** The first 42 runs record `commit: 7e44ca6`, the repository HEAD while the arm and harness changes were still uncommitted; the three re-runs record `33b2901`, when the harness and arms were committed. The arm configs and harness are published with this result set, and `tests/unit/test_benchmark_arms.py` pins the arm configs to their source configs.
- **Published artifacts are path-sanitized.** Machine-specific home, repository, workspace, template, temporary, and user paths are replaced with `<home>`, `<repo>`, `<workspace>`, `<template>`, `<tmp>`, and `<user>`. Token, cost, and changed-file data are unaffected.

## Reproducing this result

The fixture setup is documented in [real Hono fixtures](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/benchmarks/real-hono-fixtures.md). A minimal reproduction:

```bash
git clone --no-checkout --filter=blob:none https://github.com/honojs/hono /tmp/toolwright-hono
git -C /tmp/toolwright-hono fetch --depth 1 origin f6fbaf0299c48eea9e656e03e2ffe7ac755e8823
git -C /tmp/toolwright-hono checkout --detach FETCH_HEAD
cd /tmp/toolwright-hono
pnpm install --frozen-lockfile
toolwright install --profile minimal --target /tmp/toolwright-hono --apply

OPENCODE_BENCH_MODEL=deepseek/deepseek-flash \
  /path/to/ToolWright/benchmarks/harness/run.sh \
  --arm coordinator-slim \
  --task /path/to/ToolWright/benchmarks/real/hono/tasks/set-cookie.json \
  --workspace /tmp/toolwright-hono
```

The profile install is required for every ToolWright arm, because the harness checks for the selected agent file under `.opencode/agents/`. Repeat for each arm and task, or drive the matrix with a script. Use a fresh checkout per run for `baseline`, and reinstall the profile before switching back to `optimized`, because the harness overwrites `<workspace>/.opencode/opencode.jsonc` with the selected arm config.

## Artifacts

Each run directory is self-contained so a reviewer can audit the numbers without rerunning the model. The table lists each file and what it contains, from run metadata and derived statistics to the raw session stream, the verification output, and the workspace diff. Start with `meta.json` and `run-stats.json` for the headline values, then use `session.jsonl` and the diff files when you need to check what the agent actually did.

| File | Contents |
|---|---|
| `meta.json` | Arm, agent, model, task, commit, wall limit, exit statuses, wall time |
| `run-stats.json` | Cost, tokens, steps, tool calls, prompts derived from the session |
| `session.jsonl` | Raw OpenCode event stream for the run |
| `export.json` | Sanitized session export |
| `stats.json` | Raw `opencode stats --project .` snapshot; not used for the result |
| `verification.log` | Output of the task's verification command |
| `status.txt` | `git status --short` after the agent run |
| `diff.patch` | Tracked modifications after the agent run |
| `diff-stat.txt` | Summary of `diff.patch` |
| `notes.md` | Run notes and the correctness/rework fields |

The [aggregate summary](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/benchmarks/results/hono-cost-ab-2026-11-16/summary.json) has one row per run with cost, tokens, wall time, changed files, scope score, and verification status. It is the machine-readable table behind this page.

Related: [benchmark methodology](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/benchmarks/methodology.md), [real Hono fixtures](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/benchmarks/real-hono-fixtures.md), [benchmark arms](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/benchmarks/arms/README.md), and the [cost and performance plan](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/plans/cost-performance-optimization.md).
