#!/usr/bin/env python3
"""Put Swedish labels on the realistic snowmobile illustrations."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

SRC = Path("/Users/wille/.cursor/projects/Users-wille-daniel-bok-Willes-uppdrag/assets")
DST = Path(__file__).resolve().parents[1] / "assets"

PINE = (20, 53, 42)
WHITE = (255, 255, 255)
COPPER = (196, 92, 38)
INK = (28, 28, 25)
MUTED = (92, 103, 95)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    path = (
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
        if bold
        else "/System/Library/Fonts/Supplemental/Arial.ttf"
    )
    return ImageFont.truetype(path, size)


def banner(img: Image.Image, title: str) -> Image.Image:
    out = img.convert("RGB")
    d = ImageDraw.Draw(out)
    d.rectangle((0, 0, out.width, 56), fill=PINE)
    d.text((22, 14), title, fill=WHITE, font=font(24, True))
    return out


def caption(d: ImageDraw.ImageDraw, x: int, y: int, text: str, color=PINE) -> None:
    d.text((x, y), text, fill=color, font=font(20, True))


def save(img: Image.Image, name: str) -> None:
    DST.mkdir(exist_ok=True)
    img.save(DST / name, "PNG", optimize=True)
    print("wrote", name, img.size)


def labeled_row(src: str, dest: str, title: str, labels: list[tuple[int, str]]) -> None:
    img = banner(Image.open(SRC / src), title)
    d = ImageDraw.Draw(img)
    for x, text in labels:
        caption(d, x, img.height - 48, text)
    save(img, dest)


def _callouts(img: Image.Image, labels: list[tuple[tuple[int, int], tuple[int, int], str]]) -> None:
    d = ImageDraw.Draw(img)
    for (ax, ay), (tx, ty), name in labels:
        d.line((ax, ay, tx, ty + 22), fill=COPPER, width=2)
        d.ellipse((ax - 4, ay - 4, ax + 4, ay + 4), fill=COPPER)
        d.text((tx, ty), name, fill=PINE, font=font(22, True))


def parts() -> None:
    img = banner(Image.open(SRC / "skoter-sida.png"), "Snöskoterns delar")
    _callouts(
        img,
        [
            ((180, 500), (40, 80), "Skida"),
            ((430, 175), (430, 70), "Styre"),
            ((340, 290), (200, 80), "Huv"),
            ((640, 215), (640, 70), "Säte"),
            ((980, 270), (1080, 90), "Tunnel"),
            ((880, 500), (880, 640), "Drivmatta"),
            ((1145, 300), (1180, 140), "Baklyse"),
        ],
    )
    save(img, "skoterns-delar.png")


def reglage() -> None:
    img = banner(Image.open(SRC / "skoter-reglage-raw.png"), "Reglage på styret")
    _callouts(
        img,
        [
            ((355, 268), (40, 70), "Broms — vänster"),
            ((448, 418), (40, 180), "Nödstopp"),
            ((1008, 288), (1020, 70), "Gas — höger"),
        ],
    )
    save(img, "skoter-reglage.png")


def motor() -> None:
    img = banner(Image.open(SRC / "skoter-motor-raw.png"), "Under huven")
    _callouts(
        img,
        [
            ((500, 90), (900, 70), "Huv"),
            ((560, 400), (40, 360), "Motor"),
        ],
    )
    save(img, "skoter-motor.png")


def main() -> None:
    # Keep one authoritative build path so this legacy labelling command cannot
    # restore old captions or unsafe instructions.
    from bygg_bilder import main as build_all

    build_all()


if __name__ == "__main__":
    main()
