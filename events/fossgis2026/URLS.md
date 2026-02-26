# URLs im FOSSGIS-Event (Fahrplan-Druck 2026)

Alle per URL eingebundenen oder referenzierten Ressourcen in `index.html` und `style.css`.

---

## Eingebundene Ressourcen (werden geladen)

### Scripts
| Beschreibung | URL |
|--------------|-----|
| Lucide Icons (UMD) | `https://unpkg.com/lucide@latest/dist/umd/lucide.js` |

### Bilder / CSS-Hintergründe (lokal)
| Beschreibung | Pfad |
|--------------|------|
| FOSSGIS-Logo (Header) | `assets/FOSSGIS_Logo_white.svg` |

### API / Daten (fetch)
| Beschreibung | URL |
|--------------|-----|
| Fahrplan-JSON (pretalx) | `https://pretalx.com/fossgis2026/schedule/export/schedule.json` |
| Widget-JSON (Pausen) | `https://pretalx.com/fossgis2026/schedule/v/latest/widgets/schedule.json` |

### Bilder (img src – QR-Codes, lokal)
| Beschreibung | Pfad |
|--------------|------|
| QR-Code bahnhof.de | `assets/qr-bahnhof_de.png` |
| QR-Code Online-Fahrplan (pretalx) | `assets/qr-fahrplan_pretalx_2026.png` |
| QR-Code Fahrplan-Druck (online) | `assets/qr-fahrplan_druck_online_2026.png` |
| QR-Code FOSSGIS Mastodon | `assets/qr-fossgis-mastodon.png` |

---

## Links (href – nur Verweise, keine Einbindung)

| Beschreibung | URL |
|--------------|-----|
| bahnhof.de | `https://bahnhof.de` |
| Online-Fahrplan (pretalx) | `https://pretalx.com/fossgis2026/schedule/` |
| Fahrplan-Druck (online) | `https://gislars.github.io/fossgis-fahrplan-druck/events/fossgis2026/` |
| FOSSGIS Mastodon | `https://mastodon.online/@FOSSGISeV` |
| Repo fossgis-fahrplan-druck | `https://github.com/gislars/fossgis-fahrplan-druck` |
| Repo c3-fahrplan-druck (Original) | `https://github.com/felixdivo/c3-fahrplan-druck` |

---

## Lokale Ressourcen (relative Pfade, keine externen URLs)

- `style.css` (Stylesheet)
- `assets/qr-*.png` (QR-Code-Bilder: bahnhof.de, pretalx, Fahrplan-Druck, FOSSGIS Mastodon)
- `fonts/*` (Schriftdateien in style.css)

---

*Stand: Erstellt aus dem Code in `events/fossgis2026/`.*
