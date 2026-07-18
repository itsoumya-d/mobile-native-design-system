# Product Model Contract

Use `mobile-native-project/2` as the root artifact.

- `screen_graph` records screens, routes, native presentation surfaces, edges,
  entry points, and confidence.
- `behavior_contract` records callbacks, navigation, data writes, analytics,
  permissions, persistence, services, repositories, and protected signatures.
- `design_language` records observed type, color, spacing, shape, icon,
  component, motion, accessibility, adaptive, and inconsistency signals.
- `evidence` records relative path, line, symbol, kind, confidence, evidence
  type, and an excerpt hash rather than copied source.
- `uncertainties` block planning or implementation when an unproven
  relationship could change behavior.

Scanning is deterministic and read-only. Optional compiler or toolchain
evidence may strengthen a relationship, but absence of a toolchain never turns
an inference into a proven fact.
