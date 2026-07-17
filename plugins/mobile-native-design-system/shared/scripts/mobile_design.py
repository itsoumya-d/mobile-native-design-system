#!/usr/bin/env python3
"""Validate mobile screen briefs and query compact native design intelligence."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "assets" / "design-intelligence.json"
FRAMEWORKS = {"flutter", "react-native", "swiftui", "compose", "all"}
REQUIRED_BRIEF_FIELDS = {
    "format",
    "name",
    "subject",
    "user_job",
    "primary_action",
    "hierarchy",
    "signature_interaction",
    "dials",
    "components",
}
REQUIRED_DIALS = {"density", "contrast", "shape", "typography", "motion"}


def validate_brief(brief: dict[str, Any]) -> list[str]:
    """Return deterministic validation errors for a mobile screen brief."""
    errors: list[str] = []
    missing = sorted(REQUIRED_BRIEF_FIELDS - set(brief))
    if missing:
        errors.append("missing fields: " + ", ".join(missing))
    if brief.get("format") != "mobile-screen-brief/1":
        errors.append("format must be mobile-screen-brief/1")
    for field in ("name", "subject", "user_job", "primary_action", "signature_interaction"):
        if field in brief and not isinstance(brief[field], str):
            errors.append(f"{field} must be a string")
    if "hierarchy" in brief and (not isinstance(brief["hierarchy"], list) or not brief["hierarchy"]):
        errors.append("hierarchy must be a non-empty list")
    if "components" in brief and (not isinstance(brief["components"], list) or not brief["components"]):
        errors.append("components must be a non-empty list")
    dials = brief.get("dials")
    if not isinstance(dials, dict):
        errors.append("dials must be an object")
    else:
        missing_dials = sorted(REQUIRED_DIALS - set(dials))
        if missing_dials:
            errors.append("missing dials: " + ", ".join(missing_dials))
    return errors


def _catalog() -> list[dict[str, Any]]:
    document = json.loads(CATALOG.read_text(encoding="utf-8"))
    records = document.get("records")
    if not isinstance(records, list):
        raise ValueError("design intelligence records must be a list")
    return records


def query_catalog(query: str, platform: str = "all") -> list[dict[str, Any]]:
    """Return deterministic platform-filtered catalog records ranked by keyword overlap."""
    if platform not in FRAMEWORKS:
        raise ValueError(f"unsupported platform: {platform}")
    terms = {term.lower() for term in re.findall(r"[a-z0-9-]+", query)}
    matches: list[tuple[int, str, dict[str, Any]]] = []
    for record in _catalog():
        frameworks = record["frameworks"]
        if platform != "all" and platform not in frameworks:
            continue
        haystack = " ".join([record["title"], *record["keywords"], record["guidance"]]).lower()
        score = sum(term in haystack for term in terms)
        if score:
            matches.append((-score, record["id"], record))
    return [record for _, _, record in sorted(matches)]


def _read_json(path: Path) -> dict[str, Any]:
    document = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise ValueError("input JSON must be an object")
    return document


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    validate = subparsers.add_parser("validate")
    validate.add_argument("brief", type=Path)
    query = subparsers.add_parser("query")
    query.add_argument("query")
    query.add_argument("--platform", choices=sorted(FRAMEWORKS), default="all")
    args = parser.parse_args(argv)
    try:
        if args.command == "validate":
            errors = validate_brief(_read_json(args.brief))
            print(json.dumps({"ok": not errors, "errors": errors}, sort_keys=True))
            return 0 if not errors else 1
        print(json.dumps(query_catalog(args.query, args.platform), indent=2, sort_keys=True))
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
