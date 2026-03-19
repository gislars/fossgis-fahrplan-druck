# Gemeinsame Assets (Projektroot)

Dieser Ordner enthält **projektweite** Ressourcen, die von mehreren Events oder Skripten genutzt werden können.

## Logo für QR-Codes

- **`FossgisKompassRGB_600dpi.png`** – FOSSGIS-Kompass (RGB, Raster) für die Mitte der **PNG**-QR-Codes (`generate_qr_code.py`, Pillow).
- **`FossgisKompassRGB.svg`** – dieselbe Grafik als **SVG** für vektorische QR-Ausgabe (`generate_qr_code_svg.py`, z. B. Wrapper mit `--format svg`).
- Dateien hier ablegen und bei Bedarf mit `--logo` angeben:
  ```bash
  # PNG-QR (von Projektroot):
  python scripts/generate_qr_code.py --url "https://…" --logo assets/FossgisKompassRGB_600dpi.png --out events/fossgis2025/assets/qr-….png

  # SVG-QR:
  python scripts/generate_qr_code_svg.py --url "https://…" --logo assets/FossgisKompassRGB.svg --out events/fossgis2026/assets/qr-….svg
  ```
Event-spezifische Bilder (QR-Codes, Logos pro Event) liegen weiterhin in `events/<event>/assets/`.
