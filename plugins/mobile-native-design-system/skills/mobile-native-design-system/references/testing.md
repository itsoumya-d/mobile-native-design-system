# Testing and Completion Gates

## Shared gates

Run:

```bash
python scripts/verify_release.py
python plugins/mobile-native-design-system/shared/scripts/mobile_tokens.py validate plugins/mobile-native-design-system/shared/assets/financial-wellbeing.tokens.json
python plugins/mobile-native-design-system/shared/scripts/mobile_tokens.py generate plugins/mobile-native-design-system/shared/assets/financial-wellbeing.tokens.json --platform all --out .build/generated
python plugins/mobile-native-design-system/shared/scripts/mobile_tokens.py parity plugins/mobile-native-design-system/shared/assets/financial-wellbeing.tokens.json .build/generated
```

Also run the skill package validator. The public repository carries immutable
source-lock and line-audit evidence; it does not distribute upstream source
trees for a fresh line-hash scan.

## Coverage matrix

Within every target framework cover:

- compact phone, large phone, and tablet;
- portrait and landscape;
- light, dark, and high contrast;
- default and largest supported text scale;
- English left-to-right and Arabic right-to-left;
- reduced motion off and on;
- safe areas, edge-to-edge insets, and software keyboard;
- clipping, overflow, and minimum touch targets;
- role, label, value, focus order, grouping, and contrast;
- buttons, icon buttons, text fields, cards, rows, navigation, modal/sheet;
- loading, empty, error, retry, and populated states;
- press feedback and entrance/exit motion.

Semantic parity across frameworks is required. Pixel identity across frameworks is not. Compare each framework only with its own approved baseline.

## SwiftUI

- Swift unit tests and XCTest.
- `xcodebuild test` through the configured simulator workflow.
- iPhone SE, iPhone 17 Pro, and iPad Pro 11-inch simulator coverage.
- iOS 18.5 and 26.2 runtime coverage where installed.

## Compose

- Unit tests and lint.
- Compose screenshot tests.
- `assembleDebug`.
- Connected instrumentation on Pixel 9 and Pixel Tablet API 36.

Use the official BOM as compatibility truth.

## React Native

- TypeScript, Jest, and native component tests.
- iOS and Android debug builds.
- Native launch and smoke tests with Hermes and the New Architecture.

## Flutter

- Static analysis.
- Unit, widget, golden, and accessibility-guideline tests.
- Android and iOS builds.
- Integration tests using the project-local 3.44 SDK.

## Completion report

Report commands with exit status and concise results. Separate:

- tests actually run and passed;
- tests skipped because a runtime or emulator was unavailable;
- manual or physical-device checks not performed.

Do not convert a skipped device matrix into a passing claim.
