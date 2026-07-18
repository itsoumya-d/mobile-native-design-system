#!/usr/bin/env python3
"""Route one request to the smallest mobile-native skill and framework reference."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


FRAMEWORK_TERMS = {
    "flutter": ("flutter", "dart"),
    "react-native": ("react native", "react-native", "expo", "typescript"),
    "swiftui": ("swiftui", "swift", "ios", "iphone", "ipad"),
    "compose": (
        "jetpack compose",
        "compose",
        "kotlin",
        "android",
    ),
}
WEB_TERMS = (
    "next.js",
    "nextjs",
    "tailwind",
    "dom",
    "css",
    "browser",
    "marketing page",
    "website",
    "web app",
)
SKILL_TERMS = (
    (
        "mobile-native-implement",
        (
            "implement",
            "apply the approved",
            "approved screen",
            "approved flow",
            "make the changes",
            "edit the screen",
            "dirty worktree",
        ),
    ),
    (
        "mobile-native-audit",
        (
            "audit",
            "critique",
            "review this screen",
            "accessibility review",
            "performance review",
        ),
    ),
    (
        "mobile-native-plan",
        (
            "plan",
            "roadmap",
            "prioritize",
            "redesign strategy",
            "whole-product redesign",
        ),
    ),
    (
        "mobile-native-understand",
        (
            "understand",
            "scan",
            "inventory",
            "discover",
            "map every",
            "whole codebase",
            "every route",
            "every screen",
        ),
    ),
    (
        "mobile-native-motion",
        (
            "motion",
            "animation",
            "transition",
            "spring",
            "gesture",
            "stagger",
            "shared element",
        ),
    ),
    (
        "mobile-native-component-forge",
        (
            "component",
            "card",
            "button",
            "field",
            "sheet",
            "dialog",
            "loading",
            "empty state",
            "retry",
        ),
    ),
)


def _framework(text: str) -> str:
    matches = [
        framework
        for framework, terms in FRAMEWORK_TERMS.items()
        if any(term in text for term in terms)
    ]
    return matches[0] if len(matches) == 1 else "needs-project-evidence"


def route_request(request: str) -> dict[str, Any]:
    """Return a deterministic progressive-disclosure decision for one request."""
    if not isinstance(request, str) or not request.strip():
        raise ValueError("request must be a non-empty string")
    normalized = " ".join(request.lower().split())
    if any(term in normalized for term in WEB_TERMS):
        return {
            "format": "mobile-native-route/1",
            "scope": "out-of-scope",
            "framework": "not-mobile",
            "skill": None,
            "skills_to_load": [],
            "references": [],
            "reason": "The request explicitly targets a web or browser runtime.",
            "rejected_runtimes": [
                "DOM",
                "CSS",
                "Tailwind",
                "browser",
                "GSAP runtime",
                "Framer Motion runtime",
            ],
        }

    framework = _framework(normalized)
    skill = next(
        (
            candidate
            for candidate, terms in SKILL_TERMS
            if any(term in normalized for term in terms)
        ),
        "mobile-native-understand"
        if framework == "needs-project-evidence"
        else "mobile-native-design-system",
    )
    references = (
        []
        if framework == "needs-project-evidence"
        else [f"references/{framework}.md"]
    )
    return {
        "format": "mobile-native-route/1",
        "scope": "mobile",
        "framework": framework,
        "skill": skill,
        "skills_to_load": [skill],
        "references": references,
        "reason": "Matched the smallest task phase and one native framework adapter.",
        "rejected_runtimes": [
            "DOM",
            "CSS",
            "browser",
            "GSAP runtime",
            "Framer Motion runtime",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("request", nargs="?")
    parser.add_argument("--request-file", type=Path)
    args = parser.parse_args(argv)
    if bool(args.request) == bool(args.request_file):
        parser.error("provide exactly one request string or --request-file")
    try:
        request = (
            args.request_file.read_text(encoding="utf-8")
            if args.request_file
            else args.request
        )
        print(json.dumps(route_request(request), indent=2, sort_keys=True))
        return 0
    except (OSError, ValueError) as error:
        print(json.dumps({"ok": False, "error": str(error)}, sort_keys=True), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
