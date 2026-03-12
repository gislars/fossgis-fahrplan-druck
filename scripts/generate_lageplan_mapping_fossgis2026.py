#!/usr/bin/env python3
"""
Erzeugt die Mapping-Tabelle lageplan-urls.js für den FOSSGIS-2026-Fahrplan.
Nur für FOSSGIS 2026. Die Zuordnung Kürzel → Lageplan-URL liegt direkt im Skript.

Verwendung (von Projektroot):
  python scripts/generate_lageplan_mapping_fossgis2026.py

Ausgabe: events/fossgis2026/lageplan-urls.js
"""
from pathlib import Path

# Alle für FOSSGIS 2026 genutzten Kürzel (abbreviateRoom + Mensa).
# Wert = volle Lageplan-URL (ident oder ?q=); für jeden Raum eine URL.
# URL muss exakt auf den Raum/das Gebäude im Lageplan führen.
LAGEPLAN_BASE = "https://lageplan.uni-goettingen.de"

# Zuordnung Kürzel → Lageplan-URL (direkt im Skript).
# Raumnummern = Anzeigenamen aus Pretalx-Fahrplan (FOSSGIS 2026).
ROOM_TO_LAGEPLAN_URL = {
    # ZHG Hörsäle
    "HS1": f"{LAGEPLAN_BASE}/?ident=5257_1_1.OG_1.151",   # ZHG 011
    "HS2": f"{LAGEPLAN_BASE}/?ident=5257_1_1.OG_1.153",   # ZHG 010
    "HS3": f"{LAGEPLAN_BASE}/?ident=5257_1_1.OG_1.152",   # ZHG 009
    "HS4": f"{LAGEPLAN_BASE}/?ident=5257_1_1.OG_1.150",   # ZHG 008
    # BoF = Birds-of-a-Feather
    "BoF1": f"{LAGEPLAN_BASE}/?ident=5257_1_EG_0.161",   # ZHG 001
    "BoF2": f"{LAGEPLAN_BASE}/?ident=5257_1_EG_0.155",   # ZHG 005
    "BoF3": f"{LAGEPLAN_BASE}/?ident=5257_1_EG_0.154",   # ZHG 006
    # VG = Verfügungsgebäude, Workshops
    "WS1": f"{LAGEPLAN_BASE}/?ident=5361_1_1.OG_1.104",  # VG 1.104
    "WS2": f"{LAGEPLAN_BASE}/?ident=5361_1_1.OG_1.103",  # VG 1.103
    "WS3": f"{LAGEPLAN_BASE}/?ident=5361_1_1.OG_1.102",  # VG 1.102
    "WS4": f"{LAGEPLAN_BASE}/?ident=5361_1_1.OG_1.105",  # VG 1.105
    # OSM-Tracks / Opening (Institut für Geographie)
    "OSM1": f"{LAGEPLAN_BASE}/?ident=2410_1_EG_0.161",   # MN 11
    "OSM2": f"{LAGEPLAN_BASE}/?ident=2410_1_EG_0.162",   # MN 10
    "OSM3": f"{LAGEPLAN_BASE}/?ident=2410_1_EG_0.163",   # MN 12
    "OO": f"{LAGEPLAN_BASE}/?ident=2409_1_EG_0.102",    # MN 09 (Opening OSM)
    # Foyer / Poster / Mensa
    "Post": f"{LAGEPLAN_BASE}/?ident=5257_1_EG_0.103",   # Posterausstellung (Foyer)
    "Foyer": f"{LAGEPLAN_BASE}/?ident=5257_1_EG_0.103",  # Foyer MH / Community Sprint
    "Mensa": f"{LAGEPLAN_BASE}/?ident=5236_1_2.OG_2.140",  # Mensa
}


def main():
    repo_root = Path(__file__).resolve().parent.parent
    out_path = repo_root / "events" / "fossgis2026" / "lageplan-urls.js"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "// Generiert von scripts/generate_lageplan_mapping_fossgis2026.py – nicht von Hand bearbeiten.",
        "const lageplanUrlByRoom = {",
    ]
    for key, url in ROOM_TO_LAGEPLAN_URL.items():
        escaped = url.replace("\\", "\\\\").replace('"', '\\"')
        lines.append(f'    "{key}": "{escaped}",')
    lines.append("};")

    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Geschrieben: {out_path}")


if __name__ == "__main__":
    main()
