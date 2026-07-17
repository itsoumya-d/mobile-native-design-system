# Mobile-Native Design System

[![Core validation](https://github.com/itsoumya-d/mobile-native-design-system/actions/workflows/core.yml/badge.svg)](https://github.com/itsoumya-d/mobile-native-design-system/actions/workflows/core.yml)

![Mobile-Native Design System icon](plugins/mobile-native-design-system/assets/logo.png)

A Flutter-first Codex plugin for designing, planning, animating, auditing, and
tokenizing genuinely native mobile interfaces. It supports Flutter/Dart, React
Native/TypeScript, SwiftUI/Swift, and Jetpack Compose/Kotlin without turning
mobile apps into browser-shaped UI.

## Install

```bash
codex plugin marketplace add itsoumya-d/mobile-native-design-system --ref v1.0.0
codex plugin add mobile-native-design-system@mobile-native-design-system
```

Restart or start a new Codex task after installing so the skill catalog refreshes.

## Four focused skills

| Skill | Use it for |
|---|---|
| `mobile-native-design-system` | Route mobile-only design-system and token work to the smallest relevant guidance. |
| `mobile-native-component-forge` | Convert a brief into a native component plan with states, semantics, adaptive behavior, and tokens. |
| `mobile-native-motion` | Produce native timeline, spring, gesture, presence, and reduced-motion recipes. |
| `mobile-native-audit` | Review one screen or flow at a time without breaking existing app behavior. |

## What it ships

- A versioned registry mapping all ten requested source families to native
  capability, validation, legal treatment, and explicit runtime exclusions.
- Searchable mobile design intelligence and local brief → component-plan
  refinement—no required external component service.
- Deterministic standard-library tools for design intelligence, component plans,
  motion recipes, typed design-token generation, and static app audits.
- Typed token adapter APIs retaining `MobileTokens` and `MobileTheme` names for
  Flutter, React Native, SwiftUI, and Compose.
- Four Token Gallery fixtures with semantic components, states, motion,
  accessibility stress coverage, adaptive layout, and RTL/reduced-motion hooks.

## Platform support

| Platform | v1 support |
|---|---|
| Flutter/Dart | Deepest path: native widgets, `ThemeExtension`, `LayoutBuilder`, `TextScaler`, `Semantics`, and native animation. |
| React Native/TypeScript | Native components, state/render rules, lists, images, navigation, and Expo-only routing when detected. |
| SwiftUI/Swift | Semantic system type, environment values, dynamic type, size classes, native navigation, sheets, and animation. |
| Jetpack Compose/Kotlin | Immutable token types, composition locals, Material3, window size classes, semantics, Insets, and transitions. |

## Source-family translation

| Source family | Mobile-native result |
|---|---|
| frontend-design | Screen brief, hierarchy, signature interaction, critique gate. |
| ui-ux-pro-max | Revalidated mobile design intelligence and token-scale audits. |
| design-taste-frontend | Design dials and anti-generic mobile critique. |
| shadcn-ui MCP | React Native discovery only; never a Flutter, SwiftUI, or Compose dependency. |
| 21st.dev Magic MCP | Local brief → constraints → native refinement workflow. |
| React best practices | React Native render/state/performance rules, not server or browser guidance. |
| GSAP and Motion/Framer | Native timeline, variant, spring, gesture, and reduced-motion recipes. |
| Convex component | Conditional typed async component boundary; no backend dependency. |
| Vercel React Native | React Native/Expo detection, lists, images, navigation, accessibility, and performance checks. |

## Validation

Run the deterministic public gate:

```bash
python scripts/verify_release.py
```

The repository also includes native fixture workflows for Flutter, React Native,
SwiftUI, and Compose. Native SDK and simulator/emulator coverage is recorded in
[`audit/validation-status.md`](audit/validation-status.md); unavailable local
runtimes are documented rather than claimed as passed.

## Scope and privacy

This plugin is mobile-only. It does not generate or require DOM, CSS, Tailwind,
browser, GSAP, Framer Motion, or a remote MCP service. It is backend-independent
and never uploads application source. Physical-device and manual screen-reader
certification remain outside v1 unless you perform and record them.

## Licensing and provenance

This project is [MIT licensed](LICENSE). It retains source locks and a
line-by-line audit for the ten requested research inputs without distributing
their upstream repositories. See [third-party notices](THIRD_PARTY_NOTICES.md)
and [`audit/sources.lock.json`](audit/sources.lock.json).

Security contact: see [SECURITY.md](SECURITY.md). Release details are in
[`docs/RELEASE_NOTES.md`](docs/RELEASE_NOTES.md).
