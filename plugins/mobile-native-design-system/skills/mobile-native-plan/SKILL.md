---
name: mobile-native-plan
description: Use when creating a product-wide redesign roadmap or a detailed one-screen implementation contract for a previously scanned Flutter, React Native, SwiftUI, or Jetpack Compose app; especially when recommendations must cite current code, select relevant capabilities from all ten source families, score benefit and risk, preserve behavior, define native composition and motion, bound files, and state verification criteria. Web planning is out of scope.
---

# Mobile Native Plan

Plan the whole product, then isolate one screen or flow for approval.

## Workflow

1. Require a current `mobile-native-project/2` artifact. If source hashes drift,
   rerun `$mobile-native-understand`.
2. Create the prioritized product roadmap:

```bash
python shared/scripts/mobile_plan.py create project-model.json --scope app --out redesign-plan
```

3. Review recommendation scores, current-code evidence, user benefit, selected
   capabilities, native implementation, behavior invariants, accessibility,
   motion, risk, confidence, commands, and acceptance criteria.
4. Select one screen and create its bounded contract:

```bash
python shared/scripts/mobile_plan.py screen project-model.json ScreenID --out screen-plan.json
```

5. Leave `approval.status` as `approval-required` until the user accepts that
   exact screen or flow and file scope. Planning does not authorize edits.

## Selection rules

Select only source capabilities supported by screen evidence. Keep all ten
families available through the registry, but do not force irrelevant
capabilities onto a screen. Mark backend, registry, Expo, and other conditional
capabilities explicitly.

Read `references/planning-contract.md` for scoring, required recommendation
fields, and stop conditions.
