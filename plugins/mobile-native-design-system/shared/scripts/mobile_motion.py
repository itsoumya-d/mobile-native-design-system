#!/usr/bin/env python3
"""Validate mobile motion specifications and generate native starter recipes."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


FRAMEWORKS = {"flutter", "react-native", "swiftui", "compose", "all"}
REQUIRED = {"format", "name", "kind", "states", "duration_ms", "easing", "distance", "stagger_ms", "reduced_motion"}


def validate_motion(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    missing = sorted(REQUIRED - set(spec))
    if missing:
        errors.append("missing fields: " + ", ".join(missing))
    if spec.get("format") != "mobile-motion-spec/1":
        errors.append("format must be mobile-motion-spec/1")
    if "states" in spec and (not isinstance(spec["states"], list) or len(spec["states"]) < 2):
        errors.append("states must contain at least two names")
    for field in ("duration_ms", "distance", "stagger_ms"):
        if field in spec and (not isinstance(spec[field], int) or spec[field] < 0):
            errors.append(f"{field} must be a non-negative integer")
    if spec.get("reduced_motion") not in {"immediate", "opacity"}:
        errors.append("reduced_motion must be immediate or opacity")
    return errors


def _flutter(spec: dict[str, Any]) -> str:
    return f'''// Generated native motion starter. Do not edit generated values.\nimport 'package:flutter/animation.dart';\n\nclass MobileMotion {{\n  const MobileMotion._();\n  static const duration = Duration(milliseconds: {spec['duration_ms']});\n  static const stagger = Duration(milliseconds: {spec['stagger_ms']});\n  static const distance = {spec['distance']}.0;\n  static const reducedMotion = '{spec['reduced_motion']}';\n  static AnimationController controller(TickerProvider vsync) =>\n      AnimationController(vsync: vsync, duration: duration);\n}}\n'''


def _react_native(spec: dict[str, Any]) -> str:
    return f'''// Generated native motion starter.\nimport {{ Animated, Easing }} from 'react-native';\n\nexport const mobileMotion = {{\n  duration: {spec['duration_ms']},\n  stagger: {spec['stagger_ms']},\n  distance: {spec['distance']},\n  reducedMotion: '{spec['reduced_motion']}',\n  easing: Easing.out(Easing.cubic),\n  opacity: (value: Animated.Value) => Animated.timing(value, {{ duration: {spec['duration_ms']}, useNativeDriver: true }}),\n}} as const;\n'''


def _swiftui(spec: dict[str, Any]) -> str:
    return f'''// Generated native motion starter.\nimport SwiftUI\n\nenum MobileMotion {{\n    static let duration: Double = {spec['duration_ms']} / 1000.0\n    static let stagger: Double = {spec['stagger_ms']} / 1000.0\n    static let distance: CGFloat = {spec['distance']}\n    static let animation = Animation.easeOut(duration: duration)\n    static let reducedMotion = "{spec['reduced_motion']}"\n}}\n'''


def _compose(spec: dict[str, Any]) -> str:
    return f'''// Generated native motion starter.\npackage mobile.motion\n\nimport androidx.compose.animation.core.tween\n\nobject MobileMotion {{\n    const val durationMillis: Int = {spec['duration_ms']}\n    const val staggerMillis: Int = {spec['stagger_ms']}\n    const val distanceDp: Int = {spec['distance']}\n    const val reducedMotion: String = "{spec['reduced_motion']}"\n    val enter = tween<Float>(durationMillis = durationMillis)\n}}\n'''


def generate_recipes(spec: dict[str, Any], platform: str, output: Path) -> list[Path]:
    """Write deterministic framework-native starter recipes and return their paths."""
    errors = validate_motion(spec)
    if errors:
        raise ValueError("; ".join(errors))
    if platform not in FRAMEWORKS:
        raise ValueError(f"unsupported platform: {platform}")
    renderers = {
        "flutter": ("mobile_motion.dart", _flutter),
        "react-native": ("mobileMotion.ts", _react_native),
        "swiftui": ("MobileMotion.swift", _swiftui),
        "compose": ("MobileMotion.kt", _compose),
    }
    selected = renderers if platform == "all" else {platform: renderers[platform]}
    output.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for _, (filename, renderer) in selected.items():
        path = output / filename
        path.write_text(renderer(spec), encoding="utf-8")
        written.append(path)
    return written


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    validate = subparsers.add_parser("validate")
    validate.add_argument("spec", type=Path)
    generate = subparsers.add_parser("generate")
    generate.add_argument("spec", type=Path)
    generate.add_argument("--platform", choices=sorted(FRAMEWORKS), default="all")
    generate.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        spec = json.loads(args.spec.read_text(encoding="utf-8"))
        if not isinstance(spec, dict):
            raise ValueError("input JSON must be an object")
        if args.command == "validate":
            errors = validate_motion(spec)
            print(json.dumps({"ok": not errors, "errors": errors}, sort_keys=True))
            return 0 if not errors else 1
        files = generate_recipes(spec, args.platform, args.out)
        print(json.dumps([path.name for path in files]))
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
