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

## Status

In progress. Launch-prep documentation is pushed to `origin/main`, GitHub
metadata is set, and release `v0.1.0` exists with verified wheel and sdist
assets. Repository visibility remains private because the automated public
visibility change was blocked for disclosure risk and must be completed manually
by the repository owner in GitHub settings.

## Notes

- Use `contextos.quantumleapit.in` as the first marketing/docs site.
- Do not block launch on buying a separate product domain.
- Do not block launch on PyPI package publishing.
- GitHub is the canonical source, issue, and release home.
- `gh repo view` confirmed the repository is still private.
- `gh repo view` confirmed description and homepage are set.
- `gh release view v0.1.0` confirmed the release exists and is not draft or
  prerelease.

## Verification

- [x] Secret scan has no real findings.
- [x] `mypy src`
- [x] `ruff check .`
- [x] `pytest`
- [x] `vulture src tests`
- [x] `uv build`
- [x] GitHub repository metadata is set.
- [x] GitHub release `v0.1.0` exists.
- [ ] Repository visibility is public.
