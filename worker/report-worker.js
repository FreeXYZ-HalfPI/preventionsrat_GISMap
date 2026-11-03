// Cloudflare Worker: nimmt Meldungen aus dem Formular entgegen und legt sie als GitHub-Issue an,
// damit Anwohnende kein GitHub-Konto brauchen. Kostenlos im Free-Plan.
// Secrets/Variablen (wrangler secret put GH_TOKEN): GH_TOKEN = Fine-grained Token, nur dieses Repo, nur "Issues: Read and write".
// Variablen: REPO ("FreeXYZ-HalfPI/preventionsrat_GISMap"), ORIGIN ("https://freexyz-halfpi.github.io")
const THEMEN = ["Beleuchtung / dunkle Wege", "Müll / Verschmutzung", "Verkehr / Schulweg", "Treffpunkt / Aufenthalt / Grünfläche", "Zusammenleben / Konflikte", "Barrierefreiheit", "Sonstiges"];
const SEIT = ["", "Seit heute", "Seit einigen Tagen", "Seit einigen Wochen", "Seit einigen Monaten", "Schon sehr lange", "Weiß ich nicht"];
const clip = (v, n) => String(v ?? "").replace(/\r/g, "").trim().slice(0, n);

export default {
  async fetch(req, env) {
    const cors = { "Access-Control-Allow-Origin": env.ORIGIN, "Access-Control-Allow-Methods": "POST, OPTIONS", "Access-Control-Allow-Headers": "Content-Type", "Vary": "Origin" };
    const out = (obj, status = 200) => new Response(JSON.stringify(obj), { status, headers: { ...cors, "Content-Type": "application/json" } });
    if (req.method === "OPTIONS") return new Response(null, { status: 204, headers: cors });
    if (req.method !== "POST" || req.headers.get("Origin") !== env.ORIGIN) return out({ error: "forbidden" }, 403);
    let m; try { m = await req.json(); } catch { return out({ error: "bad json" }, 400); }
    if (m.website) return out({ number: 0 });                       // Honeypot: Bots füllen das Feld aus
    const lat = Number(m.lat), lon = Number(m.lon), text = clip(m.beschreibung, 1500);
    if (!THEMEN.includes(m.thema) || !SEIT.includes(m.seit_wann || "") || text.length < 10 || !(lat > 52.3 && lat < 52.5 && lon > 9.6 && lon < 9.95)) return out({ error: "invalid" }, 422);
    const ort = clip(m.ort, 120);
    // Gleiche Überschriften wie in .github/ISSUE_TEMPLATE/meldung.yml, damit die Karte die Meldung lesen kann
    const body = `### Thema\n\n${m.thema}\n\n### Ort\n\n${ort}\n\n### Koordinaten\n\n${lat.toFixed(5)}, ${lon.toFixed(5)}\n\n### Was ist das Problem?\n\n${text}\n\n### Seit wann gibt es das Problem?\n\n${m.seit_wann || "_No response_"}\n\n### Was schlagen Sie vor?\n\n${clip(m.vorschlag, 1000) || "_No response_"}\n\n_Eingegangen über das Formular der Karte._`;
    const r = await fetch(`https://api.github.com/repos/${env.REPO}/issues`, {
      method: "POST",
      headers: { Authorization: `Bearer ${env.GH_TOKEN}`, Accept: "application/vnd.github+json", "User-Agent": "praeventionsatlas-report", "Content-Type": "application/json" },
      body: JSON.stringify({ title: `[Meldung] ${ort}`, body, labels: ["meldung", "gemeldet"] }),
    });
    if (!r.ok) return out({ error: "upstream" }, 502);
    const j = await r.json();
    return out({ number: j.number, url: j.html_url });
  },
};
