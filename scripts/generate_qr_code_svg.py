#!/usr/bin/env python3
"""
QR-Code als SVG mit runden Modulen, runden Finder-Markern,
optionalem zentriertem Logo-Overlay und Caption unterhalb.

Abhängigkeit:
  pip install qrcode

Verwendung (von Projektroot):
  python scripts/generate_qr_code_svg.py --url "https://example.org" --out events/fossgis2026/assets/qr-example.svg
"""

from __future__ import annotations

import argparse
import base64
import mimetypes
import sys
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape

import qrcode
from qrcode.constants import ERROR_CORRECT_H

# Konfigurierbare Konstanten (analog zum PNG-Skript)
DEFAULT_FONT_SIZE = 14
LOGO_SIZE_FRACTION = 4  # Logo-Höhe = QR-Höhe / LOGO_SIZE_FRACTION
CAPTION_GAP_ABOVE = 0
CAPTION_GAP_BELOW = 4
CAPTION_LINE_HEIGHT_FACTOR = 1.2


def _is_in_finder_area(x: int, y: int, total_modules: int, border: int) -> bool:
    """True, wenn Modul im 7x7 Finder-Bereich eines der drei Augen liegt."""
    top_left = (border, border)
    top_right = (total_modules - border - 7, border)
    bottom_left = (border, total_modules - border - 7)

    for ox, oy in (top_left, top_right, bottom_left):
        if ox <= x < ox + 7 and oy <= y < oy + 7:
            return True
    return False


def _finder_svg(ox: int, oy: int, module_size: int, color: str, mask_id: str) -> str:
    """SVG fuer ein Finder-Auge: schwarzer Aussenring, transparenter Ring, schwarzes Zentrum."""
    cx = ox + 3.5 * module_size
    cy = oy + 3.5 * module_size
    outer_r = 3.5 * module_size
    middle_r = 2.5 * module_size
    inner_r = 1.5 * module_size
    return (
        f'<defs><mask id="{mask_id}">\n'
        f'  <rect x="{ox}" y="{oy}" width="{7 * module_size}" height="{7 * module_size}" fill="white"/>\n'
        f'  <circle cx="{cx}" cy="{cy}" r="{middle_r}" fill="black"/>\n'
        f'</mask></defs>\n'
        f'<circle cx="{cx}" cy="{cy}" r="{outer_r}" fill="{color}" mask="url(#{mask_id})"/>\n'
        f'<circle cx="{cx}" cy="{cy}" r="{inner_r}" fill="{color}"/>\n'
    )


def _encode_file_as_data_uri(path: Path) -> str:
    """Liest eine Datei und gibt sie als data: URI zurück."""
    mime, _ = mimetypes.guess_type(str(path))
    if not mime:
        mime = "application/octet-stream"
    data = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{data}"


def make_qr_svg(
    data: str,
    *,
    box_size: int = 10,
    border: int = 1,
    logo_path: str | Path | None = None,
    caption: str | None = None,
    back_color: str = "transparent",
) -> str:
    """
    Erzeugt SVG-Text für QR-Code mit runden Modulen und optionalem Overlay/Caption.

    Args:
        data: Inhalt des QR-Codes (z. B. URL).
        box_size: Pixel pro Modul.
        border: Rahmen in Modulbreiten.
        logo_path: Optionaler Pfad zum Logo (PNG oder SVG, als data URI eingebettet).
        caption: Text unter dem QR-Code.
        back_color: Hintergrundfarbe ('transparent' oder CSS-Farbe).

    Returns:
        SVG als String.
    """
    qr = qrcode.QRCode(
        error_correction=ERROR_CORRECT_H,
        box_size=box_size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)
    matrix = qr.get_matrix()

    total_modules = len(matrix)
    qr_size_px = total_modules * box_size

    caption_height = 0
    if caption:
        caption_height = (
            CAPTION_GAP_ABOVE
            + int(DEFAULT_FONT_SIZE * CAPTION_LINE_HEIGHT_FACTOR)
            + CAPTION_GAP_BELOW
        )
    total_height = qr_size_px + caption_height

    parts: list[str] = []
    parts.append('<?xml version="1.0" encoding="UTF-8"?>')
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{qr_size_px}" height="{total_height}" '
        f'viewBox="0 0 {qr_size_px} {total_height}" role="img" aria-label="QR Code">'
    )

    is_transparent_bg = back_color.strip().lower() == "transparent"
    if not is_transparent_bg:
        parts.append(
            f'<rect x="0" y="0" width="{qr_size_px}" height="{total_height}" fill="{xml_escape(back_color)}"/>'
        )

    parts.append('<g id="qr">')

    # Runde Module, Finder-Bereiche werden separat gezeichnet.
    radius = box_size / 2
    for y, row in enumerate(matrix):
        for x, is_dark in enumerate(row):
            if not is_dark:
                continue
            if _is_in_finder_area(x, y, total_modules, border):
                continue
            cx = x * box_size + radius
            cy = y * box_size + radius
            parts.append(f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="black"/>')

    # Finder-Augen zeichnen (rund mit transparentem Ring).
    finder_origins = (
        (border, border),
        (total_modules - border - 7, border),
        (border, total_modules - border - 7),
    )
    for idx, (mx, my) in enumerate(finder_origins):
        parts.append(
            _finder_svg(
                mx * box_size,
                my * box_size,
                box_size,
                "black",
                f"finder-mask-{idx}",
            )
        )

    # Optionales Logo zentriert als Overlay.
    logo_file = Path(logo_path) if logo_path else None
    if logo_file and logo_file.exists():
        logo_size = qr_size_px // LOGO_SIZE_FRACTION
        logo_x = (qr_size_px - logo_size) // 2
        logo_y = (qr_size_px - logo_size) // 2
        logo_uri = _encode_file_as_data_uri(logo_file)
        parts.append(
            f'<image x="{logo_x}" y="{logo_y}" width="{logo_size}" height="{logo_size}" '
            f'href="{logo_uri}" preserveAspectRatio="xMidYMid meet"/>'
        )

    parts.append("</g>")

    # Optional Caption unterhalb.
    if caption:
        text_y = qr_size_px + CAPTION_GAP_ABOVE + DEFAULT_FONT_SIZE
        parts.append(
            f'<text x="{qr_size_px / 2}" y="{text_y}" '
            f'font-family="DejaVu Sans, Liberation Sans, Arial, sans-serif" '
            f'font-size="{DEFAULT_FONT_SIZE}" fill="black" text-anchor="middle">{xml_escape(caption)}</text>'
        )

    parts.append("</svg>")
    return "\n".join(parts)


def main() -> int:
    p = argparse.ArgumentParser(
        description="QR-Code als SVG mit runden Modulen, optional Logo und Text."
    )
    p.add_argument("--url", required=True, help="URL oder Text fuer den QR-Code")
    p.add_argument(
        "--logo",
        default=None,
        help="Optional: Pfad zum Logo (PNG oder SVG, zentriert als data URI)",
    )
    p.add_argument(
        "--caption",
        default=None,
        help="Text unter dem QR (Standard: gleicher Inhalt wie --url)",
    )
    p.add_argument(
        "--background",
        default="transparent",
        metavar="FARBE",
        help="Hintergrundfarbe (Standard: transparent, z. B. #f0f0f0 oder white).",
    )
    p.add_argument(
        "--box-size",
        type=int,
        default=10,
        help="Pixel pro Modul (Standard: 10).",
    )
    p.add_argument(
        "--border",
        type=int,
        default=1,
        help="Rahmen in Modulbreiten (Standard: 1).",
    )
    p.add_argument(
        "--out",
        default="qr-output.svg",
        help="Pfad der Ausgabedatei (SVG)",
    )
    args = p.parse_args()

    logo_path = None
    if args.logo:
        logo_path = Path(args.logo)
        if not logo_path.is_absolute():
            logo_path = (Path.cwd() / logo_path).resolve()
        if not logo_path.exists():
            print(
                f"Warnung: Logo-Datei nicht gefunden, ohne Logo fortgesetzt: {logo_path}",
                file=sys.stderr,
            )
            logo_path = None

    caption = args.caption if args.caption is not None else args.url

    svg = make_qr_svg(
        args.url,
        box_size=max(1, args.box_size),
        border=max(0, args.border),
        logo_path=logo_path,
        caption=caption,
        back_color=args.background,
    )

    out_path = Path(args.out)
    if not out_path.is_absolute():
        out_path = (Path.cwd() / out_path).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if out_path.suffix.lower() != ".svg":
        raise SystemExit("Fehler: Das Skript erzeugt ausschließlich SVG-Ausgaben.")
    out_path.write_text(svg, encoding="utf-8")
    print(f"Gespeichert: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

