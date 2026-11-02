"""Fetch named streets (geometry) from OpenStreetMap via Overpass and reduce them to one
label per street: longest segment midpoint + angle. Writes data/street_labels.json."""
import json, math, sys
from collections import defaultdict
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from fetch_osm import overpass, OUT
from district import D

BBOX = D["bbox"]
Q = f"""[out:json][timeout:120];
way[highway~"^(primary|secondary|tertiary|unclassified|residential|living_street|pedestrian)$"][name]({BBOX});
out tags geom;
"""
RANK = {"primary": 0, "secondary": 1, "tertiary": 2, "unclassified": 3, "residential": 3, "living_street": 4, "pedestrian": 4}
LAT0 = D["lat0"]
KX, KY = 111320 * math.cos(math.radians(LAT0)), 110574


def main():
    d = overpass(Q)
    by = defaultdict(list)
    for e in d["elements"]:
        g = [(p["lon"], p["lat"]) for p in e.get("geometry", [])]
        if len(g) > 1:
            by[e["tags"]["name"]].append((e["tags"]["highway"], g))
    out = []
    for name, ways in by.items():
        best = None
        for hw, g in ways:
            for a, b in zip(g, g[1:]):
                L = math.hypot((b[0] - a[0]) * KX, (b[1] - a[1]) * KY)
                if best is None or L > best[0]:
                    best = (L, a, b, hw)
        L, a, b, hw = best
        ang = math.degrees(math.atan2((b[1] - a[1]) * KY, (b[0] - a[0]) * KX))
        if ang > 90: ang -= 180
        if ang < -90: ang += 180
        total = sum(math.hypot((q[0] - p[0]) * KX, (q[1] - p[1]) * KY) for _, g in ways for p, q in zip(g, g[1:]))
        out.append([name, round((a[1] + b[1]) / 2, 5), round((a[0] + b[0]) / 2, 5), round(-ang), min(RANK[h] for h, _ in ways), round(total)])
    (OUT / "street_labels.json").write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")))
    print(len(out), "streets")


if __name__ == "__main__":
    main()
