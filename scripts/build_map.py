"""Combine fetched data with the template into one self-contained index.html.
Entwickelt von MB Saryazdi für den Präventionsrat Buchholz-Kleefeld."""
import json, os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
SRC = ROOT / "src"


def in_ring(x, y, ring):
    inside = False
    j = len(ring) - 1
    for i in range(len(ring)):
        xi, yi = ring[i]
        xj, yj = ring[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            inside = not inside
        j = i
    return inside


def in_feature(x, y, f):
    return any(in_ring(x, y, poly[0]) for poly in f["geometry"]["coordinates"])


def pack_basemap(base):
    """Shrink basemap: integer coords (1e-5 deg) delta-encoded per shape, short keys."""
    out = {}
    for layer, fc in base.items():
        kinds, shapes = [], []
        for f in fc["features"]:
            g = f["geometry"]
            ring = g["coordinates"][0] if g["type"] == "Polygon" else g["coordinates"]
            k = f["properties"].get("k") or ""
            if k not in kinds:
                kinds.append(k)
            flat, px, py = [], 0, 0
            for x, y in ring:
                ix, iy = round(x * 1e5), round(y * 1e5)
                flat += [ix - px, iy - py]
                px, py = ix, iy
            shapes.append([kinds.index(k), 1 if g["type"] == "Polygon" else 0, flat])
        out[layer] = {"kinds": kinds, "shapes": shapes}
    return out


def build(slug, cfg, all_cfg):
    d = ROOT / cfg["data_dir"]
    load = lambda n: json.loads((d / n).read_text())
    boundaries = load("boundaries.geojson")
    pois = load("pois.geojson")
    stadtteile = [f for f in boundaries["features"] if f["properties"]["level"] == "stadtteil"]

    for f in pois["features"]:
        x, y = f["geometry"]["coordinates"]
        f["geometry"]["coordinates"] = [round(x, 6), round(y, 6)]
        f["properties"]["stadtteil"] = next(
            (s["properties"]["name"] for s in stadtteile if in_feature(x, y, s)), None)

    here = (ROOT / cfg["out"]).parent
    district = {k: cfg[k] for k in ("name", "nr", "home_view", "praeventionsrat", "polizeistation", "has_proposal", "has_kennzahlen")}
    district["report_api"] = cfg.get("report_api", "")
    district["report_mode"] = cfg.get("report_mode", "")
    district["slug"] = slug
    district["districts"] = [{"slug": k, "name": v["name"], "href": os.path.relpath(ROOT / v["out"], here).replace(os.sep, "/")}
                             for k, v in all_cfg.items()]
    data = {
        "district": district,
        "meta": load("meta.json"),
        "boundaries": boundaries,
        "pois": pois,
        "unlit": load("unlit_paths.geojson"),
        "issues": load("issues.json"),
        "schulwege": load("schulwege.json"),
        "streets": load("street_labels.json"),
        "kennzahlen": load("kennzahlen.json"),
        "basemap": pack_basemap(load("basemap.json")),
    }
    html = (SRC / "map.template.html").read_text()
    root = os.path.relpath(ROOT, (ROOT / cfg["out"]).parent).replace(os.sep, "/")
    root = "" if root == "." else root + "/"
    html = html.replace("/*__LEAFLET_CSS__*/", (SRC / "leaflet-1.9.4.css").read_text())
    html = html.replace("/*__FONTS_CSS__*/", (SRC / "fonts.css").read_text().replace("__ROOT__", root))
    html = html.replace("/*__LEAFLET_JS__*/", (SRC / "leaflet-1.9.4.min.js").read_text())
    html = html.replace("__ROOT__", root)
    html = html.replace("/*__DATA__*/null", json.dumps(data, separators=(",", ":"), ensure_ascii=False).replace("</", "<\\/"))
    if slug == "buchholz-kleefeld":
        # Fragment for claude.ai Artifacts (they add the document skeleton themselves)
        (ROOT / "build").mkdir(exist_ok=True)
        (ROOT / "build" / "artifact.html").write_text(html)
    # Full document for GitHub Pages / any static host
    page = ('<!doctype html>\n<html lang="de">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            '<style>body{margin:0}</style>\n</head>\n<body>\n' + html + '\n</body>\n</html>\n')
    out = ROOT / cfg["out"]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page)
    print(f"{cfg['out']} {len(page) / 1e6:.1f} MB, {len(pois['features'])} places")


def main():
    cfg = json.loads((ROOT / "config" / "districts.json").read_text())
    cfg = {k: v for k, v in cfg.items() if not k.startswith("_")}
    only = os.environ.get("DISTRICT")
    # "enabled": false in config/districts.json hides a district from the public build;
    # name it explicitly (DISTRICT=<slug>) to build it for local work.
    cfg = {k: v for k, v in cfg.items() if v.get("enabled", True) or k == only}
    for slug, c in cfg.items():
        if only and slug != only:
            continue
        if not (ROOT / c["data_dir"] / "street_labels.json").exists() or not (ROOT / c["data_dir"] / "schulwege.json").exists():
            print(f"skip {slug}: data incomplete")
            continue
        build(slug, c, cfg)
    if not only:
        import build_legal
        build_legal.build()


if __name__ == "__main__":
    main()
