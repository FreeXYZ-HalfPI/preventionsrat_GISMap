# Präventionsatlas Buchholz-Kleefeld

**Entwickelt von MB Saryazdi**

**Karte online:** https://freexyz-halfpi.github.io/preventionsrat_GISMap/

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

## Schulwege, Licht und Zahlen

Drei Tabs ergänzen die Orte-Karte:

- **Schulwege & Licht**: um jede der 14 Schulen eine Kernzone (100 m) und ein Schulumfeld (300 m), eingefärbt nach Prüfbedarf. Der Punktwert kommt aus OSM-Daten (Hauptstraße im Umfeld, erfasste Querungen, unbeleuchtete Wege, Haltestellen, Kitas) und ist ein Hinweis, wo sich eine Begehung lohnt, keine Unfallanalyse. Zu jeder Schule passende Maßnahmen mit Quelle (Schulwegplan, Tempo 30, Querung, Elternhaltestelle, Schulstraße, Unfallkommission, Radfahrausbildung, Schulwegüberwachung). Dazu 12 Beleuchtungs-Schwerpunkte: Felder mit viel unbeleuchtetem Weg nahe Schulen, Kitas, Spielplätzen und Haltestellen.
- **Wahrnehmung der Anwohnenden** (Schulwege & Licht): Zu jedem Beleuchtungs-Schwerpunkt und jeder Schule können Anwohnende angeben, ob sie sich abends eher sicher oder unsicher fühlen und warum (zu dunkel, Blendung, menschenleer, Gebüsch, Verkehr). Die Antworten sind GitHub-Issues mit dem Label `wahrnehmung` (Vorlage `wahrnehmung.yml`). Gezählt werden nur Antworten mit dem Label `geprueft`, auf der Karte erscheint ein Ergebnis erst ab drei Antworten pro Ort. Idee nach dem Mørkekort aus Dänemark, siehe `docs/research-switzerland-denmark.md`.
- **Zahlen**: Kennzahlen aus Statistischen Profilen 2022, Sozialbericht 2023 und Sicherheitsbericht 2025 je Stadtteil, auf der Karte einfärbbar (Kinderanteil, Transferleistungen, Unfälle, Radanteil), mit Einordnung für die AGs.
- **Vorschlag**: neuer Abschnitt zu Ansätzen aus Hannover und Niedersachsen (mobile Sicherheitskonferenz, Communities That Care, AK Schulwegsicherheit im Kreispräventionsrat Heidekreis, Elternhaltestelle, Mängelhinweiskarte).

- **Problem melden**: Formular in 4 Schritten mit Ortswahl auf der Karte, Status (Gemeldet, Eingegangen, Geprüft, Erledigt, Abgelehnt) und „Meine Meldungen“. Details und Einrichtung: [docs/problem-melden.md](docs/problem-melden.md).

## Impressum und Datenschutz

`impressum.html` und `datenschutz.html` werden aus `config/legal.json` erzeugt (`python3 scripts/build_map.py`). Vor der Veröffentlichung dort Name, Anschrift und E-Mail der verantwortlichen Person eintragen; unausgefüllte Felder erscheinen gelb markiert. Die Karte lädt nichts von fremden Servern außer den öffentlichen Meldungen von `api.github.com`: Schriften (`fonts/`) und Leaflet liegen im Projekt. Die Texte sind eine Vorlage und sollten vom Datenschutz der Stadt oder einer fachkundigen Person geprüft werden.

## Mehrere Stadtbezirke

> **Derzeit öffentlich nur Buchholz-Kleefeld.** Bothfeld-Vahrenheide ist vorbereitet, aber in `config/districts.json` mit `"enabled": false` abgeschaltet; Menü und Seite werden nicht gebaut. Zum Testen: `DISTRICT=bothfeld-vahrenheide python3 scripts/build_map.py`. Zum Freischalten `enabled` entfernen und neu bauen.

Oben links wählt ein Menü den Stadtbezirk. Jeder Bezirk ist eine eigene, eigenständige Seite, die aus derselben Vorlage gebaut wird:

| Bezirk | Seite |
|---|---|
| Buchholz-Kleefeld (04) | `index.html` |
| Bothfeld-Vahrenheide (03) | `bezirke/bothfeld-vahrenheide.html` |

Einen weiteren Bezirk anlegen:

1. Eintrag in `config/districts.json` (OSM-Relation des Bezirks und der Stadtteile, Kartenausschnitt, Polizeistation, Hinweis zum Präventionsgremium).
2. Daten abrufen und analysieren, zum Beispiel für `bothfeld-vahrenheide`:
   ```bash
   export DISTRICT=bothfeld-vahrenheide
   python3 scripts/fetch_osm.py && python3 scripts/fetch_basemap.py
   python3 scripts/fetch_streets.py && python3 scripts/fetch_schulumfeld.py
   python3 scripts/analyse_schulwege.py
   ```
3. In `data/<bezirk>/` von Hand `issues.json` (Themen mit Quelle) und `kennzahlen.json` anlegen.
4. `python3 scripts/build_map.py` baut alle Bezirke (oder nur einen mit `DISTRICT=...`).

Bothfeld-Vahrenheide hat bisher Themen aus Sitzungsunterlagen des Stadtbezirksrats und den Ordnungsdienst-Zahlen, aber noch keine Stadtteil-Kennzahlen und keinen Vorschlagstext.

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
python3 scripts/fetch_schulumfeld.py   # Straßennamen, Querungen für die Schulweg-Analyse
python3 scripts/analyse_schulwege.py   # Zonen, Prüfbedarf, Beleuchtungs-Schwerpunkte -> data/schulwege.json
python3 scripts/build_map.py        # erzeugt index.html
```

`data/kennzahlen.json` und `data/issues.json` werden von Hand gepflegt (jede Zahl mit Quelle).

`index.html` ist eine einzelne, eigenständige Datei und kann über GitHub Pages oder jeden
Webserver veröffentlicht werden.

## Aufbau

- `scripts/fetch_osm.py` – Abruf über die Overpass-API (Stadtbezirk = OSM-Relation 1862974)
- `scripts/fetch_basemap.py` – Grundkarte für den Kartenausschnitt
- `scripts/build_map.py` – ordnet Orte den Stadtteilen zu und baut `index.html`
- `src/map.template.html` – Kartenoberfläche (Leaflet 1.9.4)
- `scripts/fetch_schulumfeld.py`, `scripts/analyse_schulwege.py` – Schulweg- und Beleuchtungsanalyse
- `data/` – abgerufene Rohdaten (GeoJSON), Analyse (`schulwege.json`) und Kennzahlen (`kennzahlen.json`)

## Entwicklung

MB Saryazdi
