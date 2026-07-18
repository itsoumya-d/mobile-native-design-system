# React Native Token Gallery

Native iOS and Android reference fixture for the financial-wellbeing token asset. It uses React Native 0.86, TypeScript, Hermes, the New Architecture, React Native primitives, and `react-native-safe-area-context`.

`src/generated/` contains deterministic token, component, and motion output
from the canonical plugin assets. Regenerate token adapters from the repository
root:

```sh
python3 plugins/mobile-native-design-system/shared/scripts/mobile_tokens.py generate \
  plugins/mobile-native-design-system/shared/assets/financial-wellbeing.tokens.json \
  --platform react-native --out fixtures/react-native/src/generated
```

## Run

```sh
npm install
npm run start
npm run ios
npm run android
```

Before the first iOS build, install CocoaPods dependencies:

```sh
bundle install
bundle exec pod install --project-directory=ios
```

## Verify

```sh
./node_modules/.bin/jest --runInBand
./node_modules/.bin/tsc --noEmit
./node_modules/.bin/eslint . --max-warnings=0
python3 ../../plugins/mobile-native-design-system/shared/scripts/mobile_tokens.py parity \
  ../../plugins/mobile-native-design-system/shared/assets/financial-wellbeing.tokens.json src/generated
```

The gallery and production flow cover token scales, authentication-shaped
state, lists, detail, forms, settings, sheets, asynchronous states, native
navigation, touch feedback, RTL logical direction, adaptive phone/tablet
layout, large text, reduced motion, and a semantic rendering snapshot.
