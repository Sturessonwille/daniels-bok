#!/usr/bin/env python3
"""Replace broken diagrams and official signs; label the better photos."""

from __future__ import annotations

import json
import ssl
import urllib.parse
import urllib.request
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE

ROOT = Path(__file__).resolve().parents[1]
DST = ROOT / "assets"
SRC = Path("/Users/wille/.cursor/projects/Users-wille-daniel-bok-Willes-uppdrag/assets")
UA = "InstruktorsverketSkoterbok/1.0 (educational course book)"

PINE = (20, 53, 42)
MOSS = (45, 106, 79)
GOLD = (201, 162, 39)
INK = (28, 28, 25)
PAPER = (247, 244, 238)
WHITE = (255, 255, 255)
COPPER = (196, 92, 38)
MUTED = (92, 103, 95)
RED = (196, 32, 38)
BLUE = (0, 90, 160)
YELLOW = (254, 211, 0)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    path = (
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
        if bold
        else "/System/Library/Fonts/Supplemental/Arial.ttf"
    )
    return ImageFont.truetype(path, size)


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
        info = next(iter(data["query"]["pages"].values()))["imageinfo"][0]
        url = info.get("thumburl") or info["url"]
        req2 = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req2, timeout=30, context=SSL_CTX) as res:
            return Image.open(BytesIO(res.read())).convert("RGBA")
    except Exception as exc:
        print("skip", title, exc)
        return None


def save_rgb(img: Image.Image, name: str) -> None:
    DST.mkdir(exist_ok=True)
    out = img.convert("RGB")
    out.save(DST / name, "PNG", optimize=True)
    print("wrote", name, out.size)


def banner(img: Image.Image, title: str) -> Image.Image:
    out = img.convert("RGB")
    d = ImageDraw.Draw(out)
    d.rectangle((0, 0, out.width, 56), fill=PINE)
    d.text((22, 14), title, fill=WHITE, font=font(24, True))
    return out


def caption(d: ImageDraw.ImageDraw, x: int, y: int, text: str, color=PINE) -> None:
    d.text((x, y), text, fill=color, font=font(20, True))


def fit_square(img: Image.Image, size: int, pad: int = 8) -> Image.Image:
    inner = size - pad * 2
    fitted = ImageOps.contain(img, (inner, inner))
    out = Image.new("RGBA", (size, size), (255, 255, 255, 255))
    out.alpha_composite(fitted, ((size - fitted.width) // 2, (size - fitted.height) // 2))
    return out


def white_outside_circle(img: Image.Image) -> Image.Image:
    out = img.convert("RGBA")
    w, h = out.size
    cx, cy = w / 2, h / 2
    r = min(w, h) / 2 - 4
    px = out.load()
    for y in range(h):
        for x in range(w):
            if (x - cx) ** 2 + (y - cy) ** 2 > r * r:
                px[x, y] = (255, 255, 255, 255)
    return out


def rebuild_signs(official: dict[str, Image.Image]) -> None:
    if official.get("c13"):
        save_rgb(white_outside_circle(fit_square(official["c13"], 900, 20)), "marke-forbud-skoter.png")
    if official.get("d9"):
        save_rgb(white_outside_circle(fit_square(official["d9"], 900, 20)), "marke-pabjuden-skoterled.png")

    if official.get("c15"):
        save_rgb(white_outside_circle(fit_square(official["c15"], 900, 20)), "marke-forbud-gang-skidor.png")
    elif official.get("c13"):
        save_rgb(white_outside_circle(fit_square(official["c13"], 900, 20)), "marke-forbud-gang-skidor.png")

    shapes = []
    labels = ["Varning", "Väjning", "Förbud", "Påbud", "Anvisning"]
    if official.get("a1"):
        shapes.append(official["a1"])
    if official.get("b1"):
        shapes.append(official["b1"])
    shapes.append(Image.open(DST / "marke-forbud-skoter.png"))
    shapes.append(Image.open(DST / "marke-pabjuden-skoterled.png"))
    if (DST / "marke-lamplig-skoterled.png").exists():
        shapes.append(Image.open(DST / "marke-lamplig-skoterled.png"))
    row = Image.new("RGB", (1400, 430), PAPER)
    d = ImageDraw.Draw(row)
    slot = 1400 // len(shapes)
    for i, (im, lab) in enumerate(zip(shapes, labels)):
        im = ImageOps.contain(im.convert("RGBA"), (slot - 40, 260))
        x = i * slot + (slot - im.width) // 2
        bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
        bg.alpha_composite(im)
        row.paste(bg.convert("RGB"), (x, 30))
        bbox = d.textbbox((0, 0), lab, font=font(22, True))
        tw = bbox[2] - bbox[0]
        d.text((i * slot + (slot - tw) // 2, 320), lab, fill=PINE, font=font(22, True))
    save_rgb(row, "vagmarken-former.png")


def rebuild_karta() -> None:
    img = Image.new("RGB", (1400, 720), PAPER)
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, 1400, 64), fill=PINE)
    d.text((28, 16), "Slå upp kommunens lokala trafikföreskrifter", fill=WHITE, font=font(28, True))
    layers = [
        ((120, 140, 1280, 640), PINE, WHITE, "Sverige — lagar och föreskrifter"),
        ((260, 250, 1140, 560), MOSS, WHITE, "Län — länsstyrelsen"),
        ((420, 360, 980, 500), GOLD, PINE, "Kommun — lokala trafikföreskrifter"),
    ]
    for box, fill, col, lab in layers:
        d.rounded_rectangle(box, 18, fill=fill)
        bbox = d.textbbox((0, 0), lab, font=font(28, True))
        tw = bbox[2] - bbox[0]
        d.text(((box[0] + box[2] - tw) // 2, box[1] + 22), lab, fill=col, font=font(28, True))
    save_rgb(img, "karta-kommun-lansstyrelse.png")


def rebuild_broms() -> None:
    img = Image.new("RGB", (1400, 720), PAPER)
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, 1400, 64), fill=PINE)
    d.text((28, 16), "Dubbel fart = fyra gånger längre bromssträcka", fill=WHITE, font=font(28, True))
    d.text((80, 120), "20 km/h", fill=PINE, font=font(28, True))
    d.rounded_rectangle((80, 170, 380, 250), 8, fill=MOSS)
    d.text((80, 290), "Bromssträcka  1 ×", fill=MUTED, font=font(22, True))
    d.text((80, 380), "40 km/h", fill=COPPER, font=font(28, True))
    d.rounded_rectangle((80, 430, 1280, 510), 8, fill=COPPER)
    d.text((80, 540), "Bromssträcka  4 ×     samma sak: 30 km/h och 15 m  →  60 km/h och 60 m", fill=INK, font=font(22, True))
    save_rgb(img, "bromsstracka-dubbel-fart.png")


def rebuild_kamhojd() -> None:
    img = Image.new("RGB", (1400, 720), PAPER)
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, 1400, 64), fill=PINE)
    d.text((28, 16), "Kamhöjd — sidan av drivmattan", fill=WHITE, font=font(28, True))
    specs = [
        (25, "25 mm", "Hård led.\nSämst grepp med släde."),
        (39, "39 mm", "Vanlig ledkörning."),
        (75, "75 mm", "Lössnö och fjäll.\nHögre förbrukning."),
    ]
    for i, (mm, title, note) in enumerate(specs):
        x = 90 + i * 440
        d.rounded_rectangle((x, 120, x + 400, 640), 16, fill=(236, 240, 235))
        belt_y = 430
        d.rectangle((x + 40, belt_y, x + 360, belt_y + 48), fill=INK)
        lug_h = int(mm * 2.1)
        step = 46
        for lx in range(x + 55, x + 340, step):
            d.polygon(
                [
                    (lx, belt_y),
                    (lx + 14, belt_y - lug_h),
                    (lx + 28, belt_y),
                ],
                fill=GOLD,
            )
        d.text((x + 40, 160), title, fill=PINE, font=font(36, True))
        d.text((x + 40, 520), note, fill=INK, font=font(22, True))
    save_rgb(img, "kamhojd.png")


def label_photos() -> None:
    mapping = [
        (
            "renar-turnaway.png",
            "renar-omvag.png",
            "Renar: vänd och ta omväg",
            [],
        ),
        (
            "luftvag-two-panel.png",
            "luftvag-chock.png",
            "Medvetslös: 112, kontrollera andning och starta HLR vid behov",
            [(70, "Öppna luftvägen och kontrollera andningen"), (740, "Chock: varm, prata, ingen mat")],
        ),
    ]
    for src, dest, title, labels in mapping:
        path = SRC / src
        if not path.exists():
            print("missing", src)
            continue
        img = banner(Image.open(path), title)
        d = ImageDraw.Draw(img)
        for x, text in labels:
            caption(d, x, img.height - 48, text)
        save_rgb(img, dest)

    poses = SRC / "korstallningar-poses-v2.png"
    if not poses.exists():
        poses = SRC / "korstallningar-poses.png"
    if poses.exists():
        img = banner(Image.open(poses), "Körställningar — backa på knä")
        d = ImageDraw.Draw(img)
        w = img.width
        for x, text in [
            (int(w * 0.04), "Sittande"),
            (int(w * 0.28), "Knästående"),
            (int(w * 0.52), "Stående"),
            (int(w * 0.76), "Backa: på knä, se bakåt"),
        ]:
            caption(d, x, img.height - 48, text)
        save_rgb(img, "korstallningar.png")

    skra = SRC / "skra-three-panel.png"
    jack = SRC / "fallkniv-folded.png"
    if skra.exists() and jack.exists():
        three = Image.open(skra).convert("RGB")
        jack_im = Image.open(jack).convert("RGB")
        w, h = 1400, 720
        gap = 8
        p1_w, p2_w, p3_w = 360, 360, 1400 - 360 - 360 - gap * 2
        canvas = Image.new("RGB", (w, h), WHITE)
        t_w = three.width // 3
        p1 = ImageOps.fit(three.crop((0, 0, t_w, three.height)), (p1_w, h), Image.Resampling.LANCZOS)
        p2 = ImageOps.fit(
            three.crop((t_w, 0, t_w * 2, three.height)), (p2_w, h), Image.Resampling.LANCZOS
        )
        p3 = ImageOps.fit(
            jack_im, (p3_w, h), Image.Resampling.LANCZOS, centering=(0.34, 0.48)
        )
        canvas.paste(p1, (0, 0))
        canvas.paste(p2, (p1_w + gap, 0))
        canvas.paste(p3, (p1_w + p2_w + gap * 2, 0))
        img = banner(canvas, "Skrå, halt nedför och fällkniv med släde")
        d = ImageDraw.Draw(img)
        for x, text in [
            (24, "Skrå: vikt inåt"),
            (p1_w + gap + 16, "Halt: svagt gaspådrag"),
            (p1_w + p2_w + gap * 2 + 16, "Släde: fällkniv"),
        ]:
            caption(d, x, img.height - 48, text)
        save_rgb(img, "skra-nedfor-fallkniv.png")
    elif skra.exists():
        img = banner(Image.open(skra), "Skrå, halt nedför och fällkniv med släde")
        d = ImageDraw.Draw(img)
        for x, text in [
            (40, "Skrå: vikt inåt"),
            (490, "Halt: svagt gaspådrag"),
            (930, "Släde: fällkniv"),
        ]:
            caption(d, x, img.height - 48, text)
        save_rgb(img, "skra-nedfor-fallkniv.png")

    types = SRC / "skotertyper-distinct.png"
    if types.exists():
        img = banner(Image.open(types), "Fem skotertyper — kolla matta och skidbredd")
        d = ImageDraw.Draw(img)
        w = img.width
        for x, text in [
            (int(w * 0.05), "Touring"),
            (int(w * 0.24), "Sport"),
            (int(w * 0.42), "Mountain"),
            (int(w * 0.61), "Crossover"),
            (int(w * 0.80), "Arbete"),
        ]:
            caption(d, x, img.height - 48, text)
        save_rgb(img, "skotertyper.png")

    leaflet = SRC / "bipacksedel-generic.png"
    if leaflet.exists():
        save_rgb(banner(Image.open(leaflet), "Läs bipacksedeln — inte bara triangeln"), "bipacksedel.png")

    # Keep original handlebar photo; fix kill-switch label to the tether.
    raw = SRC / "skoter-reglage-raw.png"
    if raw.exists():
        img = banner(Image.open(raw), "Reglage på styret")
        d = ImageDraw.Draw(img)
        calls = [
            ((355, 268), (40, 70), "Broms — vänster"),
            ((1008, 288), (1020, 70), "Gas — höger"),
            ((920, 360), (640, 70), "Nödstopp / lina"),
        ]
        for (ax, ay), (tx, ty), name in calls:
            d.line((ax, ay, tx, ty + 22), fill=COPPER, width=2)
            d.ellipse((ax - 4, ay - 4, ax + 4, ay + 4), fill=COPPER)
            d.text((tx, ty), name, fill=PINE, font=font(22, True))
        save_rgb(img, "skoter-reglage.png")


def main() -> None:
    # Keep one authoritative build path so this legacy repair command cannot
    # restore old captions or unsafe instructions.
    from bygg_bilder import main as build_all

    build_all()


if __name__ == "__main__":
    main()
