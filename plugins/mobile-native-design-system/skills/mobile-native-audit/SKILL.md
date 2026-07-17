---
name: mobile-native-audit
description: Use when auditing, reviewing, or safely improving a Flutter, React Native, SwiftUI, or Jetpack Compose application one screen or flow at a time; especially for UX, accessibility, performance, native navigation, motion, adaptive layout, token drift, or design-system gaps. Web and desktop audits are out of scope.
---

# Mobile Native Audit

Audit one screen or flow before changing it. Preserve existing features unless
the user explicitly authorizes a behavior change.

## Workflow

1. Run the deterministic inventory from the plugin root:

```bash
python shared/scripts/mobile_app_audit.py /absolute/path/to/app --profile full --out mobile-audit.json
```

2. Pick one screen or user flow. Record its user job, current design language, dependencies, state model, platform conventions, and deterministic findings.
3. Classify recommendations as proven static findings or heuristic review items. Do not present heuristic findings as test failures.
4. Improve only the selected screen, preserve navigation and data behavior, then run that framework's tests and repeat with the next screen.
5. Verify semantics, focus, touch targets, text scale, RTL, contrast, insets, keyboard, compact/tablet widths, loading/empty/error states, and reduced motion.

## Framework focus

Flutter audits use widget tree, `Semantics`, `LayoutBuilder`, `TextScaler`,
safe areas, and list/image patterns first. React Native audits check native list
identity, image and navigation handling, and Expo only after detection. SwiftUI
and Compose audits retain their native system navigation, accessibility, and
window-size conventions.

Read `references/audit-severity.md` before reporting findings.
