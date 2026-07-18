# Flutter Token Gallery

An iOS/Android-only Flutter fixture for the canonical financial-wellbeing token
contract. `lib/generated/` contains mechanically generated token, component,
and motion sources from the canonical plugin assets; do not edit those files
by hand.

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
"$FLUTTER_SDK" build ios --simulator --no-codesign
"$FLUTTER_SDK" test integration_test/product_flow_test.dart -d emulator-5554
```

Regenerate the Flutter artifacts after changing the canonical asset:

```bash
python3 ../../plugins/mobile-native-design-system/shared/scripts/mobile_tokens.py generate \
  ../../plugins/mobile-native-design-system/shared/assets/financial-wellbeing.tokens.json \
  --platform flutter --out lib/generated
```

The gallery exercises semantic scales, controls, feedback, state samples,
navigation, sheet/dialog presentation, phone/tablet layout, RTL, scaled text,
and reduced motion. The production-shaped flow adds authentication, list/home,
detail, form, settings, sheet, async, and data-write behavior. Tests include
deterministic layout, Flutter accessibility guidelines, a compact visual
golden, and Android integration coverage.
