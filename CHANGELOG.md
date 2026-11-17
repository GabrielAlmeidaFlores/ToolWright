# Changelog

All notable changes to ToolWright are documented here.

## [Unreleased]

### Added

- Binding project-memory protocol for Claude Code, GitHub Copilot, and OpenAI Codex. The generated instructions tell agents to read `.toolwright/memory/catalog.md`, verify entries against their source, and record durable findings. OpenCode uses the opt-in preamble plugin.
- Per-project setup documentation for OpenCode, Claude Code, GitHub Copilot, and OpenAI Codex.

### Changed

- Refocused the repository on the repeatable, safe, provider-neutral environment objective. The README, documentation home, and operating contract now lead with setup, daily use, memory, verification, and lifecycle.
- Reduced the tracked tree to the environment, adapters, agents, skills, memory, verification, governance, security, release process, and optional Ralph orchestration.
- Documentation tables and diagrams require an explanatory paragraph before them.
- Documentation links use absolute GitHub URLs.

### Removed

- Benchmark harness, tasks, fixtures, arms, result artifacts, and benchmark documentation.
- Pilot runner, pilot configuration, and pilot reports.
- Stats and usage commands, cost-optimization pages, and research/plan archives.
- The scoped-router experiment and its benchmark arm.
- Cursor from setup and memory documentation.
- Generated caches, build outputs, and local tool configuration from the working tree.

### Fixed

- `toolwright memory` commands write to the selected project instead of resolving the ToolWright source checkout.
- `toolwright memory` is usable in an installed project, not only in the ToolWright repository.

## Scope

ToolWright does not claim a cost, token, benchmark, or multi-agent performance win. Its value is a consistent, verifiable, portable workflow around the model.
