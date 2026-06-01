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

In progress. Launch-prep documentation is committed locally in
`4cf0896 docs: prepare launch plan`. Remote launch mutations are pending explicit
user approval because pushing to `origin/main`, creating a public GitHub release,
and making the private repository public are external/shared-state changes.

## Notes

- Use `contextos.quantumleapit.in` as the first marketing/docs site.
- Do not block launch on buying a separate product domain.
- Do not block launch on PyPI package publishing.
- GitHub is the canonical source, issue, and release home.
- `gh repo view` confirmed the repository is still private and has no
  description or homepage set.
- `gh release list` returned no releases.

## Verification

- [x] Secret scan has no real findings.
- [x] `mypy src`
- [x] `ruff check .`
- [x] `pytest`
- [x] `vulture src tests`
- [x] `uv build`
- [ ] GitHub repository metadata is set.
- [ ] GitHub release `v0.1.0` exists.
- [ ] Repository visibility is public.
