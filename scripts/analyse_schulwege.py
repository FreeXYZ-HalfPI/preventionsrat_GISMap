"""Schulwegsicherheit und Beleuchtungs-Schwerpunkte aus den vorhandenen OSM-Daten ableiten.

Schreibt data/schulwege.json:
  schools   Schulen mit Zonen (Kernzone 100 m, Schulumfeld 300 m), Kennzahlen, Prüfbedarf und Maßnahmen
  hotspots  Schwerpunkte unbeleuchteter Wege, gewichtet nach Nähe zu Schulen, Kitas, Spielplätzen, Haltestellen

Der Prüfbedarf ist ein transparenter Punktwert aus OSM-Merkmalen, keine amtliche Unfallanalyse.
"""
import json, math
from pathlib import Path

from district import D, DATA, SLUG
LAT0 = D["lat0"]
PREFIX = "" if SLUG == "buchholz-kleefeld" else "BV-"
KX, KY = 111320 * math.cos(math.radians(LAT0)), 110574


def xy(lon, lat):
    return (lon * KX, lat * KY)


def dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def in_ring(x, y, ring):
    inside, j = False, len(ring) - 1
    for i in range(len(ring)):
        xi, yi = ring[i]; xj, yj = ring[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            inside = not inside
        j = i
    return inside


def stadtteil_of(lon, lat, parts):
    for name, polys in parts:
        if any(in_ring(lon, lat, p[0]) for p in polys):
            return name
    return None


def unlit_samples(unlit, step=15):
    """Points every ~step metres along unlit paths; each stands for `step` metres of path."""
    out = []
    for f in unlit["features"]:
        pts = [xy(*c) for c in f["geometry"]["coordinates"]]
        for a, b in zip(pts, pts[1:]):
            d = dist(a, b)
            n = max(1, int(d // step))
            for i in range(n):
                t = (i + 0.5) / n
                out.append(((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t), d / n))
    return out


MAJOR = {"primary", "secondary", "tertiary"}


def main():
    load = lambda n: json.loads((DATA / n).read_text())
    pois = load("pois.geojson")["features"]
    unlit = load("unlit_paths.geojson")
    bounds = load("boundaries.geojson")
    parts = [(f["properties"]["name"], f["geometry"]["coordinates"])
             for f in bounds["features"] if f["properties"]["level"] == "stadtteil"]
    ctx = load("schulumfeld.json")["elements"] if (DATA / "schulumfeld.json").exists() else []

    def pts(pred):
        return [(f["properties"].get("name"), xy(*f["geometry"]["coordinates"]), f["geometry"]["coordinates"])
                for f in pois if pred(f["properties"])]
    schools = pts(lambda p: p.get("amenity") == "school")
    kitas = pts(lambda p: p.get("amenity") in ("kindergarten", "childcare"))
    play = pts(lambda p: p["category"] == "spielplatz")
    stops = pts(lambda p: p["category"] == "oepnv")
    samples = unlit_samples(unlit)

    # street context from Overpass (optional)
    roads = [e for e in ctx if e["type"] == "way" and e["tags"].get("highway") in MAJOR]
    crossings = [e for e in ctx if e["type"] == "node" and e["tags"].get("highway") in ("crossing", "traffic_signals")]
    calming = [e for e in ctx if e["type"] == "node" and "traffic_calming" in e["tags"]]

    out_schools = []
    for name, p, ll in schools:
        pr = next(f["properties"] for f in pois if f["properties"].get("name") == name and f["properties"].get("amenity") == "school")
        grund = "primary" in (pr.get("school") or "") or "Grundschule" in name
        unlit_m = round(sum(w for q, w in samples if dist(p, q) <= 300))
        near = lambda L, r: [n for n, q, _ in L if dist(p, q) <= r]
        info = {
            "name": name, "coords": [ll[1], ll[0]],
            "stadtteil": stadtteil_of(ll[0], ll[1], parts),
            "art": "Grundschule" if grund and "secondary" not in (pr.get("school") or "") else
                   ("Förderschule" if "special_education_needs" in (pr.get("school") or "") or "Landesbildungszentrum" in name else "weiterführende Schule"),
            "unbeleuchtet_m": unlit_m,
            "kitas": len(near(kitas, 300)),
            "spielplaetze": len(near(play, 300)),
            "haltestellen": len(set(n for n in near(stops, 250) if n)),
        }
        if ctx:
            lonlat = lambda e: xy(e["lon"], e["lat"])
            r_major = sorted({e["tags"]["name"] for e in roads if e["tags"]["highway"] in MAJOR and e.get("lat") and dist(p, lonlat(e)) <= 220})
            info["hauptstrassen"] = r_major
            info["querungshilfen"] = sum(1 for e in crossings if dist(p, lonlat(e)) <= 250)
            info["ampeln"] = sum(1 for e in crossings if e["tags"].get("highway") == "traffic_signals" or e["tags"].get("crossing") == "traffic_signals" if dist(p, lonlat(e)) <= 250)
            info["verkehrsberuhigung"] = sum(1 for e in calming if dist(p, lonlat(e)) <= 250)
        score, why = 0, []
        if info.get("hauptstrassen"):
            score += 2; why.append("Hauptverkehrsstraße im Umfeld: " + ", ".join(info["hauptstrassen"]))
            if info["querungshilfen"] == 0:
                score += 1; why.append("keine Querungshilfe in OSM erfasst")
        if unlit_m >= 800:
            score += 2; why.append(f"{unlit_m} m unbeleuchtete Wege im Umfeld")
        elif unlit_m >= 300:
            score += 1; why.append(f"{unlit_m} m unbeleuchtete Wege im Umfeld")
        if info["haltestellen"] >= 3:
            score += 1; why.append(f"{info['haltestellen']} Haltestellen in der Nähe, viel Ein- und Aussteigen")
        if info["kitas"] >= 2:
            score += 1; why.append(f"{info['kitas']} Kitas im Umfeld, viele kleine Kinder unterwegs")
        info["punkte"] = score
        info["pruefbedarf"] = "hoch" if score >= 4 else "mittel" if score >= 2 else "gering"
        info["gruende"] = why
        # measures: only those that fit the indicators
        m = []
        if info["art"] == "Grundschule":
            m += ["schulwegplan", "radausbildung"]
        if info.get("hauptstrassen"):
            m += ["tempo30", "querung", "unfallkommission"]
        if info["art"] == "Grundschule" and (info.get("hauptstrassen") or info["haltestellen"] >= 2):
            m.append("elternhaltestelle")
        if unlit_m >= 300:
            m += ["licht_melden", "abendbegehung"]
        m.append("schulwegueberwachung")
        if info["art"] == "Grundschule" and score >= 3:
            m.append("schulstrasse")
        info["massnahmen"] = m
        out_schools.append(info)
    out_schools.sort(key=lambda s: -s["punkte"])

    # lighting hotspots: 150 m grid over unlit samples
    CELL = 150
    cells = {}
    for q, w in samples:
        k = (int(q[0] // CELL), int(q[1] // CELL))
        c = cells.setdefault(k, [0.0, 0.0, 0.0])
        c[0] += w; c[1] += q[0] * w; c[2] += q[1] * w
    sens = [("Schule", n, q) for n, q, _ in schools] + [("Kita", n, q) for n, q, _ in kitas] + \
           [("Spielplatz", n or "Spielplatz", q) for n, q, _ in play] + [("Haltestelle", n or "Haltestelle", q) for n, q, _ in stops]
    weight = {"Schule": 3, "Kita": 1.5, "Spielplatz": 1, "Haltestelle": 1}
    cand = []
    for k, (L, sx, sy) in cells.items():
        if L < 150:
            continue
        c = (sx / L, sy / L)
        hits = [(t, n) for t, n, q in sens if dist(c, q) <= 200]
        pr = L / 100 + sum(weight[t] for t, _ in hits)
        cand.append((pr, L, c, hits))
    cand.sort(key=lambda t: -t[0])
    chosen = []
    for pr, L, c, hits in cand:
        if all(dist(c, o[2]) >= 300 for o in chosen):
            chosen.append((pr, L, c, hits))
        if len(chosen) == 12:
            break
    hotspots = []
    for i, (pr, L, c, hits) in enumerate(chosen, 1):
        lon, lat = c[0] / KX, c[1] / KY
        names = sorted({n for t, n in hits if t in ("Schule", "Kita", "Spielplatz")})
        hotspots.append({
            "id": f"{PREFIX}L{i}", "coords": [round(lat, 6), round(lon, 6)], "stadtteil": stadtteil_of(lon, lat, parts),
            "unbeleuchtet_m": round(L), "radius_m": 200, "punkte": round(pr, 1),
            "naehe": {t: sum(1 for tt, _ in hits if tt == t) for t in ("Schule", "Kita", "Spielplatz", "Haltestelle")},
            "orte": names[:5],
        })
    res = {"updated": json.loads((DATA / "meta.json").read_text())["fetched"], "has_street_context": bool(ctx),
           "schools": out_schools, "hotspots": hotspots}
    (DATA / "schulwege.json").write_text(json.dumps(res, ensure_ascii=False, indent=1))
    for s in out_schools:
        print(s["punkte"], s["pruefbedarf"], s["name"], s["unbeleuchtet_m"], s.get("hauptstrassen"), s.get("querungshilfen"))
    for h in hotspots:
        print(h["id"], h["stadtteil"], h["unbeleuchtet_m"], h["punkte"], h["naehe"], h["orte"])


if __name__ == "__main__":
    main()
