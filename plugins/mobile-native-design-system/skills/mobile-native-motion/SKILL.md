---
name: mobile-native-motion
description: Use when specifying or implementing native mobile animation, press feedback, entrance or exit, staggered lists, gestures, shared transitions, springs, timeline sequencing, or reduced-motion behavior for Flutter, React Native, SwiftUI, or Jetpack Compose. Web animation runtimes are out of scope.
---

# Mobile Native Motion

Describe motion as state continuity, not decoration. Every recipe has named
states, interruption behavior, a resting state, and a reduced-motion path.

## Workflow

1. Identify the state change and user benefit. Do not animate an action whose result needs to be immediate.
2. Define duration, easing or spring, distance, stagger, gesture threshold, and cancellation behavior in a motion spec.
3. Validate and generate target-native recipes from the plugin root:

```bash
python shared/scripts/mobile_motion.py validate motion.json
python shared/scripts/mobile_motion.py generate motion.json --platform all --out generated-motion
```

4. Use the generated platform recipe as a starting point: `AnimationController` or implicit animation in Flutter, `Animated` in React Native, `Animation` in SwiftUI, and transitions in Compose.
5. In reduced motion, remove distance and stagger; use immediate or opacity-only changes while retaining all actions, labels, and information.

## Checks

- Press feedback completes or cancels with the gesture.
- Entrance and exit do not trap focus or leave an inaccessible state.
- Shared transitions only explain real continuity between native navigation destinations.
- Haptics remain intent tokens, not a requirement for every animation.

Read `references/native-motion-contracts.md` for component-specific contracts.
