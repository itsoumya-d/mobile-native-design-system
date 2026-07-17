# Core Mobile Design System

## Start with the product subject

Before choosing components, write five one-line decisions:

1. the user's primary job;
2. the product's subject and vocabulary;
3. the emotional register;
4. the hierarchy of information and actions;
5. one signature visual or interaction that belongs to this product.

Avoid a generic card stack by making domain information shape the composition. A financial-wellbeing screen, for example, should connect score, trend, explanation, and next action; status must not depend on color alone.

## Set the design dials

Choose deliberate values for:

- density: calm, balanced, or compact;
- contrast: soft, clear, or emphatic;
- shape: restrained, rounded, or expressive;
- type: neutral, editorial, or technical;
- motion: minimal, responsive, or expressive.

Record the choices. A component may vary within the selected range but should not drift into another visual system.

## Build screen hierarchy

Compose screens in this order:

1. system navigation and safe areas;
2. primary screen title and current context;
3. the dominant user decision or insight;
4. supporting groups and status;
5. persistent or contextual actions;
6. loading, empty, error, offline, and success feedback.

Use spacing, type, surface contrast, and grouping before decoration. One signature element is stronger than many unrelated effects.

## Token layers

- Primitive tokens store raw choices.
- Semantic tokens name intent such as `color.content.primary`.
- Component tokens bind intent to a reusable control.
- State tokens describe interaction and asynchronous states.

Components consume semantic or component tokens, never primitives directly. Platform overrides change values without changing semantic names.

## Scale inventory

Every system must decide and test:

- color and opacity;
- semantic typography and text scaling;
- spacing and sizing;
- icons and touch geometry;
- radii and strokes;
- shadow, material, and elevation intent;
- compact, medium, and expanded margins and gutters;
- safe areas and system insets;
- z-order and presentation layers;
- duration, easing, springs, stagger, and distance;
- haptic intent;
- component and asynchronous states.

The starter spacing scale is `0, 2, 4, 8, 12, 16, 20, 24, 32, 40, 48, 64` logical units. Add values only for a demonstrated semantic need.

## Native interaction

Use controls that provide role, focus, activation, disabled behavior, and assistive semantics. A visual container with a tap callback is not automatically a button.

For every action define:

- default, pressed, focused, selected, and disabled appearance;
- label, role, value, hint when needed, and focus order;
- minimum target size and spacing from adjacent actions;
- response to loading and repeated activation;
- optional haptic intent;
- reduced-motion behavior.

Treat gesture-only actions as enhancements. Provide a discoverable control or accessibility action for the same outcome.

## Adaptive layout

Respond to available width, height, orientation, text scale, and insets. Compact layouts usually stack; medium layouts may introduce side-by-side groups; expanded layouts may add a supporting pane. Do not infer capability solely from a device model.

Use logical leading and trailing alignment. Check mixed-direction numbers, percentages, currency, and icons under Arabic directionality.

## Typography

Prefer semantic system roles. Custom faces require a clear subject-specific reason and complete fallback/scaling validation. Never fix a control's height around one text size. Allow multiline labels where the action remains understandable.

Test the largest supported text scale. Reflow before truncating important content. Keep touch geometry independent of glyph bounds.

## Color and contrast

Build light, dark, and high-contrast resolvers. Check contrast on resolved pairs, including disabled and overlay states. Pair status color with a label, icon, sign, or pattern. Respect system settings that request differentiation without color.

## Motion and haptics

Motion communicates continuity, hierarchy, causality, or direct manipulation. Define named states first, then select native transitions. Keep entrance motion short and interruptible. Never make information available only while moving.

Reduced-motion profiles:

- remove decorative translation, parallax, and stagger;
- replace necessary spatial continuity with opacity or an immediate state change;
- keep progress and state changes understandable;
- preserve all actions;
- avoid unnecessary haptics and allow system policy to govern delivery.

## Critique pass

Ask:

- Does the composition communicate the product subject?
- Is the primary action unmistakable?
- Does every control behave natively?
- Are any visual choices present only because they are fashionable?
- Do phone, tablet, large-text, dark, high-contrast, Arabic, and reduced-motion states remain coherent?
- Can every status be understood without color or animation?
