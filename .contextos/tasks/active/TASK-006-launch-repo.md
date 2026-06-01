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
- Add the first static marketing site for `contextos.quantumleapit.in`.

## Status

In progress. Launch-prep documentation and the static marketing site are pushed
to `origin/main`, GitHub metadata is set, release `v0.1.0` exists with verified
wheel and sdist assets, and repository visibility is now public. GitHub Pages
deployment is being wired through `.github/workflows/pages.yml`; the custom
domain still needs DNS to resolve.

## Notes

- Use `contextos.quantumleapit.in` as the first marketing/docs site.
- Do not block launch on buying a separate product domain.
- Do not block launch on PyPI package publishing.
- GitHub is the canonical source, issue, and release home.
- `gh repo view` confirmed the repository is public.
- `gh repo view` confirmed description and homepage are set.
- `gh release view v0.1.0` confirmed the release exists and is not draft or
  prerelease.
- `site/` contains the first dependency-free static marketing site and is pushed
  to `origin/main` in commit `7a64c77`.
- `git ls-remote --heads origin main` confirmed `origin/main` is
  `7a64c774efa0bd164961d56679f0a4f6351c18c0`.
- `.github/workflows/pages.yml` deploys `site/` to GitHub Pages with pinned
  official Pages actions.
- GitHub Pages is enabled in workflow mode and configured with custom domain
  `contextos.quantumleapit.in`.
- The Pages workflow completed successfully.
- `curl -I https://bkalyankumar.github.io/contextos/` returns a GitHub Pages
  redirect to `http://contextos.quantumleapit.in/`, confirming Pages is routing
  to the configured custom domain.
- `curl -I https://contextos.quantumleapit.in` still fails DNS resolution.
- Required DNS record: `contextos` CNAME `bkalyankumar.github.io`.
- Static site structural QA passed: `ruff check .`, HTML fragment link check,
  and expected launch-link scan. Browser rendering was not available because
  Playwright is not installed in the Node kernel.

## Verification

- [x] Secret scan has no real findings.
- [x] `mypy src`
- [x] `ruff check .`
- [x] `pytest`
- [x] `vulture src tests`
- [x] `uv build`
- [x] GitHub repository metadata is set.
- [x] GitHub release `v0.1.0` exists.
- [x] Static marketing site exists in `site/`.
- [x] Repository visibility is public.
- [x] GitHub Pages deployment is enabled and verified.
- [ ] `contextos.quantumleapit.in` resolves and serves the static site.
