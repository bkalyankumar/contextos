from __future__ import annotations

from typer.testing import CliRunner

from checkpoint_cli.cli import app

runner = CliRunner()


def test_init_status_resume_handoff(tmp_path, monkeypatch):
    monkeypatch.setenv("CONTEXTOS_HOME", str(tmp_path / "home" / ".contextos"))

    result = runner.invoke(app, ["setup-user"])
    assert result.exit_code == 0

    result = runner.invoke(app, ["init", "--root", str(tmp_path)])
    assert result.exit_code == 0
    assert (tmp_path / ".contextos" / "context" / "project-summary.md").exists()
    assert (tmp_path / "AGENTS.md").exists()

    task_dir = tmp_path / ".contextos" / "tasks" / "active"
    task_dir.mkdir(parents=True, exist_ok=True)
    (task_dir / "TASK-001.md").write_text("# TASK-001\n\n## Status\n\nReady\n", encoding="utf-8")

    result = runner.invoke(app, ["status", "--root", str(tmp_path)])
    assert result.exit_code == 0
    assert "Active tasks" in result.output

    result = runner.invoke(app, ["resume", "--root", str(tmp_path), "--for", "codex", "--task", "TASK-001"])
    assert result.exit_code == 0
    assert "ContextOS Resume Pack" in result.output
    assert "TASK-001" in result.output

    result = runner.invoke(
        app,
        [
            "handoff",
            "--root", str(tmp_path),
            "--from", "codex",
            "--to", "claude-code",
            "--task", "TASK-001",
            "--status", "in_progress",
            "--summary", "Implemented initial CLI behavior.",
            "--files", "src/checkpoint_cli/cli.py,tests/test_cli.py",
            "--tests", "pytest passed",
            "--continuation", "Continue by reviewing CLI edge cases.",
        ],
    )
    assert result.exit_code == 0
    latest = tmp_path / ".contextos" / "handoffs" / "latest.md"
    assert "codex -> claude-code" in latest.read_text(encoding="utf-8")
