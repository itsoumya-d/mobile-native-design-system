# React Native Token Gallery

Native iOS and Android reference fixture for the financial-wellbeing token asset. It uses React Native 0.86, TypeScript, Hermes, the New Architecture, React Native primitives, and `react-native-safe-area-context`.

`src/generated/tokens.ts` and `src/generated/theme.ts` are deterministic compiler output from `skill/mobile-native-design-system/assets/financial-wellbeing.tokens.json`. Regenerate them from the repository root:

```sh
python3 skill/mobile-native-design-system/scripts/mobile_tokens.py generate \
  skill/mobile-native-design-system/assets/financial-wellbeing.tokens.json \
  --platform react-native --out fixtures/react-native/src/generated
```

## Run

```sh
bun install
bun run start
bun run ios
bun run android
```

Before the first iOS build, install CocoaPods dependencies:

```sh
bundle install
bundle exec pod install --project-directory=ios
```

## Verify

```sh
./node_modules/.bin/jest __tests__/App.test.tsx --runInBand
./node_modules/.bin/tsc --noEmit
./node_modules/.bin/eslint App.tsx __tests__/App.test.tsx
python3 ../../skill/mobile-native-design-system/scripts/mobile_tokens.py parity \
  ../../skill/mobile-native-design-system/assets/financial-wellbeing.tokens.json src/generated
```

The gallery covers token scales, controls, cards, rows, asynchronous states, navigation, modal presentation, touch feedback, native motion, RTL logical direction, adaptive phone/tablet layout, and large-text/reduced-motion behavior.
