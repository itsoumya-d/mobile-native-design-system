#!/usr/bin/env python3
"""Validate DTCG mobile tokens and generate deterministic native interfaces."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, NamedTuple


SCHEMA = "https://www.designtokens.org/schemas/2025.10/format.json"
EXTENSION = "org.mobile-native"
ALIAS = re.compile(r"^\{([A-Za-z0-9_.-]+)\}$")
REQUIRED_CATEGORIES = {
    "color",
    "opacity",
    "typography",
    "spacing",
    "sizing",
    "iconography",
    "touchTarget",
    "radius",
    "stroke",
    "elevation",
    "layout",
    "zIndex",
    "motion",
    "haptic",
    "component",
}
REQUIRED_PROFILES = {
    "base",
    "light",
    "dark",
    "highContrast",
    "ios",
    "android",
    "reducedMotion",
}
FORBIDDEN_PROFILES = {"web", "desktop", "browser", "watch", "television"}
PLATFORM_FILES = {
    "swift": ("MobileTokens.swift", "MobileTheme.swift"),
    "kotlin": ("MobileTokens.kt", "MobileTheme.kt"),
    "react-native": ("tokens.ts", "theme.ts"),
    "flutter": ("mobile_tokens.dart", "mobile_theme_extension.dart"),
}


class TokenError(ValueError):
    """Raised when the token document violates the mobile contract."""


class ResolvedToken(NamedTuple):
    path: str
    type: str
    value: Any


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _source_hash(document: dict[str, Any]) -> str:
    return hashlib.sha256(_canonical_json(document).encode("utf-8")).hexdigest()


def _collect_tokens(
    node: Any,
    prefix: tuple[str, ...] = (),
    inherited_type: str | None = None,
) -> dict[str, tuple[str, Any]]:
    if not isinstance(node, dict):
        return {}
    token_type = node.get("$type", inherited_type)
    if "$value" in node:
        if not prefix:
            raise TokenError("A token must have a non-empty path")
        if not token_type:
            raise TokenError(f"Token {'.'.join(prefix)} has no $type")
        return {".".join(prefix): (str(token_type), node["$value"])}

    tokens: dict[str, tuple[str, Any]] = {}
    for key, child in node.items():
        if key.startswith("$"):
            continue
        tokens.update(_collect_tokens(child, prefix + (key,), token_type))
    return tokens


def _profiles(document: dict[str, Any]) -> dict[str, dict[str, Any]]:
    extensions = document.get("$extensions")
    if not isinstance(extensions, dict):
        raise TokenError(f"Missing ${'extensions'} object")
    mobile = extensions.get(EXTENSION)
    if not isinstance(mobile, dict) or not isinstance(mobile.get("profiles"), dict):
        raise TokenError(f"Missing ${'extensions'}.{EXTENSION}.profiles")
    return mobile["profiles"]


def _profile_chain(
    profiles: dict[str, dict[str, Any]],
    name: str,
    stack: tuple[str, ...] = (),
) -> list[str]:
    if name not in profiles:
        raise TokenError(f"Unknown profile: {name}")
    if name in stack:
        raise TokenError(f"Profile inheritance cycle: {' -> '.join(stack + (name,))}")
    parent = profiles[name].get("extends")
    if parent is None:
        return [name]
    if not isinstance(parent, str):
        raise TokenError(f"Profile {name}.extends must be a string")
    return _profile_chain(profiles, parent, stack + (name,)) + [name]


def _number(value: Any, path: str) -> float:
    if isinstance(value, bool):
        raise TokenError(f"{path} must be numeric")
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, dict) and isinstance(value.get("value"), (int, float)):
        return float(value["value"])
    raise TokenError(f"{path} must be a number or dimension object")


def _resolve_value(
    value: Any,
    raw: dict[str, tuple[str, Any]],
    resolve_path: Any,
) -> Any:
    if isinstance(value, str):
        match = ALIAS.fullmatch(value)
        return resolve_path(match.group(1)).value if match else value
    if isinstance(value, list):
        return [_resolve_value(item, raw, resolve_path) for item in value]
    if isinstance(value, dict):
        return {key: _resolve_value(item, raw, resolve_path) for key, item in value.items()}
    return value


def resolve_document(
    document: dict[str, Any],
    selected_profiles: list[str] | tuple[str, ...] | None = None,
) -> dict[str, ResolvedToken]:
    """Resolve aliases after applying ordered profile overrides."""
    raw = _collect_tokens(document)
    if not raw:
        raise TokenError("The document contains no tokens")

    profiles = _profiles(document)
    ordered_profiles = list(selected_profiles or ["base"])
    applied: list[str] = []
    for selected in ordered_profiles:
        for profile in _profile_chain(profiles, selected):
            if profile not in applied:
                applied.append(profile)

    mutable = dict(raw)
    for profile in applied:
        definition = profiles[profile]
        overrides = definition.get("overrides", {})
        if not isinstance(overrides, dict):
            raise TokenError(f"Profile {profile}.overrides must be an object")
        for path, value in overrides.items():
            if path not in mutable:
                raise TokenError(f"Profile {profile} overrides unknown token {path}")
            original_type, _ = mutable[path]
            if isinstance(value, dict) and "$value" in value:
                mutable[path] = (str(value.get("$type", original_type)), value["$value"])
            else:
                mutable[path] = (original_type, value)

    cache: dict[str, ResolvedToken] = {}

    def resolve_path(path: str, stack: tuple[str, ...] = ()) -> ResolvedToken:
        if path in cache:
            return cache[path]
        if path not in mutable:
            raise TokenError(f"Alias references unknown token {path}")
        if path in stack:
            raise TokenError(f"Alias cycle: {' -> '.join(stack + (path,))}")
        token_type, value = mutable[path]
        resolved = ResolvedToken(
            path=path,
            type=token_type,
            value=_resolve_value(value, mutable, lambda target: resolve_path(target, stack + (path,))),
        )
        cache[path] = resolved
        return resolved

    return {path: resolve_path(path) for path in sorted(mutable)}


def validate_document(document: dict[str, Any]) -> dict[str, Any]:
    """Validate schema, resolver profiles, aliases, and mobile accessibility floors."""
    if document.get("$schema") != SCHEMA:
        raise TokenError(f"$schema must be {SCHEMA}")
    missing_categories = sorted(REQUIRED_CATEGORIES - set(document))
    if missing_categories:
        raise TokenError(f"Missing token categories: {', '.join(missing_categories)}")

    profiles = _profiles(document)
    forbidden = sorted(FORBIDDEN_PROFILES & {name.lower() for name in profiles})
    if forbidden:
        raise TokenError(f"This is a mobile-only contract; forbidden profiles: {', '.join(forbidden)}")
    missing_profiles = sorted(REQUIRED_PROFILES - set(profiles))
    if missing_profiles:
        raise TokenError(f"Missing resolver profiles: {', '.join(missing_profiles)}")

    base = resolve_document(document, ["base"])
    for profile in sorted(profiles):
        resolve_document(document, [profile])

    ios_target = _number(
        resolve_document(document, ["ios"])["touchTarget.minimum"].value,
        "iOS touchTarget.minimum",
    )
    android_target = _number(
        resolve_document(document, ["android"])["touchTarget.minimum"].value,
        "Android touchTarget.minimum",
    )
    if ios_target < 44:
        raise TokenError("iOS touchTarget.minimum must be at least 44 points")
    if android_target < 48:
        raise TokenError("Android touchTarget.minimum must be at least 48 dp")

    reduced = resolve_document(document, ["reducedMotion"])
    duration_paths = [
        path for path, token in reduced.items() if token.type == "duration" and path.startswith("motion.")
    ]
    for path in duration_paths:
        if _number(reduced[path].value, path) < 0:
            raise TokenError(f"{path} cannot be negative")
    if "motion.distance.standard" in reduced and _number(
        reduced["motion.distance.standard"].value, "motion.distance.standard"
    ) != 0:
        raise TokenError("reducedMotion must set motion.distance.standard to 0")

    return {
        "ok": True,
        "token_count": len(base),
        "profiles": sorted(profiles),
        "source_hash": _source_hash(document),
    }


def _resolved_profiles(document: dict[str, Any]) -> dict[str, dict[str, Any]]:
    profiles: dict[str, dict[str, Any]] = {}
    for profile in sorted(_profiles(document)):
        profiles[profile] = {
            path: token.value for path, token in resolve_document(document, [profile]).items()
        }
    return profiles


def _string_value(value: Any) -> str:
    if isinstance(value, str):
        return value
    return _canonical_json(value)


def _swift_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def _identifier(path: str) -> str:
    """Produce a deterministic lower-camel identifier from a token path."""
    parts = re.findall(r"[A-Za-z0-9]+", path)
    if not parts:
        return "token"
    first = parts[0].lower()
    tail = "".join(part[:1].upper() + part[1:] for part in parts[1:])
    return first + tail


def _color_paths(profiles: dict[str, dict[str, Any]]) -> list[str]:
    return [path for path in profiles.get("base", {}) if path.startswith("color.")]


def _enum_cases(paths: list[str], prefix: str = "") -> list[tuple[str, str]]:
    seen: set[str] = set()
    cases: list[tuple[str, str]] = []
    for path in paths:
        name = _identifier(path[len(prefix):] if prefix else path)
        if name in seen:
            name = _identifier(path)
        seen.add(name)
        cases.append((name, path))
    return cases


def _swift_tokens(source_hash: str, profiles: dict[str, dict[str, Any]]) -> str:
    profile_lines: list[str] = []
    for profile, values in profiles.items():
        value_lines = ",\n".join(
            f"            {_swift_string(path)}: {_swift_string(_string_value(value))}"
            for path, value in values.items()
        )
        profile_lines.append(f'        "{profile}": [\n{value_lines}\n        ]')
    body = ",\n".join(profile_lines)
    color_cases = _enum_cases(_color_paths(profiles), "color.")
    enum_body = "\n".join(
        f'    case {name} = {_swift_string(path)}' for name, path in color_cases
    )
    return f"""// Generated by mobile_tokens.py. Do not edit.
import Foundation
import SwiftUI

public enum MobileColorToken: String, CaseIterable {{
{enum_body}
}}

public enum MobileTokens {{
    public static let sourceHash = "{source_hash}"
    public static let profiles: [String: [String: String]] = [
{body}
    ]

    public static func values(for profile: String) -> [String: String] {{
        profiles[profile] ?? profiles["base"] ?? [:]
    }}

    public static func color(_ token: MobileColorToken, profile: String = "base") -> Color {{
        Color(mobileHex: values(for: profile)[token.rawValue] ?? "#00000000")
    }}

    public static func dimension(_ path: String, profile: String = "base") -> CGFloat {{
        CGFloat(Double(values(for: profile)[path] ?? "0") ?? 0)
    }}
}}

private extension Color {{
    init(mobileHex value: String) {{
        let raw = value.trimmingCharacters(in: CharacterSet(charactersIn: "#"))
        let normalized = raw.count == 6 ? "FF" + raw : raw
        let integer = UInt64(normalized, radix: 16) ?? 0
        self.init(
            .sRGB,
            red: Double((integer >> 16) & 0xFF) / 255,
            green: Double((integer >> 8) & 0xFF) / 255,
            blue: Double(integer & 0xFF) / 255,
            opacity: Double((integer >> 24) & 0xFF) / 255
        )
    }}
}}
"""


def _swift_theme() -> str:
    return """// Generated by mobile_tokens.py. Do not edit.
import SwiftUI

public struct MobileColors {
    public let profile: String
    public func color(_ token: MobileColorToken) -> Color {
        MobileTokens.color(token, profile: profile)
    }
}

public struct MobileDimensions {
    public let profile: String
    public func value(_ path: String) -> CGFloat { MobileTokens.dimension(path, profile: profile) }
}

public struct MobileTypography {
    public let profile: String
    public func font(_ role: String) -> Font { .body }
}

public struct MobileTheme {
    public let profile: String
    public let values: [String: String]
    public let colors: MobileColors
    public let dimensions: MobileDimensions
    public let typography: MobileTypography

    public init(profile: String = "base") {
        self.profile = profile
        self.values = MobileTokens.values(for: profile)
        self.colors = MobileColors(profile: profile)
        self.dimensions = MobileDimensions(profile: profile)
        self.typography = MobileTypography(profile: profile)
    }

    public subscript(path: String) -> String? { values[path] }
}
"""


def _kotlin_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def _kotlin_tokens(source_hash: str, profiles: dict[str, dict[str, Any]]) -> str:
    profile_lines: list[str] = []
    for profile, values in profiles.items():
        pairs = ",\n".join(
            f"            {_kotlin_string(path)} to {_kotlin_string(_string_value(value))}"
        for path, value in values.items()
        )
        profile_lines.append(f'        "{profile}" to mapOf(\n{pairs}\n        )')
    body = ",\n".join(profile_lines)
    color_cases = _enum_cases(_color_paths(profiles), "color.")
    enum_body = ",\n".join(f'    {name}({json.dumps(path)})' for name, path in color_cases)
    return f"""// Generated by mobile_tokens.py. Do not edit.
package mobile.tokens

import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp

enum class MobileColorToken(val path: String) {{
{enum_body}
}}

data class MobileDimensions(val values: Map<String, String>) {{
    fun dp(path: String): Dp = values[path]?.toDoubleOrNull()?.dp ?: 0.dp
}}

data class MobileTypography(val values: Map<String, String>) {{
    fun style(path: String): TextStyle = TextStyle.Default
}}

object MobileTokens {{
    const val sourceHash: String = "{source_hash}"
    val profiles: Map<String, Map<String, String>> = mapOf(
{body}
    )

    fun values(profile: String): Map<String, String> =
        profiles[profile] ?: profiles.getValue("base")

    fun color(token: MobileColorToken, profile: String = "base"): Color {{
        val value = values(profile)[token.path] ?: "#00000000"
        val raw = value.removePrefix("#")
        val normalized = if (raw.length == 6) "FF$raw" else raw
        return Color(normalized.toULongOrNull(16) ?: 0u)
    }}

    fun dimensions(profile: String = "base"): MobileDimensions = MobileDimensions(values(profile))
    fun typography(profile: String = "base"): MobileTypography = MobileTypography(values(profile))
}}
"""


def _kotlin_theme() -> str:
    return """// Generated by mobile_tokens.py. Do not edit.
package mobile.tokens

import androidx.compose.runtime.staticCompositionLocalOf

data class MobileTheme(
    val profile: String = "base",
    val values: Map<String, String> = MobileTokens.values(profile),
    val dimensions: MobileDimensions = MobileTokens.dimensions(profile),
    val typography: MobileTypography = MobileTokens.typography(profile),
)

val LocalMobileTheme = staticCompositionLocalOf { MobileTheme() }
"""


def _typescript_tokens(source_hash: str, profiles: dict[str, dict[str, Any]]) -> str:
    color_paths = _color_paths(profiles)
    color_union = " | ".join(json.dumps(path) for path in color_paths) or "never"
    return (
        "// Generated by mobile_tokens.py. Do not edit.\n"
        f"export const tokenSourceHash = {json.dumps(source_hash)} as const;\n"
        f"export const mobileTokens = {{ profiles: {_canonical_json(profiles)} }} as const;\n"
        "export type MobileTokenProfile = keyof typeof mobileTokens.profiles;\n"
        "export type MobileTokenPath = keyof typeof mobileTokens.profiles.base;\n"
        f"export type MobileColorToken = {color_union};\n"
        "export const mobileColor = (token: MobileColorToken, profile: MobileTokenProfile = 'base') =>\n"
        "  mobileTokens.profiles[profile][token];\n"
    )


def _typescript_theme() -> str:
    return """// Generated by mobile_tokens.py. Do not edit.
import { mobileTokens, type MobileTokenPath, type MobileTokenProfile } from "./tokens";

export interface MobileTheme {
  profile: MobileTokenProfile;
  values: Readonly<Record<MobileTokenPath, unknown>>;
}

export const createMobileTheme = (profile: MobileTokenProfile = "base"): MobileTheme => {
  return { profile, values: mobileTokens.profiles[profile] };
};
"""


def _dart_tokens(source_hash: str, profiles: dict[str, dict[str, Any]]) -> str:
    color_cases = _enum_cases(_color_paths(profiles), "color.")
    enum_body = ",\n  ".join(name for name, _ in color_cases)
    switch_body = "\n".join(
        f"      MobileColorToken.{name} => {json.dumps(path)}," for name, path in color_cases
    )
    return f"""// Generated by mobile_tokens.py. Do not edit.
import 'dart:ui';

enum MobileColorToken {{
  {enum_body}
}}

extension MobileColorTokenPath on MobileColorToken {{
  String get path => switch (this) {{
{switch_body}
  }};
}}

class MobileTokens {{
  MobileTokens._();
  static const String sourceHash = {json.dumps(source_hash)};
  static const Map<String, Map<String, Object?>> profiles =
      {_canonical_json(profiles)};

  static Color color(MobileColorToken token, {{String profile = 'base'}}) {{
    final value = profiles[profile]?[token.path] ?? profiles['base']![token.path] ?? '#00000000';
    final raw = (value as String).replaceFirst('#', '');
    final normalized = raw.length == 6 ? 'FF$raw' : raw;
    return Color(int.tryParse(normalized, radix: 16) ?? 0);
  }}
}}
"""


def _dart_theme() -> str:
    return """// Generated by mobile_tokens.py. Do not edit.
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'mobile_tokens.dart';

@immutable
class MobileThemeExtension extends ThemeExtension<MobileThemeExtension> {
  const MobileThemeExtension({this.profile = 'base'});
  final String profile;

  Map<String, Object?> get values =>
      MobileTokens.profiles[profile] ?? MobileTokens.profiles['base']!;

  @override
  MobileThemeExtension copyWith({String? profile}) =>
      MobileThemeExtension(profile: profile ?? this.profile);

  @override
  MobileThemeExtension lerp(covariant MobileThemeExtension? other, double t) =>
      t < 0.5 || other == null ? this : other;
}

@immutable
class MobileTokenColors extends ThemeExtension<MobileTokenColors> {
  const MobileTokenColors({required this.profile});
  final String profile;

  Color color(MobileColorToken token) => MobileTokens.color(token, profile: profile);

  @override
  MobileTokenColors copyWith({String? profile}) => MobileTokenColors(profile: profile ?? this.profile);

  @override
  MobileTokenColors lerp(covariant MobileTokenColors? other, double t) =>
      t < 0.5 || other == null ? this : other;
}

extension MobileTokenBuildContext on BuildContext {
  MobileThemeExtension get mobileTheme =>
      Theme.of(this).extension<MobileThemeExtension>() ?? const MobileThemeExtension();
  MobileTokenColors get mobileColors =>
      Theme.of(this).extension<MobileTokenColors>() ?? const MobileTokenColors(profile: 'base');
}
"""


def generate_all(
    document: dict[str, Any],
    output: Path,
    platform: str = "all",
) -> list[Path]:
    """Generate deterministic platform files and a parity manifest."""
    validation = validate_document(document)
    output.mkdir(parents=True, exist_ok=True)
    profiles = _resolved_profiles(document)
    source_hash = validation["source_hash"]

    renderers = {
        "swift": (
            ("MobileTokens.swift", _swift_tokens(source_hash, profiles)),
            ("MobileTheme.swift", _swift_theme()),
        ),
        "kotlin": (
            ("MobileTokens.kt", _kotlin_tokens(source_hash, profiles)),
            ("MobileTheme.kt", _kotlin_theme()),
        ),
        "react-native": (
            ("tokens.ts", _typescript_tokens(source_hash, profiles)),
            ("theme.ts", _typescript_theme()),
        ),
        "flutter": (
            ("mobile_tokens.dart", _dart_tokens(source_hash, profiles)),
            ("mobile_theme_extension.dart", _dart_theme()),
        ),
    }
    selected = list(renderers) if platform == "all" else [platform]
    if any(item not in renderers for item in selected):
        raise TokenError(f"Unsupported platform: {platform}")

    written: list[Path] = []
    artifact_hashes: dict[str, str] = {}
    for target in selected:
        for filename, content in renderers[target]:
            path = output / filename
            path.write_text(content, encoding="utf-8", newline="\n")
            written.append(path)
            artifact_hashes[filename] = hashlib.sha256(content.encode("utf-8")).hexdigest()

    manifest = {
        "format": "mobile-native-token-manifest/1",
        "source_hash": source_hash,
        "token_paths": sorted(resolve_document(document, ["base"])),
        "profiles": sorted(profiles),
        "artifacts": artifact_hashes,
    }
    manifest_path = output / "tokens.manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    written.append(manifest_path)
    return written


def check_parity(document: dict[str, Any], output: Path) -> dict[str, Any]:
    """Verify generated artifacts still match the resolved source document."""
    errors: list[str] = []
    manifest_path = output / "tokens.manifest.json"
    if not manifest_path.exists():
        return {"ok": False, "errors": ["tokens.manifest.json is missing"]}
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return {"ok": False, "errors": [f"Invalid manifest: {error}"]}

    expected_hash = _source_hash(document)
    if manifest.get("source_hash") != expected_hash:
        errors.append("source hash mismatch")
    expected_paths = sorted(resolve_document(document, ["base"]))
    if manifest.get("token_paths") != expected_paths:
        errors.append("semantic token path mismatch")
    expected_profiles = sorted(_profiles(document))
    if manifest.get("profiles") != expected_profiles:
        errors.append("resolver profile mismatch")

    for filename, expected_artifact_hash in manifest.get("artifacts", {}).items():
        path = output / filename
        if not path.exists():
            errors.append(f"missing artifact: {filename}")
            continue
        actual_hash = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual_hash != expected_artifact_hash:
            errors.append(f"artifact hash mismatch: {filename}")
        text = path.read_text(encoding="utf-8")
        if filename not in {"MobileTheme.swift", "MobileTheme.kt", "theme.ts", "mobile_theme_extension.dart"}:
            for token_path in expected_paths:
                if token_path not in text:
                    errors.append(f"{filename} omits {token_path}")
                    break
    return {"ok": not errors, "errors": errors, "token_count": len(expected_paths)}


def _load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise TokenError(f"Cannot read {path}: {error}") from error
    if not isinstance(value, dict):
        raise TokenError("Token input must be a JSON object")
    return value


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    validate = commands.add_parser("validate", help="Validate a DTCG token file")
    validate.add_argument("tokens", type=Path)

    generate = commands.add_parser("generate", help="Generate native token interfaces")
    generate.add_argument("tokens", type=Path)
    generate.add_argument(
        "--platform",
        choices=["all", *PLATFORM_FILES],
        default="all",
    )
    generate.add_argument("--out", type=Path, required=True)

    parity = commands.add_parser("parity", help="Verify generated semantic parity")
    parity.add_argument("tokens", type=Path)
    parity.add_argument("generated_directory", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        document = _load(args.tokens)
        if args.command == "validate":
            report = validate_document(document)
        elif args.command == "generate":
            paths = generate_all(document, args.out, args.platform)
            report = {"ok": True, "artifacts": [str(path) for path in paths]}
        else:
            report = check_parity(document, args.generated_directory)
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0 if report.get("ok") else 1
    except TokenError as error:
        print(json.dumps({"ok": False, "error": str(error)}, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
