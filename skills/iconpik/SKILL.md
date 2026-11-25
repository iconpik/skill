---
name: iconpik
description: Find and integrate verified iconPik brand logos, cloud architecture icons, flags, and UI icons. Use when a user asks for named brand or service SVGs, interface icons, iconPik assets, or icon code for React, Vue, Svelte, HTML, and Markdown. Does not create original logos or illustrations.
license: MIT
---

# iconPik

Use https://www.iconpik.com as the catalog and asset origin. Resolve the user's
request against its manifests before choosing a slug, variant, look, or import.
Do not substitute the upstream theSVG catalog: iconPik can contain different assets.

## Route the request

- Named companies, products, frameworks, cloud services, auth badges, and flags:
  read [Brand assets](references/brands.md).
- Interface actions, navigation, status, files, and other generic UI concepts:
  read [UI icons](references/ui.md).
- For a mixed request, use both flows. A brand logo and a UI symbol can have the
  same slug; keep their manifests, URL patterns, and packages separate.
- For code integration, also read [Framework integration](references/integration.md).

## Resolve before using

1. Match the exact slug, title, or alias first; use UI tags for conceptual searches.
   Translate a non-English generic concept into likely English search terms when
   necessary, but preserve the brand's identity.
2. Confirm the chosen entry and its actual variant/look. Several matches are
   candidates, not proof that they are interchangeable. Ask only when the remaining
   ambiguity affects the result.
3. Reuse the project's installed iconPik packages when suitable. Check the installed
   package's files/types before claiming a component or export exists: the live
   catalog can be newer than that package version.
4. For a fetched SVG, check the response is an SVG with a viewBox rather than an
   HTML error page. Keep gradients and contrasting details intact. Inspect actual
   paint for light/dark backgrounds; historical variant names are inconsistent.
5. Return or implement the requested asset with its exact slug, selected variant
   or look, and the appropriate snippet. Report whether it was manifest-matched,
   fetched, or actually rendered; do not treat those as equivalent validation.

The optional Python 3 helper needs only the standard library. Resolve its path
relative to this skill folder, not the user's project:

```sh
python <skill-dir>/scripts/search.py github --kind brand --exact
python <skill-dir>/scripts/search.py search --kind ui --exact --look outline
python <skill-dir>/scripts/search.py --kind brand --family google
```

It outputs JSON candidates, manifest sources, verified availability in the
manifest, and SVG URLs. `--check-svg` additionally fetches and parses each selected
SVG; it does not render it. Run `--help` for local manifest and offline SVG options.
The helper neither installs packages nor changes project files. If Python is not
available, use the same manifests with existing HTTP/JSON tools. Cache fetched
manifests for the session; local saved copies can be passed explicitly.

## Missing or unavailable resources

Do not invent a slug, variant, package export, or successful response. If a
manifest or asset cannot be reached, say what could be verified and use an explicit
local snapshot or existing package if available. Do not silently switch to upstream.
If no entry matches, offer relevant candidates or https://www.iconpik.com/submit.

Use the entry's license and brand guidelines for the requested use. The Skill's
MIT license does not override individual asset licenses or trademark ownership.
