# Validation Status

Validated locally on 2026-07-18. This file separates proven repository and
compiler results from simulator, emulator, and physical-device coverage that
was unavailable.

## Deterministic repository gates — passed

- `python3.13 scripts/verify_project.py`: passed.
- Python contract suite: 40 tests passed.
- Public release staging, v1 compatibility, v2 schema, whole-codebase scan,
  route/screen/behavior/design extraction, planning, guarded one-screen
  verification, deterministic routing, component generation, motion
  generation, and forbidden-runtime gates: passed.
- Source-line audit: 36,075 classified records with no missing, duplicate,
  drifted, malformed, or unclassified records.
- DTCG token validation, deterministic generation, and parity: passed for 141
  semantic tokens across seven resolver profiles.
- All seven v2 skills and the retained v1 skill: Codex quick validation passed.
- Codex plugin ingestion validator: passed for the v2 plugin manifest and all
  seven included skills.
- Clean public allowlist staging excludes upstream clones, local app findings,
  dependencies, build caches, absolute-path artifacts, and private worktrees.

## Native fixture verification — passed locally

| Fixture | Proven local result |
|---|---|
| Flutter | Global Flutter 3.41.3: `flutter analyze`, eight widget/unit/accessibility/golden tests, one compact visual golden, and `flutter build apk --debug` passed. The integration-test source is analyzed and its API 36 execution is configured in GitHub Actions. Generated component and motion Dart are analyzer inputs. |
| React Native | React Native 0.86 / Node 26: TypeScript, ESLint, six Jest component tests, and one semantic rendering snapshot passed. Android New Architecture/Hermes `assembleDebug` passed. CocoaPods installation and the iOS workspace debug build passed. Generated component and motion TypeScript are compiler inputs. |
| SwiftUI | Swift 6 / iOS 17 deployment: the app simulator build passed through XcodeBuildMCP with no project warnings. `xcodebuild build-for-testing` compiled and linked the app, generated component/motion sources, XCTest bundle, and native `ImageRenderer` snapshot test. |
| Jetpack Compose | API 36 / JDK 17 / Gradle 9.4.1 / Compose BOM 2026.06.00: unit tests, lint, `assembleDebug`, and `assembleDebugAndroidTest` passed. The instrumented suite includes semantics, retry behavior, and a native `captureToImage` visual capture. Generated component and motion Kotlin are compiler inputs. |

## Native execution limitations — not claimed as passed

| Fixture | Limitation | Release automation |
|---|---|---|
| Flutter | The required project-local Flutter 3.44 SDK is absent. The local iOS simulator build reached CoreSimulator but failed when `AssetCatalogSimulatorAgent` could not launch. The new integration test was not executed locally because no Android emulator is connected. | Core CI pins Flutter 3.44 for analyze, unit/golden tests, and Android build. Native Android CI runs the integration test on API 36. Native Apple CI builds the Flutter iOS simulator target. |
| React Native | Native Android instrumentation and iOS UI execution were not run locally. | Android and Apple workflows build both native applications; JavaScript behavior and rendering snapshots remain required in core CI. |
| SwiftUI | Multiple `xcodebuild test` / XcodeBuildMCP attempts timed out or lost the CoreSimulator service before any XCTest executed. This is not reported as a passing runtime test. Only iOS 26.5 is installed locally; the requested 18.5 and 26.2 runtimes are absent. | Native Apple CI runs `xcodebuild test` on its latest installed iPhone simulator. |
| Jetpack Compose | No emulator is connected locally, so `connectedDebugAndroidTest` was not executed. | Native Android CI runs the compiled instrumentation and visual-capture suite on a Pixel 9 API 36 emulator. |

No physical-device, manual VoiceOver, or manual TalkBack certification is
claimed. A `v2.0.0` tag must not be created until the required GitHub Actions
jobs pass for the exact public commit.
