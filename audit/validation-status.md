# Validation Status

## Deterministic repository gates — passed

- Public-release contract, capability registry, mobile design/component/motion
  tools, typed-token generation, app-audit, and clean-staging tests: 10
  passing from the staged public tree.
- Legacy repository contract, audit, routing, forbidden-runtime, and app-audit
  tests: 14 passing before the v1 public release work.
- Source-line audit: 36,075 classified records; no missing, duplicate, drifted,
  malformed, or unclassified records.
- DTCG token validation, deterministic generation, and parity: passed for 141
  semantic tokens.
- Codex skill package validation: passed.
- Clean-context forward routing suite: passed; see
  `audit/forward-routing-tests.md`.

## Fixture verification — passed

| Fixture | Verified locally |
|---|---|
| SwiftUI | Token parity passed. `xcodebuild build` succeeded for iPhone 17 Pro on the installed iOS 26.5 simulator runtime. |
| Jetpack Compose | Token parity passed. Unit-test/build execution is tracked in the limitations below. |
| React Native | Bun install with the frozen lockfile, TypeScript, ESLint, and four Jest component tests passed under Node 26.3.0. |
| Flutter | `flutter analyze`, six widget/accessibility tests, and token parity passed using the installed global Flutter 3.41.3 without modifying it. |

## Native environment limitations — not passed or not available

| Fixture | Limitation | What is needed |
|---|---|---|
| SwiftUI | The requested iOS 18.5 and 26.2 runtimes are absent; only iOS 26.5 is installed. A direct `xcodebuild test` selected the installed iPhone 17 Pro but left it shut down and produced no valid result bundle or test output, so the repository-owned command was stopped. | Install the requested runtimes (or approve 26.5 as the coverage baseline), restore a healthy simulator launch service, and rerun `xcodebuild test` on iPhone SE, iPhone 17 Pro, and iPad Pro 11-inch. |
| Jetpack Compose | API 36 exists at the local Android SDK path. With `ANDROID_HOME` set, two `./gradlew test lint assembleDebug` invocations started a Gradle 9.4.1 daemon but made no task progress or emitted task output; both repository-owned clients were stopped. The requested AGP 9.2 + built-in Kotlin 2.3.10 combination is not provided by AGP 9.2. | Restore Gradle dependency resolution, configure an emulator, and either accept AGP 9.2's bundled Kotlin or upgrade AGP for a supported 2.3.10 pairing. |
| React Native | Android has no SDK configuration. iOS Pods are absent and the local Bundler cannot find the `cocoapods` gem. | Configure Android SDK, run `bundle install`, then `bundle exec pod install --project-directory=ios`, and execute both native debug builds/smoke tests. |
| Flutter | Required project-local Flutter 3.44.0 SDK is absent. | Install it at `fixtures/flutter/.fvm/flutter_sdk` (or set `FLUTTER_SDK`) and run the listed iOS/Android builds and integration tests. |

No physical-device, VoiceOver, or TalkBack certification is claimed.
