# CI Troubleshooting

> **Status:** Stable · **Last verified:** 2026-11-17 · **Evidence:** workflow definition and local `make ci`

The CI workflow runs static validation, the offline test suite, the CLI lifecycle, strict documentation builds, example builds, and OpenCode profile discovery. It does not run paid model calls.

## Jobs

The table below lists each CI job and what it checks. Read the job name in the failure notification, then run the matching local command before changing the workflow.

| Job | What it checks | Local equivalent |
|---|---|---|
| `static` | Validator, catalog drift, version agreement, shell syntax, ShellCheck | `make validate` and `make lint` |
| `test` | Offline unit and integration suite on Ubuntu and macOS | `make test` |
| `cli` | Wheel build, doctor, profiles, catalog, verification, governance, install lifecycle | Build the wheel and run `toolwright doctor` |
| `docs` | Strict MkDocs build | `mkdocs build --strict` |
| `examples` | TypeScript and C# fixtures | `npm test` and `dotnet test` |
| `opencode profile` | Agent discovery in a temporary installed profile | Install the profile and run `opencode debug agents` |

## Common failures

- **Validator failure:** run `make validate` and fix the reported path, provenance field, comment, link, or documentation status.
- **Test failure:** run the failing module with `python3 -m unittest <module> -v`.
- **Catalog drift:** run `python3 scripts/catalog/build_catalog.py` and commit the generated catalog.
- **Shell failure:** run `bash -n` on the reported script, then `make lint`.
- **Docs failure:** run `mkdocs build --strict`; the error names the missing page or broken navigation entry.
- **CLI failure:** reproduce the step locally with `PYTHONPATH=packages/toolwright_cli python3 -m toolwright_cli ...`.
- **OpenCode discovery failure:** verify the installed profile contains `.opencode/agents/*.md` and that `opencode --version` is 2.2.x.

## Safety

CI reads the repository and reports results. It never stages, commits, pushes, tags, or publishes a release.
