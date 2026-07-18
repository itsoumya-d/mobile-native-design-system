#!/usr/bin/env python3
"""Create evidence-backed whole-product and one-screen native redesign plans."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


class PlanError(ValueError):
    """Raised when a safe plan cannot be produced from project evidence."""


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "assets" / "capability-registry.json"
SOURCE_FAMILIES = (
    "frontend-design",
    "ui-ux-pro-max",
    "design-taste-frontend",
    "shadcn-ui-mcp-server",
    "21st.dev-magic-mcp",
    "vercel-react-best-practices",
    "gsap-master",
    "motion-framer",
    "convex-create-component",
    "vercel-react-native-skills",
)

NATIVE_IMPLEMENTATION = {
    "flutter": (
        "Compose the screen from Material or Cupertino widgets, existing Theme/ThemeExtension values, "
        "LayoutBuilder, TextScaler, SafeArea, Semantics, and Flutter animation primitives."
    ),
    "react-native": (
        "Compose the screen from React Native primitives and the app's navigator/theme, keep state ownership "
        "stable, use virtualized lists where needed, and preserve accessibility and safe-area behavior."
    ),
    "swiftui": (
        "Compose the screen with SwiftUI navigation and presentation primitives, semantic text styles, "
        "environment values, size classes, accessibility modifiers, and native animations."
    ),
    "compose": (
        "Compose the screen with Material3, immutable UI state, window size classes, Insets, semantics, "
        "and Compose animation primitives."
    ),
}


def _registry() -> list[dict[str, Any]]:
    document = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    rules = document.get("rules")
    if not isinstance(rules, list):
        raise PlanError("capability registry rules must be a list")
    return rules


def _validate_project(project: dict[str, Any]) -> tuple[str, list[dict[str, Any]]]:
    if project.get("format") != "mobile-native-project/2":
        raise PlanError("project format must be mobile-native-project/2")
    framework = project.get("framework", {}).get("id")
    if framework not in NATIVE_IMPLEMENTATION:
        raise PlanError("project framework is missing or unsupported")
    screens = project.get("screen_graph", {}).get("screens")
    if not isinstance(screens, list) or not screens:
        raise PlanError("project must contain at least one proven screen")
    return framework, screens


def _rules_for_screen(
    rules: list[dict[str, Any]],
    framework: str,
    screen: dict[str, Any],
    dependencies: set[str],
) -> list[dict[str, Any]]:
    signals = screen.get("signals", {})
    selected: list[dict[str, Any]] = []
    always = {
        "frontend-design",
        "ui-ux-pro-max",
        "design-taste-frontend",
        "21st.dev-magic-mcp",
        "vercel-react-best-practices",
    }
    conditional = {
        "gsap-master": bool(signals.get("motion")),
        "motion-framer": bool(signals.get("motion")),
        "convex-create-component": "convex" in dependencies or bool(signals.get("async_states")),
        "shadcn-ui-mcp-server": framework == "react-native",
        "vercel-react-native-skills": framework == "react-native",
    }
    for rule in rules:
        if framework not in rule.get("frameworks", []):
            continue
        source = rule.get("source_family")
        if source in always or conditional.get(source, False):
            selected.append(rule)
    selected.sort(key=lambda rule: (-int(rule.get("priority", 0)), str(rule.get("id", ""))))
    seen: set[str] = set()
    compact: list[dict[str, Any]] = []
    for rule in selected:
        source = str(rule.get("source_family"))
        if source in seen and len(compact) >= 6:
            continue
        seen.add(source)
        compact.append(rule)
        if len(compact) == 9:
            break
    return compact


def _evidence_for_screen(project: dict[str, Any], screen: dict[str, Any]) -> list[dict[str, Any]]:
    path = screen["path"]
    evidence = [
        {
            "path": item["path"],
            "line": item["line"],
            "symbol": item["symbol"],
            "kind": item["kind"],
            "confidence": item["confidence"],
        }
        for item in project.get("evidence", [])
        if item.get("path") == path
    ]
    if not evidence:
        evidence.append(
            {
                "path": path,
                "line": screen.get("evidence", {}).get("line", 1),
                "symbol": screen["name"],
                "kind": "screen",
                "confidence": screen.get("confidence", "medium"),
            }
        )
    return evidence


def _behavior_invariants(project: dict[str, Any], path: str) -> list[dict[str, Any]]:
    invariants = project.get("behavior_contract", {}).get("invariants", [])
    relevant = [
        invariant
        for invariant in invariants
        if invariant.get("evidence", {}).get("path") == path
    ]
    return relevant or [
        {
            "id": "preserve-screen-contract",
            "kind": "screen-contract",
            "description": "Preserve current routes, callbacks, state ownership, data boundaries, and side effects.",
            "evidence": {"path": path, "line": 1, "symbol": "screen"},
            "signature": project.get("source_hashes", {}).get(path, ""),
        }
    ]


def _score(screen: dict[str, Any], invariant_count: int) -> dict[str, int]:
    signals = screen.get("signals", {})
    user_impact = 5 if screen.get("entry_point") else 4
    reach = 5 if screen.get("entry_point") else 3
    native_benefit = 2
    native_benefit += int(not signals.get("accessibility", False))
    native_benefit += int(not signals.get("adaptive", False))
    reuse = 4 if screen["name"].endswith(("App", "HomeScreen", "RootView")) else 3
    risk = min(5, 1 + invariant_count)
    verification = 4
    total = (
        user_impact * 6
        + reach * 5
        + native_benefit * 5
        + reuse * 3
        + verification * 3
        - risk * 4
    )
    return {
        "total": total,
        "user_impact": user_impact,
        "frequency_reach": reach,
        "native_benefit": native_benefit,
        "reuse_potential": reuse,
        "implementation_risk": risk,
        "verification_strength": verification,
    }


def _recommendation(
    project: dict[str, Any],
    screen: dict[str, Any],
    framework: str,
    rules: list[dict[str, Any]],
) -> dict[str, Any]:
    invariants = _behavior_invariants(project, screen["path"])
    selected = _rules_for_screen(
        rules,
        framework,
        screen,
        set(project.get("dependencies", {}).get("direct", [])),
    )
    signals = screen.get("signals", {})
    benefits: list[str] = [
        "Make the primary screen job and hierarchy easier to understand without changing behavior."
    ]
    if not signals.get("accessibility"):
        benefits.append("Make controls and content understandable to assistive technologies.")
    if not signals.get("adaptive"):
        benefits.append("Prevent clipping and hierarchy loss at large text and tablet widths.")
    if signals.get("motion"):
        benefits.append("Make state changes feel continuous while respecting reduced motion.")
    return {
        "id": f"improve-{screen['id']}",
        "screen_id": screen["id"],
        "title": f"Evidence-backed native iteration for {screen['name']}",
        "score": _score(screen, len(invariants)),
        "current_code_evidence": _evidence_for_screen(project, screen),
        "user_benefit": benefits,
        "selected_capabilities": [
            {
                "id": rule["id"],
                "source_family": rule["source_family"],
                "reason": rule.get("benefit", rule.get("native_mapping", "")),
            }
            for rule in selected
        ],
        "native_implementation": NATIVE_IMPLEMENTATION[framework],
        "files_likely_affected": [screen["path"]],
        "behavior_invariants": invariants,
        "accessibility": {
            "consequence": "Roles, labels, state, grouping, focus order, target size, and text scaling must improve or remain equivalent.",
            "required_checks": [
                "largest supported text",
                "screen-reader semantics",
                "focus order",
                "touch targets",
                "contrast",
                "RTL",
            ],
        },
        "motion": {
            "consequence": "Motion must explain state or continuity and remain interruptible.",
            "required_checks": [
                "reduced motion",
                "cancellation",
                "resting state",
                "no information encoded only by motion",
            ],
        },
        "risk": {
            "level": "high" if len(invariants) >= 4 else "medium",
            "reasons": [invariant["description"] for invariant in invariants],
        },
        "confidence": "high" if screen.get("confidence") == "high" else "medium",
        "verification_commands": project.get("build_commands", []),
        "acceptance_criteria": [
            "All protected behavior signatures remain unchanged.",
            "Only approved UI files change.",
            "Existing tests and native build commands pass.",
            "Large text, RTL, reduced motion, compact, and tablet behavior are verified.",
            "A human accepts the subjective visual result.",
        ],
    }


def _capability_coverage(
    rules: list[dict[str, Any]],
    framework: str,
    project: dict[str, Any],
    recommendations: list[dict[str, Any]],
) -> list[dict[str, str]]:
    selected = {
        capability["source_family"]
        for recommendation in recommendations
        for capability in recommendation["selected_capabilities"]
    }
    dependencies = set(project.get("dependencies", {}).get("direct", []))
    coverage: list[dict[str, str]] = []
    for source in SOURCE_FAMILIES:
        available = any(
            rule.get("source_family") == source and framework in rule.get("frameworks", [])
            for rule in rules
        )
        if source in selected:
            status = "selected"
        elif source == "convex-create-component" and "convex" not in dependencies:
            status = "conditional"
        elif source in {"shadcn-ui-mcp-server", "vercel-react-native-skills"} and framework != "react-native":
            status = "available" if available else "not-applicable"
        else:
            status = "available" if available else "not-applicable"
        coverage.append(
            {
                "source_family": source,
                "status": status,
                "reason": (
                    "Selected by current screen evidence."
                    if status == "selected"
                    else "Available through native translation when a matching trigger is proven."
                    if status == "available"
                    else "Activates only when the project owns the corresponding integration."
                    if status == "conditional"
                    else "No meaningful mapping applies to the detected project evidence."
                ),
            }
        )
    return coverage


def create_app_plan(project: dict[str, Any]) -> dict[str, Any]:
    """Create a prioritized whole-product roadmap without authorizing code edits."""
    framework, screens = _validate_project(project)
    rules = _registry()
    recommendations = [
        _recommendation(project, screen, framework, rules) for screen in screens
    ]
    recommendations.sort(
        key=lambda item: (-item["score"]["total"], item["screen_id"])
    )
    return {
        "format": "mobile-native-app-plan/1",
        "scope": "app",
        "project_fingerprint": project.get("project", {}).get("source_fingerprint"),
        "framework": framework,
        "screen_count": len(screens),
        "planning_only": True,
        "capability_coverage": _capability_coverage(
            rules, framework, project, recommendations
        ),
        "recommendations": recommendations,
        "implementation_policy": {
            "sequence": "one-approved-screen-or-flow-at-a-time",
            "requires_screen_plan": True,
            "requires_human_visual_review": True,
            "protected_by_default": [
                "business logic",
                "repositories",
                "services",
                "APIs",
                "analytics",
                "permissions",
                "persistence",
                "navigation destinations",
            ],
        },
        "unresolved_questions": project.get("uncertainties", []),
    }


def create_screen_plan(project: dict[str, Any], screen_id: str) -> dict[str, Any]:
    """Create an approval-required contract for one proven screen."""
    framework, screens = _validate_project(project)
    screen = next(
        (
            item
            for item in screens
            if item.get("id") == screen_id or item.get("name") == screen_id
        ),
        None,
    )
    if screen is None:
        raise PlanError(f"unknown screen id: {screen_id}")
    recommendation = _recommendation(project, screen, framework, _registry())
    allowed = [screen["path"]]
    protected = sorted(set(project.get("source_files", [])) - set(allowed))
    return {
        "format": "mobile-native-screen-plan/1",
        "project_fingerprint": project.get("project", {}).get("source_fingerprint"),
        "screen": {
            "id": screen["id"],
            "name": screen["name"],
            "path": screen["path"],
            "framework": framework,
        },
        "approval": {
            "status": "approval-required",
            "approved_scope": None,
        },
        "current_behavior": recommendation["current_code_evidence"],
        "behavior_invariants": recommendation["behavior_invariants"],
        "selected_capabilities": recommendation["selected_capabilities"],
        "proposed_composition": {
            "screen_job": recommendation["title"],
            "native_implementation": recommendation["native_implementation"],
            "states": ["loading", "empty", "error", "retry", "populated"],
            "copy_policy": "Preserve product meaning; revise only screen-level UI copy included in the approved scope.",
        },
        "motion_contract": recommendation["motion"],
        "accessibility_contract": recommendation["accessibility"],
        "adaptive_contract": [
            "compact width",
            "tablet or expanded width",
            "largest supported text",
            "English LTR",
            "Arabic RTL",
            "safe areas and keyboard",
        ],
        "file_scope": {
            "allowed": allowed,
            "protected": protected,
            "prohibited": [
                "generated dependencies",
                "secrets",
                "build caches",
                "backend code",
            ],
        },
        "tests": recommendation["verification_commands"],
        "acceptance_criteria": recommendation["acceptance_criteria"],
        "stop_conditions": [
            "A required relationship has low confidence.",
            "A behavior change is needed outside the approved scope.",
            "A changed file was already dirty and ownership is ambiguous.",
            "A protected invariant cannot be verified.",
        ],
    }


def _read_json(path: Path) -> dict[str, Any]:
    document = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise PlanError("input JSON must be an object")
    return document


def _write_json(path: Path, document: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    create = subparsers.add_parser("create")
    create.add_argument("project_model", type=Path)
    create.add_argument("--scope", choices=["app"], default="app")
    create.add_argument("--out", required=True, type=Path)
    screen = subparsers.add_parser("screen")
    screen.add_argument("project_model", type=Path)
    screen.add_argument("screen_id")
    screen.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        project = _read_json(args.project_model)
        if args.command == "create":
            plan = create_app_plan(project)
            output = args.out
            output.mkdir(parents=True, exist_ok=True)
            _write_json(output / "app-plan.json", plan)
            for recommendation in plan["recommendations"]:
                screen_plan = create_screen_plan(project, recommendation["screen_id"])
                _write_json(output / "screens" / f"{recommendation['screen_id']}.json", screen_plan)
        else:
            _write_json(args.out, create_screen_plan(project, args.screen_id))
        return 0
    except (OSError, PlanError, ValueError, json.JSONDecodeError) as error:
        print(json.dumps({"ok": False, "error": str(error)}, sort_keys=True), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
