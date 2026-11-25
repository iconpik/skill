# Framework integration

Inspect the user's `package.json`, installed package version, exports, and types
before editing code. The live catalog may contain icons not yet published in an
installed release. If the required export is absent, use a verified direct asset,
or propose a suitable package update; never invent the import. Follow the user's
package manager and preserve existing UI/framework conventions.

## Package selection

| Context | Brand assets | UI icons |
| --- | --- | --- |
| React | `@iconpik/react` | `@iconpik/ui-react` |
| Vue | `@iconpik/vue` | `@iconpik/ui-vue` |
| Svelte | `@iconpik/svelte` | `@iconpik/ui-svelte` |
| React Native | `@iconpik/react-native` | `@iconpik/ui-react-native` |
| Plain web/Markdown | Verified SVG URL or fetched SVG | Verified SVG URL or fetched SVG |
| Flags | `@iconpik/flags` (separate exports) | Not a UI package |

These are package families in the source tree, not proof of every version's
published content. Read React Native's props and `react-native-svg` requirements
before generating native code; do not transplant web snippets unchanged.

## React

After confirming these exports in the selected package version:

```tsx
import Github from "@iconpik/react/github";
import { SearchIcon, BellGlassIcon } from "@iconpik/ui-react";

<Github width={24} height={24} aria-label="GitHub" />
<SearchIcon size={20} aria-hidden="true" />
<BellGlassIcon size={24} aria-label="Notifications" />
```

Brand per-icon modules have a default export. UI React/Vue per-icon modules have
named exports such as `SearchIcon` from `@iconpik/ui-react/search`. Brand names
do not have the UI `Icon` suffix. Brand `variant` is a per-icon prop; UI looks
have separate exports, for example `BellIcon`, `BellFillIcon`, and
`BellGlassOutlineIcon`. Do not pass `variant="glass"` to a UI component.

Use `Github variant="mono"` only when that package's types include `mono`.
For UI text color, use the project's text-color class. Components do not need
`"use client"` merely to render an SVG; add client behavior only when required.

## Vue and Svelte

Vue uses the same brand default imports and UI named exports with ordinary Vue
props (`:size="20"` for a numeric UI size).

Svelte supports UI barrel names, but UI per-icon default imports include the look
in the filename: `BellGlass` from `@iconpik/ui-svelte/bell-glass`, versus
`Bell` from `@iconpik/ui-svelte/bell` for outline. Check the package's exports.
Brand per-icon imports use `@iconpik/svelte/{slug}`.

## HTML and Markdown

Once the manifest match and selected SVG URL are verified:

```html
<img src="https://www.iconpik.com/icons/github/default.svg"
     width="24" height="24" alt="GitHub" />
<img src="https://www.iconpik.com/ui/search/outline.svg"
     width="20" height="20" alt="Search" />
```

```markdown
![GitHub](https://www.iconpik.com/icons/github/default.svg)
```

For purely decorative icons next to equivalent text, use an empty HTML `alt` or
hide the inline icon from assistive technology. Label icon-only controls on the
control itself. For color inheritance use inline SVG/components, not `<img>`.

If downloading SVG, preserve its viewBox, gradient definitions, and contrast
details. Check fetched content before inlining it and follow the host project's
SVG sanitization conventions. Do not change a brand's artwork to simulate a
missing official variant.
