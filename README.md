# Mobile-Native Design System

[![Core validation](https://github.com/itsoumya-d/mobile-native-design-system/actions/workflows/core.yml/badge.svg)](https://github.com/itsoumya-d/mobile-native-design-system/actions/workflows/core.yml)

![Mobile-Native Design System icon](plugins/mobile-native-design-system/assets/logo.png)

A Flutter-first Codex plugin that understands an entire native mobile
codebase, plans evidence-backed product improvements, and safely implements one
approved screen at a time. It supports Flutter/Dart, React Native/TypeScript,
SwiftUI/Swift, and Jetpack Compose/Kotlin without turning mobile apps into
browser-shaped UI.

## Install

```bash
codex plugin marketplace add itsoumya-d/mobile-native-design-system --ref v2.0.0
codex plugin add mobile-native-design-system@mobile-native-design-system
```

Restart or start a new Codex task after installing so the skill catalog refreshes.

## Seven progressively disclosed skills

| Skill | Use it for |
|---|---|
| `mobile-native-design-system` | Route mobile-only design-system and token work to the smallest relevant guidance. |
| `mobile-native-understand` | Reconstruct framework, routes, screens, behavior, state, data boundaries, design language, assets, localization, tests, and build commands. |
| `mobile-native-plan` | Create the prioritized whole-product roadmap and an approval-required contract for one screen or flow. |
| `mobile-native-component-forge` | Convert a brief into a native component plan with states, semantics, adaptive behavior, and tokens. |
| `mobile-native-motion` | Produce native timeline, spring, gesture, presence, and reduced-motion recipes. |
| `mobile-native-audit` | Review product and screen evidence without presenting heuristic findings as proven failures. |
| `mobile-native-implement` | Apply one approved screen plan with dirty-state, file-scope, and behavior-signature guards. |

## What it ships

- A read-only whole-codebase scanner emitting versioned project, screen graph,
  behavior, and design-language artifacts with relative source evidence.
- A 30-rule atomic registry mapping all ten requested source families to native
  triggers, evidence, benefit, validation, legal treatment, rejection
  conditions, provenance, and explicit runtime exclusions.
- Searchable mobile design intelligence and local brief → component-plan
  refinement—no required external component service.
- Deterministic standard-library tools for app and screen planning, guarded
  verification, design intelligence, component plans, motion recipes, typed
  design-token generation, and static audits.
- A deterministic request router that selects exactly one focused skill and
  framework reference—or rejects an explicit web-only request.
- Compileable original native component and motion starters, generated from
  shared contracts and checked as source inputs by all four fixtures.
- Typed token adapter APIs retaining `MobileTokens` and `MobileTheme` names for
  Flutter, React Native, SwiftUI, and Compose.
- Four production-shaped native fixtures with the same authentication-shaped
  entry, navigation, lists, detail, form, settings, sheet, async/error/empty
  states, localization, tablet behavior, accessibility, and motion contract,
  plus the complete Token Gallery.

## Local product-intelligence workflow

```bash
python plugins/mobile-native-design-system/shared/scripts/mobile_project.py \
  scan /absolute/path/to/app --profile full --out project-model.json

python plugins/mobile-native-design-system/shared/scripts/mobile_design.py \
  synthesize project-model.json --out design-language.json

python plugins/mobile-native-design-system/shared/scripts/mobile_plan.py \
  create project-model.json --scope app --out redesign-plan

python plugins/mobile-native-design-system/shared/scripts/mobile_plan.py \
  screen project-model.json ScreenID --out screen-plan.json

python plugins/mobile-native-design-system/shared/scripts/mobile_route.py \
  "Audit this Flutter checkout screen for accessibility"
```

Implementation remains locked until `screen-plan.json` is explicitly approved.
`mobile_guard.py baseline` records file hashes, behavior signatures, and dirty
state before changes; `mobile_guard.py verify` emits
`mobile-native-change-receipt/1` afterward.

To emit a compileable native component starter alongside its plan:

```bash
python plugins/mobile-native-design-system/shared/scripts/mobile_component.py \
  generate brief.json --platform flutter --project-context project-model.json \
  --screen-id ScreenID --out component-plan.json --code-out native_component.dart
```

## Platform support

| Platform | v2 support |
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
| shadcn-ui MCP | Local component-intent discovery for every platform; optional compatible registry metadata only in React Native. |
| 21st.dev Magic MCP | Fully local context → intent → constraints → alternatives → native refinement workflow. |
| React best practices | State ownership, derived state, stable identity, immutable events, render isolation, and async boundaries in all four reactive frameworks. |
| GSAP and Motion/Framer | Native timeline, variant, spring, gesture, lifecycle, interruption, shared-transition, performance, and reduced-motion recipes. |
| Convex component | Conditional typed async and app-facing data boundary; no backend dependency. |
| Vercel React Native | Deep React Native/Expo checks plus carefully translated native product lessons for lists, images, navigation, insets, modals, accessibility, and performance. |

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
certification remain outside automated v2 gates unless you perform and record
them.

## Licensing and provenance

This project is [MIT licensed](LICENSE). It retains source locks and a
line-by-line audit for the ten requested research inputs without distributing
their upstream repositories. See [third-party notices](THIRD_PARTY_NOTICES.md)
and [`audit/sources.lock.json`](audit/sources.lock.json).

Security contact: see [SECURITY.md](SECURITY.md). Release details are in
[`docs/RELEASE_NOTES.md`](docs/RELEASE_NOTES.md).
