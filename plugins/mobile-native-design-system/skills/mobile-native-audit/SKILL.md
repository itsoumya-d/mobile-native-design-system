---
name: mobile-native-audit
description: Use when auditing, reviewing, or safely improving a Flutter, React Native, SwiftUI, or Jetpack Compose application one screen or flow at a time; especially for UX, accessibility, performance, native navigation, motion, adaptive layout, token drift, or design-system gaps. Web and desktop audits are out of scope.
---

# Mobile Native Audit

Audit from the whole-codebase product model, then report one screen or flow at
a time. Auditing does not authorize edits.

## Workflow

1. If no current project model exists, run `$mobile-native-understand`.
2. Run the evidence-backed audit from the plugin root:

```bash
python shared/scripts/mobile_app_audit.py /absolute/path/to/app --profile full --out mobile-audit.json
```

3. Pick one screen or user flow. Cite its current user job, route, behavior,
   design language, dependencies, state model, platform conventions, and
   evidence.
4. Classify findings as proven static findings or heuristic review items. Do
   not present heuristic findings as test failures.
5. Route proposed changes to `$mobile-native-plan`. Route an approved plan to
   `$mobile-native-implement`; do not edit during audit.
6. Verify semantics, focus, touch targets, text scale, RTL, contrast, insets,
   keyboard, compact/tablet widths, loading/empty/error states, and reduced
   motion.

## Framework focus

Flutter audits use widget tree, `Semantics`, `LayoutBuilder`, `TextScaler`,
safe areas, and list/image patterns first. React Native audits check native list
identity, image and navigation handling, and Expo only after detection. SwiftUI
and Compose audits retain their native system navigation, accessibility, and
window-size conventions.

Read `references/audit-severity.md` before reporting findings.
