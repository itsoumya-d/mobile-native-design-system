---
name: mobile-native-design-system
description: Use when understanding, planning, designing, auditing, implementing, migrating, or routing a mobile-only product or design system for Flutter, React Native, SwiftUI, or Jetpack Compose; especially when a whole codebase must be modeled before a safe one-screen redesign, when translating design capabilities into native code, or when deciding which focused product-intelligence, component, motion, audit, or implementation workflow applies. Web and desktop implementations are out of scope.
---

# Mobile-Native Design System

Route the task first. Understand the existing product before recommending or
editing it. Flutter is the deepest implementation path; React Native, SwiftUI,
and Compose retain first-class native semantics and behavior.

## Route

1. Inspect the request and app manifests. If explicitly web-only, state that
   this plugin is out of scope and route to a web skill.
   Use `python shared/scripts/mobile_route.py "<request>"` when a
   machine-readable routing receipt is useful.
2. Load only the focused sibling skill needed for the current phase:

| Need | Skill |
|---|---|
| Scan the whole codebase and reconstruct screens, routes, behavior, design language, assets, and tests | `$mobile-native-understand` |
| Produce the whole-product roadmap or one-screen approval contract | `$mobile-native-plan` |
| Design component intent, alternatives, states, and native composition | `$mobile-native-component-forge` |
| Timelines, springs, gestures, transitions, or reduced motion | `$mobile-native-motion` |
| Evidence-backed UX, accessibility, performance, or token review | `$mobile-native-audit` |
| Apply one approved screen plan with baseline and behavior guards | `$mobile-native-implement` |

3. Read `references/core-design-system.md`, then only the selected framework
   reference. Read `references/token-contract.md` for token work and
   `references/routing-and-provenance.md` for source-family routing.
4. Load several framework references only when the user explicitly needs
   several target implementations.

## Invariants

- Use logical design units: points, dp, DIP, and Flutter logical pixels—not
  physical pixels.
- Scan before planning. Plan before implementation. Edit one explicitly
  approved screen or flow at a time.
- Cite path, symbol, line, confidence, and evidence type for every inferred
  project relationship. Treat uncertainty as a question or stop condition.
- Preserve routes, callbacks, state ownership, repositories, services, APIs,
  analytics, permissions, persistence, and side effects unless the approved
  plan explicitly changes them.
- Use semantic roles, native system controls, system navigation, adaptive
  layouts, assistive semantics, text scaling, safe areas, keyboard avoidance,
  RTL, and platform animation APIs.
- Resolve Apple touch targets to at least 44 points and Android targets to at
  least 48 dp.
- Model default, pressed, focused, selected, disabled, loading, empty, error,
  and high-contrast states as applicable.
- In reduced motion, remove nonessential distance and stagger while preserving
  every action and item of information.
- Keep the design system backend-independent. Convex is a conditional app
  boundary only when an existing app already uses it.
- Preserve pre-existing dirty changes. Never use destructive rollback.
- Do not install a browser runtime, stylesheet framework, or source animation
  runtime. Translate capability intent to native APIs.

## Token adapters

From the plugin root:

```bash
python shared/scripts/mobile_tokens.py validate shared/assets/financial-wellbeing.tokens.json
python shared/scripts/mobile_tokens.py generate shared/assets/financial-wellbeing.tokens.json --platform all --out generated
python shared/scripts/mobile_tokens.py parity shared/assets/financial-wellbeing.tokens.json generated
```

The generated APIs retain `MobileTokens` and `MobileTheme` names for Flutter,
React Native, SwiftUI, and Compose.

## Product intelligence

Run focused workflows through the sibling skills. The versioned artifacts are
`mobile-native-project/2`, `mobile-native-screen-graph/1`,
`mobile-native-behavior-contract/1`, `mobile-native-design-language/1`,
`mobile-native-app-plan/1`, `mobile-native-screen-plan/1`, and
`mobile-native-change-receipt/1`.

## Evidence

Report token and parity results, generated artifact hashes, framework tests,
and actual coverage for scale, directionality, contrast, reduced motion,
insets, keyboard, and accessibility. State simulator, emulator, and physical
device gaps plainly.

## Resources

- `references/core-design-system.md`
- `references/token-contract.md`
- `references/flutter.md`, `react-native.md`, `swiftui.md`, `compose.md`
- `references/routing-and-provenance.md`
