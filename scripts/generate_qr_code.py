#!/usr/bin/env python3
"""
QR-Code mit runden Modulen, optionalem Logo in der Mitte und Text unter dem Code.
Projektweites Skript für FOSSGIS-Fahrplan-QR-Codes.

Abhängigkeit: pip install "qrcode[pil]" Pillow

Verwendung (von Projektroot):
  python scripts/generate_qr_code.py --url "https://mastodon.online/@FOSSGISeV" --out events/fossgis2026/assets/qr-fossgis-mastodon.png
  python scripts/generate_qr_code.py --url "https://gislars.github.io/fossgis-fahrplan-druck/events/fossgis2025/" --logo assets/FossgisKompassRGB_600dpi.png --out events/fossgis2025/assets/qr-fahrplan_druck_online_2025.png
  python scripts/generate_qr_code.py --url "https://pretalx.com/fossgis2025/schedule/" --logo assets/FossgisKompassRGB_600dpi.png --out events/fossgis2025/assets/qr-fahrplan_pretalx_2025.png
"""
import argparse
import sys
from pathlib import Path

import qrcode
from qrcode.constants import ERROR_CORRECT_H
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.colormasks import SolidFillColorMask
from qrcode.image.styles.moduledrawers.pil import CircleModuleDrawer, SquareModuleDrawer

try:
    from PIL import Image, ImageDraw, ImageFont, ImageColor
except ImportError:
    raise SystemExit("Bitte installieren: pip install 'qrcode[pil]' Pillow")

# Konfigurierbare Konstanten (PEP 8: UPPER_CASE für Modul-Konstanten)
DEFAULT_FONT_SIZE = 14
LOGO_SIZE_FRACTION = 4  # Logo-Höhe = Bildhöhe / LOGO_SIZE_FRACTION
CAPTION_GAP_ABOVE = 0
CAPTION_GAP_BELOW = 4
CAPTION_LINE_HEIGHT_FACTOR = 1.2

# Typische System-Font-Pfade (erster existierender wird genutzt)
FONT_SEARCH_PATHS = (
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/System/Library/Fonts/Helvetica.ttc",  # macOS
)


def _get_caption_font(size: int = DEFAULT_FONT_SIZE):
    """Lädt eine verfügbare TrueType-Schrift oder nutzt die Standard-Schrift als Fallback."""
    for path in FONT_SEARCH_PATHS:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
    return ImageFont.load_default()


def make_qr(
    data: str,
    *,
    box_size: int = 10,
    border: int = 1,
    logo_path: str | Path | None = None,
    caption: str | None = None,
    back_color: str = "white",
) -> Image.Image:
    """
    Erzeugt ein QR-Code-Bild mit runden Modulen, optionalem Logo und Beschriftung.

    Args:
        data: Inhalt des QR-Codes (z. B. URL).
        box_size: Pixel pro Modul.
        border: Rahmen in Modulbreiten.
        logo_path: Pfad zum Logo-Bild (zentriert eingeblendet).
        caption: Text unter dem QR-Code.
        back_color: Hintergrundfarbe (Name oder Hex, z. B. 'white' oder '#f0f0f0') oder
            'transparent' (PNG mit Alpha).

    Returns:
        PIL Image im RGBA-Modus (PNG-kompatibel).
    """
    is_transparent_bg = back_color.strip().lower() == "transparent"
    # Wir rendern den Hintergrund zunächst in einer Magic-Farbe und machen sie danach transparent.
    # So beeinflussen wir keine Logo-Pixel, die ggf. auch weiß sind.
    magic_back_rgb = (1, 2, 3)

    qr = qrcode.QRCode(
        error_correction=ERROR_CORRECT_H,
        box_size=box_size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)

    rgb_back: tuple[int, int, int] | None
    if is_transparent_bg:
        rgb_back = None
        back_rgb_for_mask = magic_back_rgb
    else:
        rgb_back = ImageColor.getrgb(back_color)
        back_rgb_for_mask = rgb_back

    color_mask = SolidFillColorMask(back_color=back_rgb_for_mask, front_color=(0, 0, 0))

    img = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=CircleModuleDrawer(),
        eye_drawer=SquareModuleDrawer(),
        color_mask=color_mask,
    )
    if hasattr(img, "_img"):
        img = img._img
    img = img.convert("RGBA")

    if is_transparent_bg:
        # Hintergrund-Magic-Farbe auf Alpha 0 setzen.
        px = img.load()
        w, h = img.size
        for y in range(h):
            for x in range(w):
                r, g, b, a = px[x, y]
                if (r, g, b) == magic_back_rgb:
                    px[x, y] = (r, g, b, 0)

    logo_path = Path(logo_path) if logo_path else None
    if logo_path and logo_path.exists():
        logo = Image.open(logo_path).convert("RGBA")
        size = img.height // LOGO_SIZE_FRACTION
        logo.thumbnail((size, size), Image.Resampling.LANCZOS)
        x = (img.width - logo.size[0]) // 2
        y = (img.height - logo.size[1]) // 2
        img.paste(logo, (x, y), logo)

    if caption:
        font = _get_caption_font(DEFAULT_FONT_SIZE)
        font_size = DEFAULT_FONT_SIZE
        pad = (
            CAPTION_GAP_ABOVE
            + int(font_size * CAPTION_LINE_HEIGHT_FACTOR)
            + CAPTION_GAP_BELOW
        )
        new_h = img.height + pad
        if is_transparent_bg:
            out = Image.new("RGBA", (img.width, new_h), (0, 0, 0, 0))
        else:
            assert rgb_back is not None
            out = Image.new("RGBA", (img.width, new_h), (*rgb_back, 255))
        out.paste(img, (0, 0))
        draw = ImageDraw.Draw(out)
        text_y = img.height + CAPTION_GAP_ABOVE
        draw.text(
            (img.width // 2, text_y),
            caption,
            fill=(0, 0, 0, 255),
            font=font,
            anchor="mt",
        )
        return out
    return img


def main() -> int:
    """
    Kommandozeilen-Aufruf: Liest die Optionen, erzeugt den QR-Code und speichert die PNG-Datei.

    Returns:
        0 bei Erfolg (bei Fehlern wird eine Exception ausgelöst).
    """
    p = argparse.ArgumentParser(
        description="QR-Code mit runden Modulen, optional Logo und Text (FOSSGIS-Fahrplan)."
    )
    p.add_argument("--url", required=True, help="URL oder Text für den QR-Code")
    p.add_argument(
        "--logo",
        default=None,
        help="Optional: Pfad zum Logo-Bild (wird zentriert in den QR-Code eingeblendet)",
    )
    p.add_argument(
        "--caption",
        default=None,
        help="Text unter dem QR (Standard: gleicher Inhalt wie --url)",
    )
    p.add_argument(
        "--background",
        default="white",
        metavar="FARBE",
        help="Hintergrundfarbe des QR-Codes (Standard: white, z. B. #f0f0f0) oder 'transparent'",
    )
    p.add_argument(
        "--out",
        default="qr-output.png",
        help="Pfad der Ausgabedatei (PNG)",
    )
    args = p.parse_args()

    logo_path = None
    if args.logo:
        logo_path = Path(args.logo)
        if not logo_path.is_absolute():
            logo_path = (Path.cwd() / logo_path).resolve()
        if not logo_path.exists():
            logo_path = None

    caption = args.caption if args.caption is not None else args.url

    img = make_qr(
        args.url,
        logo_path=logo_path,
        caption=caption,
        back_color=args.background,
    )
    out_path = Path(args.out)
    if not out_path.is_absolute():
        out_path = (Path.cwd() / out_path).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if out_path.suffix.lower() != ".png":
        raise SystemExit("Fehler: Das Skript erzeugt ausschließlich PNG-Ausgaben.")
    img.save(out_path, format="PNG")
    print(f"Gespeichert: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
