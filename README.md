# Präventionsatlas Buchholz-Kleefeld

Interaktive GIS-Karte des Präventionsrats für den Stadtbezirk Buchholz-Kleefeld in Hannover
(Stadtteile Groß-Buchholz, Kleefeld und Heideviertel).

Die Karte zeigt öffentlich zugängliche Orte, die für Prävention und Sicherheit im Stadtteil wichtig sind:

| Ebene | Inhalt |
|---|---|
| Kinder & Jugend | Jugendzentren, Jugendhilfe-Einrichtungen |
| Bildung & Betreuung | Schulen, Kitas, Bibliotheken |
| Soziales & Beratung | Beratungsstellen, Begegnungsstätten, soziale Einrichtungen, Vereine |
| Sicherheit & Notfall | Polizei, Feuerwehr, Defibrillatoren (AED) |
| Gesundheit | Arztpraxen, Apotheken, Kliniken |
| Spielplätze, Sport, Parks & Grün | Treffpunkte im öffentlichen Raum |
| Religiöse Gemeinden | Kirchen, Moscheen und andere Gemeinden |
| Haltestellen | Stadtbahn, Bus, S-Bahn |
| Gastronomie & Kioske | Bars, Kneipen, Kioske, Spielhallen |
| Öffentliche Infrastruktur | WCs, Post, Recycling |
| Unbeleuchtete Wege | Fuß- und Radwege, die in OpenStreetMap als unbeleuchtet erfasst sind |

Filter nach Stadtteil, Volltextsuche und eine Ortsliste sind eingebaut. Die Karte funktioniert ohne
externen Kachel-Server: die Grundkarte (Straßen, Gebäude, Grünflächen, Gewässer) wird aus
OpenStreetMap-Daten selbst gezeichnet.

## Datenquelle

Alle Daten stammen aus [OpenStreetMap](https://www.openstreetmap.org) © OpenStreetMap-Mitwirkende,
lizenziert unter der [Open Database License (ODbL)](https://opendatacommons.org/licenses/odbl/).
Fehlende oder falsche Orte lassen sich direkt in OpenStreetMap korrigieren und erscheinen nach dem
nächsten Datenabruf in der Karte.

## Aktualisieren

Benötigt nur Python 3 (keine zusätzlichen Pakete).

```bash
python3 scripts/fetch_osm.py        # Grenzen, Orte, unbeleuchtete Wege
rm -rf data/basemap_parts && python3 scripts/fetch_basemap.py   # Grundkarte
python3 scripts/build_map.py        # erzeugt index.html
```

`index.html` ist eine einzelne, eigenständige Datei und kann über GitHub Pages oder jeden
Webserver veröffentlicht werden.

## Aufbau

- `scripts/fetch_osm.py` – Abruf über die Overpass-API (Stadtbezirk = OSM-Relation 1862974)
- `scripts/fetch_basemap.py` – Grundkarte für den Kartenausschnitt
- `scripts/build_map.py` – ordnet Orte den Stadtteilen zu und baut `index.html`
- `src/map.template.html` – Kartenoberfläche (Leaflet 1.9.4)
- `data/` – abgerufene Rohdaten als GeoJSON
