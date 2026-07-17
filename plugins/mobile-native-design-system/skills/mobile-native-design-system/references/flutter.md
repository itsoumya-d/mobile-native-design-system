# Flutter Adapter

## Theme boundary

Generate `mobile_tokens.dart` and `mobile_theme_extension.dart`. Convert canonical values once into typed colors, text styles, shapes, shadows, curves, durations, and springs. Register `MobileThemeExtension` with the application theme.

Use the project-local Flutter 3.44 SDK for the planned fixture. Limit generated platforms to iOS and Android and leave any globally installed SDK unchanged.

## Source-to-Flutter translation matrix

Treat the ten requested source families as a routing vocabulary, not ten
dependencies to add to an app. Load only the rows that solve the current
screen's problem; this keeps an audit or implementation focused and bounded.

| Source family | Flutter-native treatment |
|---|---|
| `frontend-design` | Write the screen's subject, user job, hierarchy, design dials, and one signature interaction before composing widgets. Replace page/hero/hover language with screen, navigation, touch, sheet, and gesture decisions. |
| `ui-ux-pro-max` | Audit repeated color, type, spacing, radius, elevation, state, and motion values. Move validated intent into DTCG tokens and `ThemeExtension`; recheck every dataset recommendation against Flutter and platform guidance. |
| `design-taste-frontend` | Use density, contrast, shape, type, and motion dials to critique a real screen. Reject landing-page, DOM, stylesheet, and web-vitals directives. |
| `shadcn-ui-mcp-server` | Do not consume its React Native registry in Flutter. Use its component-inventory idea only, then compose the selected interaction from Material, Cupertino, or app-owned Flutter primitives. |
| `21st.dev Magic MCP` | Recreate its brief → constraints → refine workflow locally. Deliver a dependency-free Flutter composition with loading, empty, error, disabled, and success states. |
| `vercel-react-best-practices` | Translate only platform-neutral state and render discipline: isolate state, retain stable list identity, avoid unnecessary rebuild work, and measure before tuning. Implement with Flutter widgets, providers, and `ListView.builder` or slivers—not React. |
| `gsap-master` | Convert timeline, easing, sequencing, stagger, and performance intent to `AnimationController`, `TweenSequence`, `Curves`, and `Interval`. Keep controllers lifecycle-safe and use immediate or opacity-only reduced motion. |
| `motion-framer` | Convert variants, presence, springs, gestures, and shared-transition intent to `AnimatedSwitcher`, implicit animations, `AnimatedScale`, `AnimatedSlide`, `Dismissible`, `Hero`, or a controller when coordination is necessary. |
| `convex-create-component` | Trigger only if a Flutter app already uses Convex or explicitly requests it. Keep the data/auth boundary app-owned and pass typed loading, empty, error, and populated states to widgets. Do not introduce Convex into Firebase-backed apps. |
| `vercel-react-native-skills` | Do not import or copy React Native implementation. Use it only as a mobile performance/reliability checklist, then apply the equivalent Flutter profiler, image/list, keyboard, and native-build checks. |

Never install or import GSAP, Framer Motion, React, or React Native for a
Flutter screen. Never emit DOM, CSS, utility-class styling, browser, or
web-bundle code.

## Components

- Start from Material or Cupertino controls according to application convention.
- Preserve semantics, focus, ink/press feedback, disabled state, and native presentation.
- Use `SafeArea`, scaffold insets, dialogs, bottom sheets, navigation, and form controls.
- Keep every action at least as large as the active Apple or Android resolver target.

Custom drawing is appropriate for subject-specific visualization, but it must expose equivalent semantics and adapt to appearance, contrast, text, and directionality.

## Adaptive layout and text

Use `LayoutBuilder` for local constraints and media information for system settings. Select compact, medium, or expanded profiles from available width. Use `Flexible`, `Expanded`, wrapping, and scrolling deliberately; do not hide overflow as a layout strategy.

Honor the ambient `TextScaler` and test the largest supported scale. Avoid fixed-height text containers. Use `Directionality` and logical alignment, padding, and border values.

Keep focused fields and actions visible when the input method appears. Consume safe areas and view insets at the appropriate layout boundary.

## Accessibility

Use `Semantics`, merge/exclude semantics carefully, focus traversal, tooltips, live regions, and labeled actions. Run Flutter accessibility guideline checks for labels, target size, and contrast where applicable.

## Motion

Use implicit animations for simple state changes and an `AnimationController`
for coordinated sequences. Use `AnimatedSwitcher` for semantic presence changes
and hero transitions only when they explain continuity. Keep controllers
lifecycle-safe and animations interruptible.

When reduced motion is enabled, select immediate or opacity-only state changes, remove translation and stagger, and retain all content and controls.

## Testing

- Run static analysis and unit, widget, golden, and integration tests.
- Run accessibility guideline checks in widget tests.
- Build iOS and Android artifacts with the project-local SDK.
- Capture phone and tablet goldens for both orientations, appearance profiles, largest text scale, Arabic, insets, input-method behavior, and reduced motion.
