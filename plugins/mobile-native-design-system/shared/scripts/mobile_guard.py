#!/usr/bin/env python3
"""Capture and verify bounded one-screen mobile redesign invariants."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


class GuardError(ValueError):
    """Raised when a screen change cannot be guarded safely."""


def _load_project_tool():
    path = Path(__file__).with_name("mobile_project.py")
    spec = importlib.util.spec_from_file_location("mobile_guard_project", path)
    if not spec or not spec.loader:
        raise GuardError(f"cannot load project scanner: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_paths(root: Path, values: Any, field: str) -> list[str]:
    if not isinstance(values, list) or not all(isinstance(item, str) for item in values):
        raise GuardError(f"{field} must be a list of relative paths")
    normalized: list[str] = []
    for value in values:
        candidate = Path(value)
        if candidate.is_absolute() or ".." in candidate.parts:
            raise GuardError(f"{field} contains an unsafe path: {value}")
        resolved = (root / candidate).resolve()
        if root != resolved and root not in resolved.parents:
            raise GuardError(f"{field} escapes the project root: {value}")
        normalized.append(candidate.as_posix())
    return sorted(set(normalized))


def _dirty_state(root: Path) -> list[dict[str, str]]:
    git_marker = root / ".git"
    if not git_marker.exists():
        parent = root
        while parent != parent.parent and not (parent / ".git").exists():
            parent = parent.parent
        if not (parent / ".git").exists():
            return []
    completed = subprocess.run(
        ["git", "-C", str(root), "status", "--porcelain=v1", "--untracked-files=all"],
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode:
        return [{"status": "unknown", "path": "<git-status-unavailable>"}]
    records: list[dict[str, str]] = []
    for line in completed.stdout.splitlines():
        if len(line) < 4:
            continue
        records.append({"status": line[:2], "path": line[3:]})
    return records


def _behavior_signatures(model: dict[str, Any]) -> list[dict[str, Any]]:
    return sorted(
        [
            {
                "kind": action["kind"],
                "path": action["path"],
                "symbol": action["symbol"],
                "statement_hash": action["statement_hash"],
            }
            for action in model.get("behavior_contract", {}).get("actions", [])
        ],
        key=lambda item: (
            item["path"],
            item["kind"],
            item["statement_hash"],
            item["symbol"],
        ),
    )


def _validate_plan(plan: dict[str, Any]) -> None:
    if plan.get("format") != "mobile-native-screen-plan/1":
        raise GuardError("screen plan format must be mobile-native-screen-plan/1")
    approval = plan.get("approval")
    if not isinstance(approval, dict) or approval.get("status") != "approved":
        raise GuardError("screen plan must be explicitly approved before a baseline is captured")
    screen = plan.get("screen")
    if not isinstance(screen, dict) or not isinstance(screen.get("id"), str):
        raise GuardError("screen plan must identify one screen")
    file_scope = plan.get("file_scope")
    if not isinstance(file_scope, dict):
        raise GuardError("screen plan file_scope must be an object")


def capture_baseline(app_root: Path | str, screen_plan: dict[str, Any]) -> dict[str, Any]:
    """Capture source, dirty-state, and behavior signatures before approved UI edits."""
    _validate_plan(screen_plan)
    root = Path(app_root).resolve()
    if not root.is_dir():
        raise GuardError(f"app root does not exist: {root}")
    allowed = _safe_paths(root, screen_plan["file_scope"].get("allowed"), "file_scope.allowed")
    protected = _safe_paths(
        root, screen_plan["file_scope"].get("protected", []), "file_scope.protected"
    )
    overlap = sorted(set(allowed).intersection(protected))
    if overlap:
        raise GuardError("allowed and protected scopes overlap: " + ", ".join(overlap))
    for relative in allowed:
        if not (root / relative).is_file():
            raise GuardError(f"approved file does not exist: {relative}")
    model = _load_project_tool().scan_project(root, profile="full")
    expected_fingerprint = screen_plan.get("project_fingerprint")
    if expected_fingerprint and expected_fingerprint != model["project"]["source_fingerprint"]:
        raise GuardError("project changed after the screen plan was created; regenerate the plan")
    dirty = _dirty_state(root)
    dirty_allowed = sorted(
        item["path"] for item in dirty if item["path"] in set(allowed)
    )
    acknowledgement = screen_plan.get("approval", {}).get(
        "preexisting_changes_acknowledged", False
    )
    if dirty_allowed and not acknowledgement:
        raise GuardError(
            "approved files already contain unacknowledged changes: "
            + ", ".join(dirty_allowed)
        )
    files = sorted(set(allowed + protected))
    hashes = {
        relative: _hash_file(root / relative)
        for relative in files
        if (root / relative).is_file()
    }
    signatures = _behavior_signatures(model)
    return {
        "format": "mobile-native-guard-baseline/1",
        "screen_id": screen_plan["screen"]["id"],
        "project_fingerprint": model["project"]["source_fingerprint"],
        "allowed_files": allowed,
        "protected_files": protected,
        "source_hashes": hashes,
        "source_files": model.get("source_files", []),
        "behavior_signatures": signatures,
        "dirty_state": dirty,
        "required_commands": screen_plan.get("tests", model.get("build_commands", [])),
    }


def verify_change(
    app_root: Path | str,
    screen_plan: dict[str, Any],
    baseline: dict[str, Any],
) -> dict[str, Any]:
    """Verify file scope and behavior invariants after an approved screen edit."""
    _validate_plan(screen_plan)
    if baseline.get("format") != "mobile-native-guard-baseline/1":
        raise GuardError("baseline format must be mobile-native-guard-baseline/1")
    if baseline.get("screen_id") != screen_plan.get("screen", {}).get("id"):
        raise GuardError("baseline and screen plan target different screens")
    root = Path(app_root).resolve()
    allowed = set(_safe_paths(root, baseline.get("allowed_files"), "baseline.allowed_files"))
    protected = set(
        _safe_paths(root, baseline.get("protected_files"), "baseline.protected_files")
    )
    changed: list[str] = []
    missing: list[str] = []
    for relative, digest in sorted(baseline.get("source_hashes", {}).items()):
        path = root / relative
        if not path.is_file():
            missing.append(relative)
        elif _hash_file(path) != digest:
            changed.append(relative)
    out_of_scope = sorted(set(changed).difference(allowed))
    protected_changes = sorted(set(changed).intersection(protected))
    model = _load_project_tool().scan_project(root, profile="full")
    baseline_source_files = set(baseline.get("source_files", []))
    current_source_files = set(model.get("source_files", []))
    added_source_files = sorted(current_source_files - baseline_source_files)
    current_signatures = {
        (
            item["kind"],
            item["path"],
            item["symbol"],
            item["statement_hash"],
        )
        for item in _behavior_signatures(model)
    }
    invariants: list[dict[str, Any]] = []
    for original in baseline.get("behavior_signatures", []):
        key = (
            original["kind"],
            original["path"],
            original["symbol"],
            original["statement_hash"],
        )
        preserved = key in current_signatures
        invariants.append(
            {
                "id": f"preserve-{original['kind']}:{original['path']}:{original['statement_hash'][:12]}",
                "kind": original["kind"],
                "path": original["path"],
                "preserved": preserved,
                "evidence": original["statement_hash"],
            }
        )
    violations: list[dict[str, Any]] = []
    if out_of_scope:
        violations.append(
            {
                "id": "file-scope.outside-approved",
                "message": "Files outside the approved UI scope changed.",
                "paths": out_of_scope,
            }
        )
    if protected_changes:
        violations.append(
            {
                "id": "file-scope.protected-changed",
                "message": "Protected files changed.",
                "paths": protected_changes,
            }
        )
    if missing:
        violations.append(
            {
                "id": "file-scope.missing",
                "message": "Baseline files were removed.",
                "paths": sorted(missing),
            }
        )
    if added_source_files:
        violations.append(
            {
                "id": "file-scope.source-added",
                "message": "New source files were added outside the approved baseline.",
                "paths": added_source_files,
            }
        )
    broken = [item for item in invariants if not item["preserved"]]
    if broken:
        violations.append(
            {
                "id": "behavior.signature-changed",
                "message": "One or more protected behavior signatures changed.",
                "paths": sorted({item["path"] for item in broken}),
            }
        )
    return {
        "format": "mobile-native-change-receipt/1",
        "ok": not violations,
        "screen_id": baseline["screen_id"],
        "changed_files": changed,
        "added_source_files": added_source_files,
        "invariants": invariants,
        "violations": violations,
        "dirty_state_before": baseline.get("dirty_state", []),
        "dirty_state_after": _dirty_state(root),
        "commands": [
            {"command": command, "status": "required-not-run-by-static-guard"}
            for command in baseline.get("required_commands", [])
        ],
        "screenshots": [],
        "unresolved_risks": [
            "Subjective aesthetic quality requires human review.",
            "Physical-device assistive-technology certification is not performed by this static guard.",
        ],
    }


def _read_json(path: Path) -> dict[str, Any]:
    document = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise GuardError("input JSON must be an object")
    return document


def _write_json(path: Path, document: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    baseline = subparsers.add_parser("baseline")
    baseline.add_argument("app_root", type=Path)
    baseline.add_argument("screen_plan", type=Path)
    baseline.add_argument("--out", required=True, type=Path)
    verify = subparsers.add_parser("verify")
    verify.add_argument("app_root", type=Path)
    verify.add_argument("screen_plan", type=Path)
    verify.add_argument("baseline", type=Path)
    verify.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        plan = _read_json(args.screen_plan)
        if args.command == "baseline":
            document = capture_baseline(args.app_root, plan)
        else:
            document = verify_change(args.app_root, plan, _read_json(args.baseline))
        _write_json(args.out, document)
        return 0 if document.get("ok", True) else 1
    except (OSError, GuardError, ValueError, json.JSONDecodeError) as error:
        print(json.dumps({"ok": False, "error": str(error)}, sort_keys=True), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
