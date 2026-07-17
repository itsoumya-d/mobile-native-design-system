# React Native Adapter

## Baseline and routing

Target React Native 0.86 with the New Architecture and Hermes for the planned fixture. Detect Expo from the project manifest before applying Expo-only rules. Do not add Expo to a bare project solely for this skill.

Use platform-neutral React guidance only when it also applies to native rendering. Native list, image, gesture, animation, navigation, and bridge behavior takes precedence.

## Theme boundary

Generate `tokens.ts` and `theme.ts`. Convert canonical values once in the theme/provider layer. Expose typed semantic tokens to components; do not parse token strings during render.

Use `StyleSheet` or the project's established native styling layer. Keep all generated token names available through `mobileTokens`, `MobileTheme`, and `createMobileTheme`.

## Components

- Use `View`, `Text`, `Image`, `Pressable`, `TextInput`, native switches, and the project's native navigation library.
- Use `Pressable` state for touch feedback and include disabled and loading behavior.
- Use virtualized lists for large collections with stable keys and lightweight rows.
- Use `react-native-safe-area-context` for safe-area values.
- Keep icon-only actions at the platform resolver's minimum target size.

Confirm native compatibility before consulting or adopting a registry component. Treat a registry as discovery, then bind the component to local semantics, tokens, tests, and dependency policy.

## Adaptive layout and text

Use `useWindowDimensions` and flex layout to select compact, medium, or expanded profiles from available width. Do not store the first measured width as a permanent device category.

Honor native font scaling. Let important labels wrap, set maximum scaling only when a documented product constraint requires it, and test both platforms at the largest supported scale.

Use logical start/end values and test right-to-left layout. Account for input-method avoidance and scrolling rather than moving a fixed screen by a guessed offset.

## Accessibility

Set native roles, labels, hints, values, checked/selected/disabled/busy states, live announcements, and focus order. Group only when the resulting announcement remains operable. Test with component queries that match assistive semantics.

## Motion

Use the built-in native animation system or Reanimated when it is already an intentional project dependency. Animate state changes, not render side effects. Keep work off the JavaScript thread where the chosen API supports it.

Observe the system reduce-motion setting. Remove translation and stagger, preserve final states, and avoid continuous decorative loops.

## Testing

- Run TypeScript, Jest, and native component tests.
- Build iOS and Android debug variants and launch native smoke tests.
- Cover phone and tablet dimensions, both orientations, appearance profiles, largest font scale, Arabic, insets, input-method behavior, and reduced motion.
- Profile representative lists and image-heavy rows rather than adding memoization speculatively.
