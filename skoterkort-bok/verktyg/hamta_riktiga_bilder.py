#!/usr/bin/env python3
"""Download Commons photos for research only.

Do not put these files into the printed book unless the license is
public domain / CC0, or the customer owns the photo. CC BY and
CC BY-SA images are still copyrighted.
"""

from __future__ import annotations

import json
import ssl
import time
import urllib.parse
import urllib.request
from io import BytesIO
from pathlib import Path

SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "assets" / "_kallor"
UA = "InstruktorsverketSkoterbok/1.0 (educational course book)"

FILES = {
    "touring-skidoo-600.jpg": "2017-01-15 Ski-Doo 600.jpg",
    "touring-skidoo-900ace.jpg": "Innsbruck-Bombadier Ski-Doo 900ACE-snow mobile-01ASD.jpg",
    "sport-mxz-800.jpg": "Snowmobile Ski-Doo MXZ 800.jpg",
    "mountain-rmk.jpg": "Polaris 800 PRO-RMK 163 at Legendy 2018 in Prague.jpg",
    "utility-nordic.jpg": "Polaris S4 Nordic Pro, Lompensenteret, Longyearbyen.jpg",
    "utility-lynx.jpg": "Lynx GLX 5900.JPG",
    "crossover-enduro.jpg": "Snowmobile Lynx Enduro 400.jpg",
    "reglage-tumgas.jpg": "Motorschlitten Daumengashebel.jpg",
    "ledkryss-sylan.jpg": "Red crosses mark the winter route in Sylan in Sweden.jpg",
    "ledkryss-blahammaren.jpg": "On the way up to Blåhammaren Fjällstation in Sweden.jpg",
    "ledkryss-skoterled.jpg": "Skoterledsmarkering Särvfjället.jpg",
    "isdubbar.jpg": "Isdubbar, Eisdorn.jpg",
    "staende.jpg": "Motoneige à conduite debout.jpg",
    "sittande.jpg": "Airmen ride snowmobiles at Monarch mountain (5938574).jpg",
    "ren-lappland.jpg": "Ren, Lappland Sverige.jpg",
}


def commons_bytes(title: str, width: int = 1600) -> bytes:
    api = (
        "https://commons.wikimedia.org/w/api.php"
        "?action=query&format=json&prop=imageinfo&iiprop=url|mime"
        f"&iiurlwidth={width}&titles=File:{urllib.parse.quote(title)}"
    )
    req = urllib.request.Request(api, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=45, context=SSL_CTX) as res:
        data = json.load(res)
    info = next(iter(data["query"]["pages"].values()))["imageinfo"][0]
    url = info.get("thumburl") or info["url"]
    req2 = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req2, timeout=60, context=SSL_CTX) as res:
        return res.read()


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    for dest, title in FILES.items():
        path = RAW / dest
        if path.exists() and path.stat().st_size > 1000:
            print("have", dest)
            continue
        print("fetch", title)
        for attempt in range(5):
            try:
                data = commons_bytes(title)
                path.write_bytes(data)
                print("  ->", path, len(data))
                time.sleep(2)
                break
            except Exception as exc:
                print("  retry", attempt + 1, exc)
                time.sleep(4 + attempt * 3)
        else:
            print("FAILED", title)


if __name__ == "__main__":
    main()
