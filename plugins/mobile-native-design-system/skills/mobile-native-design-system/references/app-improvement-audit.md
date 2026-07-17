# Flutter and React Native App Improvement Audit

Use this reference when a user asks which capabilities apply to an existing
mobile app, which screens should improve first, or how to make several apps
more usable without blindly rewriting them.

## Inventory first

Run the local read-only audit from the plugin root:

```bash
python shared/scripts/mobile_app_audit.py /absolute/path/to/flutter-app \
  /absolute/path/to/react-native-app --out app-audit.json
```

The report identifies exactly one supported framework per project (Flutter,
React Native, SwiftUI, or Compose), records
screen-like source files and existing motion, adaptation, accessibility, and
asynchronous-state signals, then emits a prioritized capability route.

Do not scan dependency folders, generated output, backups, or unrelated
projects. Inspect the app's working tree before editing; preserve user changes
and stop if the requested improvement overlaps an unresolved conflicting edit.

## Capability selection

| Capability | Use when | Source family | Native action |
|---|---|---|---|
| Design direction | Hierarchy feels generic or the subject is unclear | frontend-design, ui-ux-pro-max, design-taste | Set subject, user job, signature element, density, type, contrast, and screen hierarchy. |
| Token contract | Values are repeated or inconsistent | ui-ux-pro-max | Replace hard-coded visual values with semantic mobile tokens and generate adapters. |
| Component ideation | A new component needs a deliberate shape | Magic workflow | Locally refine brief → constraints → native primitive composition. |
| Native motion | A state transition, press, entry, exit, or sequence needs feedback | GSAP and Motion concepts | Translate named states, spring, easing, and stagger into Flutter or React Native animation. |
| Accessibility/adaptation | Any interactive screen changes | mobile core | Check touch size, semantics, contrast, font scaling, RTL, insets, keyboard, phone, and tablet. |
| Flutter components | Flutter screen work | Flutter reference | Use ThemeExtension, Material/Cupertino primitives, LayoutBuilder, TextScaler, Semantics, and Flutter animation. |
| React Native components | React Native screen work | shadcn registry model, Vercel React Native | Use native primitives; consult a compatible registry only for discovery. |
| React Native performance | Large list, render issue, media-heavy interaction | Vercel React + React Native | Profile first, then apply native list/image/state improvements. |
| Expo route | The manifest declares Expo | Vercel React Native | Apply Expo-specific advice only in that project. |
| Convex boundary | The app already declares Convex | Convex architectural concepts | Keep data/auth wrappers in the app; feed typed states into UI components. |

Sources that do not match a route stay unloaded. A web runtime request is out
of scope for this skill.

## Prioritization

Rank candidate improvements by:

1. blocked core task or inaccessible action;
2. a screen with user-visible layout, contrast, target-size, text-scale, or
   RTL failure;
3. a repeated component that lacks semantic tokens;
4. a slow or unstable high-traffic list, form, or navigation flow;
5. visual polish or nonessential motion.

Choose one complete flow rather than applying superficial styling to every
screen. Every improved flow needs populated, loading, empty, error, disabled,
and reduced-motion behavior where relevant.

## Flutter workflow

1. Read the app theme, navigation root, and feature screen before changing it.
2. Map literals to semantic tokens through a local theme adapter.
3. Prefer `Scaffold`, native navigation, `SafeArea`, `LayoutBuilder`, scrolling,
   focus traversal, and `Semantics` over custom replacements.
4. Honor `TextScaler`, directionality, insets, and contrast.
5. Use implicit animation for simple state and controllers for coordinated
   transitions; remove distance and stagger under reduced motion.
6. Add unit/widget/accessibility tests and local goldens for phone and tablet.

## React Native workflow

1. Read the manifest first: detect bare React Native, Expo, navigation, and
   existing animation/data dependencies.
2. Map literals to generated `mobileTokens` and a typed theme boundary.
3. Prefer `Pressable`, `TextInput`, virtualized lists, safe-area context, and
   the app's native navigation convention.
4. Honor font scaling, RTL, keyboard avoidance, and accessibility role/label/
   state properties.
5. Use built-in native animation, or Reanimated only when the app already
   intentionally uses it. Respect the system reduced-motion setting.
6. Add TypeScript, Jest/component, native build, and smoke-test coverage.

## Proof

For each app and changed flow, report:

- screen or feature path and selected capability IDs;
- source family routes actually used and ones intentionally not loaded;
- before/after observable behavior;
- token, component, and accessibility tests;
- native build and runtime results;
- simulator/emulator or physical-device gaps.
