#!/usr/bin/env python3
"""Build a designed HTML book for screen and print-to-PDF."""

from __future__ import annotations

import html
import re
import sys
from pathlib import Path

from teman import DEFAULT_THEME, THEMES, Theme, css_vars

BOLD = re.compile(r"\*\*(.+?)\*\*")
LINK = re.compile(
    r"\[([^\]]+)\]\((https?://[^)\s]+)\)|<(https?://[^>\s]+)>"
)
BOOK_FILES = [
    "00-forord.md",
    "01-forare-och-fordon.md",
    "02-miljo-och-natur.md",
    "03-trafikregler.md",
    "04-straff-behorighet-forsakring.md",
    "05-trafiksakerhet.md",
    "06-manniskan.md",
    "07-olyckor-forsta-hjalpen.md",
    "08-praktik.md",
    "09-infor-provet.md",
]

CHAPTER_META = [
    ("00", "Förord", "Instruktörsverket · Tänndalen"),
    ("01", "Förare och fordon", "Maskinen, kläderna, kontrollen"),
    ("02", "Miljö, natur och hänsyn", "Spår, djur och avgaser"),
    ("03", "Trafikregler", "Skyltar, led och 20 km/h"),
    ("04", "Straff, behörighet och försäkring", "Vem får köra, vad som täcks"),
    ("05", "Trafiksäkerhet", "Fart, is, barn och stoppsträcka"),
    ("06", "Människan som förare", "Trötthet, alkohol, grupptryck"),
    ("07", "Olyckor och första hjälpen", "Vältning, chock, 112"),
    ("08", "Praktisk körning", "Körgård, ställning, fastkörd"),
    ("09", "Inför kunskapsprovet", "Legitimation, 16 år, boken undan"),
]

# Key used for the sources appendix and for page lookup in the PDF.
SOURCES_KEY = "kallor"
SOURCES_TITLE = "Källförteckning"
SOURCES_LEAD = (
    "Lagtext, myndighetsinformation och riktlinjer som kapitlen bygger på. "
    "Regler kan ändras; kontrollera alltid aktuell källa."
)
BOOK_TITLE = "Förarbevis snöskoter"
PUBLISHER = "Instruktörsverket AB"


def running_header(num: str, title: str) -> str:
    """Text shown in the top-left margin box on every page of a chapter."""
    if num == "00":
        return title
    if num == "09":
        return title
    return f"Kapitel {num.lstrip('0')} · {title}"


def page_css(theme: Theme) -> str:
    """Named @page rules: running header per chapter, page number in footer."""
    chapter_color = theme.page_chapter
    rules = [
        "@page { size: A4; margin: 19mm 14mm 19mm; }",
        f"@page {{ @bottom-center {{ content: counter(page); font: 9.5px 'Avenir Next', 'Segoe UI', sans-serif; color: {theme.page_footer}; }} }}",
        f"@page {{ @top-right {{ content: '{BOOK_TITLE} · {PUBLISHER}'; font: 8.5px 'Avenir Next', 'Segoe UI', sans-serif; color: {theme.page_header}; letter-spacing: .04em; }} }}",
        "@page cover { margin: 0; @top-left { content: none; } @top-right { content: none; } @bottom-center { content: none; } }",
        f"@page toc {{ @top-left {{ content: 'Innehåll'; font: 8.5px 'Avenir Next', 'Segoe UI', sans-serif; color: {chapter_color}; letter-spacing: .04em; }} }}",
        ".cover { page: cover; }",
        ".toc { page: toc; }",
    ]
    for num, title, _deck in CHAPTER_META:
        header = running_header(num, title).replace("'", "\\'")
        rules.append(
            f"@page kap{num} {{ @top-left {{ content: '{header}'; "
            f"font: 8.5px 'Avenir Next', 'Segoe UI', sans-serif; color: {chapter_color}; letter-spacing: .04em; }} }}"
        )
        rules.append(f".kap{num} {{ page: kap{num}; }}")
    rules.append(
        f"@page {SOURCES_KEY} {{ @top-left {{ content: '{SOURCES_TITLE}'; "
        f"font: 8.5px 'Avenir Next', 'Segoe UI', sans-serif; color: {chapter_color}; letter-spacing: .04em; }} }}"
    )
    rules.append(f".{SOURCES_KEY} {{ page: {SOURCES_KEY}; }}")
    return "\n".join(rules)


CSS_TEMPLATE = r"""
* { box-sizing: border-box; }
html { background: var(--html-bg); }
body {
  margin: 0;
  font-family: "Source Serif 4", "Iowan Old Style", Georgia, serif;
  color: var(--ink);
  background: var(--paper);
  line-height: 1.55;
  font-size: 17px;
}
.page-wrap { max-width: 820px; margin: 0 auto; background: var(--cream); box-shadow: 0 0 0 1px var(--shadow-border), 0 18px 50px var(--shadow-glow); }
.cover {
  min-height: 100vh;
  background: var(--cover-bg);
  color: var(--cover-ink);
  padding: 0;
  display: flex;
  flex-direction: column;
}
.cover-top {
  padding: 2.2rem 3rem 1.3rem;
  background: var(--cover-bg);
}
.cover-kicker {
  letter-spacing: .28em;
  text-transform: uppercase;
  font-size: .72rem;
  font-family: "Avenir Next", "Segoe UI", sans-serif;
  color: var(--moss);
}
.cover h1 {
  font-size: 3.2rem;
  line-height: 1.04;
  font-weight: 650;
  margin: 1rem 0 0;
  max-width: 12ch;
  color: var(--cover-title);
}
.cover .sub { font-size: 1.05rem; color: var(--cover-sub); margin: .7rem 0 0; }
.cover-rule { width: 4.2rem; height: 3px; background: var(--gold); margin: 1rem 0 0; border: 0; }
.cover-visual {
  flex: 1;
  background: var(--cover-visual-bg);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  min-height: 340px;
}
.cover-visual img {
  width: 100%;
  height: auto;
  max-height: 100%;
  object-fit: contain;
  object-position: center;
  display: block;
}
.cover-foot {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  padding: 1.05rem 3rem 1.25rem;
  font-family: "Avenir Next", "Segoe UI", sans-serif;
  font-size: .85rem;
  color: var(--cover-sub);
  letter-spacing: .04em;
  background: var(--cover-foot-bg);
}
.toc, .chapter, .endcard { padding: 2.6rem 3rem 3rem; }
.toc h2, .endcard h1 { font-family: "Avenir Next", "Segoe UI", sans-serif; color: var(--pine); margin: 0 0 1.4rem; }
.toc-list { list-style: none; padding: 0; margin: 0; }
.toc-list li { display: flex; justify-content: space-between; gap: 1rem; padding: .85rem 0; border-bottom: 1px solid var(--line); font-family: "Avenir Next", "Segoe UI", sans-serif; }
.toc-num { color: var(--gold); font-weight: 700; min-width: 2.2rem; }
.toc-title { flex: 1; color: var(--pine); font-weight: 600; }
.toc-deck { color: var(--muted); font-size: .86rem; font-weight: 400; display: block; margin-top: .15rem; }
.toc-page { color: var(--muted); font-weight: 600; min-width: 2.2rem; text-align: right; font-variant-numeric: tabular-nums; }
.hero {
  background: linear-gradient(135deg, var(--hero-from) 0%, var(--hero-to) 100%);
  color: var(--hero-ink);
  padding: 1.8rem 1.7rem 1.5rem;
  border-radius: 6px;
  margin: 0 0 1.8rem;
  position: relative;
  overflow: hidden;
}
.hero:after {
  content: "";
  position: absolute;
  right: -40px; top: -40px;
  width: 140px; height: 140px;
  border: 18px solid var(--hero-ring);
  border-radius: 50%;
}
.hero-kicker {
  font-family: "Avenir Next", "Segoe UI", sans-serif;
  letter-spacing: .22em;
  text-transform: uppercase;
  font-size: .68rem;
  color: var(--moss);
}
.hero h1 { font-size: 2rem; margin: .45rem 0 0; line-height: 1.15; }
h2 {
  font-family: "Avenir Next", "Segoe UI", sans-serif;
  color: var(--pine);
  font-size: 1.22rem;
  margin: 2rem 0 .7rem;
  padding-bottom: .35rem;
  border-bottom: 2px solid var(--h2-border);
}
h3 {
  font-family: "Avenir Next", "Segoe UI", sans-serif;
  color: var(--moss);
  font-size: 1.02rem;
  margin: 1.4rem 0 .45rem;
}
p { margin: 0 0 .85rem; }
strong { color: var(--pine); }
a { color: var(--moss); text-decoration-thickness: 1px; text-underline-offset: 2px; }
ul, ol { margin: 0 0 1rem; padding-left: 1.2rem; }
li { margin: .28rem 0; }
table {
  width: 100%;
  border-collapse: collapse;
  margin: 0 0 1.2rem;
  font-size: .92rem;
  font-family: "Avenir Next", "Segoe UI", sans-serif;
}
th { background: var(--th-bg); color: #fff; text-align: left; padding: .55rem .7rem; font-weight: 600; }
td { padding: .5rem .7rem; border-bottom: 1px solid var(--line); }
tr:nth-child(even) td { background: var(--ice); }
.callout, .photo {
  border-radius: 4px;
  padding: .85rem 1rem .85rem 1.05rem;
  margin: 1rem 0 1.2rem;
  font-size: .98rem;
}
.callout {
  background: var(--ice);
  border-left: 5px solid var(--moss);
  color: var(--pine);
  font-style: italic;
}
.callout.remember { border-left-color: var(--copper); background: var(--remember-bg); }
.photo {
  background: repeating-linear-gradient(-45deg, var(--photo-stripe-a), var(--photo-stripe-a) 8px, var(--photo-stripe-b) 8px, var(--photo-stripe-b) 16px);
  border: 1.5px dashed var(--photo-border);
  color: var(--muted);
  font-family: "Avenir Next", "Segoe UI", sans-serif;
  font-size: .88rem;
  font-style: normal;
  text-align: center;
  min-height: 4.2rem;
  display: flex;
  align-items: center;
  justify-content: center;
}
.photo-fig {
  margin: 1.1rem 0 1.4rem;
  padding: 1rem 1rem .85rem;
  background: #fff;
  border: 1px solid var(--line);
  border-radius: 6px;
  text-align: center;
}
.photo-fig img {
  display: block;
  width: 100%;
  max-width: 100%;
  max-height: 480px;
  height: auto;
  object-fit: contain;
  margin: 0 auto;
}
.photo-fig.sign img { max-height: 240px; width: auto; }
.photo-fig figcaption {
  font-family: "Avenir Next", "Segoe UI", sans-serif;
  font-size: .82rem;
  color: var(--muted);
  margin: .7rem 0 0;
}
.sources-note {
  font-family: "Avenir Next", "Segoe UI", sans-serif;
  font-size: .8rem;
  color: var(--muted);
  border-top: 1px solid var(--line);
  padding-top: .6rem;
  margin-top: 1.8rem;
}
.sources h1 { font-family: "Avenir Next", "Segoe UI", sans-serif; color: var(--pine); margin: 0 0 .4rem; }
.sources .lead { color: var(--muted); font-size: .95rem; margin-bottom: 1.2rem; }
.sources h2 { font-size: 1.02rem; margin: 1.3rem 0 .4rem; }
.sources ul {
  font-family: "Avenir Next", "Segoe UI", sans-serif;
  font-size: .78rem;
  line-height: 1.35;
}
.sources a { word-break: break-all; }
.endcard {
  background: linear-gradient(180deg, var(--cream), var(--ice));
}
.endcard .stamp {
  display: inline-block;
  font-family: "Avenir Next", "Segoe UI", sans-serif;
  letter-spacing: .18em;
  text-transform: uppercase;
  font-size: .7rem;
  color: var(--copper);
  border: 1px solid var(--copper);
  padding: .25rem .6rem;
  margin-bottom: 1rem;
}
@media print {
  html, body { background: white; }
  body { font-size: 16px; line-height: 1.48; }
  .page-wrap { box-shadow: none; max-width: none; }
  .cover, .toc, .chapter, .endcard, .sources { page-break-after: always; padding: 0; }
  .cover { min-height: 100vh; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  .cover-visual { min-height: auto; flex: 1; align-items: center; padding: .4rem 0; }
  .cover-visual img { width: 100%; height: auto; max-height: 11.5cm; object-fit: contain; }
  h2 { margin-top: 1.55rem; }
  h3 { margin-top: 1.1rem; }
  p { margin-bottom: .7rem; }
  ul, ol { margin-bottom: .8rem; }
  .photo-fig { margin: .9rem 0 1.1rem; padding: .6rem; }
  .photo-fig img { width: 100%; max-height: 11cm; object-fit: contain; }
  .photo-fig.sign img { max-height: 5.5cm; width: auto; }
  .hero, th, tr:nth-child(even) td, .callout, .photo, .photo-fig { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
}
"""


def book_css(theme: Theme) -> str:
    return f"{css_vars(theme)}\n{CSS_TEMPLATE}\n{page_css(theme)}"


def _inline_text(text: str) -> str:
    parts = BOLD.split(html.escape(text))
    out = []
    for i, part in enumerate(parts):
        out.append(f"<strong>{part}</strong>" if i % 2 else part)
    return "".join(out)


def inline(text: str) -> str:
    out: list[str] = []
    end = 0
    for match in LINK.finditer(text):
        out.append(_inline_text(text[end : match.start()]))
        label = match.group(1)
        url = match.group(2) or match.group(3)
        link_text = label or url
        out.append(
            f'<a href="{html.escape(url, quote=True)}">{_inline_text(link_text)}</a>'
        )
        end = match.end()
    out.append(_inline_text(text[end:]))
    return "".join(out)


BILD_RE = re.compile(
    r"^(?:\*\*)?Bild:(?:\*\*)?\s*`([^`]+)`(?:\s*[—–-]\s*(.*))?",
    re.I,
)


def render_figure(body: str, assets_dir: Path, assets_prefix: str = "../assets/") -> str | None:
    m = BILD_RE.match(body)
    if not m:
        return None
    rel = m.group(1).strip()
    caption = (m.group(2) or "").strip()
    name = Path(rel).name
    src_path = assets_dir / name
    if not src_path.exists():
        return None
    cls = "photo-fig sign" if name.startswith("marke-") or name.startswith("ledkryss") or name.startswith("vagmarken") else "photo-fig"
    alt = html.escape(caption or name)
    cap_html = f"<figcaption>{inline(caption)}</figcaption>" if caption else ""
    return (
        f'<figure class="{cls}">'
        f'<img src="{assets_prefix}{html.escape(name)}" alt="{alt}">'
        f"{cap_html}</figure>"
    )


def parse_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip("|").split("|")]


ORDERED_RE = re.compile(r"^\d+\. ")
SOURCES_HEADING_RE = re.compile(r"^## Källor(?:\s*[—–-]\s*(.*))?$", re.I)


def starts_block(line: str) -> bool:
    """True if the line opens a new block and must not be merged into a paragraph."""
    return line.startswith(("#", ">", "- ", "|")) or bool(ORDERED_RE.match(line))


def split_sources(lines: list[str]) -> tuple[list[str], list[str], str]:
    """Return (chapter lines, source lines, review note) for a chapter.

    The chapter's own "## Källor — kontrollerade ..." block is moved to the
    appendix at the back of the book. The review date is kept as a short
    note at the end of the chapter.
    """
    for idx, raw in enumerate(lines):
        m = SOURCES_HEADING_RE.match(raw.strip())
        if not m:
            continue
        end = idx + 1
        while end < len(lines) and not lines[end].startswith("## "):
            end += 1
        note = (m.group(1) or "").strip()
        return lines[:idx] + lines[end:], lines[idx + 1 : end], note
    return lines, [], ""


def md_to_html(
    lines: list[str], assets_dir: Path, skip_first_h1: bool = True, assets_prefix: str = "../assets/"
) -> str:
    chunks: list[str] = []
    i = 0
    skipped = False
    while i < len(lines):
        line = lines[i].rstrip()
        if not line:
            i += 1
            continue
        if line.startswith("|") and line.endswith("|"):
            rows = []
            while i < len(lines) and lines[i].rstrip().startswith("|"):
                raw = lines[i].rstrip()
                if not re.match(r"^\|[\s:|-]+\|$", raw):
                    rows.append(parse_row(raw))
                i += 1
            if rows:
                chunks.append("<table>")
                for r, row in enumerate(rows):
                    tag = "th" if r == 0 else "td"
                    tds = "".join(f"<{tag}>{inline(c)}</{tag}>" for c in row)
                    chunks.append(f"<tr>{tds}</tr>")
                chunks.append("</table>")
            continue
        if line.startswith("# "):
            if skip_first_h1 and not skipped:
                skipped = True
                i += 1
                continue
            chunks.append(f"<h2>{inline(line[2:].strip())}</h2>")
        elif line.startswith("## "):
            heading = line[3:].strip()
            cls = ' class="sources-heading"' if heading.startswith("Källor") else ""
            chunks.append(f"<h2{cls}>{inline(heading)}</h2>")
        elif line.startswith("### "):
            chunks.append(f"<h3>{inline(line[4:].strip())}</h3>")
        elif line.startswith(">"):
            # A blockquote may be hard-wrapped over several "> " lines.
            quoted = []
            while i < len(lines) and lines[i].rstrip().startswith(">"):
                quoted.append(lines[i].rstrip()[1:].strip())
                i += 1
            body = " ".join(part for part in quoted if part)
            fig = render_figure(body, assets_dir, assets_prefix)
            if fig:
                chunks.append(fig)
            else:
                cls = "photo" if body.lower().startswith("**bild") or body.lower().startswith("bild:") else "callout"
                if "kom ihåg" in body.lower():
                    cls = "callout remember"
                chunks.append(f'<div class="{cls}">{inline(body)}</div>')
            continue
        elif line.startswith("- "):
            items = []
            while i < len(lines) and lines[i].startswith("- "):
                item = lines[i][2:].strip()
                i += 1
                while i < len(lines) and lines[i].startswith(("  ", "\t")):
                    item += " " + lines[i].strip()
                    i += 1
                items.append(f"<li>{inline(item)}</li>")
            chunks.append("<ul>" + "".join(items) + "</ul>")
            continue
        elif re.match(r"^\d+\. ", line):
            items = []
            while i < len(lines) and re.match(r"^\d+\. ", lines[i]):
                item = re.sub(r"^\d+\. ", "", lines[i]).strip()
                i += 1
                while i < len(lines) and lines[i].startswith(("  ", "\t")):
                    item += " " + lines[i].strip()
                    i += 1
                items.append(f"<li>{inline(item)}</li>")
            chunks.append("<ol>" + "".join(items) + "</ol>")
            continue
        else:
            # A paragraph may be hard-wrapped over several source lines.
            para = [line.strip()]
            i += 1
            while i < len(lines):
                nxt = lines[i].rstrip()
                if not nxt or starts_block(nxt):
                    break
                para.append(nxt.strip())
                i += 1
            chunks.append(f"<p>{inline(' '.join(para))}</p>")
            continue
        i += 1
    return "\n".join(chunks)


def sources_note_html(note: str) -> str:
    text = "Källor till kapitlet finns i källförteckningen längst bak i boken."
    if note:
        text += f" {note[0].upper() + note[1:]}."
    return f'<p class="sources-note">{html.escape(text)}</p>'


def sources_appendix_html(
    per_chapter: list[tuple[str, str, list[str], str]],
    assets_dir: Path,
    assets_prefix: str = "../assets/",
) -> str:
    """One appendix with every chapter's sources, in book order."""
    blocks = [
        f'<section class="sources {SOURCES_KEY}"><h1>{SOURCES_TITLE}</h1>',
        f'<p class="lead">{html.escape(SOURCES_LEAD)}</p>',
    ]
    for num, title, lines, note in per_chapter:
        if not lines:
            continue
        heading = title if num in ("00", "09") else f"Kapitel {num.lstrip('0')} — {title}"
        if note:
            heading += f" <span class='toc-deck'>{html.escape(note[0].upper() + note[1:])}</span>"
        blocks.append(f"<h2>{heading}</h2>")
        blocks.append(md_to_html(lines, assets_dir, skip_first_h1=False, assets_prefix=assets_prefix))
    blocks.append("</section>")
    return "\n".join(blocks)


def build(
    kapitel: Path,
    page_numbers: dict[str, int] | None = None,
    *,
    theme_id: str = DEFAULT_THEME,
    chapters: list[str] | None = None,
    assets_prefix: str = "../assets/",
) -> str:
    """Render the book as one HTML document.

    ``page_numbers`` maps a chapter number ("01"…"09") or SOURCES_KEY to the
    PDF page where that section starts. When given, the table of contents
    shows page numbers. md_till_pdf.py fills it in on a second pass.

    ``theme_id`` selects a colour scheme from ``teman.THEMES``.
    ``chapters`` limits which chapter files are included (e.g. preview sample).
    """
    page_numbers = page_numbers or {}
    theme = THEMES[theme_id]
    chapter_filter = set(chapters) if chapters else None

    def toc_item(label: str, title: str, deck: str, key: str) -> str:
        page = page_numbers.get(key)
        page_html = f'<span class="toc-page">{page}</span>' if page else ""
        return (
            f'<li><span class="toc-num">{html.escape(label)}</span>'
            f'<span class="toc-title">{html.escape(title)}'
            f'<span class="toc-deck">{html.escape(deck)}</span></span>{page_html}</li>'
        )

    toc_items = []
    for num, title, deck in CHAPTER_META:
        if num == "00":
            continue
        label = "Prov" if num == "09" else num.lstrip("0") or "0"
        toc_items.append(toc_item(label, title, deck, num))
    toc_items.append(toc_item("", SOURCES_TITLE, "Lagar, föreskrifter och riktlinjer per kapitel", SOURCES_KEY))

    parts = [
        "<!DOCTYPE html><html lang='sv'><head><meta charset='utf-8'>",
        "<meta name='viewport' content='width=device-width, initial-scale=1'>",
        "<title>Förarbevis snöskoter — Instruktörsverket</title>",
        "<link rel='preconnect' href='https://fonts.googleapis.com'>",
        "<link href='https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,400;8..60,600;8..60,650&display=swap' rel='stylesheet'>",
        f"<style>{book_css(theme)}</style></head><body><div class='page-wrap'>",
        f"""<section class="cover">
          <div class="cover-top">
            <div class="cover-kicker">Instruktörsverket AB · Tänndalen</div>
            <h1>Förarbevis snöskoter</h1>
            <hr class="cover-rule">
            <p class="sub">Utbildningsmaterial</p>
          </div>
          <div class="cover-visual">
            <img src="{assets_prefix}omslag-skoter.jpg" alt="Snöskoter på is vid Tänndalen">
          </div>
          <div class="cover-foot">
            <span>Teori · praktik</span>
            <span>Förarbevis snöskoter</span>
          </div>
        </section>""",
        f"<section class='toc'><h2>Innehåll</h2><ul class='toc-list'>{''.join(toc_items)}</ul></section>",
    ]

    assets_dir = kapitel.parent / "assets"
    all_sources: list[tuple[str, str, list[str], str]] = []
    for name, (num, title, deck) in zip(BOOK_FILES, CHAPTER_META):
        if chapter_filter is not None and num not in chapter_filter:
            continue
        raw_lines = (kapitel / name).read_text(encoding="utf-8").splitlines()
        chapter_lines, source_lines, note = split_sources(raw_lines)
        all_sources.append((num, title, source_lines, note))
        body = md_to_html(chapter_lines, assets_dir, assets_prefix=assets_prefix)
        if source_lines:
            body += "\n" + sources_note_html(note)
        if num == "00":
            parts.append(f"<section class='chapter kap{num}'><div class='hero'><div class='hero-kicker'>Välkommen</div><h1>{html.escape(title)}</h1></div>{body}</section>")
        elif num == "09":
            parts.append(f"<section class='endcard kap{num}'><div class='stamp'>Examination</div><h1>{html.escape(title)}</h1>{body}</section>")
        else:
            n = num.lstrip("0")
            parts.append(
                f"<section class='chapter kap{num}'><div class='hero'><div class='hero-kicker'>Kapitel {n} · {html.escape(deck)}</div>"
                f"<h1>{html.escape(title)}</h1></div>{body}</section>"
            )

    if chapter_filter is None:
        parts.append(sources_appendix_html(all_sources, assets_dir, assets_prefix))
    parts.append("</div></body></html>")
    return "\n".join(parts)


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    out = root / "export" / "Forarbevis-snoskoter.html"
    out.write_text(build(root / "kapitel"), encoding="utf-8")
    print(out)
