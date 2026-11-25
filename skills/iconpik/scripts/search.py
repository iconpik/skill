#!/usr/bin/env python3
"""Read-only iconPik catalog lookup; Python 3 standard library only."""
import argparse
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlparse
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

BASE = "https://www.iconpik.com"


def read_source(source):
    if urlparse(str(source)).scheme in ("https", "http"):
        request = Request(str(source), headers={"User-Agent": "iconpik-skill/1"})
        with urlopen(request, timeout=20) as response:
            return response.read()
    return Path(source).read_bytes()


def load_manifest(source):
    document = json.loads(read_source(source).decode("utf-8-sig"))
    entries = document if isinstance(document, list) else document.get("icons")
    if not isinstance(entries, list) or not all(
        isinstance(i, dict) and isinstance(i.get("slug"), str) for i in entries
    ):
        raise ValueError("Expected an icon array or an object with an icons array")
    return document, entries


def rank(entry, query, exact=False):
    if not query:
        return 1
    fields = [entry["slug"], entry.get("title", ""), *entry.get("aliases", [])]
    fields = [value.casefold() for value in fields]
    q = query.casefold().strip()
    if q == fields[0]:
        return 100
    if q in fields:
        return 90
    if exact:
        return 0
    tags = [tag.casefold() for tag in entry.get("tags", [])]
    if q in tags:
        return 80
    if any(q in value for value in fields):
        return 60
    if any(q in value for value in tags):
        return 40
    return 0


def filter_entries(entries, args, kind, family_slugs=None):
    if args.exact and args.query:
        exact_slugs = [e for e in entries if e["slug"].casefold() == args.query.strip().casefold()]
        if exact_slugs:
            entries = exact_slugs
    matched = []
    for entry in entries:
        if family_slugs is not None and entry["slug"] not in family_slugs:
            continue
        if args.collection and entry.get("collection") != args.collection:
            continue
        categories = entry.get("categories", [entry.get("category", "")])
        if args.category and args.category.casefold() not in [c.casefold() for c in categories]:
            continue
        if args.domain and entry.get("domain") != args.domain:
            continue
        if args.set and entry.get("set") != args.set:
            continue
        score = rank(entry, args.query, args.exact)
        if score:
            matched.append((score, entry))
    return sorted(matched, key=lambda pair: (-pair[0], pair[1]["slug"]))


def asset_path(entry, kind, manifest, selected):
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", entry["slug"]):
        raise ValueError("Invalid catalog slug: " + entry["slug"])
    if kind == "brand":
        variants = entry.get("variants", {})
        available = [k for k, v in variants.items() if v] if isinstance(variants, dict) else variants
        template = "/icons/{slug}/{variant}.svg"
    else:
        available = manifest.get("looks", [])
        template = manifest.get("files", "/ui/{slug}/{look}.svg")
    if selected not in available:
        return None, available
    path = template.format(slug=entry["slug"], variant=selected, look=selected)
    if kind == "brand" and isinstance(variants, dict):
        path = variants[selected]
    elif kind == "brand" and selected not in ("default", "mono", "light", "dark", "color"):
        # The lightweight registry has keys, not filenames. Camel-case keys can
        # map to dashed filenames. Require the full index instead of guessing.
        raise ValueError("This brand variant needs icons-full.json with actual file paths")
    # Files stay on the configured origin, even when a remote manifest is malformed.
    if not path.startswith("/") or path.startswith("//") or ".." in path.split("/"):
        raise ValueError("Expected an absolute same-origin SVG path")
    return path, available


def inspect_svg(content):
    root = ET.fromstring(content)
    if root.tag.split("}")[-1] != "svg" or not root.get("viewBox"):
        raise ValueError("Response is not an SVG with a viewBox")
    return {
        "viewBox": root.get("viewBox"),
        "fills": sorted({e.get("fill") for e in root.iter() if e.get("fill")}),
        "strokes": sorted({e.get("stroke") for e in root.iter() if e.get("stroke")}),
        "validation": "parsed-svg-not-rendered",
    }


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("query", nargs="?", default="", help="One search term; repeat calls for multiple brands")
    p.add_argument("--kind", choices=["brand", "ui", "both"], default="both")
    p.add_argument("--exact", action="store_true", help="Exact slug, title, or alias only")
    p.add_argument("--limit", type=int, default=8)
    p.add_argument("--category", help="Brand category or UI display category label")
    p.add_argument("--collection", help="Brand collection ID; requires --kind brand")
    p.add_argument("--family", help="Current family members including parent; requires --kind brand")
    p.add_argument("--domain", help="UI domain ID; requires --kind ui")
    p.add_argument("--set", help="UI release set ID; requires --kind ui")
    p.add_argument("--variant", default="default", help="Brand variant key")
    p.add_argument("--look", default="outline", help="UI look key")
    p.add_argument("--base-url", default=BASE, help="Explicit alternate iconPik deployment origin")
    p.add_argument("--brand-manifest", help="Saved JSON path or explicit manifest URL")
    p.add_argument("--ui-manifest", help="Saved JSON path or explicit manifest URL")
    p.add_argument("--families-manifest", help="Saved families JSON path or URL")
    p.add_argument("--check-svg", action="store_true", help="Fetch/parse selected SVGs, no rendering")
    p.add_argument("--svg-root", help="Use a local public/ directory for --check-svg, without network")
    return p


def run(args):
    if args.limit < 1:
        raise ValueError("--limit must be positive")
    if (args.family or args.collection) and args.kind != "brand":
        raise ValueError("--family and --collection require --kind brand")
    if (args.domain or args.set) and args.kind != "ui":
        raise ValueError("--domain and --set require --kind ui")
    origin = urlparse(args.base_url)
    if origin.scheme not in ("https", "http") or not origin.netloc or origin.path not in ("", "/") or origin.query or origin.fragment:
        raise ValueError("--base-url must be an HTTP(S) origin without a path or query")
    base = args.base_url.rstrip("/")
    output = {"sources": {}, "results": [], "total": 0, "errors": []}
    kinds = ["brand", "ui"] if args.kind == "both" else [args.kind]
    for kind in kinds:
        source = (args.brand_manifest or base + "/api/icons-full.json") if kind == "brand" else (args.ui_manifest or base + "/api/ui-icons.json")
        output["sources"][kind] = source
        manifest, entries = load_manifest(source)
        if kind == "ui" and (not isinstance(manifest, dict) or manifest.get("kind") != "ui"):
            raise ValueError("Expected a UI manifest with kind=ui")
        if kind == "brand" and isinstance(manifest, dict) and manifest.get("kind") == "ui":
            raise ValueError("UI manifest supplied as brand manifest")
        if args.collection and entries and not any("collection" in e for e in entries):
            raise ValueError("Collection filtering needs icons-full.json or src/data/icons.json, not registry.json")
        family_slugs = None
        if args.family:
            family_source = args.families_manifest or base + "/api/families.json"
            output["sources"]["families"] = family_source
            families = json.loads(read_source(family_source).decode("utf-8-sig"))["families"]
            family = next((f for f in families if f["slug"] == args.family), None)
            if family is None:
                raise ValueError("Unknown family: " + args.family)
            family_slugs = {family["slug"], *family["members"]}
        matches = filter_entries(entries, args, kind, family_slugs)
        output["total"] += len(matches)
        for _, entry in matches[:args.limit]:
            selected = args.variant if kind == "brand" else args.look
            path, available = asset_path(entry, kind, manifest, selected)
            result = {"kind": kind, "slug": entry["slug"], "title": entry.get("title"),
                      "selected": selected, "available": available,
                      "detail_url": base + ("/icon/" if kind == "brand" else "/ui/") + entry["slug"],
                      "svg_url": base + path if path else None,
                      "validation": "manifest-only"}
            for key in ("license", "guidelines", "family", "collection", "categories", "domain", "category", "set", "tags"):
                if key in entry:
                    result[key] = entry[key]
            if path is None:
                output["errors"].append(f"{kind}/{entry['slug']}: {selected} is unavailable")
            elif args.check_svg:
                try:
                    svg_source = Path(args.svg_root) / path.lstrip("/") if args.svg_root else base + path
                    result["svg_check"] = inspect_svg(read_source(svg_source))
                    result["validation"] = "parsed-svg-not-rendered"
                except (OSError, ValueError, ET.ParseError) as error:
                    output["errors"].append(f"{kind}/{entry['slug']}: SVG check failed: {error}")
            output["results"].append(result)
    output["returned"] = len(output["results"])
    output["limit_per_kind"] = args.limit
    return output


def main():
    args = parser().parse_args()
    try:
        output = run(args)
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return 1 if output["errors"] or not output["total"] else 0
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(json.dumps({"error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
