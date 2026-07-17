# Routing and Provenance

This skill is an independently written mobile synthesis. The audit locks exact upstream lines and records whether each line is adopted as a general principle, adapted, routed to another concern, or rejected.

| Source | Trigger | Mobile treatment |
|---|---|---|
| `frontend-design` | New UI, redesign, art direction | Keep subject grounding, intentional typography, signature element, and critique. Translate page/hero/hover language into screens, flows, touch, gestures, and system navigation. |
| `ui-ux-pro-max` | Design-system generation, token selection, audit | Use searchable design intelligence and mobile rows as research input. Revalidate every rule against current official platform guidance. |
| `design-taste-frontend` | Ambiguous brief, anti-generic review, design dials | Translate density, variance, and motion dials into mobile screens and states. Reject CSS, DOM, web-vitals, and landing-page instructions. |
| `shadcn-ui-mcp-server` | React Native component discovery | Use only its React Native registry model when compatible. Other frameworks use native primitives. |
| `21st.dev Magic MCP` | Component ideation and refinement | Recreate the brief/refine workflow locally. Do not depend on its API or component output. |
| `vercel-react-best-practices` | React Native code with platform-neutral React concerns | Keep compatible render, state, and JavaScript guidance. Reject SSR, Next.js, DOM, browser caching, and web bundle rules. |
| GSAP skills | Timeline, easing, sequencing, performance, reduced motion | Translate concepts into native animation APIs. Never install or import GSAP. |
| Motion/Framer | Variants, presence, gestures, springs, shared transitions | Translate declarative state and spring concepts into native APIs. Never install Framer Motion. |
| `convex-create-component` | Existing Convex app or requested data-backed component | Preserve UI/backend isolation and small app-facing boundaries. Do not make the design system backend-dependent. |
| `vercel-react-native-skills` | React Native or Expo implementation/performance | Use as the primary React Native source after current-version validation. Apply Expo-only rules only when Expo is detected. |

## Conflict order

1. Current official framework and accessibility guidance.
2. The target application's established native architecture.
3. The versioned registry in `shared/assets/capability-registry.json`.
4. Platform-neutral design and React principles.
5. Translated animation or component-workflow concepts.

Reject any upstream instruction that requires a web runtime, conflicts with native assistive behavior, freezes scalable text, weakens touch targets, or introduces an unrelated backend or dependency.

## Registry discovery

For React Native, component discovery may use a React Native-compatible registry path. Confirm:

- the returned implementation is actually native;
- its dependencies match project policy;
- it exposes native accessibility semantics;
- it supports the active React Native architecture;
- it can consume local semantic tokens;
- it has tests for all required states.

Registry blocks that are unavailable for React Native are not substitutes for native screen composition.

## Data-backed components

Only route to Convex guidance when the repository already uses Convex or the user requests it. Keep authentication, environment access, and app-owned identifiers at the application boundary. The UI receives typed loading, empty, error, and populated state plus callbacks.

Convex and Magic sources at the pinned revisions do not provide a complete repository license suitable for copying. This skill uses independently authored concepts only.

## Audit artifacts

The project repository contains:

- `audit/sources.lock.json`: URL, revision, branch, paths, and license status;
- `audit/scope.json`: exact deep-review scope;
- `audit/line-audit.jsonl`: one deterministic record per scoped source line;
- `audit/line-audit.jsonl`: recorded classified source-line evidence. The
  upstream source trees are intentionally not distributed in the public plugin.
