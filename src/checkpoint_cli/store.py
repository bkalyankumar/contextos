from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import json
import os
import re
from typing import Iterable

from .templates import AGENTS_MD, CLAUDE_MD, PROJECT_CONTEXT_FILES, USER_ABOUT_ME


SECRET_PATTERNS = [
    re.compile(r"(?i)\b(api[_-]?key|secret|token|password|private[_-]?token)\s*[:=]\s*([^\s`]+)"),
    re.compile(r"(?i)\b(bearer)\s+([A-Za-z0-9._~+/=-]+)"),
]


@dataclass(frozen=True)
class ProjectPaths:
    root: Path

    @property
    def contextos(self) -> Path:
        return self.root / ".contextos"

    @property
    def context_dir(self) -> Path:
        return self.contextos / "context"

    @property
    def plans_dir(self) -> Path:
        return self.contextos / "plans"

    @property
    def tasks_active_dir(self) -> Path:
        return self.contextos / "tasks" / "active"

    @property
    def tasks_completed_dir(self) -> Path:
        return self.contextos / "tasks" / "completed"

    @property
    def handoffs_dir(self) -> Path:
        return self.contextos / "handoffs"

    @property
    def sessions_dir(self) -> Path:
        return self.contextos / "sessions"

    @property
    def state_dir(self) -> Path:
        return self.contextos / "state"

    @property
    def events_file(self) -> Path:
        return self.state_dir / "events.jsonl"

    @property
    def latest_handoff(self) -> Path:
        return self.handoffs_dir / "latest.md"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def handoff_id(timestamp: datetime | None = None) -> str:
    timestamp = timestamp or datetime.now(timezone.utc)
    return f"HOFF-{timestamp.strftime('%Y%m%dT%H%M%S%fZ')}"


def user_context_dir() -> Path:
    return Path(os.environ.get("CONTEXTOS_HOME", Path.home() / ".contextos")).expanduser()


def safe_write(path: Path, content: str, overwrite: bool = False) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not overwrite:
        return False
    path.write_text(content.rstrip() + "\n", encoding="utf-8")
    return True


def read_text(path: Path, default: str = "") -> str:
    try:
        return path.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        return default


def redact_secrets(text: str) -> str:
    redacted = text
    for pattern in SECRET_PATTERNS:
        redacted = pattern.sub(lambda match: f"{match.group(1)} [REDACTED]", redacted)
    return redacted


def init_user(overwrite: bool = False) -> list[Path]:
    home = user_context_dir()
    written: list[Path] = []
    if safe_write(home / "about-me.md", USER_ABOUT_ME, overwrite=overwrite):
        written.append(home / "about-me.md")
    safe_write(home / "preferences.md", "# Preferences\n\n", overwrite=overwrite)
    safe_write(home / "tools.md", "# Tools\n\n", overwrite=overwrite)
    return written


def init_project(root: Path, overwrite: bool = False) -> list[Path]:
    paths = ProjectPaths(root=root)
    written: list[Path] = []

    for directory in [
        paths.context_dir,
        paths.plans_dir,
        paths.tasks_active_dir,
        paths.tasks_completed_dir,
        paths.handoffs_dir,
        paths.sessions_dir,
        paths.state_dir,
    ]:
        directory.mkdir(parents=True, exist_ok=True)

    for filename, content in PROJECT_CONTEXT_FILES.items():
        target = paths.context_dir / filename
        if safe_write(target, content, overwrite=overwrite):
            written.append(target)

    if safe_write(paths.plans_dir / "active-plan.md", "# Active Plan\n\n", overwrite=overwrite):
        written.append(paths.plans_dir / "active-plan.md")

    if safe_write(paths.sessions_dir / "current.md", "# Current Session\n\n", overwrite=overwrite):
        written.append(paths.sessions_dir / "current.md")

    if safe_write(paths.latest_handoff, "# Latest Handoff\n\nNo handoff recorded yet.\n", overwrite=overwrite):
        written.append(paths.latest_handoff)

    if safe_write(root / "AGENTS.md", AGENTS_MD, overwrite=overwrite):
        written.append(root / "AGENTS.md")

    if safe_write(root / "CLAUDE.md", CLAUDE_MD, overwrite=overwrite):
        written.append(root / "CLAUDE.md")

    paths.events_file.parent.mkdir(parents=True, exist_ok=True)
    paths.events_file.touch(exist_ok=True)
    append_event(paths, {"type": "project.initialized"})
    return written


def append_event(paths: ProjectPaths, event: dict) -> None:
    paths.events_file.parent.mkdir(parents=True, exist_ok=True)
    payload = {"created_at": now_iso(), **event}
    with paths.events_file.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, sort_keys=True) + "\n")


def list_active_tasks(paths: ProjectPaths) -> list[Path]:
    if not paths.tasks_active_dir.exists():
        return []
    return sorted(paths.tasks_active_dir.glob("*.md"))


def task_file(paths: ProjectPaths, task_id: str | None) -> Path | None:
    if not task_id:
        tasks = list_active_tasks(paths)
        return tasks[0] if tasks else None
    candidates = [
        paths.tasks_active_dir / f"{task_id}.md",
        paths.tasks_active_dir / f"{task_id.upper()}.md",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    matches = sorted(paths.tasks_active_dir.glob(f"*{task_id}*.md"))
    return matches[0] if matches else None


def create_handoff(
    paths: ProjectPaths,
    *,
    from_agent: str,
    to_agent: str,
    task_id: str,
    status: str,
    summary: str,
    files_changed: Iterable[str],
    tests_run: str,
    blockers: str,
    decisions: str,
    continuation_prompt: str,
) -> Path:
    created_at = now_iso()
    handoff_id_value = handoff_id()
    agent_dir = paths.handoffs_dir / from_agent
    agent_dir.mkdir(parents=True, exist_ok=True)
    target = agent_dir / f"{handoff_id_value}.md"
    clean_summary = redact_secrets(summary)
    clean_tests_run = redact_secrets(tests_run)
    clean_blockers = redact_secrets(blockers)
    clean_decisions = redact_secrets(decisions)
    clean_continuation = redact_secrets(continuation_prompt)
    clean_files = [redact_secrets(item.strip()) for item in files_changed if item.strip()]
    files_md = "\n".join(f"- `{item}`" for item in clean_files) or "- None recorded"
    content = f"""---
handoff_id: {handoff_id_value}
task_id: {task_id}
from_agent: {from_agent}
to_agent: {to_agent}
status: {status}
created_at: {created_at}
---

# Handoff: {from_agent} -> {to_agent}

## Current Task

{task_id}

## Current Status

{status}

## Summary

{clean_summary or 'No summary provided.'}

## Files Changed

{files_md}

## Tests Run

{clean_tests_run or 'Not recorded.'}

## Blockers

{clean_blockers or 'None recorded.'}

## Decisions

{clean_decisions or 'None recorded.'}

## Next Recommended Agent

{to_agent}

## Continuation Prompt

{clean_continuation or 'Continue from this handoff and inspect the active task file.'}
"""
    safe_write(target, content, overwrite=True)
    safe_write(paths.latest_handoff, content, overwrite=True)
    append_event(paths, {
        "type": "handoff.created",
        "handoff_id": handoff_id_value,
        "task_id": task_id,
        "from_agent": from_agent,
        "to_agent": to_agent,
        "status": status,
    })
    return target


def markdown_section(text: str, heading: str) -> str:
    lines = text.splitlines()
    heading_marker = f"## {heading}".casefold()
    collecting = False
    collected: list[str] = []
    for line in lines:
        normalized = line.strip().casefold()
        if normalized == heading_marker:
            collecting = True
            continue
        if collecting and normalized.startswith("## "):
            break
        if collecting:
            collected.append(line)
    return "\n".join(collected).strip()


def current_blocker(task_text: str, handoff_text: str) -> str:
    for heading in ["Blockers", "Current Blocker", "Current Blockers"]:
        blocker = markdown_section(task_text, heading) or markdown_section(handoff_text, heading)
        if blocker:
            return blocker
    return "None recorded."


def relevant_files(task_text: str) -> str:
    files = markdown_section(task_text, "Relevant Files")
    return files or "- No relevant files recorded in the active task."


def next_action(target_agent: str, task_id: str | None) -> str:
    task_label = task_id or "the active task"
    actions = {
        "codex": f"Continue implementing {task_label}, keep changes scoped, run the project checks, and leave a handoff.",
        "claude": f"Review {task_label}, refine the plan, and leave a handoff with decisions and next steps.",
        "claude-code": f"Debug {task_label} from the latest failing behavior, verify the fix, and leave a handoff.",
        "antigravity": f"Work autonomously on {task_label} within the active scope, stop on blockers, and leave artifacts.",
    }
    return actions.get(target_agent, f"Continue {task_label} using the context pack and leave a handoff before stopping.")


def generate_resume_pack(paths: ProjectPaths, *, target_agent: str, mode: str, task_id: str | None) -> str:
    user_profile = read_text(user_context_dir() / "about-me.md", "No user-level about-me.md found.")
    project_summary = read_text(paths.context_dir / "project-summary.md", "No project summary found.")
    architecture = read_text(paths.context_dir / "architecture.md", "No architecture context found.")
    constraints = read_text(paths.context_dir / "constraints.md", "No constraints found.")
    decisions = read_text(paths.context_dir / "decisions.md", "No decisions recorded.")
    active_plan = read_text(paths.plans_dir / "active-plan.md", "No active plan found.")
    handoff = read_text(paths.latest_handoff, "No latest handoff found.")
    task_path = task_file(paths, task_id)
    task_text = read_text(task_path, "No active task found.") if task_path else "No active task found."

    agent_guidance = {
        "codex": "Focus on implementation, tests, small safe changes, and writing a precise handoff before stopping.",
        "claude": "Focus on architecture, planning, tradeoffs, task decomposition, and continuation context.",
        "claude-code": "Focus on debugging, critical reasoning, minimal safe fixes, and verification.",
        "antigravity": "Focus on autonomous execution with strict scope, stop conditions, and required artifacts.",
    }.get(target_agent, "Use the context below to continue safely and leave a handoff before stopping.")

    return f"""# ContextOS Resume Pack

## Target Agent

{target_agent}

## Mode

{mode}

## Agent Guidance

{agent_guidance}

## Current Task And Status

{task_text}

## Current Blocker

{current_blocker(task_text, handoff)}

## Non-Negotiable Constraints

{constraints}

## Relevant Plan

{active_plan}

## Relevant Architecture

{architecture}

## Relevant Files

{relevant_files(task_text)}

## Recent Handoff

{handoff}

## Durable Decisions

{decisions}

## Project Summary

{project_summary}

## User Profile

{user_profile}

## Next Recommended Action

{next_action(target_agent, task_id)}

## Handoff Instructions

Update `.contextos/handoffs/latest.md` and the active task file. Include what changed, files modified, tests run, blockers, decisions, next recommended agent, and exact continuation prompt.
"""
