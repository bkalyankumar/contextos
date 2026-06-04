from __future__ import annotations

import os
import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path

from .store import (
    ProjectPaths,
    append_event,
    generate_resume_pack,
    list_active_tasks,
    read_text,
    redact_secrets,
    task_file,
)

KNOWN_AGENTS = {"antigravity", "claude", "claude-code", "codex", "cursor", "generic"}
AGENT_CLUE_ENV = {
    "CODEX_SANDBOX": "codex",
    "CODEX_SESSION_ID": "codex",
    "CLAUDECODE": "claude-code",
    "CLAUDE_CODE_SESSION": "claude-code",
    "ANTIGRAVITY_SESSION": "antigravity",
    "CURSOR_TRACE_ID": "cursor",
}
NO_HANDOFF_MARKERS = ("No handoff recorded yet.", "No latest handoff found.")


class ContinuationError(Exception):
    """Base class for user-correctable continuation failures."""

    recovery: str = "Run `checkpoint status` to inspect local ContextOS state."


class AmbiguousTaskError(ContinuationError):
    recovery = "Run `checkpoint continue --task <TASK-ID>` to choose the active task."


class TaskNotFoundError(ContinuationError):
    recovery = "Run `checkpoint status` and pass an existing task with `--task <TASK-ID>`."


class SourceHandoffNotFoundError(ContinuationError):
    recovery = "Run `checkpoint handoff --from <agent> ...` first, or omit `--from` to use the latest handoff."


class OutputWriteError(ContinuationError):
    recovery = "Choose a writable `--output` path or omit `--output` to print to stdout."


@dataclass(frozen=True)
class DetectionClue:
    name: str
    value: str


@dataclass(frozen=True)
class DetectionResult:
    agent: str
    source: str
    confidence: str
    fallback: bool
    clues: tuple[DetectionClue, ...] = ()


@dataclass(frozen=True)
class ResolvedHandoff:
    text: str
    path: Path | None
    source_agent: str
    task_id: str | None
    missing: bool = False


@dataclass(frozen=True)
class ContinuationContext:
    paths: ProjectPaths
    target_agent: str
    source_agent: str
    task_id: str | None
    handoff_path: Path | None
    handoff_missing: bool
    detection: DetectionResult
    provenance: tuple[str, ...] = field(default_factory=tuple)


def normalize_agent(value: str | None) -> str | None:
    if not value:
        return None
    normalized = value.strip().lower().replace("_", "-")
    aliases = {
        "claudecode": "claude-code",
        "claude-code-cli": "claude-code",
        "openai-codex": "codex",
    }
    normalized = aliases.get(normalized, normalized)
    return normalized if normalized in KNOWN_AGENTS else None


def detect_current_agent(
    explicit_agent: str | None = None,
    *,
    environ: Mapping[str, str] | None = None,
) -> DetectionResult:
    env = os.environ if environ is None else environ
    explicit = normalize_agent(explicit_agent)
    if explicit:
        return DetectionResult(
            agent=explicit,
            source="--for",
            confidence="explicit",
            fallback=False,
            clues=(DetectionClue("--for", explicit),),
        )

    env_agent = normalize_agent(env.get("CONTEXTOS_AGENT"))
    if env_agent:
        return DetectionResult(
            agent=env_agent,
            source="CONTEXTOS_AGENT",
            confidence="high",
            fallback=False,
            clues=(DetectionClue("CONTEXTOS_AGENT", env_agent),),
        )

    if "CONTEXTOS_AGENT" in env:
        return DetectionResult(
            agent="generic",
            source="fallback",
            confidence="low",
            fallback=True,
            clues=(DetectionClue("CONTEXTOS_AGENT", "unrecognized"),),
        )

    for env_name, agent in AGENT_CLUE_ENV.items():
        if env.get(env_name):
            return DetectionResult(
                agent=agent,
                source=env_name,
                confidence="medium",
                fallback=False,
                clues=(DetectionClue(env_name, "present"),),
            )

    return DetectionResult(
        agent="generic",
        source="fallback",
        confidence="low",
        fallback=True,
        clues=(DetectionClue("fallback", "no allowlisted agent clue found"),),
    )


def detect_agent_report(explicit_agent: str | None = None) -> str:
    detection = detect_current_agent(explicit_agent)
    clues = "\n".join(f"- {clue.name}: {clue.value}" for clue in detection.clues)
    return f"""# Checkpoint Agent Detection

Detected agent: {detection.agent}
Source: {detection.source}
Confidence: {detection.confidence}
Fallback: {'yes' if detection.fallback else 'no'}

## Safe Clues

{clues}
"""


def parse_frontmatter_value(text: str, key: str) -> str | None:
    if not text.startswith("---"):
        return None
    match = re.search(rf"(?m)^{re.escape(key)}:\s*(.+?)\s*$", text)
    return match.group(1).strip() if match else None


def is_missing_handoff(text: str) -> bool:
    return any(marker in text for marker in NO_HANDOFF_MARKERS)


def latest_handoff_for_source(paths: ProjectPaths, source_agent: str) -> Path | None:
    agent_dir = paths.handoffs_dir / source_agent
    if not agent_dir.exists():
        return None
    matches = sorted(agent_dir.glob("HOFF-*.md"))
    return matches[-1] if matches else None


def resolve_handoff(paths: ProjectPaths, source_agent: str | None) -> ResolvedHandoff:
    if source_agent:
        handoff_path = latest_handoff_for_source(paths, source_agent)
        if not handoff_path:
            raise SourceHandoffNotFoundError(f"No handoff found for source agent `{source_agent}`.")
        text = read_text(handoff_path)
        return ResolvedHandoff(
            text=text,
            path=handoff_path,
            source_agent=source_agent,
            task_id=parse_frontmatter_value(text, "task_id"),
        )

    text = read_text(paths.latest_handoff, "No latest handoff found.")
    if is_missing_handoff(text):
        return ResolvedHandoff(
            text=text,
            path=None,
            source_agent="none",
            task_id=None,
            missing=True,
        )

    return ResolvedHandoff(
        text=text,
        path=paths.latest_handoff,
        source_agent=parse_frontmatter_value(text, "from_agent") or "latest",
        task_id=parse_frontmatter_value(text, "task_id"),
    )


def resolve_task(paths: ProjectPaths, requested_task: str | None, handoff_task_id: str | None) -> str | None:
    if requested_task:
        path = task_file(paths, requested_task)
        if not path:
            raise TaskNotFoundError(f"No active task matched `{requested_task}`.")
        return path.stem

    if handoff_task_id and task_file(paths, handoff_task_id):
        return handoff_task_id

    tasks = list_active_tasks(paths)
    if len(tasks) == 1:
        return tasks[0].stem
    if len(tasks) > 1:
        task_labels = ", ".join(task.stem for task in tasks)
        raise AmbiguousTaskError(f"Multiple active tasks found: {task_labels}.")
    return None


def resolve_continuation(
    paths: ProjectPaths,
    *,
    source_agent: str | None,
    target_agent: str | None,
    task_id: str | None,
) -> ContinuationContext:
    detection = detect_current_agent(target_agent)
    handoff = resolve_handoff(paths, normalize_agent(source_agent) or source_agent)
    resolved_task = resolve_task(paths, task_id, handoff.task_id)

    provenance = [
        f"target_agent={detection.agent} ({detection.source}, confidence={detection.confidence})",
        f"source_agent={handoff.source_agent} ({'no handoff found yet' if handoff.missing else 'resolved from local handoff'})",
        f"task_id={resolved_task or 'none'} ({'explicit' if task_id else 'inferred'})",
    ]
    if detection.fallback:
        provenance.append("target fallback used; pass `--for <agent>` or set `CONTEXTOS_AGENT` for precision")
    if handoff.path:
        provenance.append(f"handoff_path={handoff.path}")

    return ContinuationContext(
        paths=paths,
        target_agent=detection.agent,
        source_agent=handoff.source_agent,
        task_id=resolved_task,
        handoff_path=handoff.path,
        handoff_missing=handoff.missing,
        detection=detection,
        provenance=tuple(provenance),
    )


def render_continuation_pack(context: ContinuationContext) -> str:
    pack = generate_resume_pack(
        context.paths,
        target_agent=context.target_agent,
        mode="implement",
        task_id=context.task_id,
    )
    provenance = "\n".join(f"- {item}" for item in context.provenance)
    first_run = ""
    if context.handoff_missing:
        task_flag = f" --task {context.task_id}" if context.task_id else " --task <TASK-ID>"
        first_run = f"""
## First Run / No Handoff Yet

No previous handoff was found. Use this pack to start from project memory and write the first durable handoff before stopping:

```bash
checkpoint handoff --from {context.target_agent}{task_flag} --status in_progress --summary "What changed"
```
"""

    return redact_secrets(
        pack.replace(
            "## Target Agent",
            f"## Continuation Provenance\n\n{provenance}{first_run}\n## Target Agent",
            1,
        )
    )


def generate_continuation_pack(
    paths: ProjectPaths,
    *,
    source_agent: str | None,
    target_agent: str | None,
    task_id: str | None,
) -> tuple[str, ContinuationContext]:
    context = resolve_continuation(
        paths,
        source_agent=source_agent,
        target_agent=target_agent,
        task_id=task_id,
    )
    from .runtime import create_execution_contract

    create_execution_contract(paths, target_agent=context.target_agent, task_id=context.task_id)
    return render_continuation_pack(context), context


def write_output_all_or_error(path: Path, content: str) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    except OSError as exc:
        raise OutputWriteError(f"Could not write continuation pack to `{path}`: {exc}") from exc


def append_continue_event(context: ContinuationContext, *, output: Path | None) -> None:
    append_event(
        context.paths,
        {
            "type": "continue.generated",
            "target_agent": context.target_agent,
            "source_agent": context.source_agent,
            "task_id": context.task_id,
            "handoff": str(context.handoff_path) if context.handoff_path else None,
            "output": str(output) if output else "stdout",
            "fallback": context.detection.fallback,
        },
    )
