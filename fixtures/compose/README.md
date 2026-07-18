# Jetpack Compose Token Gallery

Android phone and tablet fixture for the shared financial-wellbeing semantic
token contract. The generated Kotlin adapter is under
`app/src/main/java/mobile/tokens/`; regenerate it instead of hand-editing:

```sh
python3 ../../plugins/mobile-native-design-system/shared/scripts/mobile_tokens.py generate \
  ../../plugins/mobile-native-design-system/shared/assets/financial-wellbeing.tokens.json \
  --platform kotlin --out app/src/main/java
```

## Toolchain

- API/compile/target SDK 36
- JDK 17
- AGP 9.2.0 and Gradle 9.4.1
- Compose BOM `2026.06.00` with Material 3
- Built-in Kotlin is enabled through `android.builtInKotlin=true`.

AGP 9.2.0's published distribution bundles Kotlin 2.2.10, so it cannot also
provide the plan's requested built-in Kotlin 2.3.10. The Compose BOM remains
the source of truth for Compose library compatibility; upgrade AGP before
claiming a 2.3.10 built-in-Kotlin matrix.

## Run and verify

Set `ANDROID_HOME` (or add `android/local.properties`) before native work:

```sh
./gradlew test lint assembleDebug
./gradlew connectedDebugAndroidTest
python3 ../../plugins/mobile-native-design-system/shared/scripts/mobile_tokens.py parity \
  ../../plugins/mobile-native-design-system/shared/assets/financial-wellbeing.tokens.json \
  app/src/main/java/mobile/tokens
```

The gallery covers all token scales, interactive controls, sheet/dialog
presentation, loading/empty/error states, font scaling, RTL, reduced motion,
insets, and semantic labels. The production flow adds authentication, list,
detail, form, settings, sheet, and data-write contracts. Instrumentation tests
exercise primary and error-state semantics and capture a native visual
baseline; execute them on phone and tablet API 36 emulators for the intended
matrix.
