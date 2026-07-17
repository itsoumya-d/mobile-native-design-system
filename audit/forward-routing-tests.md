# Clean-Context Forward Routing Tests

On 2026-07-17, three independent read-only contexts received only the v1
plugin path and realistic prompts. They selected the four focused skills and
native references without being shown intended answers. No result authorized a
browser runtime, stylesheet framework, source animation runtime, or remote
component service.

| Prompt family | Route observed | Result |
|---|---|---|
| Flutter subscription checkout with async payment states, tablet layout, and confirmation motion | Router → `mobile-native-component-forge`; Flutter, component-contract, and testing references; motion skill only for a subsequent animation pass | Correct: app-owned payment boundary, typed ready/processing/error/retry/success states, `ThemeExtension`, `LayoutBuilder`, `TextScaler`, `Semantics`, native press feedback, and an interruptible `AnimatedSwitcher` reduced-motion path. |
| SwiftUI iPad spending review with reduced motion | Router → component forge → SwiftUI adapter | Correct: system navigation, Dynamic Type, 44-point targets, adaptive regular-width layout, typed async states, and immediate or opacity-only reduced motion. |
| Same semantic feature in Compose and a platform-unspecified design system | Router → component forge plus Compose or token references | Correct: Material3, window-size classes, semantics, 48-dp targets, insets, state-driven motion, semantic parity rather than pixel identity, and a request for platform/product clarification when no adapter exists. |
| React Native sheet requested with GSAP and Framer Motion | Router → `mobile-native-motion` → React Native adapter | Correct: translate closed/open/dragging/settling states to native `Animated`; do not install either source runtime; validate gesture cancellation, modal semantics, keyboard, RTL, and reduced motion. |
| Explicit Convex-backed Flutter activity component | Router → component forge → Flutter adapter | Correct: Convex/auth/environment stays behind an app-owned repository/controller; Flutter UI consumes typed loading/empty/error/retry/populated states. |
| Explicit Next.js/Tailwind marketing page | Router out-of-scope gate | Correct: mobile plugin stopped and routed to a web workflow without emitting a mobile implementation. |

These are behavioral routing tests, not a claim about upstream source
correctness. The machine-enforced companion gate is
`tests/test_release_contract.py`.
