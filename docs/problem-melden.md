# Problem melden: Formular, Status und Ausbaustufen

## Was Anwohnende sehen
Ein Formular mit einer Frage pro Bildschirm (4 Schritte, große Schrift, Zurück jederzeit, Fortschrittsbalken):
1. **Worum geht es?** Große Auswahlfelder mit Symbol (Beleuchtung, Müll, Verkehr/Schulweg, Treffpunkt, Zusammenleben, Barrierefreiheit, Sonstiges).
2. **Wo?** Auf die Karte tippen, den Punkt verschieben oder „Meinen Standort nehmen“. Angezeigt wird die nächste Straße und der Stadtteil.
3. **Erzählen Sie uns mehr:** „Was ist das Problem?“, „Seit wann?“ (Auswahl), „Was schlagen Sie vor?“ (freiwillig).
4. **Prüfen und absenden.** Der Hinweis, dass die Meldung öffentlich lesbar ist, muss bestätigt werden.

Vorher steht die Weiche: Notfall (110/112), defekte Lampe und Schäden gehen direkt an die Stadt, alles andere hierher.

## Status einer Meldung
| Anzeige | Label am GitHub-Issue | Bedeutung für Anwohnende |
|---|---|---|
| Gemeldet | `gemeldet` (automatisch) | Abgeschickt, noch nicht gelesen |
| Eingegangen | `eingegangen` | Beim Präventionsrat angekommen |
| Geprüft | `geprueft` (oder `in-bearbeitung`) | Geprüft, erscheint auf der Karte |
| Erledigt | `umgesetzt` oder Issue geschlossen | Behoben / umgesetzt |
| Abgelehnt | `abgelehnt` | Nichts zu tun; Begründung steht als Kommentar im Issue |

Unter **„Meine Meldungen“** sehen Anwohnende den Stand ihrer Meldungen (die Nummern merkt sich der Browser, oder sie tragen eine Nummer ein). Auf der öffentlichen Karte erscheinen nur geprüfte Meldungen.

Der Präventionsrat ändert den Status, indem er das Label am Issue setzt (GitHub-Oberfläche oder `gh issue edit 12 --add-label eingegangen`).

## Einrichtung (einmalig)
**Labels anlegen:**
```bash
for l in meldung gemeldet eingegangen geprueft in-bearbeitung umgesetzt abgelehnt; do gh label create $l --repo FreeXYZ-HalfPI/preventionsrat_GISMap 2>/dev/null; done
```
**Absenden ohne GitHub-Konto:** `worker/report-worker.js` ist ein kleiner Cloudflare Worker (Free-Plan), der die Meldung als Issue anlegt. Er prüft Thema, Ort (liegt im Bezirk), Textlänge und ein Honeypot-Feld und akzeptiert nur Anfragen von der Seite der Karte.
1. Fine-grained Token auf GitHub: nur dieses Repo, nur „Issues: Read and write“.
2. `wrangler deploy worker/report-worker.js`, Variablen `REPO`, `ORIGIN` setzen, `wrangler secret put GH_TOKEN`.
3. Die Worker-URL in `config/districts.json` bei `report_api` eintragen und `python3 scripts/build_map.py` ausführen.

Solange `report_api` leer ist, öffnet „Weiter zu GitHub“ das vorbefüllte GitHub-Formular (Konto nötig) und bietet „Text kopieren“ an.

## Grenzen, ehrlich benannt
- Meldungen sind öffentlich lesbar (öffentliches Repo). Das steht im Formular. Kontaktdaten werden bewusst nicht abgefragt; für Rückfragen gibt es nur die Kommentare im Issue.
- Missbrauchsschutz ist einfach (Honeypot, Prüfung der Felder). Bei Spam kommt eine Ratenbegrenzung hinzu.
- Noch nicht mit Menschen von 60 bis 70 Jahren getestet. Das sollte vor dem Start mit 3 bis 5 Personen passieren.

## Ausbaustufe: Sprache zu Text
Anwohnende tippen nur den Ort an und sprechen die Antworten auf „Was ist das Problem?“, „Seit wann?“ und „Was schlagen Sie vor?“.
- Heute schon: Handy-Tastaturen haben ein Mikrofon-Symbol (im Formular als Tipp genannt).
- Phase 2: Mikrofon-Knopf je Frage, Web Speech API im Browser (kostenlos, Chrome/Edge/Safari, Audio geht dabei an den Browser-Anbieter) mit sichtbarem Text zum Korrigieren.
- Phase 3, datenschutzfreundlicher: Spracherkennung auf dem Gerät oder auf EU-Servern (zum Beispiel Whisper), Audio wird nicht gespeichert, nur der Text.
- Phase 4: Gesprächsmodus, bei dem die App die Fragen vorliest und die Antworten Frage für Frage einträgt. Die Felder des Formulars sind dafür schon als einzelne Fragen angelegt.
Jeweils vor dem Einsatz Datenschutz (DSGVO, Einwilligung) mit der Stadt klären.
