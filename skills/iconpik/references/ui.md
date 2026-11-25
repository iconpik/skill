# UI icons

Read https://www.iconpik.com/api/ui-icons.json. The equivalent generated manifest
is `/ui/manifest.json`. The document has `kind: "ui"`, `icons`, `looks`, `sets`,
`files`, and `lookFiles`. Each icon includes `slug`, `title`, `category`, `domain`,
`concept`, `modifiers`, `tags`, and `set`.

## Independent dimensions

- Domain is functional taxonomy: arrows, interface, files, security, etc.
  `/ui/categories` indexes used domains; `/ui/category/{domain}` is a category page.
- The display `category` is the domain label. `/ui?cat=Files` filters the browser
  using that label, whereas `domain` uses an ID such as `files`.
- Set identifies a release batch: `/ui?set=wave-4`. It is not a visual style.
- Look identifies a rendering of the same geometry: `/ui?v=duotone`.
- Concept and modifiers express relationships, such as `folder` + `plus`.
- Tags help search; they do not create separate category routes.

Read the current manifest's looks. Current examples are `outline`, `glass`,
`duotone`, `offset`, `fill`, `glass-outline`, and `depth`. For unspecified interface
icons, start with outline and match the surrounding project's existing style.

## Files and delivery

Use the manifest's `files` template, currently `/ui/{slug}/{look}.svg`.
`/ui/{slug}` is an HTML detail page, not the downloadable SVG.
`lookFiles` provides a JSON mapping of slugs to complete SVG markup, one look at a
time. Use it if individual files are unavailable; do not substitute brand assets.

The standard UI components use `currentColor`. Inline SVG or components can inherit
surrounding text color; an external `<img>` cannot. For repeated inline SVG with
gradients/masks, prefer package components, which scope IDs per instance. If raw
SVG is required, ensure IDs and all references are unique per instance.

```sh
python <skill-dir>/scripts/search.py search --kind ui --exact --look outline
python <skill-dir>/scripts/search.py folder --kind ui --look duotone
python <skill-dir>/scripts/search.py --kind ui --domain security --set wave-4
```

UI docs: `/ui/docs`. Release batches: `/ui/changelog`. UI extensions:
`/ui/extensions`. Brand ownership families do not apply to generic UI icons.
Social UI glyphs and brand marks may be related, but their paths/packages remain
distinct; use the requested representation rather than interchanging them.
