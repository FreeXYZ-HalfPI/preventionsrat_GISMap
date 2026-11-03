"""Erzeugt impressum.html und datenschutz.html aus config/legal.json.
Unausgefüllte Felder (in eckigen Klammern) werden gelb markiert, damit sie nicht übersehen werden."""
import html, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

CSS = (ROOT / "src" / "fonts.css").read_text().replace("__ROOT__", "") + """
:root { --paper:#f3f5f9; --panel:#fff; --ink:#141d2b; --ink-2:#46546a; --line:#d5dce8; --accent:#3446b0; --mark:#ffe58a; }
@media (prefers-color-scheme: dark) { :root { --paper:#0e1622; --panel:#162030; --ink:#e8eef7; --ink-2:#a3b3c9; --line:#27364b; --accent:#8fa3ff; --mark:#6b5a12; } }
* { box-sizing: border-box; }
body { margin: 0; background: var(--paper); color: var(--ink); font: 18px/1.6 "Atkinson Hyperlegible", system-ui, sans-serif; }
main { max-width: 760px; margin: 0 auto; padding: 24px 20px 64px; }
h1, h2 { font-family: "Lexend", "Atkinson Hyperlegible", system-ui, sans-serif; line-height: 1.2; }
h1 { font-size: 30px; margin: 16px 0 8px; } h2 { font-size: 21px; margin: 32px 0 6px; }
a { color: var(--accent); font-weight: 700; }
.back { display: inline-block; min-height: 44px; line-height: 44px; }
.note { background: var(--panel); border: 1px solid var(--line); border-left: 4px solid var(--accent); border-radius: 8px; padding: 10px 14px; font-size: 16px; color: var(--ink-2); }
mark { background: var(--mark); color: inherit; padding: 0 3px; border-radius: 3px; }
address { font-style: normal; }
nav { margin-top: 40px; display: flex; gap: 20px; flex-wrap: wrap; }
"""

def val(legal, key, optional=False):
    v = legal.get(key, "").strip()
    if not v:
        return "" if optional else "<mark>[bitte ergänzen]</mark>"
    esc = html.escape(v)
    return f"<mark>{esc}</mark>" if v.startswith("[") else esc

def page(title, body):
    return (f'<!doctype html>\n<html lang="de">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            f'<meta name="robots" content="noindex">\n<title>{title} · Präventionsatlas Buchholz-Kleefeld</title>\n<style>{CSS}</style>\n</head>\n<body>\n<main>\n'
            f'<a class="back" href="index.html">← Zurück zur Karte</a>\n{body}\n'
            f'<nav><a href="impressum.html">Impressum</a><a href="datenschutz.html">Datenschutzerklärung</a><a href="index.html">Zur Karte</a></nav>\n</main>\n</body>\n</html>\n')

def build():
    L = json.loads((ROOT / "config" / "legal.json").read_text())
    name, strasse, ort, mail = val(L, "name"), val(L, "strasse"), val(L, "plz_ort"), val(L, "email")
    tel = val(L, "telefon", optional=True)
    tel_line = f"<br>Telefon: {tel}" if tel else ""
    stand = html.escape(L.get("stand", ""))
    who = f"<address>{name}<br>{strasse}<br>{ort}<br>E-Mail: {mail}{tel_line}</address>"

    impressum = f"""<h1>Impressum</h1>
<h2>Angaben gemäß § 5 Digitale-Dienste-Gesetz (DDG)</h2>
{who}
<h2>Über dieses Angebot</h2>
<p>Der Präventionsatlas Buchholz-Kleefeld ist ein Prototyp. Er wurde von Mohammad B. Saryazdi für den Präventionsrat Buchholz-Kleefeld entwickelt, um Orte, Schulwege und Meldungen im Stadtbezirk sichtbar zu machen. Es ist <b>keine amtliche Seite der Landeshauptstadt Hannover</b>. Auskünfte der Stadt und ihre offiziellen Meldewege finden Sie unter <a href="https://www.hannover.de/" rel="noopener">hannover.de</a>.</p>
<h2>Inhalte und Quellen</h2>
<p>Die Inhalte beruhen auf den im jeweiligen Eintrag genannten Quellen (Berichte der Stadt, Sitzungsunterlagen) und auf Daten von OpenStreetMap. Trotz sorgfältiger Prüfung kann keine Gewähr für Richtigkeit, Vollständigkeit und Aktualität übernommen werden. Der angezeigte „Prüfbedarf“ an Schulwegen ist ein Hinweis, wo sich eine Begehung lohnt, und keine Unfallanalyse.</p>
<h2>Haftung für Links</h2>
<p>Diese Seite verweist auf externe Seiten. Auf deren Inhalte haben wir keinen Einfluss. Verantwortlich ist jeweils der Betreiber der verlinkten Seite. Bei Hinweisen auf Rechtsverstöße entfernen wir solche Links.</p>
<h2>Urheberrecht und Lizenzen</h2>
<p>Kartendaten: © <a href="https://www.openstreetmap.org/copyright" rel="noopener">OpenStreetMap-Mitwirkende</a>, Open Database License (ODbL). Kartenbibliothek: Leaflet (BSD-2-Clause). Schriften Atkinson Hyperlegible und Lexend: SIL Open Font License 1.1. Der Quelltext des Projekts liegt öffentlich auf <a href="https://github.com/FreeXYZ-HalfPI/preventionsrat_GISMap" rel="noopener">GitHub</a>.</p>
<p class="note">Stand: {stand}</p>"""

    datenschutz = f"""<h1>Datenschutzerklärung</h1>
<p class="note">Kurz gesagt: Diese Seite setzt keine Cookies, nutzt keine Werbe- oder Analysedienste und lädt keine Schriften oder Skripte von fremden Servern. Ihr Standort wird nur auf Ihren Knopfdruck im Browser verwendet und nicht gespeichert.</p>
<h2>1. Verantwortlich</h2>
{who}
<h2>2. Aufruf der Seite (Hosting)</h2>
<p>Die Seite liegt bei GitHub Pages (GitHub Inc., USA, ein Unternehmen von Microsoft). Beim Aufruf verarbeitet GitHub technisch notwendige Daten, insbesondere Ihre IP-Adresse, Datum und Uhrzeit sowie die aufgerufene Seite, um die Seite auszuliefern und abzusichern. Rechtsgrundlage ist unser berechtigtes Interesse an einem sicheren, funktionierenden Angebot (Art. 6 Abs. 1 lit. f DSGVO). Weitere Angaben, auch zur Übermittlung in die USA, finden Sie in der <a href="https://docs.github.com/de/site-policy/privacy-policies/github-general-privacy-statement" rel="noopener">Datenschutzerklärung von GitHub</a>.</p>
<h2>3. Abruf von Meldungen und Einschätzungen</h2>
<p>Die Karte fragt beim Laden öffentliche Meldungen und Einschätzungen von der Schnittstelle von GitHub (api.github.com) ab. Dabei erhält GitHub Ihre IP-Adresse. Es werden keine Daten von Ihnen an uns übertragen. Rechtsgrundlage ist Art. 6 Abs. 1 lit. f DSGVO (Anzeige der geprüften Meldungen).</p>
<h2>4. Schriften, Karte und Bibliotheken</h2>
<p>Schriften und die Kartenbibliothek werden von dieser Seite selbst ausgeliefert, es gibt keine Verbindung zu Google Fonts oder anderen Anbietern. Die Karte wird im Browser aus mitgelieferten OpenStreetMap-Daten gezeichnet. Es werden keine Kartenkacheln von fremden Servern geladen.</p>
<h2>5. Speicherung im Browser</h2>
<p>Die Seite setzt keine Cookies. Sie speichert in Ihrem Browser (Local Storage) nur Einstellungen, die Sie selbst wählen, etwa eingeschaltete Ebenen, sowie im Prototyp die Meldungen, die Sie im Formular eingeben, damit sie auf Ihrem Gerät auf der Karte stehen bleiben. Diese Daten verlassen Ihr Gerät nicht. Sie können sie jederzeit über „Meine Test-Meldungen löschen“ oder in den Browser-Einstellungen entfernen. Rechtsgrundlage ist § 25 Abs. 2 Nr. 2 TDDDG, weil die Speicherung für den von Ihnen gewünschten Dienst erforderlich ist.</p>
<h2>6. Standort</h2>
<p>Wenn Sie „Meinen Standort nehmen“ oder die Ortungstaste wählen, fragt Ihr Browser Sie um Erlaubnis. Der Standort wird nur in Ihrem Browser verwendet, um die Karte zu zentrieren und einen Punkt zu setzen. Er wird nicht an uns oder Dritte gesendet und nicht gespeichert (Art. 6 Abs. 1 lit. a DSGVO, Ihre Einwilligung über die Browserabfrage).</p>
<h2>7. Meldeformular</h2>
<p><b>Im jetzigen Prototyp wird nichts gesendet.</b> Was Sie eingeben, bleibt auf Ihrem Gerät (siehe Punkt 5). Sobald das Formular Meldungen übermittelt, wird diese Erklärung vorher ergänzt. Geplant ist: Meldungen werden als öffentlich lesbarer Eintrag bei GitHub gespeichert und vom Präventionsrat geprüft. Bitte schreiben Sie darin keine Namen, Kennzeichen oder Fotos von Personen. Kontaktdaten werden nicht abgefragt.</p>
<h2>8. Einschätzungen und Meldungen über GitHub</h2>
<p>Wer heute über die Links zu GitHub eine Meldung oder Einschätzung abgibt, benötigt dort ein Konto. Der Inhalt ist dann öffentlich lesbar, und GitHub verarbeitet Ihre Kontodaten nach seiner eigenen Datenschutzerklärung. Auf der Karte erscheinen Einschätzungen nur als Zahlen pro Ort und erst ab drei geprüften Antworten.</p>
<h2>9. Externe Links</h2>
<p>Wenn Sie einen Link zu einer anderen Seite anklicken (zum Beispiel hannover.de oder OpenStreetMap), gilt dort die Datenschutzerklärung der jeweiligen Seite.</p>
<h2>10. Ihre Rechte</h2>
<p>Sie haben das Recht auf Auskunft (Art. 15), Berichtigung (Art. 16), Löschung (Art. 17), Einschränkung der Verarbeitung (Art. 18), Datenübertragbarkeit (Art. 20) und Widerspruch (Art. 21 DSGVO). Wenden Sie sich dafür an die oben genannte Adresse. Sie können sich außerdem bei einer Aufsichtsbehörde beschweren, zum Beispiel bei der Landesbeauftragten für den Datenschutz Niedersachsen, Prinzenstraße 5, 30159 Hannover.</p>
<p class="note">Stand: {stand}</p>"""

    (ROOT / "impressum.html").write_text(page("Impressum", impressum))
    (ROOT / "datenschutz.html").write_text(page("Datenschutzerklärung", datenschutz))
    missing = [k for k in ("name", "strasse", "plz_ort", "email") if L.get(k, "").strip().startswith("[") or not L.get(k, "").strip()]
    print("impressum.html, datenschutz.html" + (f"  ACHTUNG, unausgefüllt in config/legal.json: {', '.join(missing)}" if missing else ""))

if __name__ == "__main__":
    build()
