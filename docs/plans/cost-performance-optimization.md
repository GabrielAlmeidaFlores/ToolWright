# Cost and Performance Optimization Plan

> **Status:** Planned · **Last verified:** 2026-11-16 · **Evidence:** Phase 0 harness, arms, and a 45-run Hono A/B completed; no promotion, see [Hono cost A/B results](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/benchmarks/results-hono-cost-ab.md)

## Implementation progress

- Phase 0 is implemented: the harness supports `--workspace`, isolated `XDG_CONFIG_HOME`, and `opencode --standalone`; real Hono fixtures live under `benchmarks/real/hono/`.
- A baseline smoke run on Hono passed verification with no global MCP leakage.
- Phase 1 benchmark-only arms are implemented under `benchmarks/arms/`.
- The initial A/B is complete: 45 isolated runs (5 arms, 3 Hono tasks, 3 repeats), all verified, all scope score 4. No arm met the promotion bar; stock `baseline` was cheapest. See [Hono cost A/B results](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/benchmarks/results-hono-cost-ab.md).
- Production defaults, agent prompts, and profiles remain unchanged. The 125-run Phase 5 matrix is still required before any production change.

## 1. Purpose

Define a complete, reproducible plan to reduce the cost per correctly completed software task without reducing correctness or increasing rework.

The plan is based on:

- the 30-run DeepSeek Flash example benchmark;
- the 27-run real Hono tool matrix;
- nine tool probes;
- one Ralph research run;
- the committed pilot reports under [`docs/pilots/results/`](https://github.com/GabrielAlmeidaFlores/ToolWright/tree/main/docs/pilots/results); local `/tmp` pilot artifacts were inspected but are not repository evidence;
- the upstream [Hono](https://github.com/honojs/hono) and [Turborepo](https://github.com/vercel/turborepo) checkouts used for local review. They are not repository evidence.

This plan does not claim a cost win. It defines the experiments and changes required to find one.



## Pre-implementation validation findings

These findings were resolved before Phase 0 implementation; they are retained as design history. The approved decisions are recorded below.

1. **`minimal` is not MCP-free.** The current `minimal` profile installs no Serena/CodeGraph binaries, but `configs/opencode/opencode.jsonc` still declares both MCP servers. Installing `minimal` therefore does not create the proposed `direct`/no-MCP behavior. The approved decision is benchmark-only config variants; production profile semantics remain unchanged in Phase 1.

2. **“Direct by default” has no routing mechanism yet.** OpenCode has one `default_agent`. The current default is `coordinator`. A direct-agent default plus automatic routing requires either a minimal router agent, a deterministic `toolwright` wrapper/command, or keeping the coordinator as a lightweight router. The approved decision is benchmark-only arms first; production routing changes only after the A/B result.

3. **Step limits must not start at 8–10.** The real Hono runs reached 33–36 steps in several tasks. A coordinator cap of 8–10 would truncate valid work. Treat 16–24 as the first experimental range and calibrate from the benchmark.

4. **Reasoning configuration lacks a concrete mechanism.** The plan correctly says not to hardcode model IDs, but it does not yet say how per-role variants are selected. The approved benchmark mechanism is an explicit per-run model/variant; production uses provider or environment configuration after validation. No provider-specific IDs are committed.

5. **`tool_output` is global.** It cannot be varied per task through agent prompts. Lowering it requires a profile-specific config variant or accepting a global change. The approved approach is a benchmark-only config variant.

6. **The CHANGELOG entry must merge into the existing `### Added` section.** Resolved: the entry was merged into the existing heading.

7. **The plan document itself needs repository conventions.** Resolved: the plan page has a status block and MkDocs navigation. Agent modifications still require provenance registry updates.

8. **The exact benchmark tasks are not yet defined as repository fixtures.** Phase 0 added the three existing Hono fixtures. The two additional fixtures must be added before the final A/B.

9. **Tool coverage claims must stay honest.** `write` is unavailable to the coordinator in the current setup, and slash commands are not expanded by `opencode run`. The plan keeps those as unverified until a TUI/API test exists.

10. **The 125-run benchmark needs a cost/time estimate.** The final A/B must record its budget and wall-time estimate before running.

## Approved decisions

The recommendations were approved for staged implementation:

1. **Routing:** benchmark-only arms first. Keep the current coordinator as the production default until the A/B result. Do not add a router agent or CLI wrapper yet.
2. **MCP profiles:** use benchmark-only config variants. Do not change the installer or production profile semantics in Phase 1.
3. **Reasoning/model:** select variants per benchmark run. Production uses provider/environment configuration after validation; no provider/model IDs are committed.
4. **Tasks:** start with the three existing Hono tasks. Add the multi-file and investigation fixtures before the final five-task A/B.
5. **Default agent:** keep `coordinator` until the A/B completes.
6. **Edit permissions:** implementers keep `edit`/`write`; the coordinator remains read-only and must not use shell for edits.
7. **Step budgets:** start in the 12–32 range, not 8–10; calibrate from the benchmark.
8. **Scope:** OpenCode reference adapter and `deepseek/deepseek-flash` only for this stage.

The plan is ready for Phase 0 and Phase 1 implementation. Production defaults remain unchanged until the A/B result.

## 2. Evidence summary

### 2.1 Published benchmark evidence

The table below summarizes the published evidence that motivated this plan. Each row is a measured change against the baseline, so a positive cost percentage means the optimized configuration spent more. The baseline column is the reference, the optimized column is the current ToolWright profile, and the full-forced column is the aggressive tool-encouragement arm. Read the rows together: a token reduction that comes with a cost or wall-time increase is not a saving.

| Benchmark | Baseline | Optimized | Full-forced |
|---|---:|---:|---:|
| Example tasks: cost change | — | +14.2% | not run |
| Example tasks: wall change | — | +37.3% | not run |
| Hono real: cost change | — | +18.3% | +79.1% |
| Hono real: wall change | — | +67.8% | +376.4% |
| Hono real: tokens change | — | −18.0% | +19.5% |
| Hono real: verification | 9/9 | 9/9 | 9/9 |

The real Hono matrix shows the central problem:

- the optimized arm reduced total tokens by 18.0%;
- it still cost 18.3% more because output and reasoning rose;
- the full-forced arm passed every test but cost 79.1% more and was 4.8× slower.

### 2.2 Cost structure

Using DeepSeek Flash off-peak prices:

| Component | Example baseline | Example optimized | Hono baseline | Hono optimized |
|---|---:|---:|---:|---:|
| Input | 37.5% | 32.2% | 47.9% | 30.6% |
| Cache hits | 9.9% | 9.0% | 14.8% | 16.1% |
| Output + reasoning | 52.5% | 58.9% | 37.3% | 53.4% |

Input compression is not enough. Output and reasoning are the dominant cost lever.

### 2.3 Tool evidence

The real Hono run exercised:

- Serena: 163 execute calls in the full-forced arm;
- CodeGraph: 9 calls in the optimized arm;
- ast-grep: 27 shell commands in the full-forced arm;
- `systematic-debugging` skill: 9 calls;
- `code-reviewer` subagent: 11 calls;
- memory plugin: returned the configured memory title;
- `todowrite`: used;
- Ralph: 2 iterations, 176.2s, completion promise;
- commands: **not verified** because `opencode run` passes `/review` as literal text;
- `write`: **not available to the coordinator**; the coordinator edits through `shell`.

### 2.4 Observations from upstream repositories

These are design observations, not independent cost benchmarks.

**Hono CI**

- skips docs, README, license, and adapter changes with path filters;
- caches dependencies;
- splits runtimes and test suites into separate jobs;
- runs targeted checks before broader checks;
- runs performance and bundle-size checks only for relevant PRs;
- uses deterministic commands as gates.

Implication: use selective gates and targeted verification. Do not run the most expensive path for every change.

**Turborepo**

- `AGENTS.md` tells the agent to resolve the installed `turbo` package and read the version-matched docs under `node_modules`;
- a managed block is reinserted by `turbo` before agent commands;
- `CLAUDE.md` only references `@AGENTS.md`.

Implication: context should be local, versioned, and loaded at the point of use. One source of instructions is better than duplicated global prompts.

**Prior pilot artifacts**

- discovery tasks used the `backend-developer` agent directly, not the coordinator;
- prompts limited investigation (“inspect at most 5 files”);
- prompts requested one artifact and forbade unrelated edits;
- discovery tasks often forbade running tests;
- code tasks named exact files and targeted verification;
- observed costs were roughly $0.0025–$0.031 per task.

Implication: direct specialist plus narrow scope is the default for small work.

## 3. Goals and non-goals

### Goals

1. Reduce cost per verified task by at least 15–20% versus the current optimized arm.
2. Preserve correctness scores and verification outcomes.
3. Avoid increasing rework or human intervention.
4. Reduce wall time or keep it flat where possible.
5. Make the default route predictable, inspectable, and provider-neutral.
6. Keep all tool capabilities available, but only expose or use them on demand.
7. Produce a reproducible benchmark that compares the new route against the current arms.

### Non-goals

- Do not add a new MCP server or external tool in the first implementation.
- Do not remove existing tools or agents.
- Do not claim cross-tool results for Claude, Copilot, or Codex from an OpenCode run.
- Do not optimize token count alone.
- Do not auto-commit or change the Git safety rules.
- Do not hardcode model IDs or provider IDs in committed configuration.
- Do not make Ralph the default for small tasks.

## 4. Design principles

1. **Direct by default.** Small, explicit work goes to one specialist agent.
2. **Coordinator as router.** The coordinator classifies and delegates only when needed.
3. **Few choices.** Expose the smallest tool set that can complete the task.
4. **Point-of-need context.** Load documentation and skills when the task needs them.
5. **Output contract.** Ask for evidence, not narration.
6. **Selective gates.** Run the narrow test first; widen only when the diff requires it.
7. **Cache-friendly prompts.** Keep instructions and tool order stable.
8. **Measure cost per successful task.** Token reduction without correctness is not a result.

## 5. Target architecture

### 5.1 Routing policy

Add a deterministic routing table to the coordinator and documentation.

| Task signal | Default agent | Coordinator | Tool profile |
|---|---|---|---|
| One file, known path, simple verification | `backend-developer`, `frontend-developer`, or `documentation-engineer` | No | `direct` |
| Bug with unclear location | `test-engineer` or `researcher` | No | `standard` |
| Refactor across 2–3 related files | `architect` then implementer | Optional | `standard` or `symbols` |
| Multi-file feature with independent parts | `coordinator` | Yes | `symbols` or `graph` |
| Security review | `security-reviewer` | No | `direct` |
| Independent parallel research | `coordinator` + subagents | Yes | `standard` |
| Large, ambiguous, multi-wave work | `coordinator` / Ralph | Yes | `full` |
| Documentation-only | `documentation-engineer` | No | `direct` |

The router must be deterministic based on the request and repository paths, not another model call. If a model call is required to classify, the saving is already lost.

### 5.2 Tool profiles

Do not expose every MCP server in every session.

| Profile | MCP/tool surface | Use |
|---|---|---|
| `direct` | native read, grep, glob, edit, write, shell | small edits, docs, tests |
| `standard` | native + ast-grep | structural search |
| `symbols` | native + Serena | symbol navigation and references |
| `graph` | native + CodeGraph | dependency and impact analysis |
| `full` | native + Serena + CodeGraph + Ralph + plugin | explicitly requested complex work |

**Implementation note:** the current profile mechanism installs components but does not rewrite the MCP block in `configs/opencode/opencode.jsonc`. A new `direct` profile alone will still load the MCP servers declared in that config. The implementation must choose one of:

- profile-specific config documents;
- an installer flag that writes `disabled: true` for unselected MCP servers;
- a generated config overlay applied after installation.

Do not claim the `direct` profile is MCP-free until one of these is implemented and tested.

Implementation options:

1. Prefer per-agent permissions and `mcp.servers.<name>.disabled`.
2. Add profile-specific config variants only if permissions cannot hide enough tools.
3. Keep the current `minimal`, `standard`, and `full` install profiles. Prefer reusing them with config variants; add new install profiles only when the installer can select the matching config. Do not add a `direct` profile that still installs the MCP block.

### 5.3 Agent contracts

**Coordinator**

- classify the task;
- choose the shortest adequate route;
- delegate only independent work;
- do not edit directly;
- stop when the verification command passes;
- return changed files, tests, evidence, and risks;
- never spawn a subagent just to “use a subagent”.

**Implementers**

- receive exact file paths and acceptance criteria;
- use `edit` and `write`, not shell redirection;
- run the narrow verification command;
- return no restating of the plan;
- stop after tests and scope are confirmed.

**Reviewers**

- read-only;
- return findings in severity order with file:line;
- do not rewrite the implementation;
- do not repeat the task description.

**Researchers/planners**

- cap file inspection;
- produce a compact artifact;
- do not run unrelated tests;
- cite file:line;
- stop at the requested depth.

### 5.4 Reasoning and output policy

The table below sets the planned reasoning and step budgets per agent for the first experiment. Read it as a starting hypothesis, not a production rule: each row names a role, the reasoning level to try, a step range to try, and the intended behavior. The budgets exist to stop a role from looping or over-explaining, and they must be calibrated against correctness before any of them is promoted.

| Agent | Reasoning target | Max steps | Notes |
|---|---|---:|---|
| coordinator | low/medium | 16–24 first experiment | route and stop |
| backend/frontend | low | 24–32 first experiment | implement and test |
| test-engineer | low | 12–16 first experiment | targeted tests |
| code-reviewer | low | 12 | findings only |
| architect | high | 16 | design only |
| security-reviewer | high | 16 | security findings |
| documentation-engineer | none/low | 12 | docs only |
| researcher | low | 16 | bounded exploration |

Do not start with 8–10 steps. The real Hono tasks used 33–36 steps in some runs; an untested low cap risks incomplete work.

These are starting points, not final values. Each value must be tested against correctness and rework.

### 5.5 Context and output controls

- lower `tool_output.max_lines` and `max_bytes` for small tasks;
- keep MCP off unless the task requires it;
- load skills on demand;
- keep memory plugin opt-in;
- keep instructions and tool order stable for prompt caching;
- do not enable warming by default;
- use a single `AGENTS.md` source; avoid duplicating rules across adapters.

## 6. Work breakdown

### Phase 0 — Baseline and measurement

Deliverables:

- freeze the current arms and results;
- add a “cost per verified task” metric to benchmark analysis;
- record cache hit rate, input/output/reasoning share, steps, tool calls, wall time;
- document the clean isolated environment requirement (`XDG_CONFIG_HOME` empty, `opencode --standalone`);
- confirm that global MCP servers are absent from benchmark runs;
- enforce each task's `max_wall_time_seconds` and terminate the run process group so MCP servers cannot outlive a run;
- record `status.txt`, `diff.patch`, and `diff-stat.txt` for scope analysis.

Files:

- `benchmarks/harness/run.sh`
- `scripts/benchmarking/summarize_session.py`
- `benchmarks/results/README.md`
- `docs/benchmarks/methodology.md`

Acceptance:

- all benchmark runs produce per-run `run-stats.json`;
- no global MCP contamination and no surviving MCP server after a run;
- cost per verified task is reported;
- every run records its changed files and diff.

### Phase 1 — Benchmark-only routing contract

This phase creates benchmark-only variants. Do **not** change the production coordinator, default agent, permissions, or step budgets until the A/B result. If a variant cannot be expressed without changing production files, create a separate benchmark config; do not promote it.

Deliverables:

- add the routing table to the benchmark configuration and documentation;
- add the routing table to `agents/coordinator/AGENT.md` only after the A/B result;
- create benchmark-only direct/coordinator-slim variants;
- add stop conditions and output contracts to those variants;
- add an explicit “do not delegate trivial tasks” rule to the benchmark variant;
- document examples of direct vs coordinator routes.

Status: the config-level variants and the route documentation are implemented. Stop conditions, output contracts, and the “do not delegate trivial tasks” rule change agent prompts, so they are deferred together with the production routing table until Phase 5 produces a result.

Files:

- `agents/coordinator/AGENT.md`
- `agents/*/AGENT.md`
- `AGENTS.md`
- `docs/agents/roles.md`
- `docs/orchestration/ralph.md` if Ralph guidance changes

Tests/gates:

- agent contract validation;
- documentation validation;
- no permission regressions;
- `make ci`.

Acceptance:

- a reviewer can determine the intended route from the task description;
- agent instructions never require the coordinator for a single-file edit;
- no new agent is added.

#### Implemented in Phase 1

The routing decision is expressed only in benchmark configuration; no production agent prompt, default agent, permission, profile, or step budget changed.

| Arm | Config | Agent | Difference from the current optimized arm |
|---|---|---|---|
| `coordinator-slim` | `benchmarks/arms/slim.jsonc` | `coordinator` | No MCP servers, 400-line tool output cap |
| `direct-slim` | `benchmarks/arms/slim.jsonc` | `backend-developer` | No MCP servers, 400-line tool output cap, no coordinator hop |
| `tools-on-demand` | `benchmarks/arms/tools-on-demand.jsonc` | `coordinator` | Full MCP surface, 400-line tool output cap |

The harness assigns the config and agent per arm and copies non-workspace arm configs into the disposable checkout before the run, so one installed profile can serve every arm. The routing-table text in the coordinator and specialist prompts stays deferred until Phase 5 produces a result, because it changes production behavior.

Verification of the arm contract:

```bash
python3 -m unittest tests.unit.test_benchmark_arms -v
./benchmarks/harness/run.sh --arm direct-slim \
  --task benchmarks/real/hono/tasks/set-cookie.json \
  --workspace /tmp/toolwright-hono --dry-run
```

The unit test parses each arm config and asserts the MCP surface, tool output cap, default agent, and that no arm tries to override agent frontmatter. A config-level `agents` entry does not override an agent defined by a Markdown file, so a step budget in the arm would be silently ignored; step limits belong to Phase 3. The dry run proves the harness maps the arm to its config and agent without executing a model call.

### Phase 2 — Tool policy and profiles

Phase 2 also starts as benchmark-only. Production profiles change only after Phase 5 shows a win.

Deliverables:

- define `direct`, `standard`, `symbols`, `graph`, and `full` benchmark tool surfaces;
- prefer per-agent permissions and `disabled` MCP entries;
- add profile-specific config variants because the current `minimal` profile does not disable MCP servers declared in `configs/opencode/opencode.jsonc`;
- ensure coordinator has no `edit`/`write` and does not use shell for edits;
- add explicit shell deny rules for file-writing commands if shell remains allowed for tests;
- give implementers `edit` and `write`;
- document when each MCP server should and should not be used.

Files:

- `configs/opencode/opencode.jsonc`
- `profiles/*.yml`
- `agents/*/AGENT.md`
- `docs/compatibility/*.md`
- `docs/code-intelligence/*.md`

Tests/gates:

- config validation;
- permission resolution checks;
- adapter discovery checks;
- `make ci` and `make lint`.

Acceptance:

- a direct profile starts with no MCP servers;
- Serena is not loaded for a one-file documentation edit;
- coordinator cannot silently edit through shell;
- all profiles remain installable and documented.

### Phase 3 — Reasoning and output budgets

Deliverables:

- add step budgets to agents where supported, starting in the 12–32 range and calibrating from the benchmark;
- define reasoning targets per role without hardcoding model IDs;
- choose and document the concrete mechanism: environment substitution in a generated config, provider/model settings, or an explicit per-run model argument;
- add output contracts to agent prompts;
- reduce tool-output limits for small tasks;
- document how to select variants through environment or provider config.

Files:

- `agents/*/AGENT.md`
- `configs/opencode/opencode.jsonc`
- `docs/configuration/*.md`
- `docs/cost-optimization/*.md`

Tests/gates:

- agent frontmatter validation;
- configuration schema validation;
- benchmark A/B for correctness.

Acceptance:

- no task is truncated by a step budget in the benchmark;
- correctness remains equal to baseline;
- output/reasoning share falls in at least one arm.

### Phase 4 — Context and verification discipline

Deliverables:

- update AGENTS and agent prompts with “inspect at most N files” and “do not run tests” for discovery;
- add exact-file and targeted-test guidance for implementation;
- add selective gate rules modeled on Hono CI;
- document when to run the full suite.

Files:

- `AGENTS.md`
- `agents/*/AGENT.md`
- `commands/*.md`
- `docs/architecture/testing.md`
- `docs/validation-checklist.md`

Acceptance:

- prompts require less exploration than the current coordinator;
- targeted verification is the default;
- full-suite runs are justified by the change scope.

### Phase 5 — Benchmark A/B

Arms:

| Arm | Description |
|---|---|
| `baseline` | stock OpenCode |
| `coordinator-current` | current ToolWright coordinator |
| `coordinator-slim` | routing + low reasoning + step caps |
| `direct-slim` | direct specialist + low reasoning |
| `tools-on-demand` | selected profile per task |

Tasks:

- Hono `set-cookie`;
- Hono `redirect`;
- Hono `request-id`;
- one multi-file Hono feature task;
- one read-only investigation task.

Before running, add all five tasks as repository fixtures with exact prompts, acceptance criteria, verification commands, working directories, allowed files, and provenance. Do not leave them as prose placeholders.

Procedure:

- 5 repeats per task and arm; 5 arms × 5 tasks × 5 repeats = 125 runs;
- estimate budget and wall time before starting; at benchmark costs this is cheap in dollars but takes hours;
- fresh clone each run, placed in a temporary root that contains no harness files or sibling run artifacts;
- isolated `XDG_CONFIG_HOME`;
- `opencode --standalone run`;
- off-peak DeepSeek pricing;
- targeted verification;
- record correctness, scope, cost, tokens, steps, tools, wall time, cache hit, rework.

Acceptance:

- same verification result as baseline;
- no worse scope score;
- at least 15–20% lower cost than `coordinator-current` and never more expensive than the stock baseline;
- no wall-time regression;
- no increase in rework;
- results published with limitations.

If `coordinator-slim` does not win, keep the current behavior and document the negative result.

#### Implemented: initial 3-task screen

The first screen ran the three existing Hono fixtures with 3 repeats instead of the full 125-run matrix. Result:

| Arm | Total cost | Cost per verified task | Median wall | Verified | Scope 4 |
|---|---|---|---|---|---|
| `baseline` | $0.0663 | $0.0074 | 39s | 9/9 | 9/9 |
| `optimized` | $0.0872 | $0.0097 | 72s | 9/9 | 9/9 |
| `coordinator-slim` | $0.0772 | $0.0086 | 59s | 9/9 | 9/9 |
| `direct-slim` | $0.0833 | $0.0093 | 46s | 9/9 | 9/9 |
| `tools-on-demand` | $0.0783 | $0.0087 | 55s | 9/9 | 9/9 |

No arm met the 15% bar against both `baseline` and `optimized`. All three new arms were cheaper than `optimized` (11.5%, 10.2%, and 4.5%) but 16–26% above stock. Production behavior stays unchanged. The screen is published at [Hono cost A/B results](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/benchmarks/results-hono-cost-ab.md) with limitations.

Two findings move to Phase 3 before another A/B run:

1. Coordinator arms never call `edit`; they edit through `shell` and spend 109–132 shell calls per nine runs. This is a permission/contract problem, not a routing problem.
2. The two no-MCP arms did not use any MCP tools, but they still cost more than baseline. MCP schema weight is not the dominant cost on these tasks.

### Phase 6 — Documentation and release

Deliverables:

- add the plan to `docs/plans/cost-performance-optimization.md` with a docs status block;
- add the page to `mkdocs.yml` navigation;
- update README, methodology, cost-optimization docs, and result pages;
- update `docs/provenance/registry.yml` and agent headers for modified agents;
- add the CHANGELOG entry;
- bump the version only after the validated behavior change;
- keep the previous configuration available for comparison.

Files:

- `docs/plans/cost-performance-optimization.md`
- `docs/benchmarks/*`
- `docs/cost-optimization/*`
- `README.md`
- `CHANGELOG.md`
- `VERSION`
- `packages/toolwright_cli/pyproject.toml`

## 7. Proposed CHANGELOG entry

`[Unreleased]` already contains an `### Added` section. Merge these bullets into that existing section; do not add a second `### Added` heading.

```markdown
- Cost and performance optimization plan covering task routing, direct-agent defaults, tool policies, reasoning/output budgets, selective verification gates, and an A/B validation matrix.
- [Cost and performance optimization plan](docs/plans/cost-performance-optimization.md)
```

The plan page must carry a status block in the first eight lines. In Plan mode, `CHANGELOG.md` is not modified.

## 8. Metrics and success criteria

The table below defines the success criteria for the whole plan. Each row names a metric, the artifact that measures it, and the target the change must meet. The primary metric is cost per verified task; the remaining rows are guardrails that prevent a cheaper configuration from winning by producing worse code, more rework, or more human intervention. A result that misses a guardrail is not a success even if cost falls.

| Metric | Source | Target |
|---|---|---|
| Cost per verified task | `run-stats.json` | −15–20% versus coordinator-current |
| Verification success | task command | equal or better |
| Scope score | changed-path rubric | equal or better |
| Output + reasoning share | `run-stats.json` | lower |
| Cache hit rate | `run-stats.json` | stable or better |
| Wall time | harness timer | equal or lower |
| Steps | `run-stats.json` | lower on simple tasks |
| Tool calls | `run-stats.json` | lower on simple tasks |
| Rework | follow-up count | no increase |
| Human intervention | manual log | no increase |

## 9. Risks and mitigations

The table below lists the main ways this plan could fail and the mitigation for each. Each row pairs a concrete risk, such as a step cap truncating valid work or a token saving hiding a correctness loss, with the check that keeps it honest. Read it before changing budgets or routing, and treat an unmitigated risk as a reason to stop rather than to proceed.

| Risk | Mitigation |
|---|---|
| Step caps truncate valid work | benchmark all tasks; adjust per role |
| Low reasoning hurts correctness | require equal score before accepting cost |
| Hiding tools hurts retrieval | measure with and without Serena/CodeGraph |
| Routing table is ignored | put it in coordinator prompt and permissions; test |
| Shell edits bypass audit | give implementers edit/write; restrict coordinator shell |
| Cache invalidated by prompt changes | keep stable prefixes; measure cache hit |
| Model IDs hardcoded | use environment/provider configuration |
| Results overfit Hono | add a second repository before broad claims |
| Commands remain unverified | test through TUI/API, not `opencode run` |
| Benchmark contamination | isolate XDG, use `--standalone`, assert no global MCP |

## 10. Rollout and rollback

1. Implement behind benchmark-only profiles.
2. Run the A/B matrix.
3. Promote only the winning route to default.
4. Keep current coordinator and full profile available.
5. Document the negative result if no arm wins.
6. Roll back by restoring the previous profile or agent instructions.
7. No automatic commits; no automatic release.

## 11. Implementation guardrails

Every code or configuration change follows the repository contract:

- Python edits use named constants and the string-literal ledger test.
- New shell entry points have a header, documented functions, and an integration test.
- New configuration fields have validator coverage and a failing fixture where applicable.
- New docs pages have `Status`, `Last verified`, and `Evidence` in the first eight lines.
- Modified agents/commands/skills update provenance and attribution.
- Every change runs `make ci`, `make lint`, `make validate`, `mkdocs build --strict`, and `git diff --check` when applicable.
- No change stages, commits, tags, or releases automatically.
- Benchmark runs use isolated `XDG_CONFIG_HOME`, `opencode --standalone`, and off-peak pricing.

## 12. Decisions requiring human approval

- whether to make direct-agent routing the default;
- whether to reduce reasoning for implementers;
- whether to disable Serena/CodeGraph by default;
- whether to grant edit/write to implementers and deny shell edits;
- the step budgets;
- whether to add a deterministic `toolwright route` command after the experiment;
- whether to cut a minor release after the validated change.

## 13. Current recommendation

Do not add a new tool and do not promote an arm yet.

The 45-run screen did not produce a cost win. The next useful change is the Phase 3 editing/permission work: give the coordinator path a native `edit` route or route edits to a specialist, then re-run the 3-task screen. Only if that closes the gap to baseline should the full 125-run matrix decide a production change. A deterministic router or repository map is not justified by this result.
