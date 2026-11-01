"""Fetch boundaries and prevention-relevant public places for Stadtbezirk
Buchholz-Kleefeld (Hannover) from OpenStreetMap via Overpass, write GeoJSON."""
import json, sys, time, urllib.parse, urllib.request
from pathlib import Path

ENDPOINTS = [
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
    "https://overpass-api.de/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
]
UA = "PraeventionsratBuchholzKleefeld/1.0 (community map)"
OUT = Path(__file__).resolve().parent.parent / "data"
BEZIRK = 1862974
STADTTEILE = [3360790, 3360791, 3360792]


def overpass(q):
    body = urllib.parse.urlencode({"data": q}).encode()
    for attempt in range(4):
        for ep in ENDPOINTS:
            try:
                req = urllib.request.Request(ep, body, {"User-Agent": UA})
                with urllib.request.urlopen(req, timeout=180) as r:
                    return json.load(r)
            except Exception as e:
                print(f"  {ep}: {e}", file=sys.stderr, flush=True)
        time.sleep(10 * (attempt + 1))
    sys.exit("Overpass unreachable")


def ring_join(ways):
    """Join outer way segments of a relation into closed rings."""
    segs = [[(p["lon"], p["lat"]) for p in w] for w in ways]
    rings = []
    while segs:
        ring = segs.pop(0)
        while ring[0] != ring[-1]:
            for i, s in enumerate(segs):
                if s[0] == ring[-1]:
                    ring += s[1:]
                elif s[-1] == ring[-1]:
                    ring += s[::-1][1:]
                else:
                    continue
                segs.pop(i)
                break
            else:
                break
        rings.append([list(c) for c in ring])
    return rings


def boundaries():
    ids = ",".join(map(str, [BEZIRK, *STADTTEILE]))
    d = overpass(f"[out:json][timeout:120];rel(id:{ids});out geom;")
    feats = []
    for rel in d["elements"]:
        outer = [m["geometry"] for m in rel["members"] if m["type"] == "way" and m.get("role") == "outer"]
        feats.append({
            "type": "Feature",
            "properties": {
                "name": rel["tags"]["name"],
                "level": "bezirk" if rel["id"] == BEZIRK else "stadtteil",
                "population": rel["tags"].get("population"),
                "wikidata": rel["tags"].get("wikidata"),
                "osm": f"relation/{rel['id']}",
            },
            "geometry": {"type": "MultiPolygon", "coordinates": [[r] for r in ring_join(outer)]},
        })
    return {"type": "FeatureCollection", "features": feats}


# (category, Overpass filter). Order matters: first match wins.
POI_QUERIES = [
    ("jugend", 'nwr["amenity"="community_centre"]["community_centre"~"youth"](area.a);'),
    ("jugend", 'nwr["leisure"="youth_centre"](area.a);'),
    ("jugend", 'nwr["amenity"="social_facility"]["social_facility:for"~"juvenile|child"](area.a);'),
    ("sicherheit", 'nwr["amenity"~"^(police|fire_station)$"](area.a);'),
    ("sicherheit", 'node["emergency"="defibrillator"](area.a);'),
    ("bildung", 'nwr["amenity"~"^(school|kindergarten|childcare|library|college|university|music_school|language_school)$"](area.a);'),
    ("soziales", 'nwr["amenity"~"^(social_facility|social_centre|community_centre)$"](area.a);'),
    ("soziales", 'nwr["healthcare"="counselling"](area.a);'),
    ("soziales", 'nwr["office"~"^(ngo|association|charity)$"](area.a);'),
    ("soziales", 'nwr["social_facility"](area.a);'),
    ("gesundheit", 'nwr["amenity"~"^(hospital|clinic|doctors|pharmacy|dentist)$"](area.a);'),
    ("spielplatz", 'nwr["leisure"="playground"](area.a);'),
    ("sport", 'nwr["leisure"~"^(sports_centre|stadium|swimming_pool|fitness_station|sports_hall)$"](area.a);'),
    ("sport", 'nwr["leisure"="pitch"]["access"!~"private"](area.a);'),
    ("gruen", 'nwr["leisure"~"^(park|garden)$"]["name"](area.a);'),
    ("religion", 'nwr["amenity"="place_of_worship"](area.a);'),
    ("oepnv", 'nwr["railway"~"^(tram_stop|station|halt)$"](area.a);'),
    ("oepnv", 'node["highway"="bus_stop"](area.a);'),
    ("nachtleben", 'nwr["amenity"~"^(bar|pub|nightclub|biergarten|casino|gambling)$"](area.a);'),
    ("nachtleben", 'nwr["shop"~"^(kiosk|alcohol)$"](area.a);'),
    ("infra", 'nwr["amenity"~"^(toilets|townhall|post_office|recycling)$"]["access"!~"private"](area.a);'),
]

KEEP_TAGS = ["name", "operator", "addr:street", "addr:housenumber", "addr:postcode",
             "website", "contact:website", "phone", "contact:phone", "email", "opening_hours",
             "amenity", "leisure", "healthcare", "social_facility", "social_facility:for",
             "community_centre", "school", "isced:level", "religion", "denomination",
             "wheelchair", "railway", "highway", "shop", "office", "emergency", "sport", "lit"]


def pois():
    # One request for all categories; a derived "sep" element marks where each category starts.
    parts = [f'make sep cat="{c}"; out; ({f}); out center;' for c, f in POI_QUERIES]
    d = overpass(f"[out:json][timeout:180];rel({BEZIRK});map_to_area->.a;" + "".join(
        p.replace("(area.a)", "(area.a)") for p in parts))
    seen, feats, cat, counts = set(), [], None, {}
    for e in d["elements"]:
        if e["type"] == "sep":
            cat = e["tags"]["cat"]
            continue
        key = f"{e['type']}/{e['id']}"
        if key in seen:
            continue
        seen.add(key)
        lat = e.get("lat") or e.get("center", {}).get("lat")
        lon = e.get("lon") or e.get("center", {}).get("lon")
        if lat is None:
            continue
        props = {k: v for k, v in e.get("tags", {}).items() if k in KEEP_TAGS}
        props.update(category=cat, osm=key)
        feats.append({"type": "Feature", "properties": props,
                      "geometry": {"type": "Point", "coordinates": [lon, lat]}})
        counts[cat] = counts.get(cat, 0) + 1
    for c, n in counts.items():
        print(f"{c:12s} {n:4d}")
    return {"type": "FeatureCollection", "features": feats}


def unlit_paths():
    d = overpass(f"""[out:json][timeout:120];rel({BEZIRK});map_to_area->.a;
      way["highway"~"^(footway|path|cycleway|pedestrian|steps|living_street|track)$"]["lit"="no"](area.a);
      out geom;""")
    feats = [{"type": "Feature",
              "properties": {"name": w["tags"].get("name"), "highway": w["tags"]["highway"], "osm": f"way/{w['id']}"},
              "geometry": {"type": "LineString", "coordinates": [[p["lon"], p["lat"]] for p in w["geometry"]]}}
             for w in d["elements"]]
    print(f"unlit paths  {len(feats)}")
    return {"type": "FeatureCollection", "features": feats}


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    only = sys.argv[1:]
    for name, fn in [("boundaries", boundaries), ("pois", pois), ("unlit_paths", unlit_paths)]:
        if only and name not in only:
            continue
        (OUT / f"{name}.geojson").write_text(json.dumps(fn(), ensure_ascii=False))
        print("wrote", name, flush=True)
    (OUT / "meta.json").write_text(json.dumps({"fetched": time.strftime("%Y-%m-%d")}))
