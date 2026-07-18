---
name: mobile-native-implement
description: Use when implementing an explicitly approved mobile-native-screen-plan/1 for exactly one Flutter, React Native, SwiftUI, or Jetpack Compose screen or coherent flow; especially when existing features, navigation, state, data writes, analytics, permissions, persistence, dirty changes, accessibility, adaptive behavior, motion, tests, and native builds must be preserved and verified. Do not use for unapproved plans, whole-app bulk rewrites, web, or desktop.
---

# Mobile Native Implement

Change one approved screen or flow and prove protected behavior remains intact.

## Preconditions

Require `approval.status: approved`, an exact allowed file list, current source
hashes, behavior invariants, tests, and acceptance criteria. Stop and return to
`$mobile-native-plan` if any item is missing or stale.

## Workflow

1. Capture the guard baseline before edits:

```bash
python shared/scripts/mobile_guard.py baseline /absolute/path/to/app screen-plan.json --out baseline.json
```

2. Inspect the current dirty state. Preserve user changes and stop when
   ownership of an approved dirty file is not acknowledged.
3. Edit only allowed UI files. Treat business logic, repositories, services,
   APIs, analytics, permissions, persistence, navigation destinations, and
   generated code as protected unless the approved plan names them.
4. Implement the target framework's native composition, semantics, adaptive
   behavior, keyboard and inset handling, motion, haptics, and reduced motion.
5. Run existing tests, the plan's native commands, accessibility checks, and
   visual comparison. Never claim unavailable device coverage.
6. Verify static invariants:

```bash
python shared/scripts/mobile_guard.py verify /absolute/path/to/app screen-plan.json baseline.json --out change-receipt.json
```

7. Stop if the receipt is not `ok`. Never use destructive rollback. Report
   changed files, commands and results, screenshots, preserved invariants, and
   unresolved risks before choosing another screen.

Read `references/implementation-guard.md` for the protected-boundary rules.
