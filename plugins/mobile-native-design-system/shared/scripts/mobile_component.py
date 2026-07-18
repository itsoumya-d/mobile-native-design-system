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


def _quoted(value: Any) -> str:
    return json.dumps(str(value), ensure_ascii=False)


def _dart_component(brief: dict[str, Any]) -> str:
    subject = _quoted(brief["subject"])
    user_job = _quoted(brief["user_job"])
    action = _quoted(brief["primary_action"])
    return f"""// Generated native component contract.
import 'package:flutter/material.dart';

enum NativeComponentState {{ loading, empty, error, populated }}

class NativeStatusCard extends StatelessWidget {{
  const NativeStatusCard({{
    required this.title,
    required this.state,
    required this.onPrimaryAction,
    super.key,
  }});

  static const subject = {subject};
  static const userJob = {user_job};
  static const primaryActionLabel = {action};

  final String title;
  final NativeComponentState state;
  final VoidCallback onPrimaryAction;

  @override
  Widget build(BuildContext context) {{
    final body = switch (state) {{
      NativeComponentState.loading => const CircularProgressIndicator(),
      NativeComponentState.empty => const Text('Nothing here yet'),
      NativeComponentState.error => const Text('Something went wrong'),
      NativeComponentState.populated => Text(title),
    }};
    return Semantics(
      container: true,
      label: '$title, ${{state.name}}',
      child: Card(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              body,
              const SizedBox(height: 12),
              FilledButton(
                onPressed: onPrimaryAction,
                child: const Text(primaryActionLabel),
              ),
            ],
          ),
        ),
      ),
    );
  }}
}}
"""


def _react_native_component(brief: dict[str, Any]) -> str:
    subject = _quoted(brief["subject"])
    user_job = _quoted(brief["user_job"])
    action = _quoted(brief["primary_action"])
    return f"""// Generated native component contract.
import React from 'react';
import {{
  ActivityIndicator,
  Pressable,
  StyleSheet,
  Text,
  View,
}} from 'react-native';

export type NativeComponentState =
  | 'loading'
  | 'empty'
  | 'error'
  | 'populated';

export const nativeComponentContract = {{
  subject: {subject},
  userJob: {user_job},
  primaryActionLabel: {action},
}} as const;

export function NativeStatusCard({{
  title,
  state,
  onPrimaryAction,
}}: {{
  title: string;
  state: NativeComponentState;
  onPrimaryAction: () => void;
}}): React.JSX.Element {{
  const content =
    state === 'loading' ? (
      <ActivityIndicator accessibilityLabel="Loading" />
    ) : state === 'empty' ? (
      <Text>Nothing here yet</Text>
    ) : state === 'error' ? (
      <Text>Something went wrong</Text>
    ) : (
      <Text>{{title}}</Text>
    );
  return (
    <View
      accessible
      accessibilityLabel={{`${{title}}, ${{state}}`}}
      style={{styles.card}}
    >
      {{content}}
      <Pressable
        accessibilityRole="button"
        onPress={{onPrimaryAction}}
        style={{styles.action}}
      >
        <Text style={{styles.actionLabel}}>
          {{nativeComponentContract.primaryActionLabel}}
        </Text>
      </Pressable>
    </View>
  );
}}

const styles = StyleSheet.create({{
  card: {{borderRadius: 16, gap: 12, padding: 16}},
  action: {{
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 48,
    paddingHorizontal: 16,
  }},
  actionLabel: {{fontWeight: '600'}},
}});
"""


def _swift_component(brief: dict[str, Any]) -> str:
    subject = _quoted(brief["subject"])
    user_job = _quoted(brief["user_job"])
    action = _quoted(brief["primary_action"])
    return f"""// Generated native component contract.
import SwiftUI

enum NativeComponentState {{
    case loading
    case empty
    case error
    case populated
}}

struct NativeStatusCard: View {{
    static let subject = {subject}
    static let userJob = {user_job}
    static let primaryActionLabel = {action}

    let title: String
    let state: NativeComponentState
    let onPrimaryAction: () -> Void

    @ViewBuilder
    private var content: some View {{
        switch state {{
        case .loading:
            ProgressView().accessibilityLabel("Loading")
        case .empty:
            ContentUnavailableView("Nothing here yet", systemImage: "tray")
        case .error:
            Label("Something went wrong", systemImage: "exclamationmark.triangle")
        case .populated:
            Text(title)
        }}
    }}

    var body: some View {{
        GroupBox {{
            VStack(alignment: .leading, spacing: 12) {{
                content
                Button(Self.primaryActionLabel, action: onPrimaryAction)
                    .buttonStyle(.borderedProminent)
                    .frame(minHeight: 44)
            }}
            .frame(maxWidth: .infinity, alignment: .leading)
        }}
        .accessibilityElement(children: .contain)
        .accessibilityLabel("\\(title), \\(String(describing: state))")
    }}
}}
"""


def _compose_component(brief: dict[str, Any]) -> str:
    subject = _quoted(brief["subject"])
    user_job = _quoted(brief["user_job"])
    action = _quoted(brief["primary_action"])
    return f"""// Generated native component contract.
package mobile.component

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.unit.dp

enum class NativeComponentState {{ Loading, Empty, Error, Populated }}

object NativeComponentContract {{
    const val subject: String = {subject}
    const val userJob: String = {user_job}
    const val primaryActionLabel: String = {action}
}}

@Composable
fun NativeStatusCard(
    title: String,
    state: NativeComponentState,
    onPrimaryAction: () -> Unit,
    modifier: Modifier = Modifier,
) {{
    Card(
        modifier = modifier.semantics {{
            contentDescription = "$title, ${{state.name}}"
        }},
    ) {{
        Column(
            modifier = Modifier.fillMaxWidth().padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {{
            when (state) {{
                NativeComponentState.Loading -> CircularProgressIndicator()
                NativeComponentState.Empty -> Text("Nothing here yet")
                NativeComponentState.Error -> Text("Something went wrong")
                NativeComponentState.Populated -> Text(title)
            }}
            Button(
                onClick = onPrimaryAction,
                modifier = Modifier.fillMaxWidth().heightIn(min = 48.dp),
            ) {{
                Text(NativeComponentContract.primaryActionLabel)
            }}
        }}
    }}
}}
"""


def generate_component_source(brief: dict[str, Any], platform: str) -> str:
    """Return deterministic, dependency-free native component source."""
    if platform not in FRAMEWORKS:
        raise ValueError(f"unsupported platform: {platform}")
    errors = validate_component_brief(brief)
    if errors:
        raise ValueError("; ".join(errors))
    renderers = {
        "flutter": _dart_component,
        "react-native": _react_native_component,
        "swiftui": _swift_component,
        "compose": _compose_component,
    }
    return renderers[platform](brief)


def validate_component_brief(brief: dict[str, Any]) -> list[str]:
    required = {"name", "subject", "user_job", "primary_action", "hierarchy", "components"}
    missing = sorted(required - set(brief))
    errors = ["missing fields: " + ", ".join(missing)] if missing else []
    if "components" in brief and not isinstance(brief["components"], list):
        errors.append("components must be a list")
    return errors


def create_plan(
    brief: dict[str, Any],
    platform: str,
    project_context: dict[str, Any] | None = None,
    screen_id: str | None = None,
) -> dict[str, Any]:
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
    plan = {
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
    if project_context is None:
        return plan
    if project_context.get("format") != "mobile-native-project/2":
        raise ValueError("project_context format must be mobile-native-project/2")
    context_platform = project_context.get("framework", {}).get("id")
    if context_platform != platform:
        raise ValueError(
            f"project_context framework {context_platform!r} does not match {platform!r}"
        )
    screens = project_context.get("screen_graph", {}).get("screens", [])
    selected_screen = next(
        (
            screen
            for screen in screens
            if screen.get("id") == screen_id or screen.get("name") == screen_id
        ),
        None,
    )
    if selected_screen is None:
        raise ValueError(f"screen_id not found in project_context: {screen_id}")
    path = selected_screen["path"]
    invariants = [
        invariant
        for invariant in project_context.get("behavior_contract", {}).get(
            "invariants", []
        )
        if invariant.get("evidence", {}).get("path") == path
    ]
    existing = sorted(
        {
            component["name"]
            for component in project_context.get("components", [])
            if isinstance(component, dict) and isinstance(component.get("name"), str)
        }
        | {
            str(component)
            for component in project_context.get("design_language", {}).get(
                "components", []
            )
        }
    )
    plan.update(
        {
            "format": "mobile-component-plan/2",
            "screen_id": selected_screen["id"],
            "project_context": {
                "source_fingerprint": project_context.get("project", {}).get(
                    "source_fingerprint"
                ),
                "existing_components": existing,
                "design_language": {
                    key: project_context.get("design_language", {}).get(key, [])
                    for key in (
                        "typography",
                        "colors",
                        "spacing",
                        "shapes",
                        "motion_grammar",
                    )
                },
            },
            "behavior_invariants": invariants
            or [
                {
                    "id": "preserve-screen-contract",
                    "description": "Preserve current routes, callbacks, state, and data ownership.",
                    "evidence": {"path": path, "line": 1},
                }
            ],
            "file_scope": {
                "allowed": [path],
                "protected": sorted(
                    set(project_context.get("source_files", [])) - {path}
                ),
            },
            "integration": {
                "workflow": [
                    "context",
                    "intent",
                    "constraints",
                    "alternatives",
                    "selected-native-plan",
                    "integration",
                    "refinement",
                ],
                "approval_required": True,
                "verification_commands": project_context.get("build_commands", []),
            },
        }
    )
    return plan


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    validate = subparsers.add_parser("validate")
    validate.add_argument("brief", type=Path)
    generate = subparsers.add_parser("generate")
    generate.add_argument("brief", type=Path)
    generate.add_argument("--platform", required=True, choices=sorted(FRAMEWORKS))
    generate.add_argument("--out", required=True, type=Path)
    generate.add_argument(
        "--code-out",
        type=Path,
        help="Also emit a compileable native component source file.",
    )
    generate.add_argument("--project-context", type=Path)
    generate.add_argument("--screen-id")
    args = parser.parse_args(argv)
    try:
        brief = json.loads(args.brief.read_text(encoding="utf-8"))
        if not isinstance(brief, dict):
            raise ValueError("input JSON must be an object")
        if args.command == "validate":
            errors = validate_component_brief(brief)
            print(json.dumps({"ok": not errors, "errors": errors}, sort_keys=True))
            return 0 if not errors else 1
        context = None
        if args.project_context:
            context = json.loads(args.project_context.read_text(encoding="utf-8"))
            if not isinstance(context, dict):
                raise ValueError("project context JSON must be an object")
        if bool(context) != bool(args.screen_id):
            raise ValueError("--project-context and --screen-id must be supplied together")
        plan = create_plan(
            brief,
            args.platform,
            project_context=context,
            screen_id=args.screen_id,
        )
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if args.code_out:
            args.code_out.parent.mkdir(parents=True, exist_ok=True)
            args.code_out.write_text(
                generate_component_source(brief, args.platform),
                encoding="utf-8",
            )
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
