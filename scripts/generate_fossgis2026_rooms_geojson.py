#!/usr/bin/env python3
"""
Erzeugt ein GeoJSON mit den Geometrien aller Räume und Gebäude, die im Event
FOSSGIS 2026 genutzt werden. Die Geometrien werden aus dem Lageplan der
Universität Göttingen (ArcGIS Feature Service) abgerufen.

API: https://www.geodata.uni-goettingen.de/arcgis/rest/services/Lageplan_publish/Raeume_Gebaeude/FeatureServer
Layer 0 = Gebäude (Polygone), Abfrage per piz (Gebäude-ID).
Layer 2 = Räume (Polygone), Feld "ident" entspricht dem URL-Parameter ?ident=...

Verwendung (von Projektroot):
  python scripts/generate_fossgis2026_rooms_geojson.py

Ausgabe: events/fossgis2026/rooms.geojson
"""
import json
import re
import urllib.parse
import urllib.request
from pathlib import Path

# Quelle: gleiche Zuordnung wie in generate_lageplan_mapping_fossgis2026.py
LAGEPLAN_BASE = "https://lageplan.uni-goettingen.de"
ROOM_TO_LAGEPLAN_URL = {
    "HS1": f"{LAGEPLAN_BASE}/?ident=5257_1_1.OG_1.151",   # ZHG 011
    "HS2": f"{LAGEPLAN_BASE}/?ident=5257_1_1.OG_1.153",   # ZHG 010
    "HS3": f"{LAGEPLAN_BASE}/?ident=5257_1_1.OG_1.152",   # ZHG 009
    "HS4": f"{LAGEPLAN_BASE}/?ident=5257_1_1.OG_1.150",   # ZHG 008
    "BoF1": f"{LAGEPLAN_BASE}/?ident=5257_1_EG_0.161",
    "BoF2": f"{LAGEPLAN_BASE}/?ident=5257_1_EG_0.155",
    "BoF3": f"{LAGEPLAN_BASE}/?ident=5257_1_EG_0.154",
    "WS1": f"{LAGEPLAN_BASE}/?ident=5361_1_1.OG_1.104",
    "WS2": f"{LAGEPLAN_BASE}/?ident=5361_1_1.OG_1.103",
    "WS3": f"{LAGEPLAN_BASE}/?ident=5361_1_1.OG_1.102",
    "WS4": f"{LAGEPLAN_BASE}/?ident=5361_1_1.OG_1.105",
    "OSM1": f"{LAGEPLAN_BASE}/?ident=2410_1_EG_0.161",
    "OSM2": f"{LAGEPLAN_BASE}/?ident=2410_1_EG_0.162",
    "OSM3": f"{LAGEPLAN_BASE}/?ident=2410_1_EG_0.163",
    "OO": f"{LAGEPLAN_BASE}/?ident=2409_1_EG_0.102",
    "Post": f"{LAGEPLAN_BASE}/?ident=5257_1_EG_0.103",
    "Foyer": f"{LAGEPLAN_BASE}/?ident=5257_1_EG_0.103",
    "Mensa": f"{LAGEPLAN_BASE}/?ident=5236_1_2.OG_2.140",
}
# Räume mit piz/etage-URL (ohne ident): ident nur für API-Geometrieabfrage
ROOM_TO_IDENT_FOR_GEOMETRY = {}

ROOMS_LAYER_URL = (
    "https://www.geodata.uni-goettingen.de/arcgis/rest/services/"
    "Lageplan_publish/Raeume_Gebaeude/FeatureServer/2/query"
)
BUILDINGS_LAYER_URL = (
    "https://www.geodata.uni-goettingen.de/arcgis/rest/services/"
    "Lageplan_publish/Raeume_Gebaeude/FeatureServer/0/query"
)

# Etage -> Hoehe in Meter (fuer 3D-Ansicht in QGIS)
ETAGE_TO_HEIGHT_M = {"EG": 0, "1.OG": 3, "2.OG": 6}

# Gebaeude-PIZ -> schematische Hoehe in Meter (fuer 3D-Extrusion)
# 5257=ZHG, 5361=VG, 2410/2409=Geographie, 5236=Mensa
BUILDING_HEIGHT_M = {"5257": 12, "5361": 10, "2410": 10, "2409": 10, "5236": 10}


def url_ident(url: str) -> str | None:
    """Extrahiert den ident-Parameter aus einer Lageplan-URL."""
    if "ident=" not in url:
        return None
    match = re.search(r"ident=([^&\s]+)", url)
    return urllib.parse.unquote(match.group(1)) if match else None


def fetch_room_geojson(ident: str) -> dict:
    """Lädt alle Features für einen ident vom Räume-Layer (GeoJSON)."""
    params = {
        "where": f"ident = '{ident}'",
        "outFields": "*",
        "returnGeometry": "true",
        "f": "geojson",
    }
    url = ROOMS_LAYER_URL + "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=30) as resp:
        return json.load(resp)


def fetch_building_geojson(piz: str) -> dict:
    """Lädt Gebäude-Geometrie vom Gebäude-Layer (Abfrage per piz)."""
    params = {
        "where": f"piz = '{piz}'",
        "outFields": "*",
        "returnGeometry": "true",
        "f": "geojson",
    }
    url = BUILDINGS_LAYER_URL + "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=30) as resp:
        return json.load(resp)


def build_ident_to_rooms() -> dict[str, list[str]]:
    """Baut ident -> Liste aller FOSSGIS-Raumkürzel (für Geometrieabfrage)."""
    ident_to_rooms: dict[str, list[str]] = {}
    for room, url in ROOM_TO_LAGEPLAN_URL.items():
        ident = url_ident(url) or ROOM_TO_IDENT_FOR_GEOMETRY.get(room)
        if ident:
            ident_to_rooms.setdefault(ident, []).append(room)
    return ident_to_rooms


def main():
    repo_root = Path(__file__).resolve().parent.parent
    out_path = repo_root / "events" / "fossgis2026" / "rooms.geojson"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    ident_to_rooms = build_ident_to_rooms()
    all_idents = list(ident_to_rooms.keys())

    features: list[dict] = []
    for ident in all_idents:
        try:
            fc = fetch_room_geojson(ident)
        except Exception as e:
            print(f"Warnung: Abfrage für ident={ident} fehlgeschlagen: {e}")
            continue
        if not fc.get("features"):
            print(f"Warnung: Keine Geometrie für ident={ident}")
            continue
        fossgis_rooms = ident_to_rooms.get(ident, [])
        # Pro ident kann es mehrere API-Features geben (z. B. EG und 1.OG). Wir nehmen das erste.
        api_feature = fc["features"][0]
        props = api_feature.get("properties") or {}
        raumname = props.get("raumname")
        # Ein Feature pro FOSSGIS-Raum (gleiche Geometrie bei geteilten Räumen wie HS2/HS3).
        for room in fossgis_rooms:
            if len(fossgis_rooms) > 1:
                # Mehrere Räume teilen sich diesen ident → Name mit Kürzel unterscheidbar
                name = f"{room} ({raumname})" if raumname else room
            else:
                # Ein Raum: API-Name nutzen, Fallback FOSSGIS-Kürzel (z. B. bei HS4, Mensa, Foyer)
                name = raumname if raumname else room
            f = {
                "type": "Feature",
                "geometry": api_feature.get("geometry"),
                "properties": {
                    "layer": "room",
                    "name": name,
                    "ident": props.get("ident"),
                    "raumart": props.get("raumart"),
                    "raumnr": props.get("raumnr"),
                    "etage": props.get("etage"),
                    "height_m": ETAGE_TO_HEIGHT_M.get(props.get("etage"), 0),
                    "gebid": props.get("gebid"),
                    "fossgis_room": room,
                    "fossgis_event": "fossgis2026",
                },
            }
            features.append(f)

    # Gebäudegeometrien: alle in den Räumen vorkommenden gebid/piz abfragen
    building_ids = set()
    for ident in all_idents:
        # ident-Format: {piz}_1_... (z. B. 5257_1_EG_0.161)
        part = ident.split("_")[0]
        if part.isdigit():
            building_ids.add(part)
    for piz in sorted(building_ids):
        try:
            fc = fetch_building_geojson(piz)
        except Exception as e:
            print(f"Warnung: Gebäude piz={piz} fehlgeschlagen: {e}")
            continue
        if not fc.get("features"):
            print(f"Warnung: Keine Geometrie für Gebäude piz={piz}")
            continue
        api_feature = fc["features"][0]
        props = api_feature.get("properties") or {}
        features.append({
            "type": "Feature",
            "geometry": api_feature.get("geometry"),
            "properties": {
                "layer": "building",
                "name": props.get("geb_bez"),
                "piz": props.get("piz"),
                "adresse": props.get("adresse"),
                "height_m": BUILDING_HEIGHT_M.get(piz, 10),
                "fossgis_event": "fossgis2026",
            },
        })

    collection = {
        "type": "FeatureCollection",
        "features": features,
        "properties": {
            "description": "Räume und Gebäude der FOSSGIS-Konferenz 2026 (Uni Göttingen)",
            "source": "Lageplan Universität Göttingen (ArcGIS Feature Service)",
            "event": "fossgis2026",
        },
    }
    out_path.write_text(json.dumps(collection, ensure_ascii=False, indent=2), encoding="utf-8")
    n_rooms = sum(1 for f in features if f.get("properties", {}).get("layer") == "room")
    n_buildings = len(features) - n_rooms
    print(f"Geschrieben: {out_path} ({n_rooms} Räume, {n_buildings} Gebäude)")


if __name__ == "__main__":
    main()
