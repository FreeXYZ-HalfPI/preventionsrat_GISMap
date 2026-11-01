"""Fetch a light basemap (streets, rail, water, green, buildings) around
Buchholz-Kleefeld so the map renders without an external tile server."""
import json
from fetch_osm import overpass, OUT, BEZIRK

# Bezirk bbox plus a small margin (south, west, north, east)
BBOX = "52.355,9.765,52.420,9.850"

LAYERS = {
    "roads": f'way["highway"~"^(motorway|trunk|primary|secondary|tertiary|unclassified|residential|living_street|pedestrian|service|footway|path|cycleway|track|steps)$"]({BBOX});',
    "rail": f'way["railway"~"^(rail|tram|light_rail|subway)$"]({BBOX});',
    "water": f'(way["natural"="water"]({BBOX});way["waterway"~"^(river|canal|stream)$"]({BBOX}););',
    "green": f'way["landuse"~"^(forest|grass|meadow|allotments|cemetery|recreation_ground|village_green)$"]({BBOX});way["leisure"~"^(park|garden|playground|pitch)$"]({BBOX});way["natural"="wood"]({BBOX});',
    "buildings": f'way["building"]({BBOX});',
}


def r5(c):
    return [round(c["lon"], 5), round(c["lat"], 5)]


def fetch(name, q):
    d = overpass(f"[out:json][timeout:180];({q});out geom tags;")
    feats = []
    for w in d["elements"]:
        if "geometry" not in w:
            continue
        coords = [r5(p) for p in w["geometry"]]
        t = w.get("tags", {})
        closed = coords[0] == coords[-1] and len(coords) > 3
        area = name in ("buildings", "green") or (name == "water" and "natural" in t)
        geom = {"type": "Polygon", "coordinates": [coords]} if area and closed else {"type": "LineString", "coordinates": coords}
        p = {}
        if name == "roads":
            p = {"k": t["highway"], "n": t.get("name")}
        elif name == "green":
            p = {"k": t.get("landuse") or t.get("leisure") or t.get("natural")}
        elif name == "rail":
            p = {"k": t["railway"]}
        feats.append({"type": "Feature", "properties": p, "geometry": geom})
    print(f"{name:10s} {len(feats)}")
    return {"type": "FeatureCollection", "features": feats}


if __name__ == "__main__":
    cache = OUT / "basemap_parts"
    cache.mkdir(exist_ok=True)
    base = {}
    for n, q in LAYERS.items():
        f = cache / f"{n}.json"
        if not f.exists():
            f.write_text(json.dumps(fetch(n, q), separators=(",", ":"), ensure_ascii=False))
        base[n] = json.loads(f.read_text())
    (OUT / "basemap.json").write_text(json.dumps(base, separators=(",", ":"), ensure_ascii=False))
