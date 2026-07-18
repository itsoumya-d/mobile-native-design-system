---
name: mobile-native-understand
description: Use when a Flutter, React Native, SwiftUI, or Jetpack Compose codebase must be understood before design, redesign, planning, audit, or implementation; especially to reconstruct framework versions, dependencies, architecture, screens, routes, tabs, sheets, behavior, state, repositories, services, design language, components, motion, assets, localization, tests, and build commands with source evidence. Web and desktop projects are out of scope.
---

# Mobile Native Understand

Build a read-only product model before recommending changes.

## Workflow

1. Confirm one supported mobile framework from root manifests. Stop on an
   ambiguous or unsupported root.
2. Scan from the plugin root:

```bash
python shared/scripts/mobile_project.py scan /absolute/path/to/app --profile full --out project-model.json
python shared/scripts/mobile_design.py synthesize project-model.json --out design-language.json
```

3. Review every screen, route, modal surface, behavior action, state boundary,
   asset, localization resource, test, and uncertainty.
4. Record inferred relationships with relative path, line, symbol, confidence,
   and evidence type. Treat low-confidence or missing navigation and behavior
   relationships as planning questions or stop conditions.
5. Do not edit the target project in this phase.

## Framework evidence

Read only the matching router framework reference. Detect Flutter navigation
and state packages, React Navigation or Expo Router, SwiftUI navigation and
Observation/Combine, or Navigation Compose and ViewModel/StateFlow. Never
pretend an API from one framework is portable to another.

## Exclusions

Exclude dependencies, build outputs, caches, generated code, secrets, and
unrelated backend implementation. Keep only hashes and structural evidence;
do not copy secret or private source content into artifacts.

Read `references/project-model.md` when interpreting the emitted contracts.
