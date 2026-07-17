# Token Contract

## Format

Author tokens in the stable DTCG 2025.10 format:

- `$type` declares the token type and may be inherited by a group.
- `$value` stores a literal, composite value, or `{dot.path.alias}`.
- `$description` explains intent when a semantic name is not sufficient.
- `$extensions.org.mobile-native` holds logical-unit metadata and resolver profiles.

The compiler accepts color strings and structured values, resolves exact aliases recursively, and rejects missing aliases or cycles.

## Logical dimensions

One authored dimension is a logical design unit:

| Target | Mapping |
|---|---|
| SwiftUI | point |
| Jetpack Compose | dp |
| React Native | DIP |
| Flutter | logical pixel |

Typography maps to the target's scalable text system. Do not multiply dimensions by display density during generation.

## Required layers and categories

Use primitive, semantic, component, and state layers. The contract requires:

`color`, `opacity`, `typography`, `spacing`, `sizing`, `iconography`, `touchTarget`, `radius`, `stroke`, `elevation`, `layout`, `zIndex`, `motion`, `haptic`, and `component`.

Composite values may represent typography, shadow, cubic-bezier easing, or spring physics. Generators preserve their canonical structured value for platform adapters to interpret.

## Resolver profiles

The required profiles are:

- `base`: shared defaults;
- `light`, `dark`, `highContrast`: appearance;
- `ios`, `android`: native platform differences;
- `reducedMotion`: accessibility behavior.

Profiles may extend another profile and override only existing token paths. Apply them in order, such as `dark` followed by `ios`. Aliases resolve after overrides so a component alias observes the platform value.

Do not add profiles for targets outside native phone and tablet scope.

## Platform invariants

- Apple `touchTarget.minimum` resolves to at least 44 points.
- Android `touchTarget.minimum` resolves to at least 48 dp.
- `reducedMotion` sets `motion.distance.standard` to zero.
- Semantic paths remain identical across generated targets.
- Platform differences are resolver values, not renamed tokens.

## Starter scale

The fixture asset includes 141 resolved token paths. Its spacing values are:

`0, 2, 4, 8, 12, 16, 20, 24, 32, 40, 48, 64`.

Typography uses semantic system roles. Layout defines compact, medium, and expanded profiles. Motion covers duration, easing, springs, stagger, and distance. Component tokens cover buttons, icon buttons, fields, cards, rows, navigation, modal presentation, and asynchronous states.

## Commands

```bash
python shared/scripts/mobile_tokens.py validate path/to/tokens.json
python shared/scripts/mobile_tokens.py generate path/to/tokens.json --platform all --out path/to/generated
python shared/scripts/mobile_tokens.py parity path/to/tokens.json path/to/generated
```

`validate` checks schema identity, categories, resolver inheritance, aliases, platform floors, and reduced motion.

`generate` writes deterministic source plus `tokens.manifest.json`. The manifest contains the normalized source hash, all semantic paths, resolver names, and artifact hashes.

`parity` fails on source drift, missing semantic paths, missing files, or changed generated artifacts.

## Generated adapters

Swift exposes `MobileTokens` and `MobileTheme`.

Kotlin exposes immutable maps through `MobileTokens`, `MobileTheme`, and a composition local.

React Native exposes `mobileTokens`, `MobileTheme`, and `createMobileTheme`.

Flutter exposes `MobileTokens` and `MobileThemeExtension`.

Generated values are a transport layer. Framework components should convert colors, text roles, shadows, easing, and springs once at the theme boundary rather than parsing them in individual views.

## Migration

1. Inventory existing names and resolved values.
2. Map each token to semantic intent.
3. Mark collisions and genuine platform exceptions.
4. Create aliases so components no longer consume primitives.
5. Add all required resolver profiles.
6. Validate and generate.
7. Compare old and new fixtures at default settings.
8. Test accessibility profiles.
9. Remove old tokens only after all consumers move.
