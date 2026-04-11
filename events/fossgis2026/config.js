/**
 * FOSSGIS 2026: event-spezifische Konfiguration (Track-Kürzel, Pretalx-URL,
 * Zeitfenster für die Darstellung, Pausen-Texte, Akzent-Räume, Livestreams).
 * Wird von index.html vor dem Hauptskript geladen.
 */
window.FossgisFahrplanEventConfig = {
  scheduleUrl:
    "https://pretalx.com/fossgis2026/schedule/export/schedule.json",

  trackMap: {
    "Grundlagen Open-Source-GIS und OpenStreetMap": "OSG",
    "Neuigkeiten und Interessantes aus den Open-Source-Projekten": "NEW",
    OpenStreetMap: "OSM",
    Praxisberichte: "PRA",
    "Daten, Datenbanken und Datenprozessierung": "DDD",
    "Routing und Mobilität": "RUM",
    "Raum-zeitliche Analysen und Modelle": "RZM",
    "Rasterdaten und Fernerkundung": "RAS",
    "3D, Drohnen, LIDAR, Geo-AR/VR": "3D",
    "Kartographie und Visualisierung": "KUV",
    "Offene Standards, z.B. INSPIRE, OGC": "STA",
    Geodatenmanagement: "GDM",
    "Open Data, Datenschutz und Lizenzen": "LIZ",
    "Ausbildung, Lehre, Open Science": "EDU",
    null: "NAT",
    undefined: "NAT",
  },

  timeRanges: [
    { start: 9, end: 11, label: "9.00 — 11.00" },
    { start: 12, end: 13, label: "12.00 — 13.00" },
    { start: 14, end: 15, label: "14.00 — 15.00" },
    { start: 16, end: 18, label: "16.00 — 18.00" },
    { start: 19, end: 20, label: "19.00 — 20.00" },
  ],

  breakRoomName: "Alle Räume",
  breakPrefix: "PAU",
  breakTitlePrefix: "Betriebsunterbrechung wegen",

  redRoomsList: ["HS1", "HS2", "HS3", "HS4"],

  streamingUrlByRoom: {
    HS1: "https://streaming.media.ccc.de/fossgis2026/hs1",
    HS2: "https://streaming.media.ccc.de/fossgis2026/hs2",
    HS3: "https://streaming.media.ccc.de/fossgis2026/hs3",
    HS4: "https://streaming.media.ccc.de/fossgis2026/hs4",
    BoF1: "",
    BoF2: "",
    BoF3: "",
    WS1: "",
    WS2: "",
    WS3: "",
    WS4: "",
    OSM1: "",
    OSM2: "",
    OSM3: "",
    OO: "",
    Post: "",
  },
};
