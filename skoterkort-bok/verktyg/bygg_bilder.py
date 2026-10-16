#!/usr/bin/env python3
"""Build book images: official Swedish signs plus original diagrams."""

from __future__ import annotations

import json
import math
import ssl
import urllib.parse
import urllib.request
from io import BytesIO
from pathlib import Path

SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
UA = "InstruktorsverketSkoterbok/1.0 (educational course book)"

PINE = (20, 53, 42)
MOSS = (45, 106, 79)
GOLD = (201, 162, 39)
INK = (28, 28, 25)
PAPER = (247, 244, 238)
CREAM = (255, 253, 248)
MUTED = (92, 103, 95)
COPPER = (196, 92, 38)
ICE = (231, 242, 236)
RED = (196, 32, 38)
BLUE = (0, 90, 160)
WHITE = (255, 255, 255)
BLACK = (18, 18, 18)

COMMONS = {
    "d9": "Sweden road sign D9.svg",
    "c13": "Sweden road sign C13.svg",
    "c15": "Sweden road sign C15.svg",
    "a1": "Sweden road sign A1-1.svg",
    "b1": "Sweden road sign B1.svg",
    "b2": "Sweden road sign B2.svg",
    "e19": "Sweden road sign E19.svg",
    "a22": "Sweden road sign A22.svg",
}


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/Library/Fonts/Arial.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def canvas(w: int, h: int, color=PAPER) -> Image.Image:
    return Image.new("RGBA", (w, h), color + ((255,) if len(color) == 3 else ()))


def rounded(draw: ImageDraw.ImageDraw, box, fill, radius=18, outline=None, width=2):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def save(img: Image.Image, name: str) -> Path:
    ASSETS.mkdir(exist_ok=True)
    path = ASSETS / name
    if img.mode == "RGBA":
        bg = Image.new("RGB", img.size, WHITE)
        bg.paste(img, mask=img.split()[3])
        out = bg
    else:
        out = img.convert("RGB")
    out.save(path, "PNG", optimize=True)
    return path


def commons_png(title: str, width: int = 1000) -> Image.Image | None:
    api = (
        "https://commons.wikimedia.org/w/api.php"
        f"?action=query&format=json&prop=imageinfo&iiprop=url|mime"
        f"&iiurlwidth={width}&titles=File:{urllib.parse.quote(title)}"
    )
    req = urllib.request.Request(api, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=30, context=SSL_CTX) as res:
            data = json.load(res)
        pages = data["query"]["pages"]
        info = next(iter(pages.values()))["imageinfo"][0]
        url = info.get("thumburl") or info["url"]
        req2 = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req2, timeout=30, context=SSL_CTX) as res:
            return Image.open(BytesIO(res.read())).convert("RGBA")
    except Exception as exc:
        print(f"skip {title}: {exc}")
        return None


def fit_square(img: Image.Image, size: int, pad: int = 8) -> Image.Image:
    inner = size - pad * 2
    fitted = ImageOps.contain(img, (inner, inner))
    out = Image.new("RGBA", (size, size), (255, 255, 255, 255))
    x = (size - fitted.width) // 2
    y = (size - fitted.height) // 2
    out.alpha_composite(fitted, (x, y))
    return out


def white_outside_circle(img: Image.Image) -> Image.Image:
    out = img.convert("RGBA")
    w, h = out.size
    cx, cy = w / 2, h / 2
    r = min(w, h) / 2 - 4
    px = out.load()
    rr = r * r
    for y in range(h):
        for x in range(w):
            if (x - cx) ** 2 + (y - cy) ** 2 > rr:
                px[x, y] = (255, 255, 255, 255)
    return out


def yield_sign(size: int = 500) -> Image.Image:
    img = Image.new("RGBA", (size, size), (255, 255, 255, 255))
    d = ImageDraw.Draw(img)
    d.polygon([(size / 2, size - 8), (8, 18), (size - 8, 18)], fill=RED)
    d.polygon([(size / 2, size - 52), (52, 48), (size - 52, 48)], fill=WHITE)
    return img


def snowmobile_mask(size: int = 620) -> Image.Image:
    """Simple official-style snowmobile pictogram if TS files cannot be fetched."""
    img = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(img)
    s = size / 620
    d.polygon(
        [
            (int(70 * s), int(340 * s)),
            (int(170 * s), int(340 * s)),
            (int(210 * s), int(300 * s)),
            (int(430 * s), int(300 * s)),
            (int(470 * s), int(250 * s)),
            (int(560 * s), int(250 * s)),
            (int(580 * s), int(280 * s)),
            (int(540 * s), int(330 * s)),
            (int(560 * s), int(370 * s)),
            (int(120 * s), int(370 * s)),
        ],
        fill=255,
    )
    d.ellipse((int(80 * s), int(350 * s), int(200 * s), int(390 * s)), fill=255)
    d.rounded_rectangle((int(220 * s), int(355 * s), int(560 * s), int(430 * s)), int(24 * s), fill=255)
    for x in range(int(250 * s), int(540 * s), int(28 * s)):
        d.rectangle((x, int(430 * s), x + int(10 * s), int(470 * s)), fill=255)
    d.polygon(
        [
            (int(250 * s), int(250 * s)),
            (int(310 * s), int(160 * s)),
            (int(390 * s), int(160 * s)),
            (int(420 * s), int(250 * s)),
        ],
        fill=255,
    )
    d.ellipse((int(330 * s), int(175 * s), int(370 * s), int(215 * s)), fill=255)
    return img


def walker_mask(size: int = 420) -> Image.Image:
    img = Image.new("L", (size, int(size * 1.5)), 0)
    d = ImageDraw.Draw(img)
    s = size / 200
    d.ellipse((int(78 * s), int(4 * s), int(122 * s), int(48 * s)), fill=255)
    d.polygon(
        [
            (int(88 * s), int(48 * s)),
            (int(112 * s), int(48 * s)),
            (int(118 * s), int(130 * s)),
            (int(82 * s), int(130 * s)),
        ],
        fill=255,
    )
    d.polygon(
        [
            (int(88 * s), int(55 * s)),
            (int(40 * s), int(118 * s)),
            (int(58 * s), int(128 * s)),
            (int(100 * s), int(78 * s)),
        ],
        fill=255,
    )
    d.polygon(
        [
            (int(110 * s), int(55 * s)),
            (int(158 * s), int(100 * s)),
            (int(142 * s), int(112 * s)),
            (int(108 * s), int(78 * s)),
        ],
        fill=255,
    )
    d.polygon(
        [
            (int(82 * s), int(125 * s)),
            (int(108 * s), int(125 * s)),
            (int(70 * s), int(230 * s)),
            (int(48 * s), int(222 * s)),
        ],
        fill=255,
    )
    d.polygon(
        [
            (int(100 * s), int(125 * s)),
            (int(118 * s), int(125 * s)),
            (int(155 * s), int(228 * s)),
            (int(132 * s), int(236 * s)),
        ],
        fill=255,
    )
    return img


def skier_mask(size: int = 420) -> Image.Image:
    img = Image.new("L", (size, int(size * 1.5)), 0)
    d = ImageDraw.Draw(img)
    s = size / 220
    d.ellipse((int(108 * s), int(8 * s), int(150 * s), int(50 * s)), fill=255)
    d.polygon(
        [
            (int(118 * s), int(48 * s)),
            (int(148 * s), int(52 * s)),
            (int(100 * s), int(140 * s)),
            (int(78 * s), int(132 * s)),
        ],
        fill=255,
    )
    d.line((int(145 * s), int(60 * s), int(195 * s), int(42 * s)), fill=255, width=int(16 * s))
    d.polygon(
        [
            (int(78 * s), int(128 * s)),
            (int(108 * s), int(132 * s)),
            (int(48 * s), int(200 * s)),
            (int(28 * s), int(188 * s)),
        ],
        fill=255,
    )
    d.polygon(
        [
            (int(95 * s), int(128 * s)),
            (int(118 * s), int(122 * s)),
            (int(168 * s), int(188 * s)),
            (int(148 * s), int(200 * s)),
        ],
        fill=255,
    )
    d.line((int(18 * s), int(208 * s), int(210 * s), int(248 * s)), fill=255, width=int(18 * s))
    d.line((int(8 * s), int(168 * s), int(70 * s), int(268 * s)), fill=255, width=int(10 * s))
    return img


def symbol_mask(img: Image.Image, mode: str) -> Image.Image:
    """Keep the pictogram, drop the plate."""
    rgba = img.convert("RGBA")
    px = rgba.load()
    w, h = rgba.size
    out = Image.new("L", (w, h), 0)
    op = out.load()
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a < 20:
                continue
            if mode == "white_on_blue":
                if r > 210 and g > 210 and b > 210:
                    op[x, y] = 255
            elif mode == "dark":
                if r < 90 and g < 90 and b < 90:
                    op[x, y] = 255
    if mode == "white_on_blue":
        cx, cy = (w - 1) / 2, (h - 1) / 2
        max_r2 = (min(w, h) * 0.34) ** 2
        for y in range(h):
            for x in range(w):
                if (x - cx) ** 2 + (y - cy) ** 2 > max_r2:
                    op[x, y] = 0
    bbox = out.getbbox()
    if not bbox:
        return out
    return out.crop(bbox)


def tint(mask: Image.Image, color: tuple[int, int, int], size: tuple[int, int]) -> Image.Image:
    m = ImageOps.contain(mask, size)
    layer = Image.new("RGBA", m.size, color + (0,))
    layer.putalpha(m)
    return layer


def paste_center(base: Image.Image, layer: Image.Image, box=None) -> None:
    if box is None:
        x = (base.width - layer.width) // 2
        y = (base.height - layer.height) // 2
    else:
        x = box[0] + (box[2] - box[0] - layer.width) // 2
        y = box[1] + (box[3] - box[1] - layer.height) // 2
    base.alpha_composite(layer, (x, y))


def round_plate(size: int, fill, ring, ring_w: int) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse((2, 2, size - 3, size - 3), fill=ring)
    inset = ring_w
    d.ellipse((inset, inset, size - inset - 1, size - inset - 1), fill=fill)
    return img


def square_plate(size: int, fill, border, border_w: int = 18) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((2, 2, size - 3, size - 3), 8, fill=border)
    d.rounded_rectangle(
        (border_w, border_w, size - border_w - 1, size - border_w - 1),
        4,
        fill=fill,
    )
    return img


def captioned_row(images: list[Image.Image], labels: list[str], w=1400, h=420) -> Image.Image:
    img = canvas(w, h, PAPER)
    d = ImageDraw.Draw(img)
    n = len(images)
    slot = w // n
    for i, (im, lab) in enumerate(zip(images, labels)):
        im = ImageOps.contain(im.convert("RGBA"), (slot - 40, 260))
        x = i * slot + (slot - im.width) // 2
        y = 30
        img.alpha_composite(im, (x, y))
        bbox = d.textbbox((0, 0), lab, font=font(22, True))
        tw = bbox[2] - bbox[0]
        d.text((i * slot + (slot - tw) // 2, 320), lab, fill=PINE, font=font(22, True))
    return img


def draw_skoter(d: ImageDraw.ImageDraw, x, y, scale=1.0, color=PINE, long=False, tall=False):
    s = scale
    body_w = int((150 if long else 120) * s)
    body_h = int(28 * s)
    ski_y = y + int(38 * s)
    d.ellipse((x, ski_y, x + int(46 * s), ski_y + int(10 * s)), fill=MUTED)
    d.rectangle((x + int(28 * s), y + int(8 * s), x + int(28 * s) + body_w, y + int(8 * s) + body_h), fill=color)
    d.polygon(
        [
            (x + int(40 * s), y + int(8 * s)),
            (x + int(68 * s), y - int(10 * s)),
            (x + int(88 * s), y - int(10 * s)),
            (x + int(96 * s), y + int(8 * s)),
        ],
        fill=color,
    )
    track_h = int((22 if not tall else 32) * s)
    d.rounded_rectangle(
        (x + int(70 * s), y + int(28 * s), x + int(28 * s) + body_w, y + int(28 * s) + track_h),
        8,
        fill=INK,
    )
    lug = int((6 if not tall else 10) * s)
    tx0 = x + int(78 * s)
    tx1 = x + int(20 * s) + body_w
    for i in range(tx0, tx1, int(10 * s)):
        d.line((i, y + int(28 * s), i, y + int(28 * s) + track_h), fill=GOLD, width=max(2, int(2 * s)))


def draw_skoter_profile(
    d: ImageDraw.ImageDraw,
    left: int,
    ground: int,
    *,
    body_len: float = 1.0,
    track_len: float = 1.0,
    lug_ht: float = 0.45,
    ski_gap: float = 1.0,
    windshield: float = 0.7,
    dual_seat: bool = False,
    cargo: bool = False,
    body_color=MOSS,
    accent=PINE,
) -> tuple[int, int]:
    """Side-profile silhouette in a consistent illustration style (SNOFED-like)."""
    ski_w, ski_h = 34, 7
    body_w = int(88 * body_len)
    body_h = 22
    track_w = int(96 * track_len)
    track_body_h = 14
    lug_px = max(4, int(14 * lug_ht))
    gap = int(18 * ski_gap)
    screen_h = int(26 * windshield)

    ski_y = ground - ski_h
    d.rounded_rectangle((left, ski_y, left + ski_w, ground), 3, fill=MUTED)
    d.rounded_rectangle((left + gap, ski_y + 1, left + gap + ski_w, ground), 3, fill=MUTED)

    body_x = left + gap // 2 + 8
    body_y = ground - body_h - ski_h - 2
    d.rounded_rectangle((body_x, body_y, body_x + body_w, body_y + body_h), 6, fill=body_color)

    if screen_h > 6:
        d.polygon(
            [
                (body_x + 8, body_y),
                (body_x + 24, body_y - screen_h),
                (body_x + body_w - 18, body_y - int(screen_h * 0.75)),
                (body_x + body_w - 8, body_y),
            ],
            fill=accent,
        )

    seat_w = 34 if dual_seat else 24
    seat_x = body_x + body_w // 2 - 4
    d.rounded_rectangle((seat_x, body_y - 8, seat_x + seat_w, body_y + 2), 4, fill=INK)
    if dual_seat:
        d.rounded_rectangle((seat_x + seat_w - 6, body_y - 18, seat_x + seat_w + 8, body_y - 2), 3, fill=INK)

    track_x = body_x + body_w - 18
    track_top = body_y + body_h - 6
    d.rounded_rectangle((track_x, track_top, track_x + track_w, track_top + track_body_h), 5, fill=INK)
    lug_y = track_top + track_body_h
    step = max(7, track_w // 12)
    for i in range(track_x + 4, track_x + track_w - 2, step):
        d.polygon(
            [(i, lug_y), (i + 3, lug_y + lug_px), (i + 6, lug_y)],
            fill=GOLD,
        )

    if cargo:
        rack_x = track_x + track_w - 8
        d.rectangle((rack_x, body_y - 14, rack_x + 18, body_y - 2), fill=COPPER)
        d.line((rack_x + 4, body_y - 14, rack_x + 4, body_y - 22), fill=COPPER, width=2)
        d.line((rack_x + 14, body_y - 14, rack_x + 14, body_y - 22), fill=COPPER, width=2)

    handle_x = body_x + body_w - 28
    d.line((handle_x, body_y - 4, handle_x + 16, body_y - 18), fill=INK, width=3)
    d.line((handle_x + 16, body_y - 18, handle_x + 28, body_y - 12), fill=INK, width=3)

    right = track_x + track_w
    d.line((left, ground, right + 6, ground), fill=MUTED, width=1)
    return left, right


def measure_arrow(d: ImageDraw.ImageDraw, x1: int, x2: int, y: int, label: str) -> None:
    d.line((x1, y, x2, y), fill=COPPER, width=2)
    d.polygon([(x1, y), (x1 + 7, y - 4), (x1 + 7, y + 4)], fill=COPPER)
    d.polygon([(x2, y), (x2 - 7, y - 4), (x2 - 7, y + 4)], fill=COPPER)
    tw = d.textlength(label, font=font(14))
    d.text((x1 + (x2 - x1 - tw) / 2, y + 6), label, fill=MUTED, font=font(14))


def build_skotertyper() -> Image.Image:
    """Five side-profile silhouettes — same style, different geometry."""
    w, h = 1600, 780
    img = canvas(w, h, CREAM)
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, w, 52), fill=PINE)
    d.text((20, 12), "Skotertyper — matta, kamhöjd och spårvidd", fill=WHITE, font=font(26, True))

    types = [
        ("Touring", dict(body_len=1.05, track_len=1.0, lug_ht=0.42, ski_gap=1.0, windshield=0.95, dual_seat=True),
         ["Tvåsits · vindruta", "Medellång matta"]),
        ("Sport", dict(body_len=0.88, track_len=0.82, lug_ht=0.32, ski_gap=0.92, windshield=0.35, dual_seat=False),
         ["Kort matta · låg kam", "Lätt och smidig"]),
        ("Mountain", dict(body_len=0.92, track_len=1.38, lug_ht=0.92, ski_gap=0.72, windshield=0.3, dual_seat=False),
         ["Lång matta · hög kam", "Smal spårvidd"]),
        ("Crossover", dict(body_len=1.0, track_len=1.12, lug_ht=0.58, ski_gap=0.9, windshield=0.55, dual_seat=False),
         ["Mellanlång matta", "Led och lös snö"]),
        ("Arbete", dict(body_len=1.08, track_len=1.22, lug_ht=0.48, ski_gap=1.12, windshield=0.45, dual_seat=False, cargo=True),
         ["Bred matta · låg växel", "Drag och last"]),
    ]

    cols = len(types)
    gap = 16
    cell_w = (w - gap * (cols + 1)) // cols
    ground = 430

    for i, (name, params, traits) in enumerate(types):
        x0 = gap + i * (cell_w + gap)
        rounded(d, (x0, 64, x0 + cell_w, h - 24), ICE, radius=8, outline=(215, 228, 220), width=1)
        left = x0 + 24
        draw_skoter_profile(d, left, ground, body_color=MOSS if i != 2 else PINE, accent=PINE, **params)
        label_center = x0 + cell_w // 2
        tw = d.textlength(name, font=font(22, True))
        d.text((label_center - tw / 2, ground + 18), name, fill=PINE, font=font(22, True))
        for j, line in enumerate(traits):
            lw = d.textlength(line, font=font(16))
            d.text((label_center - lw / 2, ground + 48 + j * 22), line, fill=MUTED, font=font(16))

    hint = "Jämför mattans längd, kammarnas höjd och avståndet mellan skidorna."
    hw = d.textlength(hint, font=font(15))
    d.text(((w - hw) / 2, h - 18), hint, fill=MUTED, font=font(15))
    return img.convert("RGB")


def person(d, x, y, scale=1.0, color=INK, kneeling=False, standing=False):
    s = scale
    head_r = int(8 * s)
    d.ellipse((x, y, x + head_r * 2, y + head_r * 2), fill=color)
    body_top = y + head_r * 2
    if kneeling:
        d.line((x + head_r, body_top, x + head_r, body_top + int(18 * s)), fill=color, width=max(3, int(3 * s)))
        d.line((x + head_r, body_top + int(18 * s), x + int(22 * s), body_top + int(18 * s)), fill=color, width=max(3, int(3 * s)))
        d.line((x + int(22 * s), body_top + int(18 * s), x + int(22 * s), body_top + int(28 * s)), fill=color, width=max(3, int(3 * s)))
    elif standing:
        d.line((x + head_r, body_top, x + head_r, body_top + int(28 * s)), fill=color, width=max(3, int(3 * s)))
        d.line((x + head_r - int(10 * s), body_top + int(10 * s), x + head_r + int(10 * s), body_top + int(10 * s)), fill=color, width=max(3, int(3 * s)))
        d.line((x + head_r, body_top + int(28 * s), x + head_r - int(8 * s), body_top + int(44 * s)), fill=color, width=max(3, int(3 * s)))
        d.line((x + head_r, body_top + int(28 * s), x + head_r + int(8 * s), body_top + int(44 * s)), fill=color, width=max(3, int(3 * s)))
    else:
        d.line((x + head_r, body_top, x + head_r, body_top + int(22 * s)), fill=color, width=max(3, int(3 * s)))
        d.line((x + head_r - int(10 * s), body_top + int(8 * s), x + head_r + int(10 * s), body_top + int(8 * s)), fill=color, width=max(3, int(3 * s)))
        d.line((x + head_r, body_top + int(22 * s), x + head_r - int(10 * s), body_top + int(34 * s)), fill=color, width=max(3, int(3 * s)))
        d.line((x + head_r, body_top + int(22 * s), x + head_r + int(10 * s), body_top + int(34 * s)), fill=color, width=max(3, int(3 * s)))


def panel(title: str, w=1400, h=720) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = canvas(w, h, PAPER)
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, w, 64), fill=PINE)
    d.text((28, 16), title, fill=WHITE, font=font(28, True))
    return img, d


def draw_ledkryss(size=700, with_sign: Image.Image | None = None) -> Image.Image:
    img = canvas(size, int(size * 1.25), (214, 226, 220))
    d = ImageDraw.Draw(img)
    d.polygon([(0, int(size * 0.72)), (size, int(size * 0.62)), (size, size * 2), (0, size * 2)], fill=(236, 240, 235))
    pole_x = size // 2
    d.rectangle((pole_x - 14, 80, pole_x + 14, int(size * 1.05)), fill=(92, 64, 42))
    # red wooden cross
    cx, cy = pole_x, 210
    arm = 118
    thick = 28
    for ang in (40, -40):
        rad = math.radians(ang)
        dx, dy = math.cos(rad), math.sin(rad)
        pts = []
        for sx, sy in ((-arm, -thick / 2), (arm, -thick / 2), (arm, thick / 2), (-arm, thick / 2)):
            px = cx + sx * dx - sy * dy
            py = cy + sx * dy + sy * dx
            pts.append((px, py))
        d.polygon(pts, fill=RED, outline=(120, 20, 24))
    if with_sign is not None:
        sign = ImageOps.contain(with_sign.convert("RGBA"), (170, 170))
        img.alpha_composite(sign, (pole_x - sign.width // 2, 330))
    d.ellipse((pole_x - 40, int(size * 1.02), pole_x + 40, int(size * 1.08)), fill=(220, 226, 222))
    return img


def build_signs(official: dict[str, Image.Image]) -> dict[str, Image.Image]:
    d9 = official.get("d9")
    c13 = official.get("c13")
    c15 = official.get("c15")
    a22 = official.get("a22")

    snow_mask = symbol_mask(d9, "white_on_blue") if d9 else snowmobile_mask()
    walk_mask = walker_mask()
    ski_mask = skier_mask()

    out: dict[str, Image.Image] = {}
    if d9:
        out["marke-pabjuden-skoterled.png"] = white_outside_circle(fit_square(d9, 900, 20))
    if c13:
        out["marke-forbud-skoter.png"] = white_outside_circle(fit_square(c13, 900, 20))

    if snow_mask:
        lam = square_plate(900, WHITE, BLUE, 28)
        icon = tint(snow_mask, BLUE, (620, 620))
        paste_center(lam, icon)
        out["marke-lamplig-skoterled.png"] = lam

        ola = lam.copy()
        bar = Image.new("RGBA", ola.size, (0, 0, 0, 0))
        bd = ImageDraw.Draw(bar)
        bd.line((90, 810, 810, 90), fill=RED + (255,), width=70)
        ola.alpha_composite(bar)
        out["marke-olamplig-led.png"] = ola

        if "marke-pabjuden-skoterled.png" not in out:
            pab = round_plate(900, BLUE, WHITE, 18)
            icon_w = tint(snow_mask, WHITE, (560, 560))
            paste_center(pab, icon_w)
            out["marke-pabjuden-skoterled.png"] = pab
        if "marke-forbud-skoter.png" not in out:
            forb = round_plate(900, WHITE, RED, 90)
            paste_center(forb, tint(snow_mask, BLACK, (520, 520)))
            out["marke-forbud-skoter.png"] = forb

    # Official C15 (förbud mot gångtrafik). Do not invent a combined skier sign.
    if c15:
        gang = white_outside_circle(fit_square(c15, 900, 20))
    elif walk_mask:
        gang = round_plate(900, WHITE, RED, 90)
        paste_center(gang, tint(walk_mask, BLACK, (420, 560)))
    else:
        gang = round_plate(900, WHITE, RED, 90)
        gd = ImageDraw.Draw(gang)
        person(gd, 350, 250, 4.2)
    out["marke-forbud-gang-skidor.png"] = gang

    ice = square_plate(900, WHITE, (40, 70, 110), 22)
    idr = ImageDraw.Draw(ice)
    idr.rectangle((60, 60, 840, 210), fill=(40, 70, 110))
    idr.text((90, 100), "IS / VATTEN", fill=WHITE, font=font(64, True))
    idr.text((90, 280), "Körning på is", fill=INK, font=font(52, True))
    idr.text((90, 360), "sker på egen risk.", fill=INK, font=font(52, True))
    idr.rounded_rectangle((90, 520, 810, 780), 8, fill=(198, 222, 236))
    idr.line((90, 620, 280, 600), fill=WHITE, width=6)
    idr.line((280, 600, 430, 640), fill=WHITE, width=6)
    idr.line((430, 640, 810, 580), fill=WHITE, width=6)
    idr.line((360, 520, 410, 780), fill=RED, width=10)
    idr.line((400, 520, 360, 780), fill=RED, width=6)
    out["marke-is-egen-risk.png"] = ice

    out["ledkryss-roda.png"] = draw_ledkryss(700)
    extra = out.get("marke-pabjuden-skoterled.png") or out.get("marke-lamplig-skoterled.png")
    out["ledkryss-tva-marken.png"] = draw_ledkryss(700, extra)

    shapes = []
    labels = ["Varning", "Väjning", "Förbud", "Påbud", "Anvisning"]
    if official.get("a1"):
        a1 = official["a1"].convert("RGBA")
        bg = Image.new("RGBA", a1.size, (255, 255, 255, 255))
        bg.alpha_composite(a1)
        shapes.append(bg)
    else:
        tri = Image.new("RGBA", (400, 400), (255, 255, 255, 255))
        td = ImageDraw.Draw(tri)
        td.polygon([(200, 20), (380, 360), (20, 360)], fill=RED)
        td.polygon([(200, 70), (340, 330), (60, 330)], fill=(244, 210, 60))
        shapes.append(tri)
    shapes.append(yield_sign(500))
    shapes.append(out["marke-forbud-skoter.png"])
    shapes.append(out["marke-pabjuden-skoterled.png"])
    shapes.append(out["marke-lamplig-skoterled.png"])
    if official.get("b2"):
        # keep stop elsewhere; shape row already has väjning
        pass
    out["vagmarken-former.png"] = captioned_row(
        [ImageOps.contain(s.convert("RGBA"), (240, 240)) for s in shapes],
        labels,
        1400,
        430,
    )
    return out


def build_diagrams() -> dict[str, Image.Image]:
    figs: dict[str, Image.Image] = {}

    img = canvas(1400, 900, PAPER)
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, 1400, 900), fill=PINE)
    d.ellipse((740, 130, 1530, 930), fill=MOSS)
    draw_skoter(d, 520, 470, 3.5, WHITE, long=True, tall=False)
    d.text((90, 115), "FÖRARBEVIS", fill=GOLD, font=font(42, True))
    d.text((90, 185), "SNÖSKOTER", fill=WHITE, font=font(82, True))
    d.text((95, 300), "Utbildningsmaterial", fill=WHITE, font=font(34))
    d.text((95, 760), "Instruktörsverket AB  •  Tänndalen", fill=WHITE, font=font(28, True))
    figs["omslag-skoter.png"] = img

    figs["skotertyper.png"] = build_skotertyper()

    img, d = panel("Snöskoterns delar")
    draw_skoter(d, 280, 280, 2.6, PINE, long=True)
    labels = [
        (200, 200, "Styre"),
        (140, 360, "Skida"),
        (430, 170, "Huv"),
        (620, 200, "Säte"),
        (820, 250, "Tunnel"),
        (900, 430, "Drivmatta"),
        (1100, 300, "Baklyse"),
    ]
    for x, y, lab in labels:
        d.ellipse((x, y, x + 10, y + 10), fill=COPPER)
        d.text((x + 16, y - 6), lab, fill=PINE, font=font(22, True))
    figs["skoterns-delar.png"] = img

    img, d = panel("Under huven — kontrollera enligt instruktionsboken")
    d.rounded_rectangle((180, 150, 1220, 610), 22, fill=ICE, outline=MOSS, width=4)
    d.arc((260, 180, 1140, 500), 180, 355, fill=PINE, width=12)
    d.rounded_rectangle((460, 300, 940, 540), 24, fill=MUTED)
    d.ellipse((320, 330, 500, 510), fill=INK)
    d.ellipse((900, 330, 1080, 510), fill=INK)
    d.text((560, 380), "MOTORRUM", fill=WHITE, font=font(40, True))
    d.text((280, 560), "Olja  •  kylvätska  •  lösa eller skadade delar", fill=PINE, font=font(28, True))
    figs["skoter-motor.png"] = img

    img, d = panel("Reglage på styret")
    d.line((220, 410, 1180, 410), fill=INK, width=34)
    d.rounded_rectangle((150, 350, 330, 470), 28, fill=MUTED)
    d.rounded_rectangle((1070, 350, 1250, 470), 28, fill=MUTED)
    d.arc((240, 270, 430, 450), 180, 330, fill=COPPER, width=14)
    d.rounded_rectangle((950, 300, 1040, 390), 14, fill=COPPER)
    d.rounded_rectangle((650, 275, 760, 370), 14, fill=RED)
    d.text((150, 520), "Broms — vänster", fill=PINE, font=font(26, True))
    d.text((605, 205), "Nödstopp / lina", fill=PINE, font=font(26, True))
    d.text((1010, 520), "Gas — höger", fill=PINE, font=font(26, True))
    figs["skoter-reglage.png"] = img

    img, d = panel("Kamhöjd — jämför alternativen och följ tillverkaren")
    heights = [
        (25, 70, "25 mm\nsämst av provets alternativ\nmed släde på hård led"),
        (39, 110, "39 mm\nmellanalternativ"),
        (75, 180, "75 mm\nfrämst för lössnö"),
    ]
    for i, (mm, h, lab) in enumerate(heights):
        x = 160 + i * 400
        d.rectangle((x, 520 - h, x + 220, 520), fill=INK)
        for lx in range(x + 16, x + 210, 28):
            d.polygon([(lx, 520 - h), (lx + 10, 520 - h - 18), (lx + 20, 520 - h)], fill=GOLD)
        d.text((x, 540), lab, fill=PINE, font=font(22, True))
    figs["kamhojd.png"] = img

    img, d = panel("Service ger mindre farliga avgaser")
    d.rounded_rectangle((80, 140, 640, 620), 20, fill=ICE)
    d.rounded_rectangle((760, 140, 1320, 620), 20, fill=(246, 228, 220))
    draw_skoter(d, 160, 280, 1.8, MOSS)
    draw_skoter(d, 840, 280, 1.8, COPPER)
    d.ellipse((430, 210, 520, 270), outline=MUTED, width=3)
    d.ellipse((1100, 180, 1260, 280), fill=(160, 160, 160))
    d.text((160, 520), "Välservad — mindre rök", fill=PINE, font=font(26, True))
    d.text((840, 520), "Sliten — mer avgaser och buller", fill=COPPER, font=font(26, True))
    figs["avgaser-service.png"] = img

    img, d = panel("Renar: vänd och ta omväg")
    d.ellipse((820, 220, 1280, 560), fill=(232, 224, 210))
    for i in range(7):
        d.ellipse((880 + (i % 4) * 70, 280 + (i // 4) * 90, 920 + (i % 4) * 70, 330 + (i // 4) * 90), fill=(140, 110, 70))
    d.text((900, 200), "Hjord", fill=MUTED, font=font(22, True))
    draw_skoter(d, 140, 340, 1.4, PINE)
    d.polygon([(430, 380), (520, 350), (520, 410)], fill=COPPER)
    d.text((140, 520), "Vänd. Kör inte genom hjorden.", fill=PINE, font=font(28, True))
    figs["renar-omvag.png"] = img

    img, d = panel("Slå upp kommunens lokala trafikföreskrifter")
    boxes = [(180, 180, 1220, 620, "Sverige"), (280, 240, 1120, 560, "Län / länsstyrelse"), (430, 310, 970, 500, "Kommun — LTF")]
    fills = [(20, 53, 42), (45, 106, 79), (201, 162, 39)]
    cols = [WHITE, WHITE, PINE]
    for box, fill, col in zip(boxes, fills, cols):
        d.rounded_rectangle(box[:4], 18, fill=fill)
        d.text((box[0] + 28, (box[1] + box[3]) // 2 - 16), box[4], fill=col, font=font(28, True))
    figs["karta-kommun-lansstyrelse.png"] = img

    img, d = panel("Dubbel fart = fyra gånger längre bromssträcka")
    d.rectangle((120, 220, 420, 300), fill=MOSS)
    d.rectangle((120, 400, 1320, 480), fill=COPPER)
    d.text((120, 160), "20 km/h", fill=PINE, font=font(28, True))
    d.text((120, 340), "40 km/h  —  sträckan × 4", fill=COPPER, font=font(28, True))
    d.text((120, 540), "Samma sak: 30 km/h och 15 m  →  60 km/h och 60 m", fill=INK, font=font(24))
    figs["bromsstracka-dubbel-fart.png"] = img

    img, d = panel("Skrå, halt nedför och fällkniv med släde")
    titles = ["Skrå: vikt in mot sluttningen", "Halt nedför: svagt gaspådrag", "Släde: fällknivseffekt"]
    for i, t in enumerate(titles):
        x0 = 60 + i * 450
        d.rounded_rectangle((x0, 140, x0 + 420, 620), 16, fill=ICE if i < 2 else (246, 228, 220))
        d.text((x0 + 24, 160), t, fill=PINE, font=font(20, True))
        draw_skoter(d, x0 + 40, 320, 1.2, PINE)
        if i == 0:
            d.polygon([(x0 + 40, 500), (x0 + 380, 280), (x0 + 380, 500)], fill=(210, 220, 214))
            person(d, x0 + 200, 250, 1.6, standing=True)
        if i == 1:
            d.text((x0 + 40, 480), "lite gas, inte hård broms", fill=MOSS, font=font(20, True))
        if i == 2:
            d.polygon([(x0 + 260, 360), (x0 + 380, 420), (x0 + 250, 470)], fill=COPPER)
            d.text((x0 + 40, 500), "släde viker in", fill=COPPER, font=font(20, True))
    figs["skra-nedfor-fallkniv.png"] = img

    img, d = panel("Isdubbar lätt åtkomliga på kroppen")
    person(d, 280, 220, 5.5, standing=True, color=PINE)
    d.ellipse((250, 300, 430, 360), outline=COPPER, width=10)
    d.polygon([(250, 320), (220, 380), (270, 340)], fill=COPPER)
    d.polygon(([(430, 320), (460, 380), (410, 340)]), fill=COPPER)
    d.rounded_rectangle((700, 240, 1180, 520), 16, fill=(246, 228, 220))
    d.text((740, 300), "Inte här.", fill=COPPER, font=font(36, True))
    d.text((740, 360), "Ryggsäcken når du inte\nnär du är i vaken.", fill=INK, font=font(26))
    figs["isdubbar.png"] = img

    img, d = panel("Läs bipacksedeln — inte bara en röd triangel")
    d.rounded_rectangle((160, 180, 520, 560), 12, fill=(90, 140, 110))
    d.text((200, 300), "MEDICIN", fill=WHITE, font=font(36, True))
    d.rounded_rectangle((600, 180, 1180, 560), 8, fill=WHITE, outline=PINE, width=3)
    d.text((640, 220), "Bipacksedel", fill=PINE, font=font(32, True))
    d.text((640, 280), "Kan jag köra?\nPåverkas omdöme\noch reaktion?", fill=INK, font=font(26))
    d.polygon([(1080, 200), (1160, 340), (1000, 340)], outline=RED, width=8)
    figs["bipacksedel.png"] = img

    img, d = panel("Provfakta: vanligaste olyckstypen är vältning")
    labels = ["Vältning", "Kollision", "Is/drunkning", "Annat"]
    for i, lab in enumerate(labels):
        x = 80 + i * 330
        fill = (246, 228, 220) if i == 0 else ICE
        d.rounded_rectangle((x, 200, x + 290, 540), 18, fill=fill, outline=COPPER if i == 0 else MOSS, width=5)
        if i == 0:
            d.arc((x + 70, 265, x + 220, 430), 20, 330, fill=COPPER, width=18)
        d.text((x + 35, 460), lab, fill=COPPER if i == 0 else PINE, font=font(25, True))
    figs["olyckstyper.png"] = img

    img, d = panel("Medvetslös: 112, kontrollera andning och starta HLR vid behov")
    d.rounded_rectangle((80, 140, 680, 620), 16, fill=ICE)
    d.rounded_rectangle((720, 140, 1320, 620), 16, fill=(246, 236, 220))
    d.text((110, 170), "Ingen eller onormal andning", fill=PINE, font=font(28, True))
    d.text((110, 230), "Ring 112 på högtalare.\nÖppna luftvägen.\nHLR 30:2.", fill=INK, font=font(24))
    d.ellipse((280, 340, 430, 490), outline=PINE, width=6)
    d.arc((250, 360, 460, 560), 200, 340, fill=PINE, width=8)
    d.text((760, 170), "Chock, vaken", fill=PINE, font=font(28, True))
    d.text((760, 230), "Håll varm. Prata lugnt.\nIngen mat eller dryck.", fill=INK, font=font(24))
    d.rectangle((860, 400, 1160, 520), fill=(180, 90, 70))
    figs["luftvag-chock.png"] = img

    img, d = panel("Körställningar — backa på knä")
    poses = [("Sittande", False, False), ("Knästående", True, False), ("Stående", False, True), ("Backa: på knä", True, False)]
    for i, (lab, kn, st) in enumerate(poses):
        x = 80 + i * 330
        d.rounded_rectangle((x, 150, x + 300, 600), 16, fill=ICE if i < 3 else (246, 236, 220))
        draw_skoter(d, x + 20, 320, 1.05, PINE)
        person(d, x + 90, 240, 2.0, kneeling=kn, standing=st)
        d.text((x + 24, 530), lab, fill=PINE, font=font(22, True))
    figs["korstallningar.png"] = img

    img, d = panel("Fastkörd: motor av, stabilisera och gräv")
    d.ellipse((180, 280, 620, 560), fill=(210, 220, 226))
    draw_skoter(d, 240, 300, 1.6, PINE)
    person(d, 780, 260, 3.2)
    d.polygon([(860, 420), (980, 420), (920, 520)], fill=MUTED)
    d.text((180, 580), "Säkra nyckel och lina. Håll avstånd till drivbandet.", fill=PINE, font=font(28, True))
    figs["fastkord-skoter.png"] = img
    return figs


def main() -> None:
    official: dict[str, Image.Image] = {}
    for key, title in COMMONS.items():
        img = commons_png(title)
        if img:
            official[key] = img
            print("got", title, img.size)
    signs = build_signs(official)
    for name, img in signs.items():
        path = ASSETS / name
        if path.exists():
            print("kept", path.name)
            continue
        path = save(img, name)
        print("wrote", path.name, img.size)
    diagrams = build_diagrams()
    for name, img in diagrams.items():
        path = ASSETS / name
        if path.exists():
            print("kept", path.name)
            continue
        path = save(img, name)
        print("wrote", path.name, img.size)


if __name__ == "__main__":
    main()
