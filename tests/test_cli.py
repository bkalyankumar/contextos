from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
from typer.testing import CliRunner

from checkpoint_cli.cli import app
from checkpoint_cli.continuation import (
    AGENT_CLUE_ENV,
    AmbiguousTaskError,
    SourceHandoffNotFoundError,
    TaskNotFoundError,
    detect_current_agent,
    resolve_continuation,
)
from checkpoint_cli.store import ProjectPaths

runner = CliRunner()


def init_project_with_task(tmp_path, task_id="TASK-001"):
    result = runner.invoke(app, ["init", "--root", str(tmp_path)])
    assert result.exit_code == 0
    task_dir = tmp_path / ".contextos" / "tasks" / "active"
    task_path = task_dir / f"{task_id}.md"
    task_path.write_text(
        f"""# {task_id}

## Status

Ready

## Relevant Files

- `src/checkpoint_cli/cli.py`
""",
        encoding="utf-8",
    )
    return task_path


def test_setup_user_and_init_preserve_existing_files(tmp_path, monkeypatch):
    monkeypatch.setenv("CONTEXTOS_HOME", str(tmp_path / "home" / ".contextos"))

    result = runner.invoke(app, ["setup-user"])
    assert result.exit_code == 0
    assert (tmp_path / "home" / ".contextos" / "about-me.md").exists()

    result = runner.invoke(app, ["init", "--root", str(tmp_path)])
    assert result.exit_code == 0
    assert (tmp_path / ".contextos" / "context" / "project-summary.md").exists()
    assert (tmp_path / ".contextos" / "state" / "events.jsonl").exists()
    assert (tmp_path / "AGENTS.md").exists()
    assert (tmp_path / "CLAUDE.md").exists()

    project_summary = tmp_path / ".contextos" / "context" / "project-summary.md"
    project_summary.write_text("# Project Summary\n\nKeep me.\n", encoding="utf-8")

    result = runner.invoke(app, ["init", "--root", str(tmp_path)])
    assert result.exit_code == 0
    assert "Keep me." in project_summary.read_text(encoding="utf-8")
    assert "Existing files were preserved" in result.output


def test_setup_user_reports_filesystem_failures_without_traceback(tmp_path, monkeypatch):
    blocked = tmp_path / "blocked"
    blocked.write_text("not a directory", encoding="utf-8")
    monkeypatch.setenv("CONTEXTOS_HOME", str(blocked / ".contextos"))

    result = runner.invoke(app, ["setup-user"])

    assert result.exit_code == 1
    assert "Could not create directory" in result.output
    assert "CONTEXTOS_HOME" in result.output
    assert "Traceback" not in result.output


def test_init_reports_filesystem_failures_without_traceback(tmp_path):
    blocked = tmp_path / "blocked"
    blocked.write_text("not a directory", encoding="utf-8")

    result = runner.invoke(app, ["init", "--root", str(blocked / "repo")])

    assert result.exit_code == 1
    assert "Could not create directory" in result.output
    assert "--root" in result.output
    assert "Traceback" not in result.output


def test_status_lists_active_tasks(tmp_path):
    result = runner.invoke(app, ["init", "--root", str(tmp_path)])
    assert result.exit_code == 0
    task_dir = tmp_path / ".contextos" / "tasks" / "active"
    (task_dir / "TASK-001.md").write_text("# TASK-001\n\n## Status\n\nReady\n", encoding="utf-8")

    result = runner.invoke(app, ["status", "--root", str(tmp_path)])

    assert result.exit_code == 0
    assert "ContextOS Status" in result.output
    assert "Active tasks" in result.output
    assert ".contextos/tasks/active/TASK-001.md" in result.output


def test_status_fails_for_missing_root(tmp_path):
    missing_root = tmp_path / "missing"

    result = runner.invoke(app, ["status", "--root", str(missing_root)])

    assert result.exit_code == 1
    assert "project root does not exist" in result.output


def test_resume_outputs_raw_ordered_context_pack(tmp_path, monkeypatch):
    monkeypatch.setenv("CONTEXTOS_HOME", str(tmp_path / "home" / ".contextos"))
    result = runner.invoke(app, ["setup-user"])
    assert result.exit_code == 0
    result = runner.invoke(app, ["init", "--root", str(tmp_path)])
    assert result.exit_code == 0

    task_dir = tmp_path / ".contextos" / "tasks" / "active"
    (task_dir / "TASK-001.md").write_text(
        """# TASK-001

## Status

Ready

## Blockers

None.

## Relevant Files

- `pyproject.toml`
- `tests/test_cli.py`

## Definition of Done

- `pip install -e '.[dev]'` succeeds.
""",
        encoding="utf-8",
    )

    result = runner.invoke(app, ["resume", "--root", str(tmp_path), "--for", "codex", "--task", "TASK-001"])

    assert result.exit_code == 0
    assert "ContextOS Resume Pack" in result.output
    assert "## Current Task And Status" in result.output
    assert "## Current Blocker" in result.output
    assert "## Relevant Files" in result.output
    assert "`pip install -e '.[dev]'` succeeds." in result.output
    assert result.output.index("## Current Task And Status") < result.output.index("## Current Blocker")
    assert result.output.index("## Current Blocker") < result.output.index("## Non-Negotiable Constraints")
    assert result.output.index("## Relevant Files") < result.output.index("## Recent Handoff")


def test_resume_outputs_agent_specific_context_packs(tmp_path):
    init_project_with_task(tmp_path)

    cases = [
        ("claude", "planning", "Claude planning pack", "pressure-test scope"),
        ("codex", "implement", "Codex implementation pack", "Implement scoped changes"),
        ("claude-code", "debug", "Claude Code debug pack", "Reproduce first"),
        ("antigravity", "autonomous", "Antigravity autonomous task pack", "bounded task"),
    ]

    for agent, mode, pack_name, expected_focus in cases:
        result = runner.invoke(
            app,
            ["resume", "--root", str(tmp_path), "--for", agent, "--mode", mode, "--task", "TASK-001"],
        )

        assert result.exit_code == 0
        assert "## Agent-Specific Pack" in result.output
        assert f"Pack: {pack_name}" in result.output
        assert expected_focus in result.output
        assert "### Stop Conditions" in result.output


def test_resume_output_write_failure_is_named(tmp_path):
    init_project_with_task(tmp_path)

    result = runner.invoke(
        app,
        ["resume", "--root", str(tmp_path), "--for", "codex", "--task", "TASK-001", "--output", str(tmp_path)],
    )

    assert result.exit_code == 1
    assert "Could not write file" in result.output
    assert "writable" in result.output
    assert "Traceback" not in result.output


def test_handoff_writes_latest_timestamped_files_and_events(tmp_path):
    result = runner.invoke(app, ["init", "--root", str(tmp_path)])
    assert result.exit_code == 0

    handoff_args = [
        "handoff",
        "--root",
        str(tmp_path),
        "--from",
        "codex",
        "--to",
        "claude-code",
        "--task",
        "TASK-001",
        "--status",
        "in_progress",
        "--summary",
        "Implemented initial CLI behavior with token=abc123.",
        "--files",
        "src/checkpoint_cli/cli.py,tests/test_cli.py",
        "--tests",
        "pytest passed",
        "--continuation",
        "Continue by reviewing CLI edge cases.",
    ]

    first = runner.invoke(app, handoff_args)
    second = runner.invoke(app, handoff_args)

    assert first.exit_code == 0
    assert second.exit_code == 0
    latest = tmp_path / ".contextos" / "handoffs" / "latest.md"
    latest_text = latest.read_text(encoding="utf-8")
    assert "codex -> claude-code" in latest_text
    assert "token [REDACTED]" in latest_text
    assert "abc123" not in latest_text

    handoff_files = sorted((tmp_path / ".contextos" / "handoffs" / "codex").glob("HOFF-*.md"))
    assert len(handoff_files) == 2

    events = [
        json.loads(line)
        for line in (tmp_path / ".contextos" / "state" / "events.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert events[-1]["type"] == "handoff.created"
    assert events[-1]["to_agent"] == "claude-code"


def test_handoff_reports_filesystem_failures_without_traceback(tmp_path):
    init_project_with_task(tmp_path)
    blocked_agent_dir = tmp_path / ".contextos" / "handoffs" / "codex"
    blocked_agent_dir.write_text("not a directory", encoding="utf-8")

    result = runner.invoke(
        app,
        [
            "handoff",
            "--root",
            str(tmp_path),
            "--from",
            "codex",
            "--to",
            "claude-code",
            "--task",
            "TASK-001",
            "--summary",
            "Done.",
        ],
    )

    assert result.exit_code == 1
    assert "Could not create directory" in result.output
    assert "writable" in result.output
    assert "Traceback" not in result.output


def test_continue_from_source_to_target_emits_provenance_and_pack(tmp_path):
    init_project_with_task(tmp_path)
    handoff = runner.invoke(
        app,
        [
            "handoff",
            "--root",
            str(tmp_path),
            "--from",
            "claude",
            "--to",
            "codex",
            "--task",
            "TASK-001",
            "--summary",
            "Planning complete.",
        ],
    )
    assert handoff.exit_code == 0

    result = runner.invoke(app, ["continue", "--root", str(tmp_path), "--from", "claude", "--for", "codex"])

    assert result.exit_code == 0
    assert "ContextOS Resume Pack" in result.output
    assert "## Continuation Provenance" in result.output
    assert "target_agent=codex (--for, confidence=explicit)" in result.output
    assert "source_agent=claude (resolved from local handoff)" in result.output
    assert "task_id=TASK-001 (inferred)" in result.output
    assert "## Recent Handoff" in result.output


def test_plain_continue_uses_latest_handoff_task_and_detected_agent(tmp_path, monkeypatch):
    monkeypatch.setenv("CONTEXTOS_AGENT", "codex")
    init_project_with_task(tmp_path, task_id="TASK-004")
    handoff = runner.invoke(
        app,
        [
            "handoff",
            "--root",
            str(tmp_path),
            "--from",
            "claude-code",
            "--to",
            "codex",
            "--task",
            "TASK-004",
            "--summary",
            "Debugged the plan.",
        ],
    )
    assert handoff.exit_code == 0

    result = runner.invoke(app, ["continue", "--root", str(tmp_path)])

    assert result.exit_code == 0
    assert "target_agent=codex (CONTEXTOS_AGENT, confidence=high)" in result.output
    assert "source_agent=claude-code (resolved from local handoff)" in result.output
    assert "task_id=TASK-004 (inferred)" in result.output


def test_continue_first_run_without_handoff_is_useful(tmp_path):
    init_project_with_task(tmp_path)

    result = runner.invoke(app, ["continue", "--root", str(tmp_path), "--for", "codex"])

    assert result.exit_code == 0
    assert "## First Run / No Handoff Yet" in result.output
    assert "No previous handoff was found" in result.output
    assert "checkpoint handoff --from codex --task TASK-001" in result.output


def test_continue_requires_task_when_multiple_active_tasks_and_no_handoff(tmp_path):
    init_project_with_task(tmp_path, task_id="TASK-001")
    task_dir = tmp_path / ".contextos" / "tasks" / "active"
    (task_dir / "TASK-002.md").write_text("# TASK-002\n\n## Status\n\nReady\n", encoding="utf-8")

    result = runner.invoke(app, ["continue", "--root", str(tmp_path), "--for", "codex"])

    assert result.exit_code == 1
    assert "Multiple active tasks found" in result.output
    assert "checkpoint continue --task <TASK-ID>" in result.output


def test_continue_reports_missing_task_and_source_handoff(tmp_path):
    init_project_with_task(tmp_path)

    missing_task = runner.invoke(app, ["continue", "--root", str(tmp_path), "--for", "codex", "--task", "TASK-404"])
    missing_source = runner.invoke(app, ["continue", "--root", str(tmp_path), "--from", "claude", "--for", "codex"])

    assert missing_task.exit_code == 1
    assert "No active task matched `TASK-404`" in missing_task.output
    assert "pass an existing task" in missing_task.output
    assert missing_source.exit_code == 1
    assert "No handoff found for source agent `claude`" in missing_source.output
    assert "checkpoint handoff --from <agent>" in missing_source.output


def test_continue_redacts_secrets_from_all_pack_sources(tmp_path, monkeypatch):
    monkeypatch.setenv("CONTEXTOS_HOME", str(tmp_path / "home" / ".contextos"))
    setup = runner.invoke(app, ["setup-user"])
    assert setup.exit_code == 0
    (tmp_path / "home" / ".contextos" / "about-me.md").write_text("api_key=profile-secret\n", encoding="utf-8")
    init_project_with_task(tmp_path)
    (tmp_path / ".contextos" / "context" / "decisions.md").write_text("token=decision-secret\n", encoding="utf-8")
    (tmp_path / ".contextos" / "tasks" / "active" / "TASK-001.md").write_text(
        "# TASK-001\n\npassword=task-secret\n",
        encoding="utf-8",
    )

    result = runner.invoke(app, ["continue", "--root", str(tmp_path), "--for", "codex"])

    assert result.exit_code == 0
    assert "profile-secret" not in result.output
    assert "decision-secret" not in result.output
    assert "task-secret" not in result.output
    assert "[REDACTED]" in result.output


def test_continue_output_write_failure_is_named_and_no_event_payload_leaks(tmp_path):
    init_project_with_task(tmp_path)

    result = runner.invoke(app, ["continue", "--root", str(tmp_path), "--for", "codex", "--output", str(tmp_path)])

    assert result.exit_code == 1
    assert "Could not write continuation pack" in result.output
    assert "Choose a writable `--output` path" in result.output
    events_text = (tmp_path / ".contextos" / "state" / "events.jsonl").read_text(encoding="utf-8")
    assert "continue.generated" not in events_text


def test_continue_output_writes_pack_and_sanitized_event(tmp_path):
    init_project_with_task(tmp_path)
    output = tmp_path / "pack.md"

    result = runner.invoke(app, ["continue", "--root", str(tmp_path), "--for", "codex", "--output", str(output)])

    assert result.exit_code == 0
    assert output.exists()
    assert "ContextOS Resume Pack" in output.read_text(encoding="utf-8")
    events = [
        json.loads(line)
        for line in (tmp_path / ".contextos" / "state" / "events.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert events[-1]["type"] == "continue.generated"
    assert events[-1]["target_agent"] == "codex"
    assert events[-1]["output"] == str(output)
    assert "ContextOS Resume Pack" not in json.dumps(events[-1])


def test_checkpoint_demo_script_runs_with_isolated_home(tmp_path):
    checkpoint_wrapper = tmp_path / "checkpoint-wrapper"
    checkpoint_wrapper.write_text(
        f"""#!{sys.executable}
from checkpoint_cli.cli import app

app()
""",
        encoding="utf-8",
    )
    checkpoint_wrapper.chmod(0o755)
    script = Path(__file__).resolve().parents[1] / "examples" / "checkpoint-demo.sh"
    env = {**os.environ, "CHECKPOINT_BIN": str(checkpoint_wrapper)}

    result = subprocess.run(
        [str(script), str(tmp_path / "demo-root")],
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )

    assert result.returncode == 0
    assert "## Continuation Provenance" in result.stdout
    assert "Tiny Notes is a small demo app" in result.stdout
    assert "DEC-001: Keep the first feature tiny" in result.stdout
    assert "Describe what this project is" not in result.stdout
    assert "List non-negotiable constraints" not in result.stdout
    assert (tmp_path / "demo-root" / "home" / ".contextos" / "about-me.md").exists()


def test_detect_agent_uses_allowlisted_safe_clues(monkeypatch):
    monkeypatch.setenv("CONTEXTOS_AGENT", "codex")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-secret")

    result = runner.invoke(app, ["detect-agent"])

    assert result.exit_code == 0
    assert "Detected agent: codex" in result.output
    assert "CONTEXTOS_AGENT: codex" in result.output
    assert "OPENAI_API_KEY" not in result.output
    assert "sk-secret" not in result.output


def test_show_fails_for_missing_file_and_directories(tmp_path):
    result = runner.invoke(app, ["init", "--root", str(tmp_path)])
    assert result.exit_code == 0

    missing = runner.invoke(app, ["show", "missing.md", "--root", str(tmp_path)])
    directory = runner.invoke(app, ["show", ".contextos", "--root", str(tmp_path)])

    assert missing.exit_code == 1
    assert "file not found" in missing.output
    assert directory.exit_code == 1
    assert "path is not a file" in directory.output


def test_resolver_matrix_named_failures_and_fallback(tmp_path, monkeypatch):
    monkeypatch.delenv("CONTEXTOS_AGENT", raising=False)
    for env_name in AGENT_CLUE_ENV:
        monkeypatch.delenv(env_name, raising=False)
    init_project_with_task(tmp_path)
    paths = ProjectPaths(root=tmp_path)

    context = resolve_continuation(paths, source_agent=None, target_agent=None, task_id="TASK-001")
    assert context.target_agent == "generic"
    assert context.detection.fallback is True
    assert context.handoff_missing is True

    with pytest.raises(TaskNotFoundError):
        resolve_continuation(paths, source_agent=None, target_agent="codex", task_id="TASK-404")

    with pytest.raises(SourceHandoffNotFoundError):
        resolve_continuation(paths, source_agent="claude", target_agent="codex", task_id="TASK-001")

    (tmp_path / ".contextos" / "tasks" / "active" / "TASK-002.md").write_text("# TASK-002\n", encoding="utf-8")
    with pytest.raises(AmbiguousTaskError):
        resolve_continuation(paths, source_agent=None, target_agent="codex", task_id=None)

    detection = detect_current_agent(environ={"CODEX_SANDBOX": "sandboxed"})
    assert detection.agent == "codex"
    assert detection.clues[0].value == "present"
