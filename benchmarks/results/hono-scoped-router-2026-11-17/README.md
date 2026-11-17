# Hono Scoped-Router Screen

This directory holds 75 isolated runs of the `scoped-router` screen: three arms, five Hono tasks, and five repeats on `deepseek/deepseek-flash`. The goal was to test whether a coordinator that edits one known file directly and delegates multi-file work reduces cost without losing correctness. The runs are experimental evidence; they do not promote a production default.

The table below reports the aggregate result for each arm. Runs is the number of completed runs, Verified is the count whose task verification command exited zero, and Cost per verified divides total recorded cost by verified runs. Read the verification and limitation sections before reusing any cost comparison.

| Arm | Runs | Verified | Total cost | Cost per verified | Median wall |
|---|---:|---:|---:|---:|---:|
| `baseline` | 25 | 25 | $0.401576 | $0.016063 | 62s |
| `optimized` | 25 | 25 | $0.399322 | $0.015973 | 112s |
| `scoped-router` | 25 | 23 | $0.336070 | $0.014612 | 63s |

The scoped-router total is lower, but the saving comes from the investigation task where two runs failed. On the four code tasks where every scoped-router run passed, the arm cost **$0.2223**, compared with **$0.2159** for `baseline` and **$0.2199** for `optimized`. It was therefore slightly more expensive on correctly completed code work, not cheaper.

The routing hypothesis also failed: the scoped-router used zero subagent calls across all 25 runs, including the three-file `hono-jwt-typ` task. It edited every task directly. On `hono-jwt-typ` it cost **$0.1135**, compared with **$0.0812** for `baseline` and **$0.0831** for `optimized`.

## Verification failures

Two runs failed verification, both the read-only investigation task:

- `r1-scoped-router-context-investigation`
- `r5-scoped-router-context-investigation`

Both hit the scoped-router 30-step cap before writing `INVESTIGATION.md`. They are agent-behavior failures, not harness failures. No rework was performed, so the published pass rate is the observed pass rate without retries.

## Limitations

- The run set spans commits `994a3b4` and `fdb7584`. The later commit changes memory, CLI, and documentation behavior, not the harness, task prompts, agents, or templates.
- The screen does not test the routing rule because the arm never delegated.
- The investigation failures mean the overall cost comparison is not a valid saving.
- Results are one model, one repository, and five repeats. Do not generalize them to other models, repositories, or task shapes.

The per-run artifacts are in the sibling run directories. `summary.json` contains the aggregate values in machine-readable form. Methodology is in [`docs/benchmarks/methodology.md`](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/benchmarks/methodology.md).
