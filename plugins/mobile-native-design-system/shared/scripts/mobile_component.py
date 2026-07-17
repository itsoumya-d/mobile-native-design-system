#!/usr/bin/env python3
"""Validate a native mobile component brief and emit a framework component plan."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


FRAMEWORKS = {"flutter", "react-native", "swiftui", "compose"}
COMPONENTS = {
    "flutter": {
        "button": "ElevatedButton", "icon-button": "IconButton", "field": "TextField",
        "card": "Card", "list-row": "ListTile", "navigation": "NavigationBar",
        "sheet": "showModalBottomSheet", "async-state": "Semantics",
    },
    "react-native": {
        "button": "Pressable", "icon-button": "Pressable", "field": "TextInput",
        "card": "View", "list-row": "FlatList row", "navigation": "native navigation",
        "sheet": "Modal", "async-state": "View",
    },
    "swiftui": {
        "button": "Button", "icon-button": "Button", "field": "TextField",
        "card": "GroupBox", "list-row": "List", "navigation": "NavigationStack",
        "sheet": "sheet", "async-state": "ContentUnavailableView",
    },
    "compose": {
        "button": "Button", "icon-button": "IconButton", "field": "OutlinedTextField",
        "card": "Card", "list-row": "ListItem", "navigation": "NavigationBar",
        "sheet": "ModalBottomSheet", "async-state": "Column",
    },
}
STATES = ["default", "pressed", "focused", "selected", "disabled", "loading", "empty", "error", "retry", "populated"]
ADAPTIVE = {
    "flutter": ["LayoutBuilder", "TextScaler", "SafeArea", "Directionality"],
    "react-native": ["useWindowDimensions", "allowFontScaling", "SafeAreaView", "I18nManager"],
    "swiftui": ["size classes", "dynamic type", "safe area", "layout direction"],
    "compose": ["window size classes", "font scale", "Insets", "layout direction"],
}


def validate_component_brief(brief: dict[str, Any]) -> list[str]:
    required = {"name", "subject", "user_job", "primary_action", "hierarchy", "components"}
    missing = sorted(required - set(brief))
    errors = ["missing fields: " + ", ".join(missing)] if missing else []
    if "components" in brief and not isinstance(brief["components"], list):
        errors.append("components must be a list")
    return errors


def create_plan(brief: dict[str, Any], platform: str) -> dict[str, Any]:
    """Create a complete, dependency-free native component plan."""
    if platform not in FRAMEWORKS:
        raise ValueError(f"unsupported platform: {platform}")
    errors = validate_component_brief(brief)
    if errors:
        raise ValueError("; ".join(errors))
    primitives = COMPONENTS[platform]
    selected = brief["components"]
    components = {
        name: {
            "native_primitive": primitives.get(name, "custom native composition"),
            "states": STATES,
            "accessibility": ["role", "label", "value when relevant", "state announcement"],
            "touch_target": "apple-44pt-or-android-48dp",
            "token_families": ["color", "typography", "spacing", "sizing", "radius", "motion", "haptic"],
        }
        for name in selected
    }
    return {
        "format": "mobile-component-plan/1",
        "name": brief["name"],
        "platform": platform,
        "subject": brief["subject"],
        "user_job": brief["user_job"],
        "primary_action": brief["primary_action"],
        "hierarchy": brief["hierarchy"],
        "signature_interaction": brief.get("signature_interaction", "native press feedback"),
        "design_dials": brief.get("dials", {}),
        "components": components,
        "adaptive_contract": ADAPTIVE[platform],
        "async_contract": ["loading", "empty", "error", "retry", "populated"],
        "motion_contract": "native press feedback with opacity-only or immediate reduced motion",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    validate = subparsers.add_parser("validate")
    validate.add_argument("brief", type=Path)
    generate = subparsers.add_parser("generate")
    generate.add_argument("brief", type=Path)
    generate.add_argument("--platform", required=True, choices=sorted(FRAMEWORKS))
    generate.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        brief = json.loads(args.brief.read_text(encoding="utf-8"))
        if not isinstance(brief, dict):
            raise ValueError("input JSON must be an object")
        if args.command == "validate":
            errors = validate_component_brief(brief)
            print(json.dumps({"ok": not errors, "errors": errors}, sort_keys=True))
            return 0 if not errors else 1
        plan = create_plan(brief, args.platform)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
