# Gemeinsame Assets (Projektroot)

Dieser Ordner enthält **projektweite** Ressourcen, die von mehreren Events oder Skripten genutzt werden können.

## Logo für QR-Codes

- **`FossgisKompassRGB_600dpi.png`** – FOSSGIS-Kompass-Logo (RGB, 600 dpi) für die Mitte der QR-Codes.
- Datei hier ablegen und bei Bedarf mit `--logo` angeben:
  ```bash
  # Von Projektroot (mit Logo):
  python scripts/generate_qr_code.py --url "https://…" --logo assets/FossgisKompassRGB_600dpi.png --out events/fossgis2025/assets/qr-….png
  ```
Event-spezifische Bilder (QR-Codes, Logos pro Event) liegen weiterhin in `events/<event>/assets/`.
