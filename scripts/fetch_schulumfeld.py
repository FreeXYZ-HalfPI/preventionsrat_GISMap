"""Fetch traffic context for the Schulweg analysis (street names, crossings, signals,
traffic calming) from OpenStreetMap via Overpass. Writes data/schulumfeld.json.
analyse_schulwege.py filters it down to the surroundings of each school."""
import datetime, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from fetch_osm import overpass, OUT

BBOX = "52.355,9.765,52.420,9.850"  # Stadtbezirk plus Rand
Q = f"""[out:json][timeout:120];
(
  way[highway~"^(primary|secondary|tertiary)$"][name]({BBOX});
  node[highway~"^(crossing|traffic_signals)$"]({BBOX});
  node[traffic_calming]({BBOX});
);
out tags center;
"""


def main():
    d = overpass(Q)
    els = [{"type": e["type"], "id": e["id"], "tags": e.get("tags", {}),
            "lat": e.get("lat") or e.get("center", {}).get("lat"),
            "lon": e.get("lon") or e.get("center", {}).get("lon")} for e in d["elements"]]
    (OUT / "schulumfeld.json").write_text(json.dumps(
        {"fetched": datetime.date.today().isoformat(), "elements": els}, ensure_ascii=False))
    print(len(els), "elements")


if __name__ == "__main__":
    main()
