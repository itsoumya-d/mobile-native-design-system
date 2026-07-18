#!/usr/bin/env python3
"""Validate briefs, synthesize project design language, and query mobile intelligence."""

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


def synthesize_design_language(project: dict[str, Any]) -> dict[str, Any]:
    """Turn a v2 project model into a concise, evidence-backed mobile Design Read."""
    if project.get("format") != "mobile-native-project/2":
        raise ValueError("project format must be mobile-native-project/2")
    framework = project.get("framework", {}).get("id")
    if framework not in FRAMEWORKS - {"all"}:
        raise ValueError("project framework is missing or unsupported")
    observed = project.get("design_language")
    if not isinstance(observed, dict):
        raise ValueError("project design_language must be an object")
    screens = project.get("screen_graph", {}).get("screens", [])
    if not isinstance(screens, list):
        raise ValueError("project screens must be a list")
    source_paths = sorted(
        {
            screen["path"]
            for screen in screens
            if isinstance(screen, dict) and isinstance(screen.get("path"), str)
        }
    )
    preserve: list[str] = []
    improve: list[str] = []
    if observed.get("colors"):
        preserve.append("Preserve recognizable product color intent while moving raw values behind semantic roles.")
    if observed.get("typography"):
        preserve.append("Preserve the established content hierarchy and vocabulary.")
    if observed.get("components"):
        preserve.append("Reuse existing component identities and interaction ownership.")
    if not preserve:
        preserve.append("Preserve current behavior, content order, and native platform conventions.")
    if not observed.get("accessibility_primitives"):
        improve.append("Add framework-native roles, labels, state, grouping, and focus behavior.")
    if not observed.get("adaptive_primitives"):
        improve.append("Define compact, medium, and expanded behavior with native insets and text scaling.")
    if not observed.get("motion_grammar"):
        improve.append("Define restrained press, presence, interruption, and reduced-motion behavior.")
    for inconsistency in observed.get("inconsistencies", []):
        if isinstance(inconsistency, dict) and inconsistency.get("message"):
            improve.append(str(inconsistency["message"]))
    if not improve:
        improve.append("Validate scale consistency and screen-to-screen component parity before visual change.")
    density_count = observed.get("density", {}).get("raw_dimension_count", 0)
    dials = {
        "density": "compact" if isinstance(density_count, int) and density_count > 20 else "comfortable",
        "contrast": "high-enough-for-accessibility",
        "shape": "preserve-observed-grammar" if observed.get("shapes") else "platform-native",
        "typography": "semantic-system-roles",
        "motion": "restrained-and-interruptible",
        "variance": "moderate",
    }
    overhaul = bool(
        len(observed.get("inconsistencies", [])) >= 3
        and not observed.get("components")
    )
    return {
        "format": "mobile-native-design-language/1",
        "framework": framework,
        "source_fingerprint": project.get("project", {}).get("source_fingerprint"),
        "observed": {
            key: observed.get(key, [])
            for key in (
                "typography",
                "colors",
                "spacing",
                "shapes",
                "iconography",
                "components",
                "motion_grammar",
                "inconsistencies",
            )
        },
        "design_read": {
            "product_subject": project.get("project", {}).get("name", "mobile product"),
            "screen_count": len(screens),
            "preserve": preserve,
            "improve": improve,
            "decision": "overhaul" if overhaul else "iterate",
            "dials": dials,
            "anti_generic_gate": [
                "Each changed screen must retain its concrete user job.",
                "Use at most one signature interaction per screen.",
                "Reject decoration that does not improve hierarchy, feedback, or comprehension.",
            ],
        },
        "evidence": [
            {"path": path, "kind": "screen-source", "confidence": "high"}
            for path in source_paths
        ],
    }


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
    synthesize = subparsers.add_parser("synthesize")
    synthesize.add_argument("project_model", type=Path)
    synthesize.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "validate":
            errors = validate_brief(_read_json(args.brief))
            print(json.dumps({"ok": not errors, "errors": errors}, sort_keys=True))
            return 0 if not errors else 1
        if args.command == "query":
            print(json.dumps(query_catalog(args.query, args.platform), indent=2, sort_keys=True))
            return 0
        language = synthesize_design_language(_read_json(args.project_model))
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(
            json.dumps(language, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
