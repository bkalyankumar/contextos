---
task_id: TASK-006
status: in_progress
created_at: 2026-06-01
owner: codex
---

# TASK-006: Launch repository and public site

## Goal

Prepare ContextOS / Checkpoint for public open-source launch and make the repo
announcement-ready.

## Scope

- Document the launch homes and domain decision.
- Prepare release notes for `v0.1.0`.
- Verify repository checks and build artifacts.
- Set GitHub repository metadata.
- Create the first GitHub release.
- Make the GitHub repository public when final launch verification is complete.
- Keep source install as the supported early-tester path.
- Move the first static marketing site and Pages deployment to private
  `contextos-site`.

## Status

In progress. Open-core launch-prep documentation is pushed to `origin/main`,
GitHub metadata is set, release `v0.1.0` exists with verified wheel and sdist
assets, and repository visibility is public. The static marketing site and Pages
deployment have been moved to private `contextos-site` so this repository stays
focused on the CLI, schema, and local-first workflow.

## Notes

- Use `contextos.quantumleapit.in` as the first marketing/docs site.
- Do not block launch on buying a separate product domain.
- Do not block launch on PyPI package publishing.
- GitHub is the canonical source, issue, and release home.
- `gh repo view` confirmed the repository is public.
- `gh repo view` confirmed description and homepage are set.
- `gh release view v0.1.0` confirmed the release exists and is not draft or
  prerelease.
- Static marketing files were moved to `/Users/bkakumar/contextos-site`.
- `contextos-site` initial commit is `f6b62d7 feat: add ContextOS marketing site`.
- `contextos-site` was pushed to `origin/main`.
- Open-core repo no longer contains `site/` or `.github/workflows/pages.yml`.
- GitHub Pages was disabled on the open-core `contextos` repo; `gh api
  repos/bkalyankumar/contextos/pages` returns 404.
- Marketing/cloud source should remain private in `bkalyankumar/contextos-site`.
- Static site structural QA passed after the move: HTML fragment link check and
  expected launch-link scan.

## Verification

- [x] Secret scan has no real findings.
- [x] `mypy src`
- [x] `ruff check .`
- [x] `pytest`
- [x] `vulture src tests`
- [x] `uv build`
- [x] GitHub repository metadata is set.
- [x] GitHub release `v0.1.0` exists.
- [x] Repository visibility is public.
- [x] Marketing site and Pages deployment moved out of open-core repo.
- [x] `contextos-site` is pushed.
- [ ] Decide whether to enable public Pages deployment from private
  `contextos-site`.
