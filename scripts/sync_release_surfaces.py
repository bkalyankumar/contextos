from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.request import urlopen

import tomllib

VERSION_PATTERN = re.compile(r"\b0\.1\.\d+\b")
V_VERSION_PATTERN = re.compile(r"\bv0\.1\.\d+\b")


def project_version(root: Path) -> str:
    with (root / "pyproject.toml").open("rb") as f:
        data = tomllib.load(f)
    return str(data["project"]["version"])


def top_changelog_version(root: Path) -> str | None:
    text = (root / "CHANGELOG.md").read_text(encoding="utf-8")
    match = re.search(r"(?m)^## (0\.1\.\d+) - ", text)
    return match.group(1) if match else None


def replace_versions(path: Path, version: str) -> bool:
    text = path.read_text(encoding="utf-8")
    updated = VERSION_PATTERN.sub(version, text)
    updated = V_VERSION_PATTERN.sub(f"v{version}", updated)
    if updated == text:
        return False
    path.write_text(updated, encoding="utf-8")
    return True


def check_no_stale(path: Path, version: str) -> list[str]:
    text = path.read_text(encoding="utf-8")
    stale = sorted({m.group(0) for m in VERSION_PATTERN.finditer(text) if m.group(0) != version})
    stale += sorted({m.group(0) for m in V_VERSION_PATTERN.finditer(text) if m.group(0) != f"v{version}"})
    return [f"{path}: stale version {item}" for item in stale]


def sync_site(site_dir: Path, version: str, write: bool) -> list[str]:
    paths = [
        site_dir / "package.json",
        site_dir / "package-lock.json",
        site_dir / "README.md",
        site_dir / "app" / "examples" / "page.tsx",
        site_dir / "app" / "demo" / "page.tsx",
    ]
    changed: list[str] = []
    for path in paths:
        if not path.exists():
            continue
        if write:
            if replace_versions(path, version):
                changed.append(str(path))
        else:
            changed.extend(check_no_stale(path, version))
    return changed


def check_pypi(package: str, version: str) -> list[str]:
    with urlopen(f"https://pypi.org/pypi/{package}/json", timeout=20) as response:
        data = json.load(response)
    actual = str(data["info"]["version"])
    if actual != version:
        return [f"PyPI latest is {actual}, expected {version}"]
    return []


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync/check public release surfaces.")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--site-dir", type=Path)
    parser.add_argument("--write", action="store_true", help="Update writable sibling surfaces.")
    parser.add_argument("--check-pypi", action="store_true", help="Verify PyPI latest version.")
    args = parser.parse_args()

    root = args.root.resolve()
    version = project_version(root)
    errors: list[str] = []

    changelog_version = top_changelog_version(root)
    if changelog_version != version:
        errors.append(f"CHANGELOG top release is {changelog_version}, expected {version}")

    ref_name = (root / ".git").exists() and None
    del ref_name

    if args.site_dir:
        site_result = sync_site(args.site_dir.resolve(), version, args.write)
        if args.write:
            for path in site_result:
                print(f"updated {path}")
        else:
            errors.extend(site_result)

    if args.check_pypi:
        errors.extend(check_pypi("checkpoint-cli", version))

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    print(f"release surfaces OK for {version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
