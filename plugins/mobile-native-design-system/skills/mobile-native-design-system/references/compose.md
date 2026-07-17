# Jetpack Compose Adapter

## Theme boundary

Generate `MobileTokens.kt` and `MobileTheme.kt`. Convert serialized values once into immutable Kotlin token types, Material 3 color and type schemes, shapes, and motion specs. Provide them through stable composition locals inside the app theme.

Use the official Compose BOM as the compatibility source. With the planned baseline, use API 36, JDK 17, Gradle 9.4.1, AGP 9.2, built-in Kotlin 2.3.10, the `2026.06.00` BOM, and Material 3.

## Components

- Start from Material 3 buttons, icon buttons, fields, cards, list items, navigation, dialogs, and sheets.
- Preserve semantics, ripple/indication, focus, enabled state, and minimum interactive sizing.
- Use `Modifier.clickable` or a component's action API rather than a raw pointer callback.
- Keep app-specific financial status separate from the Material color scheme, then expose it through the theme.

## Adaptive layout and insets

Use Android window size classes for compact, medium, and expanded decisions. Prefer constraint-aware composition over device-name checks. Support edge-to-edge layout and consume system bars, display cutouts, gesture areas, and input-method insets once.

Keep list and form actions visible under the software keyboard. Use lazy containers for long collections and give nested scrolling structures bounded constraints.

## Typography and semantics

- Use scalable text units and Material semantic roles.
- Read user font scale through density and test the supported maximum.
- Let rows grow vertically and labels wrap.
- Add semantics for role, content description, state description, progress, headings, traversal order, and custom actions as appropriate.
- Use logical start/end layout and test Arabic directionality.

## Motion

Use state-driven animation primitives, animated visibility, transitions, and native gesture APIs. Limit motion to properties the renderer handles efficiently. Give every animation a stable resting state and a descriptive label for tooling.

When reduced motion is requested, choose immediate updates or opacity when continuity is necessary. Remove decorative translation and stagger. Do not gate information behind animation.

## Testing

- Unit-test token conversion and state reducers.
- Run Compose UI tests for roles, labels, focus order, actions, and geometry.
- Run lint, screenshot tests, debug assembly, and connected instrumentation.
- Cover Pixel phone and tablet configurations at API 36, both orientations, appearance profiles, largest font scale, Arabic, and reduced motion.
