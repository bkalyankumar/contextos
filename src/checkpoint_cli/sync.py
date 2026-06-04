from __future__ import annotations

import base64
import hashlib
import io
import json
import os
import urllib.error
import urllib.request
import zipfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, cast

from .store import ProjectPaths, StoreFilesystemError, append_event, ensure_dir, now_iso, safe_write

SYNC_EXTRA_HINT = "Sync encryption support is not installed. Install with `pip install 'checkpoint-cli[sync]'`."
SYNC_KEY_ENV = "CONTEXTOS_SYNC_KEY"


class SyncError(Exception):
    """User-facing sync failure."""


class SyncDependencyError(SyncError):
    """Raised when optional sync dependencies are missing."""


class SyncConfigError(SyncError):
    """Raised when sync configuration is missing or invalid."""


class SyncCryptoError(SyncError):
    """Raised when encryption or decryption fails."""


@dataclass(frozen=True)
class SyncConfig:
    endpoint: str
    organization_id: str
    project_id: str
    repository_id: str
    client_id: str


def sync_config_path(paths: ProjectPaths) -> Path:
    return paths.contextos / "sync" / "config.json"


def write_sync_config(paths: ProjectPaths, config: SyncConfig) -> Path:
    target = sync_config_path(paths)
    safe_write(target, json.dumps(asdict(config), indent=2, sort_keys=True), overwrite=True)
    append_event(paths, {"type": "sync.configured", "endpoint": config.endpoint, "project_id": config.project_id})
    return target


def read_sync_config(paths: ProjectPaths) -> SyncConfig:
    path = sync_config_path(paths)
    if not path.exists():
        raise SyncConfigError("Sync is not configured. Run `checkpoint sync configure` first.")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        return SyncConfig(
            endpoint=str(payload["endpoint"]).rstrip("/"),
            organization_id=str(payload["organization_id"]),
            project_id=str(payload["project_id"]),
            repository_id=str(payload["repository_id"]),
            client_id=str(payload["client_id"]),
        )
    except (KeyError, TypeError, json.JSONDecodeError) as exc:
        raise SyncConfigError("Sync config is invalid. Re-run `checkpoint sync configure`.") from exc


def load_fernet_class() -> type[Any]:
    try:
        from cryptography.fernet import Fernet, InvalidToken
    except ImportError as exc:
        raise SyncDependencyError(SYNC_EXTRA_HINT) from exc
    globals()["InvalidToken"] = InvalidToken
    return cast(type[Any], Fernet)


def sync_key() -> bytes:
    raw = os.environ.get(SYNC_KEY_ENV, "")
    if not raw:
        raise SyncCryptoError(f"{SYNC_KEY_ENV} is required for sync encryption.")
    try:
        decoded = base64.urlsafe_b64decode(raw.encode("utf-8"))
        if len(decoded) == 32:
            return raw.encode("utf-8")
    except Exception:
        pass
    digest = hashlib.sha256(raw.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest)


def encrypt_bytes(data: bytes) -> str:
    key = sync_key()
    fernet = load_fernet_class()(key)
    return cast(str, fernet.encrypt(data).decode("utf-8"))


def decrypt_text(token: str) -> bytes:
    key = sync_key()
    fernet = load_fernet_class()(key)
    try:
        return cast(bytes, fernet.decrypt(token.encode("utf-8")))
    except globals().get("InvalidToken", Exception) as exc:
        raise SyncCryptoError("Could not decrypt sync bundle with the current CONTEXTOS_SYNC_KEY.") from exc


def package_contextos(paths: ProjectPaths) -> bytes:
    if not paths.contextos.exists():
        raise SyncConfigError("Project is not initialized. Run `checkpoint init` first.")
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(paths.contextos.rglob("*")):
            if not path.is_file():
                continue
            relative = path.relative_to(paths.root)
            if relative.parts[:2] == (".contextos", "sync"):
                continue
            archive.write(path, relative.as_posix())
    return buffer.getvalue()


def bundle_hash(data: bytes) -> str:
    return f"sha256:{hashlib.sha256(data).hexdigest()}"


def http_json(method: str, url: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = urllib.request.Request(
        url,
        data=body,
        method=method,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            data = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise SyncError(f"Cloud sync request failed: HTTP {exc.code} {detail}") from exc
    except urllib.error.URLError as exc:
        raise SyncError(f"Cloud sync request failed: {exc.reason}") from exc
    return cast(dict[str, Any], json.loads(data or "{}"))


def sync_status(paths: ProjectPaths) -> dict[str, Any]:
    config = read_sync_config(paths)
    return http_json(
        "GET",
        f"{config.endpoint}/v1/orgs/{config.organization_id}/projects/{config.project_id}"
        f"/repos/{config.repository_id}/sync/status",
    )


def sync_push(paths: ProjectPaths) -> dict[str, Any]:
    config = read_sync_config(paths)
    bundle = package_contextos(paths)
    encrypted_payload = encrypt_bytes(bundle)
    project_payload = {
        "organization_id": config.organization_id,
        "project_id": config.project_id,
        "repository_id": config.repository_id,
        "repository_url": None,
        "actor": {"user_id": config.client_id},
    }
    http_json("POST", f"{config.endpoint}/v1/projects", project_payload)
    upload_payload = {
        "organization_id": config.organization_id,
        "project_id": config.project_id,
        "repository_id": config.repository_id,
        "client_id": config.client_id,
        "schema_version": "contextos.sync.v1",
        "encrypted_payload": encrypted_payload,
        "content_hash": bundle_hash(bundle),
        "actor": {"user_id": config.client_id},
    }
    result = http_json("POST", f"{config.endpoint}/v1/sync/bundles", upload_payload)
    append_event(paths, {"type": "sync.pushed", "bundle_id": result.get("bundle_id", ""), "status": "success"})
    return result


def sync_pull(paths: ProjectPaths, *, bundle_id: str, output: Path) -> dict[str, Any]:
    config = read_sync_config(paths)
    payload = http_json(
        "GET",
        f"{config.endpoint}/v1/orgs/{config.organization_id}/projects/{config.project_id}"
        f"/repos/{config.repository_id}/sync/bundles/{bundle_id}",
    )
    encrypted_payload = str(payload.get("encrypted_payload", ""))
    if not encrypted_payload:
        raise SyncError("Downloaded bundle did not include encrypted_payload.")
    decrypted = decrypt_text(encrypted_payload)
    ensure_dir(output.parent)
    try:
        output.write_bytes(decrypted)
    except OSError as exc:
        raise StoreFilesystemError(f"Could not write file `{output}`: {exc.strerror or exc}.") from exc
    append_event(paths, {"type": "sync.pulled", "bundle_id": bundle_id, "output": str(output)})
    return {"status": "ok", "bundle_id": bundle_id, "output": output, "bytes_written": len(decrypted)}


def sync_config_payload(config: SyncConfig) -> dict[str, Any]:
    return {
        "endpoint": config.endpoint,
        "organization_id": config.organization_id,
        "project_id": config.project_id,
        "repository_id": config.repository_id,
        "client_id": config.client_id,
        "configured_at": now_iso(),
    }
