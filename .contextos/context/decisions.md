# Decisions

## DEC-001: ContextOS should not position as generic AI memory

Reason: generic memory is already being claimed by products such as Mem0 and by tool-native memory features.

Decision: ContextOS positions as repo-native continuity infrastructure for AI-assisted software engineering.

## DEC-002: MVP is Markdown-first

Reason: readable files support trust, git workflows, portability, and easy agent consumption.

Decision: initial source of truth is `.contextos/` Markdown plus generated `AGENTS.md` / `CLAUDE.md`.

## DEC-003: Open-source local CLI and schema

Reason: adoption depends on becoming a standard local habit.

Decision: paid features begin at encrypted sync, teams, and governance.

## DEC-004: Agent handoff through ContextOS, not direct agent-to-agent memory

Reason: direct transfer between agents is brittle and vendor-specific.

Decision: each agent reads/writes canonical ContextOS state.

## DEC-005: Generated context packs are raw Markdown output

Reason: resume packs are meant to be copied between tools and must preserve literal Markdown text such as `.[dev]`, task checklists, and bracketed notes.

Decision: CLI commands that emit stored or generated context files should write raw text instead of Rich markup-rendered output.

## DEC-006: `checkpoint continue` is the hero command

Reason: developers switch between agents during real work and should not have to remember target-agent flags while context is already broken.

Decision: keep `handoff` and `resume` as explicit primitives, but make `checkpoint continue` the primary user-facing command. It should infer the current target agent when possible, read local handoff and task state, and emit the right continuation pack.

## DEC-007: `checkpoint continue` is thin orchestration for the MVP

Reason: the approved CEO review approach is to solve the agent-switch pain without building a local session router or agent runtime before the habit loop is proven.

Decision: implement `checkpoint continue` as a thin command over existing handoff, active task, and resume-pack primitives. Defer richer session routing, cross-agent timelines, and router state machinery until after the Markdown-first MVP proves the core loop.

## DEC-008: `checkpoint continue` should show inference provenance

Reason: inferred source handoffs, target agents, and tasks must be inspectable so the command feels trustworthy instead of magical.

Decision: include a concise provenance section in `checkpoint continue` output showing what was inferred, which inputs drove the inference, and when the command fell back to generic behavior or an explicit flag.

## DEC-009: Add `checkpoint detect-agent` for detection debugging

Reason: current-agent detection will depend on environment clues that vary across tools, shells, and future integrations.

Decision: include a small `checkpoint detect-agent` command in TASK-004. It should print the detected agent, confidence or fallback state, and the non-secret environment clues used, so detection bugs are reproducible without inspecting code.

## DEC-010: `checkpoint continue` should handle no-handoff projects

Reason: the hero command should not dead-end during the first-run moment, when a project may be initialized but no agent handoff has been written yet.

Decision: when no handoff exists, `checkpoint continue` should emit a useful first-run continuation pack from project context and active task state, clearly mark the missing handoff in provenance, and show the next command to create one.

## DEC-011: Redact secrets across generated continuation packs

Reason: `checkpoint continue` assembles text from project context, task files, decisions, handoffs, and user profile, so redaction only at handoff creation is not enough to uphold the no-secrets promise.

Decision: apply secret redaction to generated continuation output before printing or writing it. Tests should cover token-shaped secrets in non-handoff source files as well as handoff text.

## DEC-012: Add an end-to-end agent switch demo test

Reason: the core product promise is not a helper function; it is the full loop from one agent writing a handoff to the next agent continuing without manual recap.

Decision: TASK-004 should include an end-to-end test or demo fixture that creates a handoff, runs `checkpoint continue --from <agent>`, and verifies the next agent receives the expected high-signal continuation pack.

## DEC-013: Current-agent detection uses explicit signals with safe fallback

Reason: `checkpoint continue` should feel smart while staying predictable and debuggable in shells and agent wrappers with uneven environment signals.

Decision: support `--for`, `CONTEXTOS_AGENT`, a small allowlist of known non-secret tool environment clues, and generic fallback. Do not use aggressive process or terminal guessing in the MVP.

## DEC-014: Use a shared continuation resolver

Reason: `checkpoint continue`, `checkpoint detect-agent`, and tests must not each reimplement target-agent, source-handoff, task, and provenance inference.

Decision: add a small internal continuation resolver that returns one structured result for target agent, source handoff, task, provenance, and fallback state. CLI commands should render from that result rather than duplicating inference logic.

## DEC-015: Use named resolver errors for user-correctable failures

Reason: ambiguous tasks, missing task IDs, missing source handoffs, and output-write failures need precise user-facing recovery instructions, not generic Typer or filesystem errors.

Decision: add named resolver errors or equivalent typed failure states for `AmbiguousTaskError`, `TaskNotFoundError`, `SourceHandoffNotFoundError`, and `OutputWriteError`. The CLI should rescue them and print exact next-step commands.

## DEC-016: `detect-agent` only prints allowlisted safe clues

Reason: agent-detection diagnostics are likely to be pasted into chats, and raw environment dumps can expose credentials.

Decision: `checkpoint detect-agent` should print only allowlisted detection clue names and safe or redacted values. It must not dump the full process environment.

## DEC-017: Generate continuation packs all-or-nothing

Reason: `checkpoint continue --output` must not leave stale, partial, or unredacted files if resolution, rendering, redaction, or writing fails.

Decision: resolve context, render the full Markdown pack, apply final redaction, and only then print or write the output. A failed command should produce a clear error and no partial success message.

## DEC-018: Put continuation resolver code in `continuation.py`

Reason: agent detection, provenance, resolver errors, first-run behavior, and continue orchestration should not turn `store.py` into a mixed storage/rendering/orchestration module.

Decision: add `src/checkpoint_cli/continuation.py` for continuation resolver dataclasses, detection, provenance, and named errors. Keep `cli.py` thin and keep `store.py` focused on local file-store and rendering primitives.

## DEC-019: Add resolver matrix tests

Reason: the continuation resolver is the decision point for source, target, task, provenance, fallback, and user-correctable failures.

Decision: add table-style resolver tests covering source inference, target fallback, task ambiguity, missing handoff, missing task, no-handoff first-run behavior, provenance, and named failure states. Keep CLI tests for the user-facing happy path and error messages.

## DEC-020: Log sanitized local `continue` events

Reason: ContextOS needs a local continuity trail for debugging and future status/history views, but generated pack content and secrets must not be logged.

Decision: `checkpoint continue` should append a sanitized event to `.contextos/state/events.jsonl` with non-secret metadata such as command, target, source, task, fallback reason, output mode, and outcome. Do not log continuation pack content.

## DEC-021: Keep repo health checks tied to repo-owned surfaces

Reason: health checks should raise actionable repo issues instead of reporting machine-level or absent-surface failures.

Decision: configure typecheck, lint, test, and dead-code checks for the MVP. Keep shell health skipped until the repo contains shell scripts, and keep GBrain health skipped because it is machine-level rather than repo-level ContextOS scope.

## DEC-022: Do not broadly launch without an explicit open-source license

Reason: a public repository without a license is readable but does not give contributors and users clear permission to use, modify, or redistribute the code.

Decision: public launch preparation may proceed, but broad announcement waits until the maintainer chooses and commits an open-source license.
