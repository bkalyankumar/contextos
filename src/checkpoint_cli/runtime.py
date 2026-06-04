from __future__ import annotations

import ast
import hashlib
import json
import re
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, cast

from .store import (
    SECRET_PATTERNS,
    ProjectPaths,
    StoreFilesystemError,
    append_event,
    create_handoff,
    ensure_dir,
    list_active_tasks,
    markdown_section,
    now_iso,
    read_text,
    redact_secrets,
    safe_write,
    task_file,
    user_context_dir,
)

VALID_GUARD_ACTIONS = {"startup", "before_edit", "scope_change", "final_answer", "finalize"}
VALID_STEER_CLASSES = {"scope_constraint", "validation_change", "strategy_change", "cancellation", "side_comment"}
INDEX_EXTENSIONS = {
    ".py": "python",
    ".md": "markdown",
    ".rst": "text",
    ".toml": "toml",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".json": "json",
    ".ini": "ini",
    ".cfg": "ini",
    ".txt": "text",
}


@dataclass(frozen=True)
class FailureRecord:
    fingerprint: str
    command: str
    exit_code: str
    message: str
    file: str
    phase: str
    status: str
    resolution: str
    created_at: str


@dataclass(frozen=True)
class StrategyRecord:
    task_id: str
    task_type: str
    files: list[str]
    commands: list[str]
    outcome: str
    summary: str
    created_at: str


@dataclass(frozen=True)
class ExecutionContract:
    task_id: str | None
    target_agent: str
    first_action: str
    edit_scope: list[str]
    expected_files: list[str]
    canonical_validation: str
    expected_evidence: str
    finalize_instruction: str
    created_at: str


@dataclass(frozen=True)
class ContractCompliance:
    status: str
    reason: str
    expected_files: list[str]
    observed_files: list[str]
    canonical_validation: str
    tests_run: str
    created_at: str


@dataclass(frozen=True)
class RepoMapEntry:
    path: str
    language: str
    symbols: list[str]
    headings: list[str]
    tokens: list[str]
    size: int


def _json_default(value: object) -> object:
    if isinstance(value, Path):
        return str(value)
    return value


def write_json(path: Path, payload: dict[str, Any]) -> None:
    safe_write(path, json.dumps(payload, indent=2, sort_keys=True, default=_json_default), overwrite=True)


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    ensure_dir(path.parent)
    try:
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(payload, sort_keys=True, default=_json_default) + "\n")
    except OSError as exc:
        raise StoreFilesystemError(f"Could not append `{path}`: {exc.strerror or exc}.") from exc


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            rows.append(value)
    return rows


def runtime_paths(paths: ProjectPaths) -> dict[str, Path]:
    return {
        "memory": paths.contextos / "memory",
        "failures": paths.contextos / "memory" / "failures.jsonl",
        "strategies": paths.contextos / "memory" / "strategies.jsonl",
        "areas": paths.contextos / "memory" / "areas.json",
        "state": paths.contextos / "state",
        "latest_contract": paths.contextos / "state" / "latest-contract.json",
        "contract_compliance": paths.contextos / "state" / "contract-compliance.jsonl",
        "execution_summary": paths.contextos / "state" / "latest-execution-summary.md",
        "reports": paths.contextos / "reports",
        "continuity_view": paths.contextos / "reports" / "continuity-view.md",
        "continuity_map": paths.contextos / "reports" / "continuity-map.mmd",
        "repo_map": paths.contextos / "repo-map",
        "repo_map_manifest": paths.contextos / "repo-map" / "manifest.json",
        "repo_map_index": paths.contextos / "repo-map" / "index.json",
        "repo_map_status": paths.contextos / "repo-map" / "status.json",
    }


def latest_task_id(paths: ProjectPaths) -> str | None:
    contract = load_latest_contract(paths)
    if contract and contract.task_id:
        return contract.task_id
    tasks = list_active_tasks(paths)
    if len(tasks) == 1:
        return tasks[0].stem
    return None


def ensure_runtime_dirs(paths: ProjectPaths) -> None:
    for key in ["memory", "state", "reports", "repo_map"]:
        ensure_dir(runtime_paths(paths)[key])


def split_csv(value: str) -> list[str]:
    return [redact_secrets(item.strip()) for item in value.split(",") if item.strip()]


def parse_relevant_file_lines(text: str) -> list[str]:
    files: list[str] = []
    for section_name in ["Relevant Files", "Files Changed"]:
        section = markdown_section(text, section_name)
        for line in section.splitlines():
            match = re.search(r"`([^`]+)`", line)
            if match:
                files.append(match.group(1).strip())
            elif line.strip().startswith("- "):
                files.append(line.strip()[2:].strip())
    return sorted(dict.fromkeys(item for item in files if item and item.lower() != "none recorded"))


def first_nonempty_section(text: str, headings: list[str], default: str) -> str:
    for heading in headings:
        value = markdown_section(text, heading)
        if value:
            return value
    return default


def infer_task_type(task_text: str, summary: str) -> str:
    source = f"{task_text}\n{summary}".lower()
    if any(word in source for word in ["bug", "fix", "debug", "failure", "error"]):
        return "debug"
    if any(word in source for word in ["plan", "design", "architecture"]):
        return "planning"
    if any(word in source for word in ["launch", "release", "publish"]):
        return "release"
    return "implementation"


def update_active_task_state(
    paths: ProjectPaths,
    *,
    task_id: str,
    status: str,
    summary: str,
    files: list[str],
    tests: str,
    blockers: str,
    next_action: str,
) -> None:
    target = task_file(paths, task_id)
    if not target:
        target = paths.tasks_active_dir / f"{task_id}.md"
        safe_write(target, f"# {task_id}\n\n", overwrite=False)
    current = read_text(target)
    update = f"""

## Latest Runtime State

Status: {redact_secrets(status)}
Updated: {now_iso()}

### Hypothesis

{redact_secrets(summary) or 'No current hypothesis recorded.'}

### Relevant Files

{chr(10).join(f'- `{item}`' for item in files) if files else '- No files recorded.'}

### Verified Items

{redact_secrets(tests) or 'No verification recorded.'}

### Unverified Assumptions

- None recorded.

### Discarded Paths

- None recorded.

### Next Action

{redact_secrets(next_action) or 'Continue from the latest handoff.'}

### Recommended Commands

{redact_secrets(tests) if tests else 'No command recorded.'}

### Risks

{redact_secrets(blockers) or 'No blockers recorded.'}
"""
    safe_write(target, f"{current.rstrip()}\n{update}", overwrite=True)


def create_execution_contract(paths: ProjectPaths, *, target_agent: str, task_id: str | None) -> ExecutionContract:
    task_path = task_file(paths, task_id)
    task_text = read_text(task_path, "") if task_path else ""
    files = parse_relevant_file_lines(task_text)[:5]
    canonical_validation = first_nonempty_section(
        task_text,
        ["Recommended Commands", "Definition of Done", "Verification", "Tests"],
        "Run the focused project checks for the task.",
    )
    first_action = first_nonempty_section(task_text, ["Next Action"], "Read the active task and latest handoff first.")
    contract = ExecutionContract(
        task_id=task_path.stem if task_path else task_id,
        target_agent=target_agent,
        first_action=redact_secrets(first_action),
        edit_scope=files or ["Use the active task's recorded scope."],
        expected_files=files[:3],
        canonical_validation=redact_secrets(canonical_validation),
        expected_evidence="Files changed, commands run, results, blockers, and next action recorded in finalize.",
        finalize_instruction="Run `checkpoint finalize` or `checkpoint handoff` before stopping.",
        created_at=now_iso(),
    )
    ensure_runtime_dirs(paths)
    write_json(runtime_paths(paths)["latest_contract"], asdict(contract))
    append_event(paths, {"type": "contract.created", "task_id": contract.task_id, "target_agent": target_agent})
    return contract


def load_latest_contract(paths: ProjectPaths) -> ExecutionContract | None:
    path = runtime_paths(paths)["latest_contract"]
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        return ExecutionContract(**payload)
    except (json.JSONDecodeError, TypeError):
        return None


def evaluate_contract(paths: ProjectPaths, *, files: list[str], tests: str) -> ContractCompliance:
    contract = load_latest_contract(paths)
    if not contract:
        return ContractCompliance(
            status="not_evaluated",
            reason="No latest execution contract exists.",
            expected_files=[],
            observed_files=files,
            canonical_validation="",
            tests_run=tests,
            created_at=now_iso(),
        )
    expected = contract.expected_files
    if not expected:
        file_status = "not_evaluated"
    else:
        observed_set = set(files)
        expected_set = set(expected)
        if expected_set.issubset(observed_set):
            file_status = "followed"
        elif observed_set & expected_set:
            file_status = "partially_followed"
        else:
            file_status = "ignored"
    validation_followed = bool(tests.strip()) and tests.strip().lower() not in {"not recorded", "none"}
    if file_status == "followed" and validation_followed:
        status = "followed"
    elif file_status in {"followed", "partially_followed"} or validation_followed:
        status = "partially_followed"
    elif file_status == "not_evaluated":
        status = "not_evaluated"
    else:
        status = "ignored"
    return ContractCompliance(
        status=status,
        reason=f"File scope {file_status}; validation {'recorded' if validation_followed else 'not recorded'}.",
        expected_files=expected,
        observed_files=files,
        canonical_validation=contract.canonical_validation,
        tests_run=redact_secrets(tests),
        created_at=now_iso(),
    )


def failure_fingerprint(command: str, message: str, file: str, phase: str) -> str:
    base = "|".join([command.strip(), message.strip(), file.strip(), phase.strip()])
    return hashlib.sha256(base.encode("utf-8")).hexdigest()[:16]


def area_id_for_file(path: str) -> str:
    clean = path.strip().strip("`")
    if not clean:
        return "unknown"
    parts = Path(clean).parts
    if len(parts) >= 2 and parts[0] in {"src", "tests", "docs", ".github"}:
        return "/".join(parts[:2])
    return parts[0] if parts else "unknown"


def refresh_area_memory(paths: ProjectPaths) -> dict[str, Any]:
    areas: dict[str, Counter[str]] = {}
    for row in read_jsonl(runtime_paths(paths)["failures"]):
        area = area_id_for_file(str(row.get("file", "")))
        areas.setdefault(area, Counter())["failures"] += 1
    for row in read_jsonl(runtime_paths(paths)["strategies"]):
        for file in row.get("files", []) if isinstance(row.get("files", []), list) else []:
            area = area_id_for_file(str(file))
            areas.setdefault(area, Counter())["strategies"] += 1
    payload = {
        "updated_at": now_iso(),
        "areas": {area: dict(counts) for area, counts in sorted(areas.items())},
    }
    write_json(runtime_paths(paths)["areas"], payload)
    return payload


def append_failure_memory(
    paths: ProjectPaths,
    *,
    command: str,
    exit_code: str,
    message: str,
    file: str,
    phase: str,
    status: str,
    resolution: str,
) -> FailureRecord | None:
    if not any([command.strip(), message.strip(), file.strip()]):
        return None
    record = FailureRecord(
        fingerprint=failure_fingerprint(command, message, file, phase),
        command=redact_secrets(command),
        exit_code=redact_secrets(exit_code),
        message=redact_secrets(message),
        file=redact_secrets(file),
        phase=phase or "unknown",
        status=status or "observed",
        resolution=redact_secrets(resolution),
        created_at=now_iso(),
    )
    append_jsonl(runtime_paths(paths)["failures"], asdict(record))
    return record


def append_strategy_memory(
    paths: ProjectPaths,
    *,
    task_id: str,
    task_text: str,
    summary: str,
    files: list[str],
    commands: list[str],
    outcome: str,
) -> StrategyRecord:
    record = StrategyRecord(
        task_id=task_id,
        task_type=infer_task_type(task_text, summary),
        files=files,
        commands=[redact_secrets(command) for command in commands],
        outcome=outcome,
        summary=redact_secrets(summary),
        created_at=now_iso(),
    )
    append_jsonl(runtime_paths(paths)["strategies"], asdict(record))
    return record


def write_execution_summary(
    paths: ProjectPaths,
    *,
    task_id: str,
    status: str,
    summary: str,
    files: list[str],
    tests: str,
    blockers: str,
    decisions: str,
    next_action: str,
    compliance: ContractCompliance,
) -> str:
    content = f"""# Latest Execution Summary

Created: {now_iso()}
Task: {task_id}
Status: {redact_secrets(status)}

## Summary

{redact_secrets(summary) or 'No summary recorded.'}

## Files Changed

{chr(10).join(f'- `{item}`' for item in files) if files else '- None recorded'}

## Tests Run

{redact_secrets(tests) or 'Not recorded.'}

## Blockers

{redact_secrets(blockers) or 'None recorded.'}

## Decisions

{redact_secrets(decisions) or 'None recorded.'}

## Next Action

{redact_secrets(next_action) or 'Continue from the latest handoff.'}

## Contract Compliance

Status: {compliance.status}

{compliance.reason}
"""
    safe_write(runtime_paths(paths)["execution_summary"], content, overwrite=True)
    return content


def finalize_execution(
    paths: ProjectPaths,
    *,
    from_agent: str,
    to_agent: str,
    task_id: str,
    status: str,
    summary: str,
    files: str,
    tests: str,
    blockers: str,
    decisions: str,
    next_action: str,
    failure_command: str,
    failure_exit_code: str,
    failure_message: str,
    failure_file: str,
    failure_phase: str,
    failure_status: str,
    failure_resolution: str,
) -> dict[str, Any]:
    ensure_runtime_dirs(paths)
    clean_files = split_csv(files)
    commands = [tests] if tests.strip() else []
    compliance = evaluate_contract(paths, files=clean_files, tests=tests)
    append_jsonl(runtime_paths(paths)["contract_compliance"], asdict(compliance))
    failure = append_failure_memory(
        paths,
        command=failure_command,
        exit_code=failure_exit_code,
        message=failure_message,
        file=failure_file,
        phase=failure_phase,
        status=failure_status,
        resolution=failure_resolution,
    )
    task_path = task_file(paths, task_id)
    task_text = read_text(task_path, "") if task_path else ""
    strategy = None
    if status.lower() in {"success", "done", "completed", "passed"}:
        strategy = append_strategy_memory(
            paths,
            task_id=task_id,
            task_text=task_text,
            summary=summary,
            files=clean_files,
            commands=commands,
            outcome=status,
        )
    refresh_area_memory(paths)
    write_execution_summary(
        paths,
        task_id=task_id,
        status=status,
        summary=summary,
        files=clean_files,
        tests=tests,
        blockers=blockers,
        decisions=decisions,
        next_action=next_action,
        compliance=compliance,
    )
    update_active_task_state(
        paths,
        task_id=task_id,
        status=status,
        summary=summary,
        files=clean_files,
        tests=tests,
        blockers=blockers,
        next_action=next_action,
    )
    handoff_path = create_handoff(
        paths,
        from_agent=from_agent,
        to_agent=to_agent,
        task_id=task_id,
        status=status,
        summary=summary,
        files_changed=clean_files,
        tests_run=tests,
        blockers=blockers,
        decisions=decisions,
        continuation_prompt=next_action,
    )
    append_event(
        paths,
        {
            "type": "execution.finalized",
            "task_id": task_id,
            "status": status,
            "from_agent": from_agent,
            "to_agent": to_agent,
            "contract_compliance": compliance.status,
            "failure_recorded": failure is not None,
            "strategy_recorded": strategy is not None,
        },
    )
    return {
        "handoff_path": handoff_path,
        "contract_compliance": asdict(compliance),
        "failure": asdict(failure) if failure else None,
        "strategy": asdict(strategy) if strategy else None,
    }


def history_records(paths: ProjectPaths, *, limit: int = 20, event_type: str | None = None) -> dict[str, Any]:
    records = read_jsonl(paths.events_file)
    if event_type:
        records = [record for record in records if record.get("type") == event_type]
    limited = list(reversed(records))[:limit]
    return {
        "status": "ok",
        "limit": limit,
        "event_type": event_type,
        "events": limited,
    }


def memory_records(paths: ProjectPaths, *, kind: str = "all", limit: int = 20) -> dict[str, Any]:
    normalized = normalize_memory_kind(kind)
    payload: dict[str, Any] = {"status": "ok", "kind": normalized, "limit": limit}
    if normalized in {"all", "failures"}:
        payload["failures"] = list(reversed(read_jsonl(runtime_paths(paths)["failures"])))[:limit]
    if normalized in {"all", "strategies"}:
        payload["strategies"] = list(reversed(read_jsonl(runtime_paths(paths)["strategies"])))[:limit]
    if normalized in {"all", "areas"}:
        areas_path = runtime_paths(paths)["areas"]
        if areas_path.exists():
            try:
                payload["areas"] = json.loads(areas_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                payload["areas"] = {"updated_at": None, "areas": {}}
        else:
            payload["areas"] = {"updated_at": None, "areas": {}}
    return payload


def search_memory(paths: ProjectPaths, *, query: str, kind: str = "all", limit: int = 20) -> dict[str, Any]:
    normalized = normalize_memory_kind(kind)
    query_tokens = set(tokens_for_text(query))
    matches: list[dict[str, Any]] = []
    if normalized in {"all", "failures"}:
        matches.extend(score_memory_rows("failure", read_jsonl(runtime_paths(paths)["failures"]), query_tokens))
    if normalized in {"all", "strategies"}:
        matches.extend(score_memory_rows("strategy", read_jsonl(runtime_paths(paths)["strategies"]), query_tokens))
    matches.sort(key=lambda item: (-int(item["score"]), str(item.get("created_at", ""))))
    return {
        "status": "ok",
        "query": redact_secrets(query),
        "kind": normalized,
        "matches": matches[:limit],
    }


def normalize_memory_kind(kind: str) -> str:
    normalized = kind.strip().lower()
    if normalized in {"failure", "failures"}:
        return "failures"
    if normalized in {"strategy", "strategies"}:
        return "strategies"
    if normalized in {"area", "areas"}:
        return "areas"
    return "all"


def score_memory_rows(kind: str, rows: list[dict[str, Any]], query_tokens: set[str]) -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []
    for row in rows:
        row_text = json.dumps(row, sort_keys=True, default=_json_default)
        score = len(query_tokens & set(tokens_for_text(row_text)))
        if score:
            matches.append({"kind": kind, "score": score, "record": row})
    return matches


def iter_indexable_files(root: Path) -> list[Path]:
    ignored_parts = {".git", ".contextos", ".venv", "__pycache__", "dist", "build", ".mypy_cache", ".pytest_cache"}
    files: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in ignored_parts for part in path.parts):
            continue
        if path.suffix.lower() in INDEX_EXTENSIONS or path.name in {"README", "Makefile"}:
            files.append(path)
    return sorted(files)


def tokens_for_text(text: str) -> list[str]:
    expanded = text.replace("_", " ").replace("-", " ")
    tokens = set(re.findall(r"[A-Za-z0-9_./-]{3,}", text.lower()))
    tokens.update(re.findall(r"[A-Za-z0-9./]{3,}", expanded.lower()))
    return sorted(tokens)[:200]


def python_symbols(text: str) -> list[str]:
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return []
    symbols: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
            symbols.append(node.name)
    return sorted(set(symbols))


def markdown_headings(text: str) -> list[str]:
    headings: list[str] = []
    for line in text.splitlines():
        if line.startswith("#"):
            headings.append(line.lstrip("#").strip())
    return headings[:50]


def build_repo_map(paths: ProjectPaths) -> dict[str, Any]:
    ensure_runtime_dirs(paths)
    entries: list[RepoMapEntry] = []
    for path in iter_indexable_files(paths.root):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        rel = str(path.relative_to(paths.root))
        language = INDEX_EXTENSIONS.get(path.suffix.lower(), "text")
        entries.append(
            RepoMapEntry(
                path=rel,
                language=language,
                symbols=python_symbols(text) if language == "python" else [],
                headings=markdown_headings(text) if language == "markdown" else [],
                tokens=tokens_for_text(f"{rel}\n{text}"),
                size=len(text.encode("utf-8")),
            )
        )
    manifest = {
        "root": str(paths.root),
        "refreshed_at": now_iso(),
        "files_indexed": len(entries),
        "symbols_indexed": sum(len(entry.symbols) for entry in entries),
        "headings_indexed": sum(len(entry.headings) for entry in entries),
        "provider": "stdlib",
    }
    index = {"entries": [asdict(entry) for entry in entries]}
    status = {
        **manifest,
        "status": "ok",
        "provider_available": True,
        "index_available": True,
        "query_available": True,
        "refresh_available": True,
    }
    write_json(runtime_paths(paths)["repo_map_manifest"], manifest)
    write_json(runtime_paths(paths)["repo_map_index"], index)
    write_json(runtime_paths(paths)["repo_map_status"], status)
    append_event(paths, {"type": "repo_map.refreshed", "files_indexed": len(entries)})
    return status


def repo_map_status(paths: ProjectPaths) -> dict[str, Any]:
    status_path = runtime_paths(paths)["repo_map_status"]
    if not status_path.exists():
        return {
            "status": "missing",
            "provider_available": True,
            "index_available": False,
            "query_available": False,
            "refresh_available": True,
            "files_indexed": 0,
            "symbols_indexed": 0,
        }
    try:
        return cast(dict[str, Any], json.loads(status_path.read_text(encoding="utf-8")))
    except json.JSONDecodeError:
        return {"status": "error", "index_available": False, "query_available": False, "refresh_available": True}


def query_repo_map(paths: ProjectPaths, query: str, *, limit: int = 5) -> dict[str, Any]:
    index_path = runtime_paths(paths)["repo_map_index"]
    if not index_path.exists():
        return {"query": query, "status": "missing", "matches": []}
    try:
        payload = json.loads(index_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"query": query, "status": "error", "matches": []}
    query_tokens = set(tokens_for_text(query))
    matches: list[dict[str, Any]] = []
    for entry in payload.get("entries", []):
        haystack = set(entry.get("tokens", []))
        symbol_hits = [symbol for symbol in entry.get("symbols", []) if symbol.lower() in query.lower()]
        heading_hits = [heading for heading in entry.get("headings", []) if heading.lower() in query.lower()]
        score = len(query_tokens & haystack) + (len(symbol_hits) * 3) + (len(heading_hits) * 2)
        if score:
            matches.append(
                {
                    "path": entry.get("path", ""),
                    "language": entry.get("language", ""),
                    "score": score,
                    "symbols": symbol_hits or entry.get("symbols", [])[:5],
                    "headings": heading_hits or entry.get("headings", [])[:5],
                }
            )
    matches.sort(key=lambda item: (-int(item["score"]), str(item["path"])))
    return {"query": query, "status": "ok", "matches": matches[:limit]}


def memory_counts(paths: ProjectPaths) -> dict[str, int]:
    return {
        "failures": len(read_jsonl(runtime_paths(paths)["failures"])),
        "strategies": len(read_jsonl(runtime_paths(paths)["strategies"])),
        "contract_compliance": len(read_jsonl(runtime_paths(paths)["contract_compliance"])),
    }


def latest_handoff_age_hours(paths: ProjectPaths) -> float | None:
    if not paths.latest_handoff.exists():
        return None
    try:
        mtime = datetime.fromtimestamp(paths.latest_handoff.stat().st_mtime, tz=timezone.utc)
    except OSError:
        return None
    return (datetime.now(timezone.utc) - mtime).total_seconds() / 3600


def doctor_report(paths: ProjectPaths) -> dict[str, Any]:
    counts = memory_counts(paths)
    map_status = repo_map_status(paths)
    active_tasks = list_active_tasks(paths)
    handoff_age = latest_handoff_age_hours(paths)
    checks: list[dict[str, Any]] = []

    def add(name: str, status: str, detail: str) -> None:
        checks.append({"name": name, "status": status, "detail": detail})

    add("contextos", "ok" if paths.contextos.exists() else "error", "project memory exists" if paths.contextos.exists() else "run checkpoint init")
    add("latest_handoff", "ok" if paths.latest_handoff.exists() else "warning", f"age_hours={handoff_age:.1f}" if handoff_age is not None else "missing")
    add("active_tasks", "ok" if active_tasks else "warning", f"{len(active_tasks)} active task(s)")
    add("user_profile", "ok" if (user_context_dir() / "about-me.md").exists() else "warning", str(user_context_dir() / "about-me.md"))
    add("failure_memory", "ok" if counts["failures"] else "warning", f"{counts['failures']} failure record(s)")
    add("strategy_memory", "ok" if counts["strategies"] else "warning", f"{counts['strategies']} strategy record(s)")
    add("repo_map", "ok" if map_status.get("index_available") else "warning", map_status.get("status", "unknown"))
    add("contract", "ok" if load_latest_contract(paths) else "warning", "latest contract exists" if load_latest_contract(paths) else "no latest contract")
    secret_hits = scan_redaction_risk(paths)
    add("redaction_risk", "warning" if secret_hits else "ok", f"{len(secret_hits)} possible secret marker(s)")
    overall = "error" if any(check["status"] == "error" for check in checks) else "warning" if any(check["status"] == "warning" for check in checks) else "ok"
    return {
        "status": overall,
        "created_at": now_iso(),
        "root": str(paths.root),
        "checks": checks,
        "memory_counts": counts,
        "repo_map": map_status,
        "recommended_actions": recommended_actions(checks),
    }


def recommended_actions(checks: list[dict[str, Any]]) -> list[str]:
    actions: list[str] = []
    for check in checks:
        if check["status"] == "ok":
            continue
        name = check["name"]
        if name == "contextos":
            actions.append("Run `checkpoint init`.")
        elif name == "repo_map":
            actions.append("Run `checkpoint map refresh`.")
        elif name == "contract":
            actions.append("Run `checkpoint resume` or `checkpoint continue` before implementation.")
        elif name == "failure_memory":
            actions.append("Use `checkpoint finalize --failure-message ...` after failed commands.")
        elif name == "strategy_memory":
            actions.append("Use `checkpoint finalize --status success` after successful work.")
        elif name == "redaction_risk":
            actions.append("Review local ContextOS files and remove secrets before sharing packs.")
    return sorted(set(actions))


def scan_redaction_risk(paths: ProjectPaths) -> list[str]:
    hits: list[str] = []
    if not paths.contextos.exists():
        return hits
    for path in paths.contextos.rglob("*"):
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if any(pattern.search(text) for pattern in SECRET_PATTERNS):
            hits.append(str(path.relative_to(paths.root)))
    return hits[:20]


def guard_report(paths: ProjectPaths, *, action: str) -> dict[str, Any]:
    normalized = action.strip().lower().replace("-", "_")
    if normalized not in VALID_GUARD_ACTIONS:
        normalized = "startup"
    doctor = doctor_report(paths)
    warnings = [check for check in doctor["checks"] if check["status"] != "ok"]
    severity = "ok"
    if any(check["status"] == "error" for check in warnings):
        severity = "blocker"
    elif warnings:
        severity = "warning"
    return {
        "action": normalized,
        "severity": severity,
        "warnings": warnings,
        "message": guard_message(normalized, severity),
        "recommended_actions": doctor["recommended_actions"],
    }


def guard_message(action: str, severity: str) -> str:
    if severity == "ok":
        return f"Continuity looks usable for {action}."
    if action in {"final_answer", "finalize"}:
        return "Refresh handoff/finalize evidence before ending if warnings matter."
    return "Continuity is usable as background evidence, but inspect warnings before relying on it."


def classify_steer_message(message: str, current_action: str) -> dict[str, Any]:
    text = message.lower()
    classification = "side_comment"
    if any(word in text for word in ["stop", "cancel", "pause", "don't continue", "do not continue"]):
        classification = "cancellation"
    elif any(word in text for word in ["don't touch", "do not edit", "only edit", "scope", "leave"]):
        classification = "scope_constraint"
    elif any(word in text for word in ["test", "verify", "run", "check", "validation"]):
        classification = "validation_change"
    elif any(word in text for word in ["instead", "approach", "strategy", "plan", "priority"]):
        classification = "strategy_change"
    if classification not in VALID_STEER_CLASSES:
        classification = "side_comment"
    return {
        "classification": classification,
        "current_action": current_action,
        "message": redact_secrets(message),
        "recommended_response": steer_recommendation(classification),
    }


def steer_recommendation(classification: str) -> str:
    return {
        "cancellation": "Stop current work and ask/confirm what should happen next.",
        "scope_constraint": "Apply the scope constraint before further edits.",
        "validation_change": "Update the validation plan and record it in the handoff.",
        "strategy_change": "Re-plan the next action before continuing implementation.",
        "side_comment": "Treat as context unless it conflicts with the active task.",
    }[classification]


def render_continuity_mermaid(paths: ProjectPaths, report: dict[str, Any]) -> str:
    task_count = len(list_active_tasks(paths))
    counts = memory_counts(paths)
    repo_map = repo_map_status(paths)
    return f"""flowchart TD
    A["Project: {paths.root.name}"] --> B["Active tasks: {task_count}"]
    A --> C["Latest handoff: {'yes' if paths.latest_handoff.exists() else 'missing'}"]
    A --> D["Failures: {counts['failures']}"]
    A --> E["Strategies: {counts['strategies']}"]
    A --> F["RepoMap: {repo_map.get('status', 'missing')}"]
    A --> G["Doctor: {report['status']}"]
"""


def render_continuity_view(paths: ProjectPaths) -> dict[str, Path]:
    ensure_runtime_dirs(paths)
    report = doctor_report(paths)
    mermaid = render_continuity_mermaid(paths, report)
    tasks = list_active_tasks(paths)
    counts = memory_counts(paths)
    map_status = repo_map_status(paths)
    content = f"""# ContextOS Continuity View

Generated: {now_iso()}
Project: `{paths.root}`

```mermaid
{mermaid.strip()}
```

## Overview

- Doctor status: `{report['status']}`
- Active tasks: {len(tasks)}
- Latest handoff: {'yes' if paths.latest_handoff.exists() else 'missing'}
- Failure records: {counts['failures']}
- Strategy records: {counts['strategies']}
- RepoMap: {map_status.get('status', 'missing')}

## Active Tasks

{chr(10).join(f'- `{task.relative_to(paths.root)}`' for task in tasks) if tasks else '- None recorded'}

## Latest Handoff

{redact_secrets(read_text(paths.latest_handoff, 'No latest handoff found.'))}

## Continuity Quality

{json.dumps(report, indent=2, sort_keys=True)}
"""
    report_paths = runtime_paths(paths)
    safe_write(report_paths["continuity_view"], redact_secrets(content), overwrite=True)
    safe_write(report_paths["continuity_map"], mermaid, overwrite=True)
    append_event(paths, {"type": "continuity_view.generated"})
    return {"view": report_paths["continuity_view"], "map": report_paths["continuity_map"]}


def json_output(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, default=_json_default)


def json_safe_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return cast(dict[str, Any], json.loads(json.dumps(payload, default=_json_default)))


def mcp_server(paths: ProjectPaths, *, profile: str) -> int:
    try:
        from mcp.server.fastmcp import FastMCP  # type: ignore[import-not-found]
    except ImportError:
        print(
            "MCP support is not installed. Install with `pip install 'checkpoint-cli[mcp]'`.",
            file=sys.stderr,
        )
        return 1

    app: Any = FastMCP("checkpoint")

    @app.tool()  # type: ignore[untyped-decorator]
    def checkpoint_doctor() -> dict[str, Any]:
        return doctor_report(paths)

    @app.tool()  # type: ignore[untyped-decorator]
    def checkpoint_guard(action: str = "startup") -> dict[str, Any]:
        return guard_report(paths, action=action)

    @app.tool()  # type: ignore[untyped-decorator]
    def checkpoint_repo_map_query(query: str, limit: int = 5) -> dict[str, Any]:
        return query_repo_map(paths, query, limit=limit)

    @app.resource("contextos://latest-handoff")  # type: ignore[untyped-decorator]
    def latest_handoff_resource() -> str:
        return redact_secrets(read_text(paths.latest_handoff, "No latest handoff found."))

    @app.resource("contextos://active-task")  # type: ignore[untyped-decorator]
    def active_task_resource() -> str:
        tasks = list_active_tasks(paths)
        if not tasks:
            return "No active task found."
        return redact_secrets(read_text(tasks[0]))

    if profile == "full":

        @app.tool()  # type: ignore[untyped-decorator]
        def checkpoint_finalize(
            from_agent: str,
            to_agent: str,
            task_id: str,
            status: str,
            summary: str,
        ) -> dict[str, Any]:
            return json_safe_payload(
                finalize_execution(
                    paths,
                    from_agent=from_agent,
                    to_agent=to_agent,
                    task_id=task_id,
                    status=status,
                    summary=summary,
                    files="",
                    tests="",
                    blockers="",
                    decisions="",
                    next_action="Continue from the latest handoff.",
                    failure_command="",
                    failure_exit_code="",
                    failure_message="",
                    failure_file="",
                    failure_phase="",
                    failure_status="",
                    failure_resolution="",
                )
            )

    app.run()
    return 0
