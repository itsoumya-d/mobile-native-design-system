# Native Motion Contracts

Use four original contract families: press feedback, presence, staggered list,
and shared continuity. A motion spec must carry `name`, `kind`, `states`,
`duration_ms`, `easing`, `distance`, `stagger_ms`, `reduced_motion`, and
`gesture` when relevant. Native APIs own timing and interruption.

Flutter uses `AnimationController`, `TweenSequence`, `AnimatedSwitcher`, and
`Hero`; React Native uses `Animated`; SwiftUI uses `Animation` and transitions;
Compose uses `animate*AsState`, `AnimatedVisibility`, and transitions.
