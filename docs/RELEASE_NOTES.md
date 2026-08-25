# v2.0.1 — Release-hardening patch

- macOS system-Python compatibility: the token compiler no longer uses the
  `write_text(newline=...)` parameter (Python 3.10+) and a new contract pair
  compiles and generates under `/usr/bin/python3`.
- Public-release staging now excludes local Flutter toolchain residue
  (`.flutter-plugins-dependencies`, `.flutter-plugins`, `**/Flutter/ephemeral/`)
  so generated files carrying absolute machine paths can never ship.

# v2.0.0 — Understand first, improve one screen at a time

v2 turns the plugin into a local-first mobile product-intelligence and guarded
implementation system.

- Adds seven progressively disclosed skills for routing, whole-codebase
  understanding, product and screen planning, component forging, native motion,
  evidence-backed audits, and approved one-screen implementation.
- Adds versioned project, screen graph, behavior, design-language, app-plan,
  screen-plan, guard-baseline, and change-receipt artifacts.
- Adds deterministic scanners for Flutter, React Native, SwiftUI, and Compose
  navigation, screens, state, data boundaries, assets, localization, tests, and
  build commands with relative source evidence and confidence.
- Replaces broad source mappings with 30 atomic native capability rules and a
  searchable 20-record product-intelligence catalog spanning all ten source
  families.
- Adds motion spec v2 with variants, timelines, gestures, cancellation,
  interruption, shared identity, haptic intent, performance budgets, lifecycle,
  and reduced motion.
- Adds a deterministic mobile-only request router plus compileable component
  and motion source generation for every supported framework. The generated
  sources are included in the corresponding native fixture compiler inputs.
- Adds approved file scopes and behavior-signature guards that block unapproved
  route, callback, data-write, analytics, permission, and persistence changes.
- Expands all four fixtures with the same production-shaped authentication,
  home/list, detail, check-in form, settings, sheet, async-state,
  localization, adaptive-layout, and accessibility flow.
- Adds Flutter golden/integration coverage, a React Native semantic rendering
  snapshot, a SwiftUI native image-renderer snapshot test, and a Compose
  `captureToImage` instrumentation contract.

v1 APIs for token generation, brief validation, component planning, motion
specification, and static audit remain supported. The `v1.0.0` tag remains
available for reproducible installs.

# v1.0.0 — Flutter-first, native by design

The first public release provides a single Codex plugin with four focused
skills for mobile-native design direction, component plans, motion, and
screen-by-screen audits. It ships deterministic design, component, motion,
token, and audit tools; typed adapters for Flutter, React Native, SwiftUI, and
Compose; four Token Gallery fixtures; and auditable provenance for the ten
research source families.

Flutter is the deepest path in v1. React Native, SwiftUI, and Compose receive
native parity adapters. No browser runtime, stylesheet framework, or source
animation runtime is bundled or required.
