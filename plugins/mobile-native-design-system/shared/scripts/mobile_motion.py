#!/usr/bin/env python3
"""Validate mobile motion specifications and generate native starter recipes."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


FRAMEWORKS = {"flutter", "react-native", "swiftui", "compose", "all"}
REQUIRED_V1 = {
    "format",
    "name",
    "kind",
    "states",
    "duration_ms",
    "easing",
    "distance",
    "stagger_ms",
    "reduced_motion",
}
REQUIRED_V2 = {
    "format",
    "name",
    "kind",
    "variants",
    "timeline",
    "gesture",
    "interruption",
    "shared_transition",
    "haptic_intent",
    "performance_budget",
    "reduced_motion",
}


def validate_motion(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    version = spec.get("format")
    required = REQUIRED_V2 if version == "mobile-motion-spec/2" else REQUIRED_V1
    missing = sorted(required - set(spec))
    if missing:
        errors.append("missing fields: " + ", ".join(missing))
    if version not in {"mobile-motion-spec/1", "mobile-motion-spec/2"}:
        errors.append("format must be mobile-motion-spec/1 or mobile-motion-spec/2")
    if version == "mobile-motion-spec/2":
        variants = spec.get("variants")
        if not isinstance(variants, dict) or len(variants) < 2:
            errors.append("variants must contain at least two named states")
            variant_names: set[str] = set()
        else:
            variant_names = set(variants)
        timeline = spec.get("timeline")
        if not isinstance(timeline, list) or not timeline:
            errors.append("timeline must be a non-empty list")
        else:
            for index, step in enumerate(timeline):
                if not isinstance(step, dict):
                    errors.append(f"timeline[{index}] must be an object")
                    continue
                missing_step = {"label", "from", "to", "duration_ms"} - set(step)
                if missing_step:
                    errors.append(
                        f"timeline[{index}] missing fields: {', '.join(sorted(missing_step))}"
                    )
                if step.get("from") not in variant_names or step.get("to") not in variant_names:
                    errors.append(f"timeline[{index}] references an unknown variant")
                duration = step.get("duration_ms")
                if not isinstance(duration, int) or duration < 0:
                    errors.append(f"timeline[{index}].duration_ms must be a non-negative integer")
        gesture = spec.get("gesture")
        if not isinstance(gesture, dict) or not {
            "kind",
            "threshold",
            "cancel_behavior",
        }.issubset(gesture):
            errors.append("gesture must define kind, threshold, and cancel_behavior")
        interruption = spec.get("interruption")
        if not isinstance(interruption, dict) or not {
            "policy",
            "resting_state",
        }.issubset(interruption):
            errors.append("interruption must define policy and resting_state")
        elif interruption.get("resting_state") not in variant_names:
            errors.append("interruption resting_state must name a variant")
        shared = spec.get("shared_transition")
        if not isinstance(shared, dict) or not {"id", "enabled"}.issubset(shared):
            errors.append("shared_transition must define id and enabled")
        budget = spec.get("performance_budget")
        if not isinstance(budget, dict) or not {
            "max_simultaneous_animations",
            "prefer_compositor",
        }.issubset(budget):
            errors.append(
                "performance_budget must define max_simultaneous_animations and prefer_compositor"
            )
        reduced = spec.get("reduced_motion")
        if not isinstance(reduced, dict) or not {
            "strategy",
            "preserve_information",
            "disable_stagger",
        }.issubset(reduced):
            errors.append(
                "reduced_motion must define strategy, preserve_information, and disable_stagger"
            )
        elif reduced.get("strategy") not in {"immediate", "opacity"}:
            errors.append("reduced_motion strategy must be immediate or opacity")
    else:
        if "states" in spec and (
            not isinstance(spec["states"], list) or len(spec["states"]) < 2
        ):
            errors.append("states must contain at least two names")
        for field in ("duration_ms", "distance", "stagger_ms"):
            if field in spec and (not isinstance(spec[field], int) or spec[field] < 0):
                errors.append(f"{field} must be a non-negative integer")
        if spec.get("reduced_motion") not in {"immediate", "opacity"}:
            errors.append("reduced_motion must be immediate or opacity")
    return errors


def _v2_duration(spec: dict[str, Any]) -> int:
    return sum(int(step["duration_ms"]) for step in spec["timeline"])


def _v2_shared_id(spec: dict[str, Any]) -> str:
    return str(spec["shared_transition"]["id"]).replace("\\", "\\\\").replace("'", "\\'")


def _v2_flutter(spec: dict[str, Any]) -> str:
    variants = ", ".join(spec["variants"])
    shared = _v2_shared_id(spec)
    return f"""// Generated native motion contract.
import 'package:flutter/animation.dart';
import 'package:flutter/widgets.dart';

enum MobileMotionVariant {{ {variants} }}

class MobileMotion {{
  const MobileMotion._();
  static const sharedTransitionId = '{shared}';
  static const totalDuration = Duration(milliseconds: {_v2_duration(spec)});
  static const interruptionPolicy = '{spec['interruption']['policy']}';
  static const restingState = MobileMotionVariant.{spec['interruption']['resting_state']};
  static const gestureKind = '{spec['gesture']['kind']}';
  static const gestureThreshold = {spec['gesture']['threshold']};
  static const reducedMotionStrategy = '{spec['reduced_motion']['strategy']}';

  static bool reduceMotion(BuildContext context) =>
      MediaQuery.disableAnimationsOf(context);

  static AnimationController controller(TickerProvider vsync) =>
      AnimationController(vsync: vsync, duration: totalDuration);

  static Animation<double> opacity(AnimationController controller) =>
      CurvedAnimation(parent: controller, curve: Curves.easeOutCubic);
}}
"""


def _v2_react_native(spec: dict[str, Any]) -> str:
    variants = " | ".join(f"'{name}'" for name in spec["variants"])
    shared = _v2_shared_id(spec)
    return f"""// Generated native motion contract.
import {{ AccessibilityInfo, Animated, Easing }} from 'react-native';

export type MobileMotionVariant = {variants};
export const mobileMotion = {{
  sharedTransitionId: '{shared}',
  totalDuration: {_v2_duration(spec)},
  interruptionPolicy: '{spec['interruption']['policy']}',
  restingState: '{spec['interruption']['resting_state']}' as MobileMotionVariant,
  gesture: {{ kind: '{spec['gesture']['kind']}', threshold: {spec['gesture']['threshold']}, cancel: '{spec['gesture']['cancel_behavior']}' }},
  reducedMotion: '{spec['reduced_motion']['strategy']}',
  shouldReduceMotion: () => AccessibilityInfo.isReduceMotionEnabled(),
  animateOpacity: (value: Animated.Value, toValue: number) =>
    Animated.timing(value, {{
      toValue,
      duration: {_v2_duration(spec)},
      easing: Easing.out(Easing.cubic),
      useNativeDriver: true,
    }}),
}} as const;
"""


def _swift_case(name: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_]", "_", name)
    return cleaned if not cleaned[:1].isdigit() else f"state_{cleaned}"


def _v2_swiftui(spec: dict[str, Any]) -> str:
    variants = "\n".join(f"    case {_swift_case(name)}" for name in spec["variants"])
    shared = _v2_shared_id(spec)
    return f"""// Generated native motion contract.
import SwiftUI

enum MobileMotionVariant {{
{variants}
}}

struct MobileMotionModifier: ViewModifier {{
    @Environment(\\.accessibilityReduceMotion) private var accessibilityReduceMotion
    static let sharedTransitionID = "{shared}"
    static let totalDuration = {_v2_duration(spec)}.0 / 1000.0
    static let interruptionPolicy = "{spec['interruption']['policy']}"
    static let restingState = MobileMotionVariant.{_swift_case(spec['interruption']['resting_state'])}

    func body(content: Content) -> some View {{
        content.animation(
            accessibilityReduceMotion ? .easeOut(duration: 0.01) : .easeOut(duration: Self.totalDuration),
            value: accessibilityReduceMotion
        )
    }}
}}
"""


def _kotlin_case(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9_]", "_", name).upper()


def _v2_compose(spec: dict[str, Any]) -> str:
    variants = ", ".join(_kotlin_case(name) for name in spec["variants"])
    shared = _v2_shared_id(spec)
    return f"""// Generated native motion contract.
package mobile.motion

import androidx.compose.animation.core.tween
import androidx.compose.ui.MotionDurationScale
import kotlin.coroutines.coroutineContext

enum class MobileMotionVariant {{ {variants} }}

object MobileMotion {{
    const val sharedTransitionId: String = "{shared}"
    const val totalDurationMillis: Int = {_v2_duration(spec)}
    const val interruptionPolicy: String = "{spec['interruption']['policy']}"
    val restingState = MobileMotionVariant.{_kotlin_case(spec['interruption']['resting_state'])}
    val opacity = tween<Float>(durationMillis = totalDurationMillis)

    suspend fun systemMotionEnabled(): Boolean =
        (coroutineContext[MotionDurationScale]?.scaleFactor ?: 1f) > 0f
}}
"""


def _flutter(spec: dict[str, Any]) -> str:
    if spec.get("format") == "mobile-motion-spec/2":
        return _v2_flutter(spec)
    return f'''// Generated native motion starter. Do not edit generated values.\nimport 'package:flutter/animation.dart';\n\nclass MobileMotion {{\n  const MobileMotion._();\n  static const duration = Duration(milliseconds: {spec['duration_ms']});\n  static const stagger = Duration(milliseconds: {spec['stagger_ms']});\n  static const distance = {spec['distance']}.0;\n  static const reducedMotion = '{spec['reduced_motion']}';\n  static AnimationController controller(TickerProvider vsync) =>\n      AnimationController(vsync: vsync, duration: duration);\n}}\n'''


def _react_native(spec: dict[str, Any]) -> str:
    if spec.get("format") == "mobile-motion-spec/2":
        return _v2_react_native(spec)
    return f'''// Generated native motion starter.\nimport {{ Animated, Easing }} from 'react-native';\n\nexport const mobileMotion = {{\n  duration: {spec['duration_ms']},\n  stagger: {spec['stagger_ms']},\n  distance: {spec['distance']},\n  reducedMotion: '{spec['reduced_motion']}',\n  easing: Easing.out(Easing.cubic),\n  opacity: (value: Animated.Value) => Animated.timing(value, {{ duration: {spec['duration_ms']}, useNativeDriver: true }}),\n}} as const;\n'''


def _swiftui(spec: dict[str, Any]) -> str:
    if spec.get("format") == "mobile-motion-spec/2":
        return _v2_swiftui(spec)
    return f'''// Generated native motion starter.\nimport SwiftUI\n\nenum MobileMotion {{\n    static let duration: Double = {spec['duration_ms']} / 1000.0\n    static let stagger: Double = {spec['stagger_ms']} / 1000.0\n    static let distance: CGFloat = {spec['distance']}\n    static let animation = Animation.easeOut(duration: duration)\n    static let reducedMotion = "{spec['reduced_motion']}"\n}}\n'''


def _compose(spec: dict[str, Any]) -> str:
    if spec.get("format") == "mobile-motion-spec/2":
        return _v2_compose(spec)
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
