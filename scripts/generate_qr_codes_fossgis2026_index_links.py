#!/usr/bin/env python3
"""
Wrapper-Skript: erzeugt QR-Codes fuer die Links aus events/fossgis2026/index.html.

Quelle: index.html Ausschnitt (Zeilen 677-692) mit 4 URLs.
Ziel: events/fossgis2026/assets/*.png
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
        help="Hintergrund fuer QR (Standard: 'transparent'; z. B. '#f0f0f0').",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Nur die aufgerufenen Kommandos anzeigen, nicht ausfuehren.",
    )
    return p.parse_args()


def main() -> int:
    args = parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    generator_script = repo_root / "scripts" / "generate_qr_code.py"
    if not generator_script.exists():
        raise SystemExit(f"Fehler: Generator-Skript nicht gefunden: {generator_script}")

    # Logo liegt im top-level assets-Verzeichnis.
    logo_path = repo_root / "assets" / "FossgisKompassRGB_600dpi.png"
    if not logo_path.exists():
        raise SystemExit(
            f"Fehler: Logo-Datei nicht gefunden: '{logo_path}'. "
            "Bitte Datei nach 'assets/' verschieben."
        )

    out_dir = repo_root / "events" / args.event / "assets"
    out_dir.mkdir(parents=True, exist_ok=True)

    # URL -> Ausgabedatei (passend zu den vorhandenen <img src="..."> Eintraegen)
    items: list[tuple[str, str]] = [
        ("https://www.bahnhof.de/goettingen/abfahrt", "qr-bahnhof_de.png"),
        ("https://pretalx.com/fossgis2026/schedule/", "qr-fahrplan_pretalx_2026.png"),
        (
            "https://gislars.github.io/fossgis-fahrplan-druck/events/fossgis2026/",
            "qr-fahrplan_druck_online_2026.png",
        ),
        ("https://mastodon.online/@FOSSGISeV", "qr-fossgis-mastodon.png"),
    ]

    for url, out_name in items:
        out_path = out_dir / out_name

        # Vor dem Generieren vorhandene Datei entfernen, damit garantiert ueberschrieben wird.
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
        # Daher unterdruecken wir dessen stdout, damit der Wrapper nur einmal loggt.
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL)
        print(f"Gespeichert: {out_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

