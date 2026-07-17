# SwiftUI Adapter

## Theme boundary

Generate `MobileTokens.swift` and `MobileTheme.swift`, then convert serialized values into typed `Color`, `Font`, `CGFloat`, `Animation`, and shadow values in one app-owned adapter. Inject the selected `MobileTheme` through the environment.

Prefer system semantic colors and text styles when the intent matches. Use asset-catalog colors when the product palette requires exact appearance variants.

## Components

- Use `Button`, `Toggle`, `TextField`, `Picker`, `NavigationLink`, and native presentation before custom gesture containers.
- Use `NavigationStack` and typed destinations.
- Present contextual actions with native sheets, confirmation dialogs, menus, and alerts.
- Use `Label` when icon and text jointly communicate an action.
- Keep the button's semantic target at least 44 by 44 points, including icon-only controls.

Apply explicit button styles for product identity while retaining role, focus, disabled behavior, and keyboard or switch activation.

## Adaptive layout

Read horizontal and vertical size classes from the environment. Compose compact screens as a single reading column; use grids or supporting panes when the available size is regular. Use `ViewThatFits`, adaptive grids, and container-relative measurement when they simplify reflow.

Respect safe areas by default. Ignore them only for intentional backgrounds, then inset interactive content. Keep primary actions visible when the software keyboard appears; use scrollable forms and native focus management.

## Typography and accessibility

- Use semantic `Font` roles and scalable custom metrics when necessary.
- Read Dynamic Type from the environment; test accessibility categories.
- Avoid fixed text frames and single-line assumptions for important actions.
- Provide `.accessibilityLabel`, value, hint, traits, and custom actions where the visible composition is insufficient.
- Combine children only when the combined announcement remains actionable.
- Respect differentiate-without-color, increased contrast, bold text, and reduced motion.

## Motion

Drive animation from state with `withAnimation` or value-scoped animation modifiers. Use transitions for insertion and removal. Use matched geometry only when it clarifies continuity and both endpoints remain understandable.

Read the reduced-motion environment value. When enabled, remove translation and stagger, use opacity only when it adds needed continuity, or update immediately. Keep animation interruptible and avoid unbounded decorative activity.

## Testing

- Unit-test resolver and formatting logic.
- Use view inspection available in the project or host-state tests for component behavior.
- Run XCTest on configured iPhone and iPad simulators.
- Capture local baselines for compact and regular size classes, both orientations, appearance profiles, largest text, Arabic, and reduced motion.
- Assert accessibility identifiers, labels, values, grouping, and target geometry.
