---
name: mobile-native-design-system
description: Use when designing, generating, implementing, migrating, or routing a mobile-only design system or interface for Flutter, React Native, SwiftUI, or Jetpack Compose; especially when translating web-shaped briefs into native screens, producing cross-platform tokens, or deciding which mobile design, component, motion, or audit guidance applies. Web and desktop implementations are out of scope.
---

# Mobile-Native Design System

Route the task first. Flutter is the deepest implementation path; React Native,
SwiftUI, and Compose are native adapters with semantic parity rather than pixel
identity.

## Route

1. Inspect the request and app manifests. If explicitly web-only, state that
   this plugin is out of scope and route to a web skill.
2. Load exactly one focused sibling skill:

| Need | Skill |
|---|---|
| Visual direction, component shape, states, or a native plan | `$mobile-native-component-forge` |
| Timelines, springs, gestures, transitions, or reduced motion | `$mobile-native-motion` |
| One-screen UX, accessibility, performance, or token review | `$mobile-native-audit` |

3. Read `references/core-design-system.md`, then only the selected framework
   reference. Read `references/token-contract.md` for token work and
   `references/routing-and-provenance.md` for source-family routing.
4. Load several framework references only when the user explicitly needs
   several target implementations.

## Invariants

- Use logical design units: points, dp, DIP, and Flutter logical pixels—not
  physical pixels.
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
