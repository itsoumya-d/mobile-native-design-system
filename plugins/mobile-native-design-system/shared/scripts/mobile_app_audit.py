#!/usr/bin/env python3
"""Inventory a mobile app, classify its native framework, and audit one screen at a time."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


class AuditError(ValueError):
    """Raised when a project cannot be safely classified."""


IGNORED = {".dart_tool", ".git", ".gradle", ".idea", "Pods", "build", "node_modules", "DerivedData"}
FRAMEWORKS = {"flutter", "react-native", "swiftui", "compose"}
SCREEN_PATTERNS = {
    "flutter": re.compile(r"\b(?:class|function|const)\s+([A-Z][A-Za-z0-9]*(?:Screen|Page|View))\b"),
    "react-native": re.compile(r"\b(?:function|const|class)\s+([A-Z][A-Za-z0-9]*(?:Screen|Page|View))\b"),
    "swiftui": re.compile(r"\b(?:struct|class)\s+([A-Z][A-Za-z0-9]*(?:Screen|Page|View))\b"),
    "compose": re.compile(r"\bfun\s+([A-Z][A-Za-z0-9]*(?:Screen|Page|View))\b"),
}
SEMANTIC_SIGNALS = {
    "flutter": r"\bSemantics\b|semanticLabel|ExcludeSemantics",
    "react-native": r"accessibility(?:Label|Role|State)|AccessibilityInfo",
    "swiftui": r"accessibility(Label|Hint|Value|AddTraits)",
    "compose": r"\.semantics\b|contentDescription|Role\.",
}
ADAPTIVE_SIGNALS = {
    "flutter": r"LayoutBuilder|MediaQuery|SafeArea|TextScaler|Directionality",
    "react-native": r"useWindowDimensions|SafeAreaView|allowFontScaling|I18nManager",
    "swiftui": r"horizontalSizeClass|dynamicTypeSize|safeAreaInset|layoutDirection",
    "compose": r"WindowSizeClass|WindowWidthSizeClass|WindowInsets|LocalLayoutDirection|fontScale",
}
MOTION_SIGNALS = {
    "flutter": r"Animated|AnimationController|Hero|Tween",
    "react-native": r"Animated|Reanimated|LayoutAnimation|Transition",
    "swiftui": r"withAnimation|\.animation\(|transition\(",
    "compose": r"animate[A-Za-z]*AsState|AnimatedVisibility|updateTransition",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def _files(root: Path, suffixes: set[str], bases: tuple[str, ...] = ()) -> list[Path]:
    candidates = [root / base for base in bases if (root / base).exists()] or [root]
    found: set[Path] = set()
    for base in candidates:
        for path in base.rglob("*"):
            if path.is_file() and path.suffix in suffixes and not any(part in IGNORED for part in path.parts):
                found.add(path)
    return sorted(found)


def _dependencies(path: Path) -> set[str]:
    try:
        document = json.loads(_read(path))
    except json.JSONDecodeError as error:
        raise AuditError(f"Invalid package manifest: {path}: {error}") from error
    groups = (document.get("dependencies", {}), document.get("devDependencies", {}))
    if not all(isinstance(group, dict) for group in groups):
        raise AuditError(f"Dependencies must be objects: {path}")
    return set(groups[0]) | set(groups[1])


def _flutter_dependencies(path: Path) -> set[str]:
    return set(re.findall(r"^\s{2}([A-Za-z0-9_]+):", _read(path), re.MULTILINE))


def _detect(root: Path) -> tuple[str, set[str], list[Path]]:
    candidates: list[tuple[str, set[str], list[Path]]] = []
    flutter = root / "pubspec.yaml"
    react = root / "package.json"
    swift_files = _files(root, {".swift"}, ("Sources", "TokenGallery", "App"))
    kotlin_files = _files(root, {".kt"}, ("app", "src"))
    gradle_files = list(root.glob("*gradle.kts")) + list(root.glob("*gradle")) + list((root / "app").glob("*gradle.kts"))

    if flutter.is_file():
        candidates.append(("flutter", _flutter_dependencies(flutter), _files(root, {".dart"}, ("lib",))))
    if react.is_file():
        files = _files(root, {".ts", ".tsx", ".js", ".jsx"}, ("src",))
        files += [path for path in (root / "App.tsx", root / "App.ts", root / "index.js") if path.is_file()]
        candidates.append(("react-native", _dependencies(react), sorted(set(files))))
    if swift_files and (list(root.glob("*.xcodeproj")) or list(root.glob("*.xcworkspace")) or (root / "Package.swift").is_file()):
        candidates.append(("swiftui", set(), swift_files))
    if kotlin_files and gradle_files and any("@Composable" in _read(path) for path in kotlin_files):
        candidates.append(("compose", set(), kotlin_files))

    if not candidates:
        raise AuditError(f"unsupported project: expected Flutter, React Native, SwiftUI, or Compose manifest in {root}")
    if len(candidates) != 1:
        raise AuditError("A project must expose exactly one mobile framework manifest")
    return candidates[0]


def _capability(identifier: str, priority: int, sources: list[str], use_when: str, action: str) -> dict[str, Any]:
    return {"id": identifier, "priority": priority, "sources": sources, "use_when": use_when, "action": action}


def _capabilities(framework: str, dependencies: set[str]) -> list[dict[str, Any]]:
    capabilities = [
        _capability("design-direction", 100, ["frontend-design", "ui-ux-pro-max", "design-taste-frontend"], "A screen needs a clearer subject or hierarchy.", "Write a native screen brief and design dials before visual edits."),
        _capability("token-contract", 100, ["ui-ux-pro-max"], "Values repeat or drift.", "Move validated intent to the token contract and check typed adapter parity."),
        _capability("native-motion", 90, ["gsap-master", "motion-framer"], "An interaction needs continuity.", "Translate state and timing intent to the framework's native animation APIs."),
        _capability("accessibility-and-adaptive", 100, ["frontend-design", "design-taste-frontend"], "Any interactive screen changes.", "Check semantics, focus, target size, scale, RTL, insets, keyboard, and width classes."),
        _capability("visual-and-semantic-testing", 100, ["ui-ux-pro-max"], "The screen is ready for verification.", "Run local tests and visual baselines; require semantic, not cross-platform pixel, parity."),
    ]
    framework_action = {
        "flutter": "Use Material or Cupertino primitives, ThemeExtension, LayoutBuilder, TextScaler, Semantics, and native animation.",
        "react-native": "Use native controls, list virtualization, accessibility props, native navigation, and animation APIs.",
        "swiftui": "Use semantic text, environment values, size classes, system navigation, sheets, and accessibility modifiers.",
        "compose": "Use Material3, immutable UI state, window size classes, semantics, Insets, and Compose animations.",
    }[framework]
    capabilities.append(_capability(f"{framework}-native-components", 95, ["mobile-original"], f"A {framework} screen is being built or upgraded.", framework_action))
    if framework == "react-native":
        capabilities.extend([
            _capability("react-native-registry", 80, ["shadcn-ui-mcp-server"], "A compatible native component shape is needed.", "Use registry metadata only for discovery, then apply local tokens and native tests."),
            _capability("react-native-performance", 90, ["vercel-react-best-practices", "vercel-react-native-skills"], "Lists, images, or rendering need measurement.", "Profile native behavior before applying state or render optimizations."),
        ])
        if "expo" in dependencies:
            capabilities.append(_capability("expo-routing", 80, ["vercel-react-native-skills"], "Expo is declared.", "Enable Expo-specific guidance only in this project."))
    if "convex" in dependencies:
        capabilities.append(_capability("convex-boundary", 85, ["convex-create-component"], "The app declares Convex.", "Keep typed async UI state at the component boundary."))
    return sorted(capabilities, key=lambda item: (-item["priority"], item["id"]))


def _screen_records(root: Path, files: list[Path], framework: str) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    pattern = SCREEN_PATTERNS[framework]
    for path in files:
        text = _read(path)
        names = (
            re.findall(r"@Composable\s+(?:private\s+)?fun\s+([A-Z][A-Za-z0-9_]*)", text)
            if framework == "compose"
            else pattern.findall(text)
        )
        if not names and path.stem.lower() in {"main", "app", "contentview"}:
            names = [path.stem.title()]
        for name in names:
            records.append({
                "name": name,
                "path": path.relative_to(root).as_posix(),
                "signals": {
                    "motion": bool(re.search(MOTION_SIGNALS[framework], text)),
                    "adaptive": bool(re.search(ADAPTIVE_SIGNALS[framework], text)),
                    "accessibility": bool(re.search(SEMANTIC_SIGNALS[framework], text)),
                    "async_states": bool(re.search(r"loading|error|empty|retry", text, re.IGNORECASE)),
                },
            })
    return records


def _finding(identifier: str, level: str, path: Path, message: str) -> dict[str, str]:
    return {"id": identifier, "evidence_level": level, "path": path.as_posix(), "message": message}


def _findings(root: Path, files: list[Path], framework: str, profile: str) -> list[dict[str, str]]:
    if profile not in {"quick", "full"}:
        raise AuditError("profile must be quick or full")
    findings: list[dict[str, str]] = []
    for path in files:
        text = _read(path)
        relative = path.relative_to(root)
        if not re.search(SEMANTIC_SIGNALS[framework], text):
            findings.append(_finding("accessibility.semantic-review", "heuristic", relative, "Review semantic role, label, state, and focus order for this screen source."))
        if profile == "full" and not re.search(ADAPTIVE_SIGNALS[framework], text):
            findings.append(_finding("adaptive.layout-review", "heuristic", relative, "Review text scaling, RTL, insets, and compact through tablet layout behavior."))
        if re.search(r"(?:width|height|frame|SizedBox)\s*[:(].{0,30}(?:[3-9]\d\d|[1-9]\d{3})", text):
            findings.append(_finding("layout.fixed-extent", "proven", relative, "A large fixed extent was found; verify it does not clip at large text or tablet widths."))
        if framework == "react-native" and "FlatList" in text and "keyExtractor" not in text:
            findings.append(_finding("react-native.list-key-review", "heuristic", relative, "Review stable keys for the native virtualized list."))
    return sorted(findings, key=lambda item: (item["path"], item["id"], item["evidence_level"]))


def audit_project(project_root: Path | str, profile: str = "quick") -> dict[str, Any]:
    """Return a deterministic report without changing project files."""
    root = Path(project_root).resolve()
    if not root.is_dir():
        raise AuditError(f"Project root does not exist: {root}")
    framework, dependencies, files = _detect(root)
    return {
        "format": "mobile-native-app-audit/2",
        "project": str(root),
        "framework": framework,
        "profile": profile,
        "screens": _screen_records(root, files, framework),
        "source_files": [path.relative_to(root).as_posix() for path in files],
        "capabilities": _capabilities(framework, dependencies),
        "findings": _findings(root, files, framework, profile),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("projects", nargs="+", type=Path)
    parser.add_argument("--profile", choices=["quick", "full"], default="quick")
    parser.add_argument("--out", type=Path, help="Write JSON report to this path")
    args = parser.parse_args(argv)
    try:
        report = {"projects": [audit_project(project, profile=args.profile) for project in args.projects]}
        rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
        if args.out:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(rendered, encoding="utf-8")
        else:
            print(rendered, end="")
        return 0
    except AuditError as error:
        print(json.dumps({"ok": False, "error": str(error)}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
