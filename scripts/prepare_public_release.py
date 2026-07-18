#!/usr/bin/env python3
"""Stage the exact allowlisted contents for the public plugin repository."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TREES = (
    ".agents",
    ".github",
    "docs",
    "fixtures",
    "LICENSES",
    "plugins",
)
FILES = (
    "LICENSE",
    "README.md",
    "SECURITY.md",
    "THIRD_PARTY_NOTICES.md",
)
AUDIT_FILES = ("sources.lock.json", "line-audit.jsonl", "validation-status.md", "forward-routing-tests.md")
SCRIPT_FILES = ("prepare_public_release.py", "verify_release.py")
TEST_FILES = (
    "__init__.py",
    "test_mobile_tooling.py",
    "test_public_release.py",
    "test_release_contract.py",
    "test_v2_product_intelligence.py",
)
IGNORED_PARTS = {
    ".bundle",
    ".cxx",
    ".dart_tool",
    ".git",
    ".gradle",
    ".idea",
    ".kotlin",
    ".worktrees",
    "DerivedData",
    "Generated.xcconfig",
    "Pods",
    "TokenGallery.xcworkspace",
    "__pycache__",
    "build",
    "flutter_export_environment.sh",
    "local.properties",
    "node_modules",
    "upstream",
}
PUBLIC_GITIGNORE = """.DS_Store
.dart_tool/
.gradle/
.idea/
.kotlin/
.cxx/
DerivedData/
Pods/
*.xcworkspace/
build/
node_modules/
coverage/
*.xcresult
*.iml
local.properties
Generated.xcconfig
flutter_export_environment.sh
__pycache__/
*.pyc
generated/
!fixtures/flutter/lib/generated/
!fixtures/react-native/src/generated/
!fixtures/swiftui/TokenGallery/Sources/Generated/
"""


def _copy_tree(source: Path, destination: Path) -> None:
    for path in sorted(source.rglob("*")):
        if any(part in IGNORED_PARTS for part in path.relative_to(source).parts):
            continue
        target = destination / path.relative_to(source)
        if path.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        elif path.is_file():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)


def stage(destination: Path) -> None:
    """Create one clean public-release tree. Existing destinations are refused."""
    destination = destination.resolve()
    if destination.exists():
        raise ValueError(f"destination already exists: {destination}")
    if destination == ROOT or ROOT in destination.parents:
        raise ValueError("destination must be outside the source workspace")
    destination.mkdir(parents=True)
    try:
        for name in TREES:
            source = ROOT / name
            if not source.is_dir():
                raise ValueError(f"allowlisted source tree is missing: {source}")
            _copy_tree(source, destination / name)
        for name in FILES:
            source = ROOT / name
            if not source.is_file():
                raise ValueError(f"allowlisted source file is missing: {source}")
            shutil.copy2(source, destination / name)
        for name in TEST_FILES:
            source = ROOT / "tests" / name
            if not source.is_file():
                raise ValueError(f"public test is missing: {source}")
            target = destination / "tests" / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
        for name in AUDIT_FILES:
            source = ROOT / "audit" / name
            if not source.is_file():
                raise ValueError(f"audit evidence is missing: {source}")
            target = destination / "audit" / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
        for name in SCRIPT_FILES:
            source = ROOT / "scripts" / name
            if not source.is_file():
                raise ValueError(f"release script is missing: {source}")
            target = destination / "scripts" / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
        (destination / ".gitignore").write_text(PUBLIC_GITIGNORE, encoding="utf-8")
    except Exception:
        shutil.rmtree(destination)
        raise


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        stage(args.out)
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    print(args.out.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
