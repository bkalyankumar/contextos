# TASK-005: Prepare For Public Open-Source Launch

## Status

Complete.

## Objective

Make the repository credible for public open-source contributors by tightening
the public-facing documentation, trust surfaces, contributor path, and launch
readiness tracking.

## Scope

- Refresh README for public launch positioning.
- Add security reporting guidance.
- Add project code of conduct.
- Add public launch checklist.
- Improve package metadata.
- Preserve MVP boundaries and avoid hosted/cloud/dashboard work.
- Add an explicit open-source license.

## Out Of Scope

- Publishing a package.
- Building a documentation site.
- Adding cloud sync, dashboards, IDE extensions, vector search, or runtime agent
  orchestration.

## Verification

- `mypy src` passed.
- `ruff check .` passed.
- `pytest` passed, 17 tests.
- `vulture src tests` passed.
- `.venv/bin/checkpoint --help` passed.
- `.venv/bin/checkpoint status` passed.
- `.venv/bin/python -c "import checkpoint_cli; print(checkpoint_cli.__name__)"` passed.
- `uv build` passed after sandbox escalation to access `~/.cache/uv`.
- `python -m pip show checkpoint-cli` failed because this shell has no `python`
  command.
- `.venv/bin/python -m pip show checkpoint-cli` failed because this uv-managed
  virtualenv has no `pip` module.

## Handoff Notes

Apache-2.0 is now committed as the open-source license for the CLI, schema,
docs, and local-first workflow. The next launch decision is whether to cut a
GitHub release before public announcement.
