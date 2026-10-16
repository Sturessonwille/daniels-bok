"""Colour themes for the book design."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Theme:
    id: str
    name: str
    description: str
    pine: str
    moss: str
    ice: str
    paper: str
    cream: str
    ink: str
    muted: str
    copper: str
    gold: str
    line: str
    html_bg: str
    cover_bg: str
    cover_ink: str
    cover_title: str
    cover_sub: str
    cover_visual_bg: str
    cover_foot_bg: str
    shadow_border: str
    shadow_glow: str
    hero_from: str
    hero_to: str
    hero_ink: str
    hero_ring: str
    h2_border: str
    th_bg: str
    remember_bg: str
    photo_stripe_a: str
    photo_stripe_b: str
    photo_border: str
    page_footer: str
    page_header: str
    page_chapter: str


THEMES: dict[str, Theme] = {
    "granskog": Theme(
        id="granskog",
        name="Granskog",
        description="Naturlig grön ton — nuvarande utseende. Känns fräsch, utomhus och trovärdig.",
        pine="#1f6b4a",
        moss="#3d8f62",
        ice="#eef8f2",
        paper="#fbfcf9",
        cream="#ffffff",
        ink="#243028",
        muted="#5f7068",
        copper="#d46a2e",
        gold="#d4a017",
        line="#d7e6dc",
        html_bg="#e8eee9",
        cover_bg="#f4faf6",
        cover_ink="#1f4d38",
        cover_title="#1f5c40",
        cover_sub="#4a6b5a",
        cover_visual_bg="#e8f2ec",
        cover_foot_bg="#eef6f1",
        shadow_border="#d8ddd6",
        shadow_glow="rgba(31,107,74,.08)",
        hero_from="#e8f6ee",
        hero_to="#d4edde",
        hero_ink="#1f5c40",
        hero_ring="rgba(212,160,23,.22)",
        h2_border="#dce8e1",
        th_bg="#3d8f62",
        remember_bg="#f8efe8",
        photo_stripe_a="#eef4f0",
        photo_stripe_b="#e4ece7",
        photo_border="#8aa396",
        page_footer="#5f7068",
        page_header="#8aa396",
        page_chapter="#1f6b4a",
    ),
    "arktisk": Theme(
        id="arktisk",
        name="Arktisk",
        description="Djupblått och isblått — vinter, snö och fjäll. Lugn och professionell.",
        pine="#1a4a6b",
        moss="#2d7aab",
        ice="#eef4fa",
        paper="#f9fbfd",
        cream="#ffffff",
        ink="#1e2a35",
        muted="#5a6b78",
        copper="#c45a28",
        gold="#3a9ec4",
        line="#d0dde8",
        html_bg="#e4ebf2",
        cover_bg="#eef4fa",
        cover_ink="#153a55",
        cover_title="#1a4a6b",
        cover_sub="#4a6578",
        cover_visual_bg="#dde8f2",
        cover_foot_bg="#e6eef6",
        shadow_border="#ccd6e0",
        shadow_glow="rgba(26,74,107,.10)",
        hero_from="#e4eef8",
        hero_to="#c8dff0",
        hero_ink="#1a4a6b",
        hero_ring="rgba(58,158,196,.25)",
        h2_border="#ccdbe8",
        th_bg="#2d7aab",
        remember_bg="#f5ece4",
        photo_stripe_a="#eef2f6",
        photo_stripe_b="#e2eaf0",
        photo_border="#8aa8be",
        page_footer="#5a6b78",
        page_header="#8aa8be",
        page_chapter="#1a4a6b",
    ),
    "granit": Theme(
        id="granit",
        name="Granit",
        description="Mörkgrå och skiffer med kopparaccent — modernt, seriöst och tidlöst.",
        pine="#2c3e50",
        moss="#4a6278",
        ice="#f0f2f4",
        paper="#fafafa",
        cream="#ffffff",
        ink="#1a1f24",
        muted="#5c6670",
        copper="#c4703a",
        gold="#b8922a",
        line="#d8dce0",
        html_bg="#e8eaec",
        cover_bg="#f2f3f5",
        cover_ink="#1a2530",
        cover_title="#2c3e50",
        cover_sub="#5c6670",
        cover_visual_bg="#e4e8ec",
        cover_foot_bg="#eceef0",
        shadow_border="#cdd2d8",
        shadow_glow="rgba(44,62,80,.10)",
        hero_from="#eceef2",
        hero_to="#d8dde4",
        hero_ink="#2c3e50",
        hero_ring="rgba(196,112,58,.20)",
        h2_border="#d0d6dc",
        th_bg="#4a6278",
        remember_bg="#f8f0ea",
        photo_stripe_a="#f0f2f4",
        photo_stripe_b="#e6e8ec",
        photo_border="#9aa4ae",
        page_footer="#5c6670",
        page_header="#9aa4ae",
        page_chapter="#2c3e50",
    ),
    "bjork": Theme(
        id="bjork",
        name="Björk",
        description="Varm björk och bärnsten — jordnära, inbjudande och lättläst.",
        pine="#5c4030",
        moss="#8b6914",
        ice="#faf6ef",
        paper="#fdfbf7",
        cream="#ffffff",
        ink="#2a2218",
        muted="#6b5c4a",
        copper="#c45a28",
        gold="#c4922a",
        line="#e8dfd0",
        html_bg="#ede8df",
        cover_bg="#faf6ef",
        cover_ink="#3d2e20",
        cover_title="#5c4030",
        cover_sub="#6b5c4a",
        cover_visual_bg="#f0e8dc",
        cover_foot_bg="#f5efe6",
        shadow_border="#ddd4c8",
        shadow_glow="rgba(92,64,48,.10)",
        hero_from="#f8f0e4",
        hero_to="#ede0cc",
        hero_ink="#5c4030",
        hero_ring="rgba(196,146,42,.22)",
        h2_border="#e4d8c8",
        th_bg="#8b6914",
        remember_bg="#f8efe4",
        photo_stripe_a="#f6f0e8",
        photo_stripe_b="#ece4d8",
        photo_border="#b0a090",
        page_footer="#6b5c4a",
        page_header="#b0a090",
        page_chapter="#5c4030",
    ),
}

DEFAULT_THEME = "granskog"


def css_vars(theme: Theme) -> str:
    """Generate :root CSS custom properties for a theme."""
    return f""":root {{
  --pine: {theme.pine};
  --moss: {theme.moss};
  --ice: {theme.ice};
  --paper: {theme.paper};
  --cream: {theme.cream};
  --ink: {theme.ink};
  --muted: {theme.muted};
  --copper: {theme.copper};
  --gold: {theme.gold};
  --line: {theme.line};
  --html-bg: {theme.html_bg};
  --cover-bg: {theme.cover_bg};
  --cover-ink: {theme.cover_ink};
  --cover-title: {theme.cover_title};
  --cover-sub: {theme.cover_sub};
  --cover-visual-bg: {theme.cover_visual_bg};
  --cover-foot-bg: {theme.cover_foot_bg};
  --shadow-border: {theme.shadow_border};
  --shadow-glow: {theme.shadow_glow};
  --hero-from: {theme.hero_from};
  --hero-to: {theme.hero_to};
  --hero-ink: {theme.hero_ink};
  --hero-ring: {theme.hero_ring};
  --h2-border: {theme.h2_border};
  --th-bg: {theme.th_bg};
  --remember-bg: {theme.remember_bg};
  --photo-stripe-a: {theme.photo_stripe_a};
  --photo-stripe-b: {theme.photo_stripe_b};
  --photo-border: {theme.photo_border};
  --page-footer: {theme.page_footer};
  --page-header: {theme.page_header};
  --page-chapter: {theme.page_chapter};
}}"""
