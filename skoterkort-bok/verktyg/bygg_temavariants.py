#!/usr/bin/env python3
"""Build colour-scheme preview PDFs for customer comparison.

Creates one sample PDF per theme (cover + contents + förord + chapter 1)
and an index page linking to all variants.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from md_till_html import build
from teman import THEMES

CHROME = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
PREVIEW_CHAPTERS = ["00", "01"]


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


def theme_tabs(path_prefix: str = "") -> str:
    buttons = []
    for i, (theme_id, theme) in enumerate(THEMES.items()):
        active = " active" if i == 0 else ""
        t = theme
        src = f"{path_prefix}{theme_id}-prov.html"
        buttons.append(
            f'<button type="button" class="tab{active}" data-theme="{theme_id}" '
            f'data-src="{src}" '
            f'style="--tab-pine:{t.pine};--tab-moss:{t.moss};--tab-gold:{t.gold}">'
            f"<strong>{theme.name}</strong>"
            f'<span class="tab-desc">{theme.description.split("—")[0].strip()}</span>'
            f'<span class="tab-swatches">'
            f'<i style="background:{t.pine}"></i>'
            f'<i style="background:{t.moss}"></i>'
            f'<i style="background:{t.gold}"></i>'
            f"</span></button>"
        )
    return "\n".join(buttons)


def theme_grid(path_prefix: str = "") -> str:
    panels = []
    for theme_id, theme in THEMES.items():
        src = f"{path_prefix}{theme_id}-prov.html"
        panels.append(
            f'<div class="grid-panel">'
            f'<div class="grid-label"><strong>{theme.name}</strong></div>'
            f'<iframe src="{src}" title="{theme.name}"></iframe>'
            f"</div>"
        )
    return "\n".join(panels)


def build_viewer_html(path_prefix: str = "") -> str:
    first_src = f"{path_prefix}granskog-prov.html"
    return f"""<!DOCTYPE html>
<html lang="sv"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Jämför färgscheman — Förarbevis snöskoter</title>
<style>
  * {{ box-sizing: border-box; }}
  html, body {{ height: 100%; margin: 0; }}
  body {{
    font-family: "Avenir Next", "Segoe UI", sans-serif;
    background: #e8ece9;
    color: #243028;
    display: flex;
    flex-direction: column;
    min-height: 100vh;
  }}
  header {{
    background: #fff;
    border-bottom: 1px solid #d8ddd6;
    padding: 1rem 1.4rem .85rem;
    flex-shrink: 0;
  }}
  header h1 {{ margin: 0; font-size: 1.35rem; }}
  header p {{ margin: .35rem 0 0; color: #5f7068; font-size: .92rem; max-width: 60ch; }}
  .toolbar {{
    display: flex;
    flex-wrap: wrap;
    gap: .55rem;
    padding: .85rem 1.4rem;
    background: #f4f6f4;
    border-bottom: 1px solid #d8ddd6;
    flex-shrink: 0;
    align-items: center;
  }}
  .tabs {{ display: flex; flex-wrap: wrap; gap: .55rem; flex: 1; }}
  .tab {{
    appearance: none;
    border: 2px solid #d8ddd6;
    background: #fff;
    border-radius: 10px;
    padding: .65rem .85rem;
    cursor: pointer;
    text-align: left;
    min-width: 150px;
    transition: border-color .15s, box-shadow .15s;
  }}
  .tab:hover {{ border-color: var(--tab-moss); }}
  .tab.active {{
    border-color: var(--tab-pine);
    box-shadow: 0 0 0 1px var(--tab-pine), 0 4px 14px rgba(0,0,0,.08);
  }}
  .tab strong {{ display: block; font-size: .95rem; color: var(--tab-pine); }}
  .tab-desc {{ display: block; font-size: .72rem; color: #5f7068; margin-top: .15rem; line-height: 1.3; }}
  .tab-swatches {{ display: flex; gap: .25rem; margin-top: .45rem; }}
  .tab-swatches i {{ width: 1.1rem; height: 1.1rem; border-radius: 3px; display: block; }}
  .mode-btn {{
    appearance: none;
    border: 1px solid #c8d0ca;
    background: #fff;
    border-radius: 8px;
    padding: .55rem .9rem;
    font-size: .85rem;
    font-weight: 600;
    cursor: pointer;
    color: #243028;
    white-space: nowrap;
  }}
  .mode-btn.active {{ background: #1f6b4a; color: #fff; border-color: #1f6b4a; }}
  .viewer {{
    flex: 1;
    min-height: 0;
    padding: 1rem 1.4rem 1.4rem;
    display: flex;
  }}
  .viewer iframe {{
    width: 100%;
    height: 100%;
    min-height: calc(100vh - 220px);
    border: 0;
    border-radius: 10px;
    background: #fff;
    box-shadow: 0 8px 32px rgba(0,0,0,.12);
  }}
  .grid-view {{
    display: none;
    flex: 1;
    min-height: 0;
    padding: 1rem 1.4rem 1.4rem;
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
    overflow: auto;
  }}
  .grid-view.visible {{ display: grid; }}
  .single-view.hidden {{ display: none; }}
  .grid-panel {{
    background: #fff;
    border-radius: 10px;
    overflow: hidden;
    box-shadow: 0 4px 18px rgba(0,0,0,.08);
    display: flex;
    flex-direction: column;
    min-height: 480px;
  }}
  .grid-label {{
    padding: .55rem .85rem;
    font-size: .88rem;
    border-bottom: 1px solid #e8ece9;
    background: #fafbfa;
  }}
  .grid-panel iframe {{
    flex: 1;
    width: 100%;
    min-height: 420px;
    border: 0;
  }}
  @media (max-width: 900px) {{
    .grid-view.visible {{ grid-template-columns: 1fr; }}
  }}
</style></head><body>
<header>
  <h1>Jämför färgscheman — Förarbevis snöskoter</h1>
  <p>Klicka på ett tema nedan för att se omslag, innehållsförteckning, förord och kapitel 1. Scrolla i förhandsvisningen för att se hela provet.</p>
</header>
<div class="toolbar">
  <div class="tabs" id="tabs">
{theme_tabs(path_prefix)}
  </div>
  <button type="button" class="mode-btn" id="grid-btn">Visa alla 4</button>
</div>
<div class="viewer single-view" id="single-view">
  <iframe id="preview" src="{first_src}" title="Förhandsvisning"></iframe>
</div>
<div class="grid-view" id="grid-view">
{theme_grid(path_prefix)}
</div>
<script>
  const tabs = document.querySelectorAll('.tab');
  const preview = document.getElementById('preview');
  const singleView = document.getElementById('single-view');
  const gridView = document.getElementById('grid-view');
  const gridBtn = document.getElementById('grid-btn');
  let gridMode = false;

  tabs.forEach(tab => {{
    tab.addEventListener('click', () => {{
      gridMode = false;
      gridBtn.classList.remove('active');
      gridView.classList.remove('visible');
      singleView.classList.remove('hidden');
      tabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      preview.src = tab.dataset.src;
    }});
  }});

  gridBtn.addEventListener('click', () => {{
    gridMode = !gridMode;
    gridBtn.classList.toggle('active', gridMode);
    gridBtn.textContent = gridMode ? 'Visa en i taget' : 'Visa alla 4';
    gridView.classList.toggle('visible', gridMode);
    singleView.classList.toggle('hidden', gridMode);
  }});
</script>
</body></html>"""


def build_index(out_dir: Path, root: Path) -> None:
    (out_dir / "index.html").write_text(build_viewer_html(), encoding="utf-8")
    (root / "export" / "JAMFOR-DESIGNS.html").write_text(
        build_viewer_html("designs/"), encoding="utf-8"
    )


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    kapitel = root / "kapitel"
    out_dir = root / "export" / "designs"
    out_dir.mkdir(parents=True, exist_ok=True)

    if not CHROME.exists():
        sys.exit(
            "Google Chrome hittades inte. Öppna HTML-filerna i export/designs/ "
            "och skriv ut till PDF manuellt (Arkiv → Skriv ut → Spara som PDF)."
        )

    for theme_id, theme in THEMES.items():
        html_path = out_dir / f"{theme_id}-prov.html"
        pdf_path = out_dir / f"{theme_id}-prov.pdf"
        html_path.write_text(
            build(
                kapitel,
                chapters=PREVIEW_CHAPTERS,
                theme_id=theme_id,
                assets_prefix="../../assets/",
            ),
            encoding="utf-8",
        )
        print_pdf(html_path, pdf_path)
        print(f"  {theme.name:10}  {pdf_path.name}")

    build_index(out_dir, root)
    print(f"\nÖppna: {root / 'export' / 'JAMFOR-DESIGNS.html'}")


if __name__ == "__main__":
    main()
