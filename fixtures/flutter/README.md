# Flutter Token Gallery

An iOS/Android-only Flutter fixture for the canonical financial-wellbeing token
contract. `lib/generated/` is produced mechanically from
`skill/mobile-native-design-system/assets/financial-wellbeing.tokens.json`; do
not edit those files by hand.

The project is pinned to Flutter 3.44.0 through FVM. Install the SDK locally at
`.fvm/flutter_sdk` (or set `FLUTTER_SDK` to its `bin/flutter`) so global Flutter
installations are never changed:

```bash
export FLUTTER_SDK="${FLUTTER_SDK:-$PWD/.fvm/flutter_sdk/bin/flutter}"
"$FLUTTER_SDK" --version
"$FLUTTER_SDK" pub get
"$FLUTTER_SDK" analyze
"$FLUTTER_SDK" test
"$FLUTTER_SDK" build apk --debug
"$FLUTTER_SDK" build ios --no-codesign
```

Regenerate the Flutter artifacts after changing the canonical asset:

```bash
python3 ../../skill/mobile-native-design-system/scripts/mobile_tokens.py generate \
  ../../skill/mobile-native-design-system/assets/financial-wellbeing.tokens.json \
  --platform flutter --out lib/generated
```

The gallery exercises semantic scales, controls, feedback, state samples,
navigation, sheet/dialog presentation, phone/tablet layout, RTL, scaled text,
and reduced motion. Widget tests include deterministic layout and Flutter
accessibility guideline coverage.
