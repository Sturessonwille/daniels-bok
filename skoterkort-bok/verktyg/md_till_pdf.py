#!/usr/bin/env python3
"""Build the HTML book, then print it to A4 PDF with Chrome.

Two passes: the first PDF is only used to find the page where each chapter
starts, so the table of contents in the final PDF can show page numbers.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from md_till_html import CHAPTER_META, SOURCES_KEY, SOURCES_LEAD, build

CHROME = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")


def print_pdf(html_path: Path, pdf_path: Path) -> None:
    subprocess.run(
        [
            str(CHROME),
            "--headless=new",
            "--disable-gpu",
            "--no-pdf-header-footer",
            f"--print-to-pdf={pdf_path}",
            html_path.resolve().as_uri(),
        ],
        check=True,
        capture_output=True,
    )


def _squash(text: str) -> str:
    """Upper-case and drop whitespace so letter-spaced headings still match."""
    return re.sub(r"\s+", "", text).upper()


def find_start_pages(pdf_path: Path) -> dict[str, int]:
    """Map chapter number / SOURCES_KEY to the 1-based PDF page it starts on.

    Looks for the chapter opener text ("KAPITEL 3 · …", the "EXAMINATION"
    stamp, the appendix title). Pages 1–2 are the cover and contents and are
    skipped so the contents list itself never matches.
    """
    try:
        from pypdf import PdfReader
    except ImportError:
        print("pypdf saknas; innehållsförteckningen får inga sidnummer.", file=sys.stderr)
        return {}

    markers: dict[str, str] = {}
    for num, _title, _deck in CHAPTER_META:
        if num == "00":
            continue
        markers[num] = "EXAMINATION" if num == "09" else f"KAPITEL{num.lstrip('0')}·"
    # The appendix title also appears in each chapter's "see the appendix"
    # note, so match the appendix lead text instead.
    markers[SOURCES_KEY] = _squash(SOURCES_LEAD)

    found: dict[str, int] = {}
    reader = PdfReader(str(pdf_path))
    for index, page in enumerate(reader.pages, start=1):
        if index <= 2:
            continue
        text = _squash(page.extract_text() or "")
        for key, marker in markers.items():
            if key not in found and marker in text:
                found[key] = index
    return found


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    html_path = root / "export" / "Forarbevis-snoskoter.html"
    pdf_path = root / "export" / "Forarbevis-snoskoter.pdf"
    html_path.parent.mkdir(exist_ok=True)
    kapitel = root / "kapitel"

    html_path.write_text(build(kapitel), encoding="utf-8")

    if not CHROME.exists():
        sys.exit(
            "Google Chrome was not found. Open export/Forarbevis-snoskoter.html "
            "and use File → Print → Save as PDF (A4)."
        )

    print_pdf(html_path, pdf_path)
    pages = find_start_pages(pdf_path)
    if pages:
        html_path.write_text(build(kapitel, pages), encoding="utf-8")
        print_pdf(html_path, pdf_path)
        for key, page in sorted(pages.items(), key=lambda kv: kv[1]):
            print(f"  {key:>6}  sida {page}")
    print(pdf_path)


if __name__ == "__main__":
    main()
