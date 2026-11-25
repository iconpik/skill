# Brand assets

## Catalogs

| URL at https://www.iconpik.com | Shape and purpose |
| --- | --- |
| `/api/registry.json` | `{total, icons}`; lightweight entries; `variants` is an array of available keys |
| `/api/icons-full.json` | Array; includes `collection`, `family` when present, and `variants` as a key-to-path object |
| `/api/categories.json` | `{categories: [{name, count}]}`; classification labels |
| `/api/families.json` | `{total, families}`; each family's current child slugs in `members`, plus its parent `slug` |

Use `icons-full.json` for resource-library filters. Do not infer ownership or
collection from a slug prefix. In a local iconPik checkout, `src/data/icons.json`
is the source registry; do not require that private checkout from other users.

Collections currently include `brands`, `aws`, `azure`, `gcp`, `k8s`, `community`,
`auth-badges`, and `flags`. Read the fetched data rather than freezing their counts.

## Organization

- Collection identifies the resource library: `/collection/gcp`.
- Category is a multi-valued classification label: `/?category=Google` is a home
  filter, while `/category/google` is its standalone category page.
- `/category/google-2026` is a custom refresh landing for the `Google 2026` label.
- Family identifies brand ownership: `/family/google`. The families manifest
  lists current children, suppressing superseded siblings; include the parent
  `slug` as well. Ordinary search does not automatically hide older marks.
- `/icon/{slug}` is an individual detail page.

These dimensions overlap. For "Google's current logos", use the family manifest;
for the 2026 refresh, filter the `Google 2026` category; for cloud diagram symbols,
use the `gcp` collection. Preserve an explicitly requested historical version.
For an unversioned product request, check whether its family lists a newer mark
before settling on an older exact unversioned slug. Use actual registry/family
entries as evidence; do not manufacture a year suffix to find a refresh.

## Assets and color

Brand files live under `/icons/{slug}/`. Prefer the exact path stored in the
`icons-full.json` entry's `variants` object. Variant keys are not always filenames:
`wordmarkLight` may map to `wordmark-light.svg`. The lightweight registry has no
paths; use it only for the conventional default/mono/light/dark/color filenames,
or retrieve the full index before selecting other variants. Read available keys;
only `default` is universally expected. `color`, `mono`, `light`, `dark`, wordmarks,
lockups, and other keys vary per entry. Do not manufacture a `mono` URL.

The registry documents available files, not their contrast against a background.
Some historic `light`/`dark` filenames describe the background, others the ink.
Inspect the actual fill/stroke/gradient or preview the SVG before choosing.
For example, GitHub's `light.svg` has dark paths in this checkout; do not apply a
global filename-to-color rule. An SVG loaded through `<img>` does not inherit the
host page's `currentColor`; use an inline/component mono variant for text theming.

Brand color is the entry's `hex`; avoid overwriting multi-color marks or turning
contrast details into the same fill as their body. Prefer an existing variant.

Flags belong to the brand-side catalog but are not company logos. Their variants
are `default` (4:3), `square`, and `circle`, subject to the entry's actual keys.
Their specialized package is `@iconpik/flags`; do not assume flag exports exist
in the ordinary brand framework packages.

Example lookups (a saved local manifest avoids repeat downloads):

```sh
python <skill-dir>/scripts/search.py github --kind brand --exact --variant mono
python <skill-dir>/scripts/search.py --kind brand --category "Google 2026" --limit 30
python <skill-dir>/scripts/search.py --kind brand --family google --limit 150
python <skill-dir>/scripts/search.py --kind brand --collection gcp --limit 8
python <skill-dir>/scripts/search.py flag-us --kind brand --exact --variant circle
```

The helper's `--family` reads the families manifest, so it follows current-family
membership rather than guessing from category names. Family results are paged by
`--limit` only; use a larger limit if every member is needed and check `total`.
