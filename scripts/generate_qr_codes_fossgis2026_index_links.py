#!/usr/bin/env python3
"""
Wrapper-Skript: erzeugt QR-Codes für die vier fest definierten Links (wie in index.html).

Ziel: events/<event>/assets/*.png oder *.svg (index.html nutzt .svg).
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


DEFAULT_EVENT = "fossgis2026"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Wrapper fuer QR-Codes aus events/fossgis2026/index.html Links."
    )
    p.add_argument(
        "--event",
        default=DEFAULT_EVENT,
        help=f"Event-Verzeichnisname unter events/ (Standard: {DEFAULT_EVENT})",
    )
    p.add_argument(
        "--background",
        default="transparent",
        help="Hintergrund für QR (Standard: 'transparent'; z. B. '#f0f0f0').",
    )
    p.add_argument(
        "--format",
        choices=("png", "svg"),
        default="png",
        help="Ausgabeformat: png oder svg (Standard: png).",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Nur die aufgerufenen Kommandos anzeigen, nicht ausführen.",
    )
    return p.parse_args()


def main() -> int:
    args = parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    if args.format == "svg":
        generator_script = repo_root / "scripts" / "generate_qr_code_svg.py"
    else:
        generator_script = repo_root / "scripts" / "generate_qr_code.py"
    if not generator_script.exists():
        raise SystemExit(f"Fehler: Generator-Skript nicht gefunden: {generator_script}")

    # Logo: SVG für vektorische QR-Ausgabe, PNG für Raster-PNG (PIL).
    assets_dir = repo_root / "assets"
    logo_svg = assets_dir / "FossgisKompassRGB.svg"
    logo_png = assets_dir / "FossgisKompassRGB_600dpi.png"
    if args.format == "svg":
        logo_path = logo_svg
        if not logo_path.exists():
            raise SystemExit(
                f"Fehler: SVG-Logo nicht gefunden: '{logo_path}'. "
                "Bitte FossgisKompassRGB.svg unter assets/ ablegen."
            )
    else:
        logo_path = logo_png
        if not logo_path.exists():
            raise SystemExit(
                f"Fehler: PNG-Logo nicht gefunden: '{logo_path}'. "
                "Bitte FossgisKompassRGB_600dpi.png unter assets/ ablegen."
            )

    out_dir = repo_root / "events" / args.event / "assets"
    out_dir.mkdir(parents=True, exist_ok=True)

    # URL -> Basis-Dateiname (ohne Dateiendung).
    items: list[tuple[str, str]] = [
        ("https://www.bahnhof.de/goettingen/abfahrt", "qr-bahnhof_de"),
        ("https://pretalx.com/fossgis2026/schedule/", "qr-fahrplan_pretalx_2026"),
        (
            "https://gislars.github.io/fossgis-fahrplan-druck/events/fossgis2026/",
            "qr-fahrplan_druck_online_2026",
        ),
        ("https://mastodon.online/@FOSSGISeV", "qr-fossgis-mastodon"),
    ]

    for url, out_basename in items:
        out_path = out_dir / f"{out_basename}.{args.format}"

        # Vor dem Generieren vorhandene Datei entfernen, damit garantiert überschrieben wird.
        if not args.dry_run:
            out_path.unlink(missing_ok=True)

        cmd = [
            sys.executable,
            str(generator_script),
            "--url",
            url,
            "--out",
            str(out_path),
        ]
        cmd += ["--background", args.background]
        cmd += ["--logo", str(logo_path)]

        if args.dry_run:
            print("DRY-RUN:", " ".join(cmd))
            continue

        # Generator-Skript gibt ebenfalls "Gespeichert: ..." aus.
        # Daher unterdrücken wir dessen stdout, damit der Wrapper nur einmal loggt.
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL)
        print(f"Gespeichert: {out_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

