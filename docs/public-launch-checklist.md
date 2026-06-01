# Public Launch Checklist

This checklist tracks what must be true before ContextOS / Checkpoint is
announced as an open-source project.

## Launch Positioning

- [x] README explains that ContextOS is continuity infrastructure, not another
  coding agent.
- [x] README shows the core workflow:
  `Plan in Claude -> Code in Codex -> Debug in Claude Code -> Delegate to Antigravity -> Resume anywhere`.
- [x] MVP boundaries are explicit: local-first Markdown now; no cloud, dashboard,
  IDE extension, vector database, or multi-agent runtime yet.
- [x] Roadmap exists in `docs/roadmap.md`.

## Trust And Governance

- [x] Choose and add an open-source license: Apache-2.0.
- [x] Add `SECURITY.md` with private vulnerability reporting guidance.
- [x] Add `CODE_OF_CONDUCT.md`.
- [x] Keep GitHub Actions pinned to immutable commit SHAs.
- [x] Ensure `.gstack/` and generated local-only state are ignored.
- [x] Keep generated handoffs free of secrets.

## Contributor Experience

- [x] `CONTRIBUTING.md` covers setup, verification, and contribution rules.
- [x] Bug report and feature request templates exist.
- [x] Pull request template exists.
- [x] README includes install-from-source and smoke-test commands.
- [x] `pyproject.toml` includes public package metadata.
- [x] Publish package install path, or keep source install clearly marked as
  the supported early-tester path.

## Release Readiness

- [x] `CHANGELOG.md` has a `0.1.0` entry.
- [x] CI runs typecheck, lint, tests, and dead-code checks.
- [x] Local health score is 10.0 for configured repo-owned checks.
- [x] Design review recorded no UI scope.
- [x] Developer experience audit top gaps were fixed.
- [x] Decide whether to cut a GitHub release before public announcement.
- [x] Cut GitHub release `v0.1.0`.
- [x] Make the GitHub repository public.
- [x] Set the repository description and homepage.
- [x] Move marketing site and Pages deployment out of this open-core repo.

## Launch Homes

- Source, issues, and releases: `https://github.com/bkalyankumar/contextos`
- Marketing and docs site: `https://contextos.quantumleapit.in`
- Marketing/cloud source: private `bkalyankumar/contextos-site`
- Publisher: QuantumLeapIT

## Recommended Launch Gate

The open-core launch gate is clear: `v0.1.0` is released, repository metadata is
set, the repository is public, and source install is the supported early-tester
path. Marketing site and future cloud work live outside this repository.
