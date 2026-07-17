# Mobile Component Contracts

Every public component plan names its semantic role, native primitive, token
families, interaction states, async states, accessibility contract, adaptive
rules, haptic intent, and reduced-motion behavior. Use the smallest native
primitive that provides the expected platform behavior.

Buttons, icon buttons, fields, cards, rows, navigation, sheets, and async
states must be modeled as component contracts rather than a screenshot target.
Use a local brief → constraints → plan loop; do not depend on a component API.
