# ToolWright Operating Contract

ToolWright is a **repeatable, safe, provider-neutral development environment for AI coding agents**. It does not make the model cheaper or smarter. It makes the workflow consistent, verifiable, and portable across clients and repositories.

Read this file before acting. The rules below are binding. When instructions conflict, prefer the stricter safety and evidence rule.

## Default loop

1. Restate the requested outcome and classify the change.
2. Inspect the repository before changing it. Read the relevant code, tests, docs, and workflows.
3. Make the smallest coherent change.
4. Add or update the test that fails without the change.
5. Run the relevant gates.
6. Update documentation, changelog, and provenance when applicable.
7. Report evidence, limitations, and the next step.
8. Leave changes unstaged unless the human explicitly requested staging and committing in the current turn.

## Autonomy and approval

Allowed without asking:

- read repository files and external documentation
- run offline validation, tests, lint, and dry runs
- write inside a temporary directory or disposable clone outside the repository
- generate adapter files into a temporary target
- propose a plan, diff, commit message, version, or release note

Ask before acting:

- installing packages globally or changing user configuration
- running paid model calls
- deleting files, rewriting history, or running destructive Git commands
- pushing, tagging, creating a release, or publishing results
- using network services that transmit repository contents

Never do:

- stage, commit, stash, reset, checkout, or clean without an explicit request in the current turn
- claim a command passed without running it and recording the result
- invent compatibility, provenance, or vendor claims
- present unverified behavior as verified

## Project memory

Before exploring code or re-deriving a decision, read `.toolwright/memory/catalog.md` when it exists. Open only the entries that match the task, taking them in the order `project/`, `user/`, and `shared/`. Treat an entry as context rather than proof: verify its claim against the cited `source` before relying on it, and ignore entries marked expired. When you learn a durable decision, constraint, convention, or failure, record it with `toolwright memory add` and cite a source. Never write credentials or secrets to memory. If the memory directory is absent, continue without it.

## Repository map

The table below maps each path to its responsibility. Read it before adding a new file so the change lands in the existing owner instead of creating a parallel structure.

| Path | Owns |
|---|---|
| `agents/` | Specialized agent prompts and permissions |
| `commands/` | Reusable command definitions |
| `skills/` | Reusable skill packages |
| `configs/` | OpenCode, Ralph, plugin, and adapter configuration |
| `packages/toolwright_cli/` | CLI, adapters, installer, lock, memory, verification, governance, specs, board |
| `scripts/validation/` | Repository and documentation checks |
| `scripts/installation/` | macOS and Linux installation and backups |
| `scripts/release/` | Version and local release verification |
| `tests/unit/` | Fast invariant and parser tests |
| `tests/integration/` | Real CLI and entry-point tests |
| `docs/` | Architecture, installation, compatibility, memory, verification, governance, security, decisions |
| `catalog/` | Generated artifact catalog |
| `docs/provenance/registry.yml` | Source of truth for artifact provenance |
| `profiles/` | Installable component profiles |

## Core principles

### Provider neutrality

The agent, command, skill, and rule content must stay usable across OpenCode, Claude Code, GitHub Copilot, and OpenAI Codex. Do not hardcode a model provider or model identifier in reusable artifacts. OpenCode is the reference adapter and must stay fully verified. The other adapters are installer-generated and must state their verification limits.

### Provenance and reuse

No agent, skill, command, prompt, template, example, or workflow may be authored from scratch when a maintained upstream artifact exists.

Evaluate sources in this order:

1. official repositories for the target system
2. official vendor or project collections
3. actively maintained community collections with a license and release history
4. original work only when 1–3 contain no suitable artifact, with a written justification

Every reusable artifact records its author, upstream repository, upstream path, commit or tag, retrieval date, license, local path, and the minimal local modification. Store this in frontmatter and in [`docs/provenance/registry.yml`](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/docs/provenance/registry.yml). Do not copy upstream text without attribution. Do not rename an artifact without recording the original name. Do not vendor an artifact under an incompatible license.

Original work is allowed only for glue code, project-specific fixtures, and configuration composition. Each exception is registered as `original` with a justification.

### Git Safety

Never stage, commit, stash, reset, checkout, or clean unless the human explicitly requested that exact operation in the current turn. Never configure an agent, script, hook, or CI job to commit automatically. Leave every change unstaged and return the diff with a proposed commit message.

Destructive Git operations require explicit confirmation even when the human is present.

### Documentation comments

Comments are documentation, not conversation. Every comment must describe purpose, contract, inputs, outputs, side effects, constraints, or a reference.

Prefer a descriptive name to a comment. Do not restate the identifier, signature, or next line. When the only available sentence would repeat the name, rename the identifier instead.

Python uses one module docstring and block-form docstrings. Inline comments are prohibited except tool directives such as `# noqa`, `# type: ignore`, or `# pragma`. Shell uses a header block and one block above each function; inline comments are prohibited except tool directives. JSONC and YAML use a header block and no per-field comments. Markdown prose and headings are not comments.

### Testing and CI

Every change to tooling, configuration, or repository invariants needs a test that fails without it.

- Use the Python standard library `unittest` runner.
- Keep the default suite deterministic and offline.
- Do not write inside the repository from tests; use temporary directories.
- Fixtures under `tests/fixtures/` are test inputs, not installable artifacts.
- Add a failing test when adding a validator rule or entry point.
- Add a new required file to the validator and cover it with a test.
- Every docs page outside `docs/decisions/` has `Status`, `Last verified`, and `Evidence` in the first eight lines.
- CI stays free of paid model calls.
- CI never stages, commits, or pushes.

### String constants and modularity

Every runtime string literal in first-party Python is defined once as a named constant and reused. Use `StrEnum` for closed vocabularies. A module has one responsibility; split command handlers, adapters, and validators when they mix unrelated concerns.

Docstrings, type annotations, fixtures, generated files, and third-party code are exempt. Existing violations are migrated module by module; new violations are rejected in review.

## Components

### Adapters

OpenCode is the fully verified reference adapter. Claude Code, GitHub Copilot, and OpenAI Codex receive installer-generated native files. Each adapter writes `toolwright.lock.json` and supports install, update check, rollback, and uninstall.

### Agents and permissions

The coordinator is primary. Specialists are subagents with least-privilege permissions. Read-only roles must not edit. The coordinator must not use shell to patch files when an edit tool is available. Do not add an agent unless a distinct responsibility exists.

### Memory

Memory is plain Markdown under `.toolwright/memory/` with `project`, `user`, and `shared` scopes. It uses lexical search, expiry, deduplication, credential rejection, and a bounded preamble. Do not add embeddings or a vector database for source-code memory.

### Verification and governance

Deterministic checks are the source of truth for correctness. Tests, lint, typecheck, scope checks, budgets, loop limits, and risk gates run without model tokens. `toolwright verify` and `toolwright govern` must stay deterministic.

### Ralph

Ralph is an optional orchestration runtime. Version 2.10.1 commits during landing and has no switch to disable it. Run it only in a separate disposable clone, never in the main checkout. A linked worktree is not sufficient because it shares `.git`.

### Code intelligence

Use the smallest useful set: ripgrep for exact search, LSP or Serena for symbols, ast-grep for structural search, and CodeGraph only when dependency questions dominate. Do not enable every MCP server by default.

## Change workflow

### Classification

The table below classifies changes and their release impact. Use the stricter row when a change fits more than one category.

| Change type | Version impact | Changelog | Release |
|---|---|---|---|
| Documentation only | none | optional | no |
| Internal maintenance | none or patch | optional | no |
| Bug fix | patch | required | yes |
| Backward-compatible feature | minor | required | yes |
| Behavior change | minor | required with migration note | yes |
| Breaking change before `1.0.0` | minor and migration note | required under Breaking | yes |
| Breaking change at `1.0.0` or later | major | required under Breaking | yes |

A documentation-only change never requires a release. A published wheel change normally does. A negative or unsupported result is publishable when correctness and limitations are included.

### Update workflow

1. Confirm scope and approval.
2. Inspect source, tests, docs, profiles, and workflows.
3. Research external changes against official documentation.
4. Implement the smallest coherent change with a failing test.
5. Run `make validate`, `make test`, `make lint`, and `make ci`.
6. Update every page whose claims the change invalidates.
7. Add a changelog entry for user-visible behavior.
8. Update provenance for added or modified artifacts.
9. Inspect the full diff and run `git diff --check`.
10. Report verified, unverified, and blocked work. Leave changes unstaged.

### Documentation rules

- Put a complete paragraph before every table, image, and diagram.
- Link repository files with absolute GitHub URLs, not relative paths.
- Update the page that owns the behavior, not only the README.
- Keep README claims short and link to the detailed page.
- Do not add a page when an existing page owns the topic.
- Remove or mark deprecated instructions instead of leaving contradictions.

### Evidence labels

The table below defines the labels used in documentation. Use the weakest accurate label and do not upgrade it without new evidence.

| Label | Meaning |
|---|---|
| Verified | A command or client check was run and recorded |
| Documented | Checked against official documentation but not executed |
| Vendor claim | Published by the vendor; not independently reproduced |
| Unverified | No check was run |
| Blocked | A required tool, credential, or funding is unavailable |

### Release workflow

A release requires explicit human authorization for the version, commit, push, tag, and publication. Update `VERSION`, the package version, the changelog, and the release page together. Run `make ci`, `make lint`, and `scripts/release/local_release_check.sh`. Verify the tag, wheel, checksum, installed version, and one adapter install before announcing the release. Never reuse or rewrite a published tag.

## Release-ready checklist

- [ ] Scope matches the request and the change classification is stated.
- [ ] Tests were added or updated and fail without the change.
- [ ] `make ci` and `make lint` pass.
- [ ] `git diff --check` passes.
- [ ] Documentation and status blocks are current.
- [ ] Every table, image, and flowchart has a paragraph before it.
- [ ] `CHANGELOG.md` has the correct entry.
- [ ] Provenance is current for artifacts.
- [ ] Adapter discovery and validation records are current for adapter changes.
- [ ] No credentials, absolute local paths, or generated drift are present.
- [ ] The report separates verified, unverified, and blocked work.
- [ ] Changes remain unstaged unless commits were explicitly authorized.
