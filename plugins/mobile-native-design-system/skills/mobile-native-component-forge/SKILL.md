---
name: mobile-native-component-forge
description: Use when planning, designing, generating, or refining a Flutter, React Native, SwiftUI, or Jetpack Compose component or screen; especially when a brief is ambiguous, a component needs complete interaction and async states, a native primitive must be chosen, or a visual result feels generic. Web implementation is out of scope.
---

# Mobile Native Component Forge

Create a component plan before code so each screen is deliberate, accessible,
adaptive, and native to its platform.

## Workflow

1. Determine the framework from the request and project manifest. Default to Flutter only if no platform is supplied.
2. Write a brief with subject, user job, primary action, hierarchy, and a signature interaction. Choose density, contrast, shape, type, and motion dials.
3. Validate and emit the component plan from the plugin root:

```bash
python shared/scripts/mobile_design.py validate brief.json
python shared/scripts/mobile_component.py generate brief.json --platform flutter --out component-plan.json
```

4. Start with the native primitive named in the plan. Include default, pressed, focused, selected, disabled, loading, empty, error, retry, and populated states when applicable.
5. Confirm semantics, focus order, minimum touch target, text scaling, RTL, safe area, keyboard, compact/tablet behavior, haptic intent, and reduced motion before custom polish.

## Native choices

| Platform | Prefer |
|---|---|
| Flutter | Material/Cupertino, `ThemeExtension`, `LayoutBuilder`, `Semantics` |
| React Native | native controls, `Pressable`, virtualized lists, accessibility props |
| SwiftUI | system controls, `NavigationStack`, `sheet`, environment values |
| Compose | Material3, immutable state, `Modifier.semantics`, window size classes |

For a component inventory, design intelligence, or source rationale, read
`references/component-contracts.md`. Do not import a React Native registry into
Flutter, SwiftUI, or Compose. Do not use a remote component service as a build
dependency.
