#!/usr/bin/env python3
"""Scan a native mobile project into a deterministic, evidence-backed product model."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable


class ProjectError(ValueError):
    """Raised when a project cannot be modeled safely."""


FRAMEWORKS = {"flutter", "react-native", "swiftui", "compose"}
IGNORED_PARTS = {
    ".dart_tool",
    ".git",
    ".gradle",
    ".idea",
    ".swiftpm",
    ".vscode",
    "DerivedData",
    "Pods",
    "__pycache__",
    "build",
    "coverage",
    "dist",
    "generated",
    "node_modules",
    "vendor",
}
SECRET_NAMES = {
    ".env",
    ".env.local",
    ".env.production",
    "google-services.json",
    "GoogleService-Info.plist",
    "key.properties",
}
SOURCE_SUFFIXES = {
    "flutter": {".dart"},
    "react-native": {".js", ".jsx", ".ts", ".tsx"},
    "swiftui": {".swift"},
    "compose": {".kt"},
}
TEST_MARKERS = {"test", "tests", "__tests__", "androidTest", "uiTest", "uitests"}
ASSET_SUFFIXES = {
    ".avif",
    ".gif",
    ".heic",
    ".jpeg",
    ".jpg",
    ".json",
    ".lottie",
    ".pdf",
    ".png",
    ".svg",
    ".ttf",
    ".webp",
    ".xcassets",
}
LOCALIZATION_SUFFIXES = {".arb", ".strings", ".stringsdict", ".xcstrings"}
CONFIDENCE = {"high", "medium", "low"}

SCREEN_PATTERNS = {
    "flutter": re.compile(
        r"\bclass\s+([A-Z][A-Za-z0-9_]*)\s+extends\s+(?:Consumer|HookConsumer|Stateful|Stateless)Widget\b"
    ),
    "react-native": re.compile(
        r"\b(?:export\s+(?:default\s+)?)?(?:function|class|const)\s+([A-Z][A-Za-z0-9_]*)\b"
    ),
    "swiftui": re.compile(r"\bstruct\s+([A-Z][A-Za-z0-9_]*)\s*:\s*View\b"),
    "compose": re.compile(
        r"@Composable(?:\s+@[A-Za-z0-9_.()]+)*\s+(?:private\s+|internal\s+|public\s+)?fun\s+([A-Z][A-Za-z0-9_]*)\b"
    ),
}
COMPONENT_HINTS = (
    "Button",
    "Card",
    "Dialog",
    "Field",
    "Form",
    "Grid",
    "Image",
    "List",
    "Modal",
    "Navigation",
    "Row",
    "Search",
    "Sheet",
    "Tab",
    "Text",
)
SCREEN_HINTS = ("App", "Detail", "Flow", "Home", "Page", "Root", "Screen", "Settings", "View")

STATE_MARKERS = {
    "flutter": {
        "riverpod": ("flutter_riverpod", "ConsumerWidget", "WidgetRef", "ref.watch"),
        "bloc": ("flutter_bloc", "BlocBuilder", "Cubit"),
        "provider": ("package:provider", "ChangeNotifierProvider", "context.watch"),
        "getx": ("package:get", "GetX", "Obx"),
        "set-state": ("setState(",),
    },
    "react-native": {
        "redux": ("@reduxjs/toolkit", "useSelector", "useDispatch"),
        "zustand": ("zustand", "create("),
        "mobx": ("mobx", "observer("),
        "context": ("createContext", "useContext"),
        "react-state": ("useState", "useReducer"),
    },
    "swiftui": {
        "observation": ("@Observable", "@Bindable"),
        "combine": ("ObservableObject", "@Published"),
        "environment": ("@Environment", "@EnvironmentObject"),
        "swiftui-state": ("@State", "@StateObject"),
    },
    "compose": {
        "stateflow": ("StateFlow", "collectAsStateWithLifecycle", "MutableStateFlow"),
        "viewmodel": ("ViewModel", "viewModel("),
        "compose-state": ("remember", "mutableStateOf", "derivedStateOf"),
    },
}

NAVIGATION_MARKERS = {
    "flutter": ("GoRoute(", "context.go(", "context.push(", "Navigator.", "AutoRoute"),
    "react-native": ("Stack.Screen", "Tabs.Screen", "navigation.navigate(", "router.push(", "router.replace("),
    "swiftui": ("NavigationStack", "NavigationSplitView", "NavigationLink", ".navigationDestination", ".sheet(", "TabView"),
    "compose": ("NavHost(", "composable(", "navController.navigate(", "ModalBottomSheet", "NavigationBar"),
}

ACCESSIBILITY_MARKERS = {
    "flutter": ("Semantics", "semanticLabel", "ExcludeSemantics", "Tooltip"),
    "react-native": ("accessibilityLabel", "accessibilityRole", "accessibilityState", "AccessibilityInfo"),
    "swiftui": (".accessibilityLabel", ".accessibilityHint", ".accessibilityValue", ".accessibilityAddTraits"),
    "compose": (".semantics", "contentDescription", "Role.", "clearAndSetSemantics"),
}

ADAPTIVE_MARKERS = {
    "flutter": ("LayoutBuilder", "MediaQuery", "SafeArea", "TextScaler", "Directionality"),
    "react-native": ("useWindowDimensions", "SafeAreaView", "allowFontScaling", "I18nManager"),
    "swiftui": ("horizontalSizeClass", "dynamicTypeSize", "safeAreaInset", "layoutDirection"),
    "compose": ("WindowSizeClass", "WindowWidthSizeClass", "WindowInsets", "LocalLayoutDirection", "fontScale"),
}

MOTION_MARKERS = {
    "flutter": ("Animated", "AnimationController", "Hero(", "Tween", "GestureDetector"),
    "react-native": ("Animated", "Reanimated", "LayoutAnimation", "GestureDetector"),
    "swiftui": ("withAnimation", ".animation(", ".transition(", "matchedGeometryEffect"),
    "compose": ("animate", "AnimatedVisibility", "updateTransition", "sharedElement"),
}

ASYNC_MARKERS = ("loading", "empty", "error", "retry", "success", "populated", "refresh")

BEHAVIOR_PATTERNS = (
    ("analytics", re.compile(r"\b(?:analytics|Analytics|telemetry|Telemetry)\b|\.track\s*\(|\.logEvent\s*\(")),
    ("permission", re.compile(r"\b(?:permission|Permission|requestAuthorization|requestPermission)\b")),
    (
        "persistence",
        re.compile(
            r"\b(?:SharedPreferences|UserDefaults|DataStore|AsyncStorage|secure[_A-Z]|Keychain)\b|"
            r"\.(?:persist|store|write|save)\s*\("
        ),
    ),
    (
        "data-write",
        re.compile(
            r"\b(?:Repository|repository|mutation|Mutation)\b|"
            r"\.(?:create|delete|insert|refresh|remove|save|submit|sync|update|write)\s*\("
        ),
    ),
    (
        "navigation",
        re.compile(
            r"\bNavigator\.|context\.(?:go|push|pop)\s*\(|navigation\.(?:navigate|goBack|push|replace)\s*\(|"
            r"router\.(?:push|replace|back)\s*\(|navController\.navigate\s*\(|NavigationLink\s*\(|"
            r"\bpath\.append\s*\("
        ),
    ),
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def _hash_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _ignored(path: Path, root: Path) -> bool:
    try:
        parts = path.relative_to(root).parts
    except ValueError:
        return True
    return (
        any(part in IGNORED_PARTS for part in parts)
        or path.name in SECRET_NAMES
        or path.name.startswith(".env.")
    )


def _walk_files(root: Path, suffixes: set[str] | None = None) -> list[Path]:
    found: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file() or _ignored(path, root):
            continue
        if suffixes is not None and path.suffix.lower() not in suffixes:
            continue
        found.append(path)
    return sorted(found, key=lambda item: _relative(item, root))


def _manifest_dependencies(root: Path, framework: str) -> tuple[list[str], dict[str, str]]:
    if framework == "flutter":
        text = _read(root / "pubspec.yaml")
        dependencies: list[str] = []
        versions: dict[str, str] = {}
        section = ""
        for line in text.splitlines():
            if re.match(r"^[A-Za-z][A-Za-z0-9_]*:\s*$", line):
                section = line.split(":", 1)[0]
                continue
            match = re.match(r"^  ([A-Za-z0-9_]+):(?:\s*(.*))?$", line)
            if section == "dependencies" and match:
                name, version = match.group(1), (match.group(2) or "sdk").strip()
                dependencies.append(name)
                versions[name] = version or "sdk"
        sdk = re.search(r'^\s+sdk:\s*["\']?([^"\']+)', text, re.MULTILINE)
        if sdk:
            versions["dart-sdk"] = sdk.group(1).strip()
        return sorted(set(dependencies)), dict(sorted(versions.items()))

    if framework == "react-native":
        try:
            document = json.loads(_read(root / "package.json"))
        except json.JSONDecodeError as error:
            raise ProjectError(f"invalid package.json: {error}") from error
        dependencies: dict[str, Any] = {}
        for key in ("dependencies", "devDependencies"):
            group = document.get(key, {})
            if isinstance(group, dict):
                dependencies.update(group)
        return sorted(dependencies), {
            str(name): str(version) for name, version in sorted(dependencies.items())
        }

    manifest_text = "\n".join(
        _read(path)
        for path in _walk_files(root)
        if path.name in {"Package.swift", "build.gradle", "build.gradle.kts", "libs.versions.toml"}
    )
    quoted = re.findall(
        r"(?:implementation|api|package|dependency)\s*\(?\s*[\"']([^\"']+)[\"']",
        manifest_text,
        re.IGNORECASE,
    )
    dependencies = sorted(set(quoted))
    return dependencies, {item: "declared" for item in dependencies}


def _detect_framework(root: Path) -> str:
    pubspec = root / "pubspec.yaml"
    package = root / "package.json"
    if pubspec.is_file():
        return "flutter"
    if package.is_file():
        try:
            document = json.loads(_read(package))
        except json.JSONDecodeError as error:
            raise ProjectError(f"invalid package.json: {error}") from error
        dependencies = {
            **(document.get("dependencies", {}) if isinstance(document.get("dependencies"), dict) else {}),
            **(document.get("devDependencies", {}) if isinstance(document.get("devDependencies"), dict) else {}),
        }
        if "react-native" in dependencies or "expo" in dependencies:
            return "react-native"
    swift = _walk_files(root, {".swift"})
    if swift and (
        (root / "Package.swift").is_file()
        or any(path.suffix in {".xcodeproj", ".xcworkspace"} for path in root.iterdir())
        or any(path.name.endswith(".xcodeproj") for path in root.iterdir())
    ):
        return "swiftui"
    kotlin = _walk_files(root, {".kt"})
    gradle = any(
        path.name in {"build.gradle", "build.gradle.kts", "settings.gradle", "settings.gradle.kts"}
        for path in root.iterdir()
        if path.is_file()
    )
    if kotlin and gradle and any("@Composable" in _read(path) for path in kotlin):
        return "compose"
    raise ProjectError(
        "unsupported or ambiguous project: expected one Flutter, React Native, SwiftUI, or Compose root"
    )


def _source_files(root: Path, framework: str) -> list[Path]:
    files = _walk_files(root, SOURCE_SUFFIXES[framework])
    if framework == "flutter":
        files = [path for path in files if "lib" in path.relative_to(root).parts]
    elif framework == "react-native":
        files = [
            path
            for path in files
            if not {"android", "ios"}.intersection(path.relative_to(root).parts)
            and not any(part in TEST_MARKERS for part in path.relative_to(root).parts)
        ]
    elif framework == "swiftui":
        files = [
            path
            for path in files
            if not any(part in TEST_MARKERS for part in path.relative_to(root).parts)
        ]
    elif framework == "compose":
        files = [
            path
            for path in files
            if "main" in path.relative_to(root).parts
            and not any(part in TEST_MARKERS for part in path.relative_to(root).parts)
        ]
    return sorted(files, key=lambda item: _relative(item, root))


def _evidence(
    root: Path,
    path: Path,
    line_number: int,
    symbol: str,
    kind: str,
    confidence: str,
    evidence_type: str,
    line: str,
) -> dict[str, Any]:
    if confidence not in CONFIDENCE:
        raise ProjectError(f"invalid confidence: {confidence}")
    return {
        "path": _relative(path, root),
        "line": line_number,
        "symbol": symbol,
        "kind": kind,
        "confidence": confidence,
        "evidence_type": evidence_type,
        "excerpt_hash": _hash_text(line.strip()),
    }


def _definition_line(text: str, symbol: str) -> int:
    match = re.search(rf"\b{re.escape(symbol)}\b", text)
    return text.count("\n", 0, match.start()) + 1 if match else 1


def _screen_candidates(
    root: Path, files: list[Path], framework: str
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    screens: list[dict[str, Any]] = []
    evidence: list[dict[str, Any]] = []
    pattern = SCREEN_PATTERNS[framework]
    for path in files:
        text = _read(path)
        names = pattern.findall(text)
        for name in names:
            is_screen = name.endswith(SCREEN_HINTS) or path.stem.lower() in {
                "app",
                "main",
                "contentview",
            }
            if not is_screen and any(name.endswith(hint) for hint in COMPONENT_HINTS):
                continue
            line_number = _definition_line(text, name)
            signals = {
                "navigation": any(marker in text for marker in NAVIGATION_MARKERS[framework]),
                "accessibility": any(marker in text for marker in ACCESSIBILITY_MARKERS[framework]),
                "adaptive": any(marker in text for marker in ADAPTIVE_MARKERS[framework]),
                "motion": any(marker in text for marker in MOTION_MARKERS[framework]),
                "async_states": any(marker in text.lower() for marker in ASYNC_MARKERS),
            }
            record = {
                "id": name,
                "name": name,
                "path": _relative(path, root),
                "entry_point": name.endswith(("App", "Root")) or path.stem.lower() in {"app", "main"},
                "signals": signals,
                "confidence": "high",
                "evidence": {
                    "path": _relative(path, root),
                    "line": line_number,
                    "symbol": name,
                    "evidence_type": "parser",
                },
            }
            screens.append(record)
            evidence.append(
                _evidence(root, path, line_number, name, "screen", "high", "parser", name)
            )
    unique = {screen["id"]: screen for screen in screens}
    return [unique[key] for key in sorted(unique)], evidence


def _route_records(
    root: Path, files: list[Path], framework: str
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    routes: list[dict[str, Any]] = []
    evidence: list[dict[str, Any]] = []
    for path in files:
        text = _read(path)
        if framework == "flutter":
            for match in re.finditer(r"\bGoRoute\s*\(\s*path:\s*['\"]([^'\"]+)['\"]", text):
                tail = text[match.start() : match.start() + 500]
                name = re.search(r"\bname:\s*['\"]([^'\"]+)['\"]", tail)
                target = re.search(r"=>\s*(?:const\s+)?([A-Z][A-Za-z0-9_]*)\s*\(", tail)
                line_number = text.count("\n", 0, match.start()) + 1
                routes.append(
                    {
                        "id": name.group(1) if name else match.group(1),
                        "path": match.group(1),
                        "kind": "route",
                        "destination": target.group(1) if target else None,
                        "source_path": _relative(path, root),
                        "line": line_number,
                        "confidence": "high",
                    }
                )
                evidence.append(
                    _evidence(
                        root,
                        path,
                        line_number,
                        match.group(1),
                        "route",
                        "high",
                        "parser",
                        match.group(0),
                    )
                )
            for match in re.finditer(
                r"['\"](/[^'\"]*)['\"]\s*:\s*\([^)]*\)\s*=>\s*(?:const\s+)?([A-Z][A-Za-z0-9_]*)\s*\(",
                text,
            ):
                line_number = text.count("\n", 0, match.start()) + 1
                routes.append(
                    {
                        "id": match.group(1),
                        "path": match.group(1),
                        "kind": "route",
                        "destination": match.group(2),
                        "source_path": _relative(path, root),
                        "line": line_number,
                        "confidence": "high",
                    }
                )
                evidence.append(
                    _evidence(
                        root,
                        path,
                        line_number,
                        match.group(1),
                        "route",
                        "high",
                        "parser",
                        match.group(0),
                    )
                )
        elif framework == "react-native":
            for match in re.finditer(
                r"<(?:Stack|Tabs)\.Screen\b[^>]*\bname=['\"]([^'\"]+)['\"][^>]*>", text
            ):
                component = re.search(r"\bcomponent=\{([A-Z][A-Za-z0-9_]*)\}", match.group(0))
                line_number = text.count("\n", 0, match.start()) + 1
                routes.append(
                    {
                        "id": match.group(1),
                        "path": match.group(1),
                        "kind": "route",
                        "destination": component.group(1) if component else None,
                        "source_path": _relative(path, root),
                        "line": line_number,
                        "confidence": "high",
                    }
                )
                evidence.append(
                    _evidence(
                        root,
                        path,
                        line_number,
                        match.group(1),
                        "route",
                        "high",
                        "parser",
                        match.group(0),
                    )
                )
            for match in re.finditer(
                r"\{\s*name:\s*['\"]([^'\"]+)['\"]\s*,\s*component:\s*([A-Z][A-Za-z0-9_]*)\s*\}",
                text,
            ):
                line_number = text.count("\n", 0, match.start()) + 1
                routes.append(
                    {
                        "id": match.group(1),
                        "path": match.group(1),
                        "kind": "route",
                        "destination": match.group(2),
                        "source_path": _relative(path, root),
                        "line": line_number,
                        "confidence": "high",
                    }
                )
                evidence.append(
                    _evidence(
                        root,
                        path,
                        line_number,
                        match.group(1),
                        "route",
                        "high",
                        "parser",
                        match.group(0),
                    )
                )
        elif framework == "swiftui":
            for marker, kind in (
                ("NavigationStack", "navigation-root"),
                ("NavigationSplitView", "navigation-root"),
                ("TabView", "tab-root"),
                (".sheet(", "sheet"),
            ):
                for index, line in enumerate(text.splitlines(), start=1):
                    if marker in line:
                        identifier = f"{path.stem}:{kind}:{index}"
                        routes.append(
                            {
                                "id": identifier,
                                "path": identifier,
                                "kind": kind,
                                "destination": None,
                                "source_path": _relative(path, root),
                                "line": index,
                                "confidence": "medium",
                            }
                        )
                        evidence.append(
                            _evidence(root, path, index, marker, "route", "medium", "pattern", line)
                        )
            product_route = re.search(
                r"\benum\s+ProductRoute\b[^{]*\{(?P<body>.*?)\n\}",
                text,
                re.DOTALL,
            )
            if product_route:
                body = product_route.group("body")
                for case_match in re.finditer(
                    r"^\s*case\s+([A-Za-z0-9_, ]+)",
                    body,
                    re.MULTILINE,
                ):
                    prefix = body[: case_match.start()]
                    line_number = (
                        text.count("\n", 0, product_route.start("body"))
                        + prefix.count("\n")
                        + 1
                    )
                    for name in re.findall(r"[A-Za-z][A-Za-z0-9_]*", case_match.group(1)):
                        routes.append(
                            {
                                "id": name,
                                "path": name,
                                "kind": "route",
                                "destination": f"{name[:1].upper()}{name[1:]}Screen",
                                "source_path": _relative(path, root),
                                "line": line_number,
                                "confidence": "high",
                            }
                        )
                        evidence.append(
                            _evidence(
                                root,
                                path,
                                line_number,
                                name,
                                "route",
                                "high",
                                "parser",
                                case_match.group(0),
                            )
                        )
        else:
            for match in re.finditer(r"\bcomposable\s*\(\s*['\"]([^'\"]+)['\"]", text):
                line_number = text.count("\n", 0, match.start()) + 1
                routes.append(
                    {
                        "id": match.group(1),
                        "path": match.group(1),
                        "kind": "route",
                        "destination": None,
                        "source_path": _relative(path, root),
                        "line": line_number,
                        "confidence": "high",
                    }
                )
                evidence.append(
                    _evidence(
                        root,
                        path,
                        line_number,
                        match.group(1),
                        "route",
                        "high",
                        "parser",
                        match.group(0),
                    )
                )
            product_route = re.search(
                r"\benum\s+class\s+ProductRoute\s*\{(?P<body>.*?)\}",
                text,
                re.DOTALL,
            )
            if product_route:
                body = product_route.group("body")
                for name_match in re.finditer(r"\b([A-Z][A-Za-z0-9_]*)\s*,?", body):
                    name = name_match.group(1)
                    line_number = (
                        text.count("\n", 0, product_route.start("body"))
                        + body[: name_match.start()].count("\n")
                        + 1
                    )
                    routes.append(
                        {
                            "id": name,
                            "path": name,
                            "kind": "route",
                            "destination": f"{name}Screen",
                            "source_path": _relative(path, root),
                            "line": line_number,
                            "confidence": "high",
                        }
                    )
                    evidence.append(
                        _evidence(
                            root,
                            path,
                            line_number,
                            name,
                            "route",
                            "high",
                            "parser",
                            name_match.group(0),
                        )
                    )
    keyed = {(item["id"], item["source_path"], item["line"]): item for item in routes}
    return [keyed[key] for key in sorted(keyed)], evidence


def _behavior_contract(
    root: Path, files: list[Path], framework: str
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    actions: list[dict[str, Any]] = []
    evidence: list[dict[str, Any]] = []
    services: set[str] = set()
    repositories: set[str] = set()
    state_transitions: list[dict[str, Any]] = []
    for path in files:
        text = _read(path)
        lines = text.splitlines()
        for line_number, line in enumerate(lines, start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith("//"):
                continue
            for kind, pattern in BEHAVIOR_PATTERNS:
                if not pattern.search(stripped):
                    continue
                symbol_match = re.search(
                    r"([A-Za-z_][A-Za-z0-9_.]*(?:\([^;{}]*\))?)", stripped
                )
                symbol = symbol_match.group(1) if symbol_match else kind
                action = {
                    "id": f"{_relative(path, root)}:{line_number}:{kind}",
                    "kind": kind,
                    "path": _relative(path, root),
                    "line": line_number,
                    "symbol": symbol,
                    "statement_hash": _hash_text(re.sub(r"\s+", " ", stripped)),
                    "confidence": "high" if kind in {"navigation", "analytics"} else "medium",
                }
                actions.append(action)
                evidence.append(
                    _evidence(
                        root,
                        path,
                        line_number,
                        symbol,
                        f"behavior.{kind}",
                        action["confidence"],
                        "pattern",
                        stripped,
                    )
                )
            for match in re.findall(r"\b([A-Z][A-Za-z0-9_]*(?:Service|Client|Api))\b", stripped):
                services.add(match)
            for match in re.findall(r"\b([A-Z][A-Za-z0-9_]*Repository)\b", stripped):
                repositories.add(match)
            if re.search(r"\b(?:setState|dispatch|emit|send|reduce|mutableStateOf)\b", stripped):
                state_transitions.append(
                    {
                        "path": _relative(path, root),
                        "line": line_number,
                        "statement_hash": _hash_text(re.sub(r"\s+", " ", stripped)),
                    }
                )
    actions = sorted(
        {(item["kind"], item["path"], item["line"], item["statement_hash"]): item for item in actions}.values(),
        key=lambda item: (item["path"], item["line"], item["kind"]),
    )
    invariants = [
        {
            "id": f"preserve-{action['kind']}-{index + 1}",
            "kind": action["kind"],
            "description": f"Preserve the {action['kind']} behavior owned by {action['path']}.",
            "evidence": {
                "path": action["path"],
                "line": action["line"],
                "symbol": action["symbol"],
            },
            "signature": action["statement_hash"],
        }
        for index, action in enumerate(actions)
    ]
    return (
        {
            "format": "mobile-native-behavior-contract/1",
            "actions": actions,
            "state_transitions": sorted(
                state_transitions, key=lambda item: (item["path"], item["line"])
            ),
            "data_boundaries": sorted(repositories),
            "services": sorted(services),
            "permissions": [item for item in actions if item["kind"] == "permission"],
            "analytics": [item for item in actions if item["kind"] == "analytics"],
            "persistence": [item for item in actions if item["kind"] == "persistence"],
            "side_effects": [
                item
                for item in actions
                if item["kind"] in {"analytics", "data-write", "navigation", "permission", "persistence"}
            ],
            "invariants": invariants,
        },
        evidence,
    )


def _architecture(files: list[Path], framework: str, dependencies: Iterable[str]) -> dict[str, Any]:
    combined = "\n".join(_read(path) for path in files)
    state = [
        name
        for name, markers in STATE_MARKERS[framework].items()
        if any(marker in combined or marker in dependencies for marker in markers)
    ]
    layers: list[str] = []
    lowered_paths = [path.as_posix().lower() for path in files]
    for name in ("data", "domain", "feature", "repository", "service", "ui"):
        if any(f"/{name}" in path or f"/{name}s/" in path for path in lowered_paths):
            layers.append(name)
    return {
        "state_management": sorted(state),
        "layers": sorted(set(layers)),
        "navigation_markers": [
            marker for marker in NAVIGATION_MARKERS[framework] if marker in combined
        ],
    }


def _components(root: Path, files: list[Path], framework: str) -> list[dict[str, Any]]:
    components: list[dict[str, Any]] = []
    pattern = SCREEN_PATTERNS[framework]
    for path in files:
        text = _read(path)
        for name in pattern.findall(text):
            if name.endswith(SCREEN_HINTS):
                continue
            if any(hint in name for hint in COMPONENT_HINTS):
                components.append(
                    {
                        "name": name,
                        "path": _relative(path, root),
                        "line": _definition_line(text, name),
                    }
                )
    return sorted(components, key=lambda item: (item["name"], item["path"]))


def _design_language(root: Path, files: list[Path], framework: str) -> dict[str, Any]:
    combined = "\n".join(_read(path) for path in files)
    colors = sorted(
        set(
            re.findall(r"#[0-9A-Fa-f]{6,8}", combined)
            + re.findall(r"0x[A-Fa-f0-9]{8}", combined)
            + re.findall(r"\bColor\.[A-Za-z0-9_]+", combined)
            + re.findall(r"\bColors\.[A-Za-z0-9_]+", combined)
        )
    )
    typography = sorted(
        set(
            re.findall(
                r"\b(?:TextTheme|TextStyle|Font\.|fontSize|fontWeight|MaterialTheme\.typography|Typography)\b[^\n,;)]*",
                combined,
            )
        )
    )[:80]
    spacing = sorted(
        set(
            re.findall(
                r"\b(?:padding|spacing|gap|EdgeInsets|Spacer|Arrangement\.spacedBy)\b[^\n,;)]*",
                combined,
                re.IGNORECASE,
            )
        )
    )[:80]
    shapes = sorted(
        set(
            re.findall(
                r"\b(?:BorderRadius|RoundedRectangle|RoundedCornerShape|Capsule|Circle|cornerRadius)\b[^\n,;)]*",
                combined,
            )
        )
    )[:80]
    icons = sorted(
        set(
            re.findall(
                r"\b(?:Icons|Image|Icon|systemName)\s*[\[(.:][^\n,;)]*",
                combined,
            )
        )
    )[:80]
    motion = sorted(
        marker for marker in MOTION_MARKERS[framework] if marker in combined
    )
    raw_value_count = len(re.findall(r"\b(?:padding|fontSize|cornerRadius)\s*[:(]\s*\d+", combined))
    inconsistencies: list[dict[str, Any]] = []
    if len(colors) > 12:
        inconsistencies.append(
            {
                "id": "color.raw-value-sprawl",
                "evidence_level": "heuristic",
                "message": "Many raw color values were found; verify semantic token ownership.",
                "count": len(colors),
            }
        )
    if raw_value_count > 12:
        inconsistencies.append(
            {
                "id": "scale.raw-value-sprawl",
                "evidence_level": "heuristic",
                "message": "Repeated raw dimensions may indicate an inconsistent scale.",
                "count": raw_value_count,
            }
        )
    return {
        "format": "mobile-native-design-language/1",
        "framework": framework,
        "typography": typography,
        "colors": colors,
        "spacing": spacing,
        "shapes": shapes,
        "iconography": icons,
        "density": {
            "raw_dimension_count": raw_value_count,
            "signal": "compact" if raw_value_count > 20 else "undetermined",
        },
        "components": sorted(
            set(re.findall(r"\b[A-Z][A-Za-z0-9_]*(?:Button|Card|Field|Row|Tile|Sheet|Dialog)\b", combined))
        ),
        "motion_grammar": motion,
        "accessibility_primitives": [
            marker for marker in ACCESSIBILITY_MARKERS[framework] if marker in combined
        ],
        "adaptive_primitives": [
            marker for marker in ADAPTIVE_MARKERS[framework] if marker in combined
        ],
        "inconsistencies": inconsistencies,
    }


def _assets(root: Path) -> list[dict[str, str]]:
    assets: list[dict[str, str]] = []
    for path in _walk_files(root):
        relative = path.relative_to(root)
        lowered = {part.lower() for part in relative.parts}
        if (
            "assets" in lowered
            or (
                "res" in lowered
                and path.suffix.lower() in ASSET_SUFFIXES
            )
            or "xcassets" in path.as_posix().lower()
        ):
            assets.append({"path": relative.as_posix(), "kind": path.suffix.lower() or "asset"})
    return assets


def _localization(root: Path) -> list[dict[str, str]]:
    localized: list[dict[str, str]] = []
    for path in _walk_files(root):
        relative = path.relative_to(root)
        if path.suffix.lower() in LOCALIZATION_SUFFIXES or (
            path.name == "strings.xml" and "values" in relative.as_posix()
        ):
            localized.append({"path": relative.as_posix(), "kind": path.suffix.lower() or "xml"})
        elif path.suffix.lower() == ".json" and any(
            part.lower() in {"i18n", "l10n", "locale", "locales"} for part in relative.parts
        ):
            localized.append({"path": relative.as_posix(), "kind": "json"})
    return localized


def _tests(root: Path) -> list[dict[str, str]]:
    tests: list[dict[str, str]] = []
    for path in _walk_files(root):
        relative = path.relative_to(root)
        lowered = {part.lower() for part in relative.parts}
        if (
            lowered.intersection({marker.lower() for marker in TEST_MARKERS})
            or path.name.endswith(("Tests.swift", "Test.kt", "Tests.kt", ".test.ts", ".test.tsx"))
            or "_test." in path.name
        ):
            tests.append({"path": relative.as_posix(), "kind": "test"})
    return tests


def _build_commands(root: Path, framework: str) -> list[str]:
    if framework == "flutter":
        return [
            "flutter pub get",
            "flutter analyze",
            "flutter test",
            "flutter build apk --debug",
            "flutter build ios --simulator --no-codesign",
        ]
    if framework == "react-native":
        package_manager = "npm"
        if (root / "yarn.lock").is_file():
            package_manager = "yarn"
        elif (root / "pnpm-lock.yaml").is_file():
            package_manager = "pnpm"
        return [
            f"{package_manager} install",
            f"{package_manager} test",
            f"{package_manager} run android",
            f"{package_manager} run ios",
        ]
    if framework == "swiftui":
        project = next((path.name for path in root.glob("*.xcodeproj")), "App.xcodeproj")
        scheme = Path(project).stem
        return [
            f"xcodebuild -project {project} -scheme {scheme} build",
            f"xcodebuild -project {project} -scheme {scheme} test",
        ]
    wrapper = "./gradlew" if (root / "gradlew").is_file() else "gradle"
    return [
        f"{wrapper} test",
        f"{wrapper} lint",
        f"{wrapper} assembleDebug",
        f"{wrapper} connectedDebugAndroidTest",
    ]


def _source_hashes(root: Path, files: list[Path]) -> dict[str, str]:
    return {
        _relative(path, root): _hash_text(path.read_bytes().hex())
        for path in files
    }


def scan_project(project_root: Path | str, profile: str = "full") -> dict[str, Any]:
    """Return a deterministic project model without changing the target project."""
    root = Path(project_root).resolve()
    if profile not in {"quick", "full"}:
        raise ProjectError("profile must be quick or full")
    if not root.is_dir():
        raise ProjectError(f"project root does not exist: {root}")
    framework = _detect_framework(root)
    source_files = _source_files(root, framework)
    if not source_files:
        raise ProjectError(f"no {framework} source files found under {root}")
    dependencies, versions = _manifest_dependencies(root, framework)
    screens, screen_evidence = _screen_candidates(root, source_files, framework)
    routes, route_evidence = _route_records(root, source_files, framework)
    behavior, behavior_evidence = _behavior_contract(root, source_files, framework)
    evidence = sorted(
        screen_evidence + route_evidence + behavior_evidence,
        key=lambda item: (item["path"], item["line"], item["kind"], item["symbol"]),
    )
    graph_edges = [
        {
            "from": action["path"],
            "to": action["symbol"],
            "kind": "navigation",
            "evidence": {"path": action["path"], "line": action["line"]},
        }
        for action in behavior["actions"]
        if action["kind"] == "navigation"
    ]
    hashes = _source_hashes(root, source_files)
    return {
        "format": "mobile-native-project/2",
        "schema_version": 2,
        "project": {
            "name": root.name,
            "root": str(root),
            "profile": profile,
            "source_fingerprint": _hash_text(
                "\n".join(f"{path}:{digest}" for path, digest in sorted(hashes.items()))
            ),
        },
        "framework": {
            "id": framework,
            "confidence": "high",
            "evidence_type": "manifest",
        },
        "versions": versions,
        "dependencies": {"direct": dependencies, "versions": versions},
        "architecture": _architecture(source_files, framework, dependencies),
        "screen_graph": {
            "format": "mobile-native-screen-graph/1",
            "screens": screens,
            "routes": routes,
            "tabs": [route for route in routes if route["kind"] == "tab-root"],
            "sheets": [route for route in routes if route["kind"] == "sheet"],
            "dialogs": [],
            "deep_links": [
                route for route in routes if isinstance(route["path"], str) and ":" in route["path"]
            ],
            "edges": graph_edges,
            "entry_points": [screen["id"] for screen in screens if screen["entry_point"]],
        },
        "behavior_contract": behavior,
        "design_language": _design_language(root, source_files, framework),
        "components": _components(root, source_files, framework),
        "assets": _assets(root),
        "localization": _localization(root),
        "tests": _tests(root),
        "build_commands": _build_commands(root, framework),
        "source_files": [_relative(path, root) for path in source_files],
        "source_hashes": hashes,
        "evidence": evidence,
        "uncertainties": [
            {
                "id": "route-coverage",
                "message": "No explicit route declaration was proven; confirm navigation entry points before implementation.",
                "stop_condition": True,
            }
        ]
        if not routes
        else [],
    }


def _write_json(path: Path, document: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    scan = subparsers.add_parser("scan")
    scan.add_argument("app_root", type=Path)
    scan.add_argument("--profile", choices=["quick", "full"], default="full")
    scan.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        model = scan_project(args.app_root, profile=args.profile)
        _write_json(args.out, model)
        return 0
    except (OSError, ProjectError, ValueError, json.JSONDecodeError) as error:
        print(json.dumps({"ok": False, "error": str(error)}, sort_keys=True), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
