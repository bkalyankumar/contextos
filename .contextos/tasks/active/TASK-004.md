# TASK-004: Add `checkpoint continue` hero command

## Status

Implemented and verified in Codex. Ready for commit/push once repository remote metadata is available.

## Recommended Agent

Codex

## Goal

Make ContextOS feel like a continuity layer a developer reaches for during an agent switch or context outage.

The normal path should be:

```bash
checkpoint continue
checkpoint continue --from claude
checkpoint continue --from codex
```

Developers should not need to specify `--for codex` while already inside Codex when the current agent can be detected.

## Scope

Implement:

- `checkpoint continue` as a thin orchestration command over local handoff, active task, and resume-pack generation.
- A shared continuation resolver for target-agent, source-handoff, task, and provenance inference.
- `src/checkpoint_cli/continuation.py` as the home for continuation resolver, detection, provenance, and named errors.
- Conservative current-agent detection with predictable fallback behavior.
- Visible inference provenance in the generated continuation output.
- `checkpoint detect-agent` as a small diagnostic helper for current-agent detection.
- Allowlisted, non-secret `checkpoint detect-agent` clue output.
- `--from`, `--for`, `--task`, and `--output` flags for ambiguous or scripted cases.
- Plain `checkpoint continue` recovery from latest handoff and active task.
- First-run continuation output when no handoff exists yet.
- Secret redaction across generated continuation output from all source files.
- An end-to-end demo-style test for the handoff-to-continue agent switch loop.
- Resolver matrix tests for source inference, target fallback, task ambiguity, missing handoff, provenance, and named failure states.
- Named resolver errors or typed failure states for ambiguous tasks, missing tasks, missing source handoffs, and output-write failures.
- All-or-nothing pack generation before stdout or `--output` write.
- Sanitized local `continue` events in `.contextos/state/events.jsonl`.
- Helpful error messages when multiple active tasks exist and no task can be inferred.

## Constraints

- Keep all state local.
- Keep Markdown as the source of truth.
- Do not build sync.
- Do not add embeddings.
- Do not add Tree-sitter.
- Do not add cloud services.
- Do not add UI.
- Do not add browser automation.
- Do not add MCP dependency.
- Do not build an agent runtime.
- Never store secrets in generated handoffs or continuation packs.

## Relevant Files

- `src/checkpoint_cli/cli.py`
- `src/checkpoint_cli/store.py`
- `tests/test_cli.py`
- `README.md`
- `.contextos/context/decisions.md`
- `/Users/bkakumar/.gstack/projects/contextos/bkakumar-unknown-design-20260601-092117.md`

## Definition of Done

- `checkpoint continue --from claude` emits a continuation pack using local project state.
- `checkpoint continue` uses the latest handoff when source is omitted.
- Continuation resolver, detection, provenance, and named errors live in `src/checkpoint_cli/continuation.py`.
- `checkpoint continue`, `checkpoint detect-agent`, and tests rely on the shared continuation resolver rather than duplicated inference logic.
- Current-agent detection is conservative and visible in fallback cases.
- Continuation output shows the inferred source, target, task, and fallback reasons.
- `checkpoint detect-agent` prints detected agent, fallback state, and non-secret detection clues.
- `checkpoint detect-agent` does not dump raw environment values; only allowlisted clues with safe or redacted values are printed.
- Initialized projects with no handoff get a useful continuation pack, missing-handoff provenance, and the next handoff command.
- Continuation packs redact token-shaped secrets from project context, task files, decisions, user profile, and handoff content.
- An end-to-end test creates a handoff, runs `checkpoint continue --from <agent>`, and verifies the next-agent continuation pack.
- Resolver matrix tests cover source inference, target fallback, task ambiguity, missing handoff, missing task, provenance, and named failure states.
- CLI rescues named resolver failures and prints exact next-step commands.
- `checkpoint continue --output` writes only after resolution, rendering, and redaction have succeeded.
- `checkpoint continue` appends sanitized local event metadata without logging pack content.
- Ambiguous task state asks for `--task` instead of guessing incorrectly.
- Output remains raw Markdown.
- Tests cover source inference, target fallback, multiple active tasks, missing handoff, raw Markdown output, and secret redaction.
- README documents `checkpoint continue` as the happy path and `handoff` / `resume` as primitives.

## Design Source

Approved /office-hours design:

`/Users/bkakumar/.gstack/projects/contextos/bkakumar-unknown-design-20260601-092117.md`

## Handoff Instructions

At the end, update this task status and write `.contextos/handoffs/latest.md` with what changed, files touched, tests run, blockers, decisions, next recommended agent, and continuation prompt.

## CEO Review Notes

- 2026-06-01: `/plan-ceo-review` began against the approved design doc.
- System audit found this checkout has no commits yet, no remote/base metadata, no stash entries, and no TODO/FIXME markers outside ignored starter/venv paths.
- Approach A approved: implement `checkpoint continue` as a thin orchestration command over existing resume/handoff/task primitives.
- Scope Expansion mode selected for `/plan-ceo-review`.
- Expansion accepted: visible inference provenance in `checkpoint continue` output.
- Expansion accepted: `checkpoint detect-agent` diagnostic helper.
- Expansion accepted: no-handoff-yet first-run continuation pack.
- Expansion accepted: continuation-wide secret redaction across all source files.
- Expansion accepted: end-to-end demo test for the agent switch loop.
- Expansion opt-in ceremony complete with five accepted expansions.
- CEO plan written: `/Users/bkakumar/.gstack/projects/contextos/ceo-plans/2026-06-01-hero-continue-command.md`.
- Spec review loop skipped because the available subagent tool requires an explicit user request for delegation.
- Temporal decision accepted: use explicit current-agent signals with safe fallback (`--for`, `CONTEXTOS_AGENT`, known non-secret env clues, generic fallback).
- Architecture decision accepted: use a shared continuation resolver for inference and provenance.
- Error/rescue decision accepted: use named resolver errors or typed failure states with exact CLI recovery messages.
- Security decision accepted: `checkpoint detect-agent` prints only allowlisted safe clues, never a raw environment dump.
- Data-flow decision accepted: generate and redact the full continuation pack before printing or writing.
- Code-quality decision accepted: add `src/checkpoint_cli/continuation.py` for resolver/detection/provenance/errors instead of overloading `store.py` or `cli.py`.
- Test decision accepted: add resolver matrix tests plus CLI happy/error-path tests.
- Performance review: no issue if `continue` stays scoped to `.contextos/` files and avoids broad repo scans.
- Observability decision accepted: append sanitized local `continue` events to `.contextos/state/events.jsonl`.
- Deployment review: no migrations, services, feature flags, or rollout sequencing needed for this local CLI change.
- Long-term review: keep session routing, cross-agent timelines, sync, dashboards, and agent runtime behavior out of TASK-004.
- Design/UX review skipped: no UI scope.
- CEO review completed with 0 unresolved decisions and 0 critical gaps.
- Engineering review completed with 0 unresolved decisions and 0 critical gaps.
- Eng review test plan written: `/Users/bkakumar/.gstack/projects/contextos/bkakumar-main-eng-review-test-plan-20260601-120543.md`.
- 2026-06-01: Implemented `checkpoint continue` as thin orchestration over resume/handoff/task state.
- 2026-06-01: Added shared continuation resolver, conservative agent detection, provenance output, first-run/no-handoff pack behavior, named resolver errors, all-or-nothing output writing, final redaction, and sanitized `continue.generated` events.
- 2026-06-01: Added `checkpoint detect-agent` with allowlisted safe clue output.
- 2026-06-01: Updated README happy path to make `checkpoint continue` primary and `handoff` / `resume` primitives secondary.
- 2026-06-01: Added CLI and resolver tests covering happy paths, source/target/task inference, no-handoff first run, missing/ambiguous tasks, missing source handoff, output write failure, redaction, safe detection clues, sanitized events, and environment fallback.
- 2026-06-01: Verification passed with `.venv/bin/pytest` (14 passed) plus manual smoke tests for `checkpoint continue --root /Users/bkakumar/contextos --for codex --task TASK-004` and `checkpoint detect-agent`.
