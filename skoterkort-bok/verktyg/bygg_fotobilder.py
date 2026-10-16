#!/usr/bin/env python3
"""Build book photos from customer images, our generated images, and official signs.

No third-party copyrighted photos. CC-BY / CC-BY-SA files are still
copyrighted and are not used in the book.
"""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
KALLOR = ASSETS / "_kallor"
GEN = Path("/Users/wille/.cursor/projects/Users-wille-daniel-bok-Willes-uppdrag/assets")
MASKINER = ASSETS / "Maskiner"

PINE = (31, 107, 74)
MOSS = (61, 143, 98)
INK = (36, 48, 40)
WHITE = (255, 255, 255)
CREAM = (251, 252, 249)
COPPER = (212, 106, 46)
MUTED = (95, 112, 104)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/Library/Fonts/Arial Unicode.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size, index=0)
    return ImageFont.load_default()


def open_rgb(path: Path) -> Image.Image:
    img = Image.open(path)
    img = ImageOps.exif_transpose(img)
    return img.convert("RGB")


def cover_box(img: Image.Image, size: tuple[int, int]) -> Image.Image:
    return ImageOps.fit(img, size, method=Image.Resampling.LANCZOS)


def contain_box(img: Image.Image, size: tuple[int, int], bg=CREAM) -> Image.Image:
    fitted = ImageOps.contain(img, size, method=Image.Resampling.LANCZOS)
    out = Image.new("RGB", size, bg)
    x = (size[0] - fitted.width) // 2
    y = (size[1] - fitted.height) // 2
    out.paste(fitted, (x, y))
    return out


def draw_text(d: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, fill, fnt) -> None:
    """Draw text word-by-word so spaces never collapse."""
    x, y = xy
    space = max(8, fnt.size // 4)
    for i, word in enumerate(text.split(" ")):
        if i:
            x += space
        d.text((x, y), word, fill=fill, font=fnt)
        x += d.textlength(word, font=fnt)


def banner(img: Image.Image, title: str) -> Image.Image:
    out = img.convert("RGB")
    d = ImageDraw.Draw(out)
    d.rectangle((0, 0, out.width, 52), fill=PINE)
    draw_text(d, (20, 12), title, WHITE, font(26, True))
    return out


def footer_bar(img: Image.Image, h: int = 56) -> Image.Image:
    out = Image.new("RGB", (img.width, img.height + h), CREAM)
    out.paste(img, (0, 0))
    return out


def label_centered(d: ImageDraw.ImageDraw, text: str, cx: int, y: int) -> None:
    fnt = font(20, True)
    words = text.split(" ")
    space = max(8, fnt.size // 4)
    widths = [d.textlength(w, font=fnt) for w in words]
    tw = sum(widths) + space * max(0, len(words) - 1)
    draw_text(d, (cx - int(tw) // 2, y), text, PINE, fnt)


def label_badge(d: ImageDraw.ImageDraw, x: int, y: int, text: str, fnt=None) -> None:
    """White pill behind label text — readable on any photo background."""
    fnt = fnt or font(24, True)
    pad_x, pad_y = 14, 8
    tw = d.textlength(text, font=fnt)
    th = fnt.size + 2 * pad_y
    box = (x, y, x + tw + 2 * pad_x, y + th)
    d.rounded_rectangle(box, radius=8, fill=WHITE, outline=PINE, width=2)
    d.text((x + pad_x, y + pad_y), text, fill=PINE, font=fnt)


def callout(d: ImageDraw.ImageDraw, ax: int, ay: int, tx: int, ty: int, text: str) -> None:
    d.line((ax, ay, tx + 8, ty + 22), fill=COPPER, width=3)
    d.ellipse((ax - 5, ay - 5, ax + 5, ay + 5), fill=COPPER, outline=WHITE, width=1)
    label_badge(d, tx, ty, text)


def save(img: Image.Image, name: str) -> None:
    path = ASSETS / name
    img.convert("RGB").save(path, "PNG", optimize=True)
    print("wrote", name, img.size)


def panel_row(paths: list[Path], labels: list[str], title: str, size=(1600, 780), fit="contain") -> Image.Image:
    n = len(paths)
    gap = 14
    footer = 58
    banner_h = 52
    cell_w = (size[0] - gap * (n + 1)) // n
    cell_h = size[1] - banner_h - footer - gap
    canvas = Image.new("RGB", size, CREAM)
    d = ImageDraw.Draw(canvas)
    d.rectangle((0, 0, size[0], banner_h), fill=PINE)
    draw_text(d, (20, 12), title, WHITE, font(26, True))
    for i, (path, lab) in enumerate(zip(paths, labels)):
        src = open_rgb(path)
        cell = contain_box(src, (cell_w, cell_h)) if fit == "contain" else cover_box(src, (cell_w, cell_h))
        x = gap + i * (cell_w + gap)
        y = banner_h + 8
        canvas.paste(cell, (x, y))
        label_centered(d, lab, x + cell_w // 2, size[1] - 42)
    return canvas


def crop_fraction(img: Image.Image, box: tuple[float, float, float, float]) -> Image.Image:
    w, h = img.size
    l, t, r, b = box
    return img.crop((int(l * w), int(t * h), int(r * w), int(b * h)))


def sled_on_snow(
    img: Image.Image,
    cell_size: tuple[int, int],
    *,
    target_h: int = 210,
    floor: int = 24,
) -> Image.Image:
    """Place a cropped sled photo on a uniform snow background, bottom-aligned."""
    cw, ch = cell_size
    snow_top = (238, 244, 240)
    snow_bot = (225, 232, 228)
    cell = Image.new("RGB", cell_size, snow_top)
    d = ImageDraw.Draw(cell)
    for y in range(ch):
        t = y / max(ch - 1, 1)
        c = tuple(int(snow_top[i] + (snow_bot[i] - snow_top[i]) * t) for i in range(3))
        d.line((0, y, cw, y), fill=c)
    ratio = target_h / img.height
    nw = max(1, int(img.width * ratio))
    nh = target_h
    if nw > cw - 16:
        ratio = (cw - 16) / img.width
        nw = max(1, int(img.width * ratio))
        nh = max(1, int(img.height * ratio))
    fitted = img.resize((nw, nh), Image.Resampling.LANCZOS)
    x = (cw - nw) // 2
    y = ch - nh - floor
    cell.paste(fitted, (x, y))
    return cell


def build_skotertyper_foto() -> Image.Image:
    """Real snowmobile photos — normalized crops on matching snow backgrounds."""
    # (label, traits, path, crop box as fractions l,t,r,b)
    types = [
        (
            "Touring",
            ["Tvåsits · vindruta", "Medellång matta"],
            MASKINER / "IMG_20230202_105732.jpg",
            (0.0, 0.22, 0.72, 0.82),
        ),
        (
            "Sport",
            ["Kort matta · låg kam", "Lätt och smidig"],
            KALLOR / "sport-mxz-800.jpg",
            (0.0, 0.02, 0.98, 0.98),
        ),
        (
            "Mountain",
            ["Lång matta · hög kam", "Smal spårvidd"],
            KALLOR / "touring-skidoo-600.jpg",
            (0.0, 0.0, 0.82, 0.92),
        ),
        (
            "Crossover",
            ["Mellanlång matta", "Led och lös snö"],
            KALLOR / "crossover-enduro.jpg",
            (0.0, 0.02, 0.88, 0.92),
        ),
        (
            "Arbete",
            ["Bred matta · last", "Drag och låg växel"],
            KALLOR / "touring-skidoo-900ace.jpg",
            (0.0, 0.08, 1.0, 0.96),
        ),
    ]

    cols, rows = 3, 2
    gap = 12
    label_h = 54
    w, h = 1600, 820
    banner_h = 0  # caption lives in the book text
    usable_h = h - label_h - gap * (rows + 1)
    usable_w = w - gap * (cols + 1)
    cell_w = usable_w // cols
    cell_h = usable_h // rows

    canvas = Image.new("RGB", (w, h), CREAM)
    d = ImageDraw.Draw(canvas)

    slots = [
        (0, 0), (1, 0), (2, 0),
        (0.5, 1), (1.5, 1),  # centred pair on bottom row
    ]
    for (name, traits, path, crop), (col, row) in zip(types, slots):
        src = crop_fraction(open_rgb(path), crop)
        cell = sled_on_snow(src, (cell_w, cell_h - label_h))
        x = gap + int(col * (cell_w + gap))
        y = gap + row * (cell_h + gap)
        canvas.paste(cell, (x, y))
        cx = x + cell_w // 2
        label_centered(d, name, cx, y + cell_h - label_h + 8)
        for j, line in enumerate(traits):
            lw = d.textlength(line, font=font(15))
            d.text((cx - lw / 2, y + cell_h - label_h + 30 + j * 18), line, fill=MUTED, font=font(15))

    # center bottom row (2 cells in row 1)
    hint = "Fem skotertyper — jämför matta, kamhöjd och spårvidd."
    hw = d.textlength(hint, font=font(14))
    d.text(((w - hw) / 2, h - 16), hint, fill=MUTED, font=font(14))
    return canvas


def skotertyper() -> None:
    save(build_skotertyper_foto(), "skotertyper.png")


def skoterns_delar() -> None:
    """Use custom cutaway illustration if provided, else build from photo."""
    custom = ASSETS / "Gemini_Generated_Image_x3vyfgx3vyfgx3vy.jpeg"
    if custom.exists():
        img = open_rgb(custom)
        max_w = 1600
        if img.width != max_w:
            ratio = max_w / img.width
            img = img.resize((max_w, int(img.height * ratio)), Image.Resampling.LANCZOS)
        save(img, "skoterns-delar.png")
        return

    w, h = 1600, 900
    snow = Image.new("RGB", (w, h), (240, 246, 242))
    d_bg = ImageDraw.Draw(snow)
    for y in range(52, h):
        t = (y - 52) / max(h - 52, 1)
        c = (
            int(240 - 8 * t),
            int(246 - 10 * t),
            int(242 - 8 * t),
        )
        d_bg.line((0, y, w, y), fill=c)

    src = crop_fraction(open_rgb(MASKINER / "IMG_20230202_105732.jpg"), (0.0, 0.16, 0.92, 0.86))
    target_w = 1280
    ratio = target_w / src.width
    sled = src.resize((target_w, int(src.height * ratio)), Image.Resampling.LANCZOS)
    sx = (w - sled.width) // 2
    sy = h - sled.height - 70
    snow.paste(sled, (sx, sy))

    img = banner(snow, "Snöskoterns delar")
    d = ImageDraw.Draw(img)
    sh, sw = sled.height, sled.width

    # anchor on sled, label position in open sky/snow area
    parts = [
        ((sx + int(0.05 * sw), sy + sh - 28), (30, 680), "Skida"),
        ((sx + int(0.13 * sw), sy + 75), (30, 140), "Huv"),
        ((sx + int(0.20 * sw), sy + 42), (180, 120), "Styre"),
        ((sx + int(0.40 * sw), sy + 58), (470, 120), "Säte"),
        ((sx + int(0.60 * sw), sy + 72), (760, 120), "Tunnel"),
        ((sx + int(0.90 * sw), sy + 65), (1180, 120), "Baklyse"),
        ((sx + int(0.68 * sw), sy + sh - 18), (900, 760), "Drivmatta"),
    ]
    for anchor, label_pos, name in parts:
        callout(d, anchor[0], anchor[1], label_pos[0], label_pos[1], name)
    save(img, "skoterns-delar.png")


def skoter_motor() -> None:
    img = cover_box(open_rgb(GEN / "skoter-motor-raw.jpg"), (1600, 900))
    img = banner(img, "Under huven")
    d = ImageDraw.Draw(img)
    callout(d, 980, 80, 1180, 70, "Huv")
    callout(d, 620, 430, 40, 360, "Motor")
    save(img, "skoter-motor.png")


def skoter_reglage() -> None:
    """Use custom handlebar illustration if provided, else build from photo."""
    custom = ASSETS / "reglage-styret-illustration.jpeg"
    if custom.exists():
        img = open_rgb(custom)
        max_w = 1600
        if img.width != max_w:
            ratio = max_w / img.width
            img = img.resize((max_w, int(img.height * ratio)), Image.Resampling.LANCZOS)
        save(img, "skoter-reglage.png")
        return

    img = cover_box(open_rgb(GEN / "reglage-tumgas-ai2.jpg"), (1600, 900))
    img = banner(img, "Reglage på styret")
    d = ImageDraw.Draw(img)
    callout(d, 280, 430, 40, 80, "Broms — vänster")
    callout(d, 980, 250, 700, 70, "Nödstopp / lina")
    callout(d, 1320, 430, 1180, 80, "Gas — höger")
    save(img, "skoter-reglage.png")


def avgaser() -> None:
    src = cover_box(open_rgb(GEN / "avgaser-service-raw.jpg"), (1600, 820))
    src = banner(src, "Service ger mindre avgaser")
    src = footer_bar(src, 56)
    d = ImageDraw.Draw(src)
    label_centered(d, "Välservad", 400, src.height - 40)
    label_centered(d, "Sliten — mer rök", 1200, src.height - 40)
    save(src, "avgaser-service.png")


def renar() -> None:
    img = cover_box(open_rgb(GEN / "renar-omvag-raw.jpg"), (1600, 900))
    save(banner(img, "Renar: vänd och ta omväg"), "renar-omvag.png")


def _draw_ledkryss_scene(w=1400, h=980, with_d9: bool = False) -> Image.Image:
    img = Image.new("RGB", (w, h), (214, 226, 232))
    d = ImageDraw.Draw(img)
    d.polygon([(0, int(h * 0.58)), (w, int(h * 0.50)), (w, h), (0, h)], fill=(236, 240, 238))
    d.ellipse((w * 0.62, h * 0.38, w * 0.92, h * 0.48), fill=(200, 210, 216))
    pole_x = int(w * 0.32)
    d.rectangle((pole_x - 16, 90, pole_x + 16, int(h * 0.78)), fill=(110, 78, 48))
    cx, cy = pole_x, 210
    arm, thick = 130, 30
    for ang in (40, -40):
        rad = math.radians(ang)
        dx, dy = math.cos(rad), math.sin(rad)
        pts = []
        for sx, sy in ((-arm, -thick / 2), (arm, -thick / 2), (arm, thick / 2), (-arm, thick / 2)):
            pts.append((cx + sx * dx - sy * dy, cy + sx * dy + sy * dx))
        d.polygon(pts, fill=(196, 32, 38), outline=(120, 20, 24))
    if with_d9:
        sign_path = ASSETS / "marke-pabjuden-skoterled.png"
        if sign_path.exists():
            sign = ImageOps.contain(open_rgb(sign_path).convert("RGBA"), (210, 210))
            # Keep only the blue disc so no white square floats in the snow.
            mask = Image.new("L", sign.size, 0)
            ImageDraw.Draw(mask).ellipse((2, 2, sign.width - 3, sign.height - 3), fill=255)
            sign.putalpha(mask)
            img.paste(sign, (pole_x - sign.width // 2, 340), sign)
    return img


def ledkryss() -> None:
    # Original drawing plus official public-domain D9 artwork. No third-party photos.
    save(_draw_ledkryss_scene(with_d9=False), "ledkryss-roda.png")
    save(_draw_ledkryss_scene(with_d9=True), "ledkryss-tva-marken.png")


def skra_nedfor() -> None:
    save(
        panel_row(
            [
                GEN / "skra-raw.jpg",
                GEN / "nedfor-raw.jpg",
                GEN / "fallkniv-raw.jpg",
            ],
            ["Skrå: vikt inåt", "Halt: svagt gaspådrag", "Släde: fällkniv"],
            "Skrå, halt nedför och fällkniv",
            (1600, 780),
            fit="cover",
        ),
        "skra-nedfor-fallkniv.png",
    )


def isdubbar() -> None:
    img = cover_box(open_rgb(GEN / "isdubbar-korrekt.jpg"), (1600, 900))
    save(banner(img, "Isdubbar på kroppen"), "isdubbar.png")


def bipacksedel() -> None:
    w, h = 1600, 900
    img = Image.new("RGB", (w, h), (236, 230, 220))
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, w, 52), fill=PINE)
    draw_text(d, (20, 12), "Läs bipacksedeln", WHITE, font(26, True))

    d.rounded_rectangle((80, 160, 520, 520), 8, fill=WHITE, outline=(210, 205, 198), width=2)
    d.rectangle((80, 160, 520, 210), fill=(245, 245, 245))
    draw_text(d, (110, 250), "Exempelmedicin", INK, font(32, True))
    draw_text(d, (110, 300), "tabletter", MUTED, font(24))
    d.polygon([(430, 400), (490, 400), (460, 455)], fill=(196, 32, 38))
    d.text((454, 408), "!", fill=WHITE, font=font(22, True))

    d.rounded_rectangle((580, 120, 1520, 820), 6, fill=WHITE, outline=(210, 205, 198), width=2)
    draw_text(d, (620, 150), "Bipacksedel: information till användaren", INK, font(24, True))
    draw_text(d, (620, 200), "Exempelmedicin tabletter", MUTED, font(20))
    lines = [
        "1. Vad Exempelmedicin är och vad det används för",
        "2. Vad du behöver veta innan du tar Exempelmedicin",
        "3. Hur du tar Exempelmedicin",
        "4. Körförmåga och användning av maskiner",
        "    Läkemedlet kan påverka reaktionsförmågan.",
        "    Kör inte om du känner dig trött, yr eller slö.",
        "    Rådfråga läkare eller apotek om du är osäker.",
        "5. Hur Exempelmedicin förvaras",
        "6. Förpackningens innehåll och övriga upplysningar",
    ]
    y = 260
    for i, line in enumerate(lines):
        color = PINE if "Körförmåga" in line or line.startswith("    ") else INK
        draw_text(d, (620, y), line.strip(), color, font(22, "Körförmåga" in line))
        y += 48 if i < 3 or i > 6 else 40
    save(img, "bipacksedel.png")


def korstallningar() -> None:
    save(
        panel_row(
            [
                GEN / "sittande-studio.jpg",
                GEN / "knaende-raw2.jpg",
                GEN / "staende-tydlig.jpg",
                GEN / "backa-kna-bak.jpg",
            ],
            ["Sittande", "Knästående", "Stående", "Backa: se bakåt"],
            "Körställningar",
            (1600, 720),
            fit="cover",
        ),
        "korstallningar.png",
    )


def kamhojd() -> None:
    """Use custom lug-height illustration if provided."""
    custom = ASSETS / "kamhojd-jamforelse.jpeg"
    if custom.exists():
        img = open_rgb(custom)
        max_w = 1600
        if img.width != max_w:
            ratio = max_w / img.width
            img = img.resize((max_w, int(img.height * ratio)), Image.Resampling.LANCZOS)
        save(img, "kamhojd.png")
        return


def fastkord() -> None:
    img = cover_box(open_rgb(GEN / "fastkord-raw.jpg"), (1600, 900))
    save(banner(img, "Fastkörd: motor av, gräv runt"), "fastkord-skoter.png")


def main() -> None:
    skotertyper()
    skoterns_delar()
    skoter_motor()
    skoter_reglage()
    kamhojd()
    avgaser()
    renar()
    ledkryss()
    skra_nedfor()
    isdubbar()
    bipacksedel()
    korstallningar()
    fastkord()


if __name__ == "__main__":
    main()
