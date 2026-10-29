"""Fluent-inspired spatial theme for NexusSearch (dark / light + collapsed nav)."""

from __future__ import annotations

from typing import Dict, Optional

import streamlit as st


_PALETTES: Dict[str, Dict[str, str]] = {
    "dark": {
        "accent": "#0078d4",
        "accent_hover": "#106ebe",
        "accent_soft": "rgba(0, 120, 212, 0.14)",
        "surface": "#1e293b",
        "surface_elevated": "#243044",
        "border": "rgba(255, 255, 255, 0.08)",
        "border_strong": "rgba(255, 255, 255, 0.12)",
        "text": "#f3f4f6",
        "text_muted": "#9ca3af",
        "bg": "#0b1220",
        "bg_alt": "#111827",
        "sidebar_bg": "linear-gradient(180deg, #0c1628 0%, #111827 100%)",
        "hero_bg": "rgba(30, 41, 59, 0.45)",
        "glass_metric_bg": "rgba(30, 41, 59, 0.5)",
        "body_muted": "#d1d5db",
        "tagline": "#cbd5e1",
        "chip_bg": "rgba(15, 23, 42, 0.6)",
    },
    "light": {
        "accent": "#0078d4",
        "accent_hover": "#106ebe",
        "accent_soft": "rgba(0, 120, 212, 0.12)",
        "surface": "#ffffff",
        "surface_elevated": "#ffffff",
        "border": "rgba(15, 23, 42, 0.12)",
        "border_strong": "rgba(15, 23, 42, 0.18)",
        "text": "#0f172a",
        "text_muted": "#334155",
        "bg": "#f0f4f8",
        "bg_alt": "#e8eef4",
        "sidebar_bg": "linear-gradient(180deg, #ffffff 0%, #f3f4f6 100%)",
        "hero_bg": "rgba(255, 255, 255, 0.92)",
        "glass_metric_bg": "rgba(255, 255, 255, 0.95)",
        "body_muted": "#1e293b",
        "tagline": "#0f172a",
        "chip_bg": "#f3f4f6",
    },
}


def get_theme() -> str:
    t = st.session_state.get("ns_theme", "dark")
    return t if t in _PALETTES else "dark"


def render_theme_toggle() -> None:
    st.markdown('<div class="ns-theme-toggle-wrap">', unsafe_allow_html=True)
    current = get_theme()
    choice = st.radio(
        "Appearance",
        options=["dark", "light"],
        format_func=lambda x: "Dark Fluent" if x == "dark" else "Light Fluent",
        index=0 if current == "dark" else 1,
        horizontal=True,
        key="ns_theme_control",
        label_visibility="collapsed",
    )
    st.caption("Theme")
    if choice != current:
        st.session_state["ns_theme"] = choice
        from frontend.components.theme_storage import persist_theme_choice

        persist_theme_choice(choice)
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


def inject_enterprise_theme(theme: str | None = None) -> None:
    theme = theme or get_theme()
    p = _PALETTES[theme]
    nav_link_color = "#cbd5e1" if theme == "dark" else "#0f172a"
    status_ok_color = "#86efac" if theme == "dark" else "#166534"
    theme_marker = "ns-theme-light" if theme == "light" else "ns-theme-dark"
    light_streamlit_fix = ""
    sidebar_brand_bg = "#0c1628" if theme == "dark" else "#ffffff"
    nav_hover_bg = "rgba(255, 255, 255, 0.06)" if theme == "dark" else "rgba(0, 0, 0, 0.06)"
    search_hint_idle = "transparent" if theme == "dark" else "#64748b"
    search_hint_active = "#94a3b8" if theme == "dark" else "#334155"

    btn_secondary_bg = "#ffffff" if theme == "light" else "#1e293b"
    btn_secondary_text = p["text"]
    btn_secondary_border = "rgba(15, 23, 42, 0.22)" if theme == "light" else p["border_strong"]
    btn_secondary_hover_bg = "#f0f9ff" if theme == "light" else "#334155"
    btn_primary_fg = "#ffffff"

    if theme == "light":
        light_streamlit_fix = f"""
    /* Light theme: high-contrast text (Streamlit defaults are often light-on-light) */
    .stApp, .stApp section.main {{
        color: {p["text"]} !important;
    }}
    .stApp p, .stApp li, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp strong,
    .stApp [data-testid="stMarkdownContainer"] p,
    .stApp [data-testid="stMarkdownContainer"] li,
    .stApp [data-testid="stMarkdownContainer"] span,
    .stApp [data-testid="stHeader"],
    .stApp label, .stApp [data-testid="stWidgetLabel"] p,
    .stApp [data-testid="stExpander"] details summary,
    .stApp [data-testid="stExpander"] p,
    .stApp [data-testid="stTabs"] button {{
        color: {p["text"]} !important;
    }}
    .stApp .stCaption, .stApp [data-testid="stCaptionContainer"] {{
        color: {p["text_muted"]} !important;
    }}
    .stApp [data-testid="stMetricValue"] {{ color: {p["text"]} !important; }}
    .stApp [data-testid="stMetricLabel"] {{ color: {p["text_muted"]} !important; }}
    .stApp input, .stApp textarea {{
        color: {p["text"]} !important;
        -webkit-text-fill-color: {p["text"]} !important;
        background-color: #ffffff !important;
    }}

    [data-testid="stSidebar"] {{
        background: #f8fafc !important;
    }}
    [data-testid="stSidebar"] [data-testid="stSidebarNav"] {{
        position: relative;
        z-index: 40;
    }}
    [data-testid="stSidebar"] [data-testid="stSidebarNav"] a,
    [data-testid="stSidebar"] [data-testid="stSidebarNav"] a span,
    [data-testid="stSidebar"] [data-testid="stSidebarNav"] a p,
    [data-testid="stSidebar"] [data-testid="stSidebarNav"] a [data-testid="stMarkdownContainer"],
    [data-testid="stSidebar"] [data-testid="stSidebarNav"] a [data-testid="stMarkdownContainer"] p {{
        color: {p["text"]} !important;
        opacity: 1 !important;
        -webkit-text-fill-color: {p["text"]} !important;
    }}
    [data-testid="stSidebar"] [data-testid="stSidebarNav"] a[aria-current="page"],
    [data-testid="stSidebar"] [data-testid="stSidebarNav"] a[aria-current="page"] span,
    [data-testid="stSidebar"] [data-testid="stSidebarNav"] a[aria-current="page"] p {{
        color: {p["accent"]} !important;
        -webkit-text-fill-color: {p["accent"]} !important;
    }}
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stCaption, [data-testid="stSidebar"] .stRadio label {{
        color: {p["text"]} !important;
    }}
    .ns-about-lead strong {{ color: {p["text"]} !important; }}
    .ns-search-hint {{
        color: {search_hint_active} !important;
        opacity: 0.92 !important;
    }}
    .kp-title {{ color: {p["text_muted"]} !important; }}

    .stButton > button,
    .stButton > button[kind="secondary"],
    [data-testid="stBaseButton-secondary"] {{
        background-color: {btn_secondary_bg} !important;
        color: {btn_secondary_text} !important;
        border: 1px solid {btn_secondary_border} !important;
    }}
    .stButton > button p,
    .stButton > button span,
    .stButton > button div,
    [data-testid="stBaseButton-secondary"] p {{
        color: {btn_secondary_text} !important;
    }}
    .stButton > button:hover,
    [data-testid="stBaseButton-secondary"]:hover {{
        background-color: {btn_secondary_hover_bg} !important;
        color: {p["accent"]} !important;
        border-color: {p["accent"]} !important;
    }}
    .stButton > button[kind="primary"],
    .stButton > button[kind="primary"] p,
    .stButton > button[kind="primary"] span {{
        color: {btn_primary_fg} !important;
    }}
    .ns-help-btn .stButton > button {{
        background-color: {btn_secondary_bg} !important;
        color: {btn_secondary_text} !important;
        border: 1px solid {btn_secondary_border} !important;
        font-weight: 700 !important;
    }}
    """
    badge_muted_bg = "rgba(55, 65, 81, 0.5)" if theme == "dark" else "rgba(229, 231, 235, 0.9)"
    badge_accent_color = "#7dd3fc" if theme == "dark" else "#0369a1"
    score_color = "#38bdf8" if theme == "dark" else "#0078d4"
    shadow = "0.2" if theme == "dark" else "0.08"
    home_pro_wordmark_grad = (
        "linear-gradient(165deg, #c4cbff 0%, #a5adf8 38%, #939ef5 68%, #b0b8ff 100%)"
        if theme == "dark"
        else "linear-gradient(165deg, #b8c0ff 0%, #9ba4f6 32%, #8b96f0 58%, #a3acf7 100%)"
    )
    home_glass_show = theme == "light"

    st.markdown(
        f"""
<div class="{theme_marker}" hidden aria-hidden="true"></div>
<style>
    html, body, [class*="css"] {{
        font-family: "Segoe UI", system-ui, -apple-system, Roboto, sans-serif;
    }}
    {light_streamlit_fix}

    .stApp {{
        background: linear-gradient(165deg, {p["bg"]} 0%, {p["bg_alt"]} 42%, {p["bg"]} 100%);
        background-size: 200% 200%;
        animation: ns-bg-shift 22s ease-in-out infinite;
    }}
    @keyframes ns-bg-shift {{
        0%, 100% {{ background-position: 0% 40%; }}
        50% {{ background-position: 100% 60%; }}
    }}

    .block-container {{
        padding-top: 1.25rem;
        padding-bottom: 3rem;
        max-width: 1080px;
    }}

    [data-testid="stSidebar"] {{
        position: relative;
        padding-top: 9.75rem !important;
        background: {p["sidebar_bg"]} !important;
        border-right: 1px solid {p["border_strong"]};
        box-shadow: 4px 0 24px rgba(0, 0, 0, {shadow});
        transition: min-width 0.35s cubic-bezier(0.4, 0, 0.2, 1),
                    width 0.35s cubic-bezier(0.4, 0, 0.2, 1);
    }}
    [data-testid="stSidebar"] > div:first-child {{
        position: relative;
        z-index: 35;
    }}

    [data-testid="stSidebarNav"] {{
        position: relative;
        z-index: 40;
    }}
    [data-testid="stSidebarNav"] ul {{ gap: 2px; }}

    [data-testid="stSidebarNav"] a {{
        border-radius: 6px !important;
        margin: 0 0.5rem !important;
        padding: 0.5rem 0.65rem !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
        color: {nav_link_color} !important;
        white-space: nowrap !important;
        transition: background 0.2s ease, color 0.2s ease, transform 0.2s ease, box-shadow 0.2s ease;
    }}
    [data-testid="stSidebar"] .stRadio label,
    [data-testid="stSidebar"] .stRadio label p {{
        white-space: nowrap !important;
    }}
    [data-testid="stSidebarNav"] a:hover {{
        background: {nav_hover_bg} !important;
        color: {p["text"]} !important;
        transform: translateX(3px);
    }}
    [data-testid="stSidebarNav"] a[aria-current="page"] {{
        background: {p["accent_soft"]} !important;
        color: {p["accent"]} !important;
        box-shadow: inset 3px 0 0 {p["accent"]};
    }}

    /* Collapsed: icons only — sit below brand / header (dark + light Fluent) */
    [data-testid="stSidebar"][aria-expanded="false"] {{
        min-width: 4.75rem !important;
        padding-top: 16.25rem !important;
    }}
    [data-testid="stSidebar"][aria-expanded="false"] [data-testid="stSidebarNav"] {{
        margin-top: 1.15rem;
    }}
    [data-testid="stSidebar"][aria-expanded="false"] [data-testid="stSidebarNav"] a {{
        justify-content: center !important;
        margin: 0 0.35rem !important;
        padding: 0.55rem !important;
    }}
    [data-testid="stSidebar"][aria-expanded="false"] [data-testid="stSidebarNav"] a span {{
        margin: 0 !important;
    }}
    [data-testid="stSidebar"][aria-expanded="false"] [data-testid="stSidebarNav"] a p,
    [data-testid="stSidebar"][aria-expanded="false"] [data-testid="stSidebarNav"] a [data-testid="stMarkdownContainer"],
    [data-testid="stSidebar"][aria-expanded="false"] [data-testid="stSidebarNav"] a span:not(:first-child) {{
        display: none !important;
    }}

    [data-testid="stSidebar"]::before {{
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4.5rem;
        background: {sidebar_brand_bg};
        border-bottom: 1px solid {p["border"]};
        z-index: 20;
        pointer-events: none;
    }}
    [data-testid="stSidebar"]::after {{
        content: "";
        position: absolute;
        top: 4.35rem;
        left: 0;
        right: 0;
        height: 2.25rem;
        padding: 0.35rem 1rem 0;
        font-size: 1.02rem;
        font-weight: 500;
        color: {p["text_muted"]};
        background: {sidebar_brand_bg};
        border-bottom: 1px solid {p["border"]};
        z-index: 20;
        box-sizing: border-box;
        pointer-events: none;
    }}

    .ns-theme-toggle-wrap {{
        margin-top: 2.5rem;
        padding: 0.75rem 0 1rem;
        border-top: 1px solid {p["border"]};
    }}
    html:has([data-testid="stSidebar"][aria-expanded="false"]) .ns-theme-toggle-wrap {{
        display: none;
    }}

    .ns-brand-expanded,
    .ns-brand-collapsed {{
        display: none;
        position: fixed;
        z-index: 1000001;
        pointer-events: none;
    }}
    .ns-brand-expanded {{
        top: 1.85rem;
        left: 1rem;
        max-width: 18rem;
    }}
    .ns-brand-collapsed {{
        top: 3.45rem;
        left: 3.75rem;
    }}
    html:has([data-testid="stSidebar"][aria-expanded="true"]) .ns-brand-expanded {{
        display: block;
    }}
    html:has([data-testid="stSidebar"][aria-expanded="false"]) .ns-brand-collapsed {{
        display: block;
    }}
    .ns-brand-title-row {{
        display: flex;
        align-items: center;
        gap: 0.45rem;
        flex-wrap: nowrap;
    }}
    .ns-brand-wordmark {{
        font-size: 1.95rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        color: {p["text"]};
        line-height: 1.15;
        white-space: nowrap;
    }}
    .ns-brand-icon {{
        width: 2rem;
        height: 2rem;
        object-fit: contain;
        flex-shrink: 0;
    }}
    .ns-brand-caption {{
        font-size: 1.02rem;
        font-weight: 500;
        color: {p["text_muted"]};
        margin-top: 0.2rem;
        line-height: 1.2;
    }}

    [data-testid="stForm"]:has(input[placeholder*="Search corpus"]) [data-testid="stFormSubmitButton"] {{
        display: none !important;
        height: 0 !important;
        overflow: hidden !important;
    }}

    .stTextInput input,
    .stTextArea textarea,
    .stSelectbox [data-baseweb="select"] {{
        transition: box-shadow 0.2s ease, border-color 0.2s ease !important;
    }}
    .stTextInput input:focus,
    .stTextArea textarea:focus {{
        box-shadow: 0 0 0 2px {p["accent_soft"]}, 0 0 12px rgba(0, 120, 212, 0.2) !important;
    }}

    .ns-search-hint {{
        font-size: 0.65rem;
        text-align: right;
        margin-top: 0.1rem;
        color: {search_hint_idle};
        transition: color 0.12s ease, opacity 0.12s ease;
    }}
    .ns-search-block:hover .ns-search-hint,
    .ns-search-block:focus-within .ns-search-hint {{
        color: {search_hint_active} !important;
        opacity: 1 !important;
    }}

    .ns-page-title {{ font-size: 1.75rem; font-weight: 600; color: {p["text"]}; margin: 0; }}
    .ns-page-sub {{ color: {p["text_muted"]}; font-size: 0.95rem; margin-top: 0.35rem; }}
    .ns-page-header {{ margin-bottom: 1.5rem; }}
    .ns-page-header.ns-anim-page-in {{
        animation: ns-fade-up 0.55s cubic-bezier(0.22, 1, 0.36, 1) both;
    }}
    .ns-section-label {{
        font-size: 0.72rem; font-weight: 600; text-transform: uppercase;
        letter-spacing: 0.06em; color: {p["text_muted"]}; margin: 1.5rem 0 0.65rem;
    }}
    .ns-section-label.ns-anim-section::after {{
        content: "";
        display: block;
        width: 2.75rem;
        height: 2px;
        margin-top: 0.4rem;
        border-radius: 2px;
        background: linear-gradient(90deg, {p["accent"]}, transparent);
        animation: ns-line-grow 0.75s cubic-bezier(0.22, 1, 0.36, 1) both;
    }}
    @keyframes ns-line-grow {{
        from {{ width: 0; opacity: 0; }}
        to {{ width: 2.75rem; opacity: 1; }}
    }}

    .ns-hero {{
        text-align: center;
        padding: 2.5rem 1.5rem 2rem;
        margin: 0 auto 1.75rem;
        max-width: 860px;
        border-radius: 12px;
        background: {p["hero_bg"]};
        backdrop-filter: blur(12px);
        border: 1px solid {p["border_strong"]};
        box-shadow: 0 8px 32px rgba(0, 0, 0, {shadow});
    }}
    .ns-hero.ns-anim-hero {{
        position: relative;
        overflow: hidden;
        animation: ns-fade-up 0.65s cubic-bezier(0.22, 1, 0.36, 1) both;
    }}
    .ns-hero.ns-anim-hero::after {{
        content: "";
        position: absolute;
        inset: 0;
        pointer-events: none;
        background: linear-gradient(
            105deg,
            transparent 38%,
            rgba(0, 120, 212, 0.08) 48%,
            transparent 58%
        );
        background-size: 220% 100%;
        animation: ns-hero-shine 7s ease-in-out infinite;
    }}
    @keyframes ns-hero-shine {{
        0%, 100% {{ background-position: 120% 0; opacity: 0.5; }}
        50% {{ background-position: -20% 0; opacity: 0.85; }}
    }}
    .ns-glass-metric-row {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
        gap: 0.75rem;
        margin: 0 0 1.5rem;
    }}
    .ns-glass-metric {{
        padding: 1rem 1.1rem;
        border-radius: 10px;
        background: {p["glass_metric_bg"]};
        backdrop-filter: blur(10px);
        border: 1px solid {p["border"]};
        transition: transform 0.22s ease, box-shadow 0.22s ease, border-color 0.22s ease;
    }}
    .ns-glass-metric.ns-anim-metric {{
        animation: ns-fade-up 0.55s cubic-bezier(0.22, 1, 0.36, 1) both;
    }}
    .ns-glass-metric.ns-anim-metric:hover {{
        transform: translateY(-2px);
        border-color: rgba(0, 120, 212, 0.35);
        box-shadow: 0 10px 28px rgba(0, 0, 0, {shadow});
    }}
    .ns-metric-value {{
        font-size: 1.65rem;
        font-weight: 600;
        color: {p["text"]};
        font-variant-numeric: tabular-nums;
    }}
    .ns-metric-label {{ font-size: 0.78rem; color: {p["text_muted"]}; margin-top: 0.25rem; }}

    .ns-tagline {{ color: {p["tagline"]}; font-size: 1.1rem; margin: 0; font-weight: 500; }}
    .ns-badge-row {{ display: flex; flex-wrap: wrap; gap: 0.5rem; justify-content: center; margin-top: 1.1rem; }}
    .ns-badge {{
        padding: 0.3rem 0.75rem; border-radius: 4px; font-size: 0.72rem; font-weight: 600;
        background: {p["accent_soft"]}; color: {badge_accent_color};
        border: 1px solid rgba(0, 120, 212, 0.35);
        animation: ns-fade-up 0.5s cubic-bezier(0.22, 1, 0.36, 1) both;
    }}
    .ns-badge-row .ns-badge:nth-child(1) {{ animation-delay: 0.12s; }}
    .ns-badge-row .ns-badge:nth-child(2) {{ animation-delay: 0.2s; }}
    .ns-badge-row .ns-badge:nth-child(3) {{ animation-delay: 0.28s; }}
    .ns-badge-muted {{
        background: {badge_muted_bg}; color: {p["text"] if theme == "light" else p["text_muted"]};
        border-color: {p["border"]}; font-weight: 500;
    }}

    .ns-workflow-panel {{
        background: {p["surface_elevated"]};
        border: 1px solid {p["border"]};
        border-radius: 8px;
        padding: 1.15rem 1.25rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, {shadow});
        transition: transform 0.22s ease, box-shadow 0.22s ease, border-color 0.22s ease;
    }}
    .ns-workflow-panel.ns-anim-panel {{
        animation: ns-fade-up 0.6s cubic-bezier(0.22, 1, 0.36, 1) both;
    }}
    .ns-workflow-panel.ns-anim-panel:hover {{
        transform: translateY(-3px);
        border-color: rgba(0, 120, 212, 0.28);
        box-shadow: 0 10px 24px rgba(0, 0, 0, {shadow});
    }}
    .ns-about-panel.ns-anim-fade-up,
    .ns-anim-fade-up {{
        animation: ns-fade-up 0.65s cubic-bezier(0.22, 1, 0.36, 1) 0.15s both;
    }}
    @keyframes ns-fade-up {{
        from {{ opacity: 0; transform: translateY(10px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    .ns-workflow-panel h4 {{ color: {p["text"]}; margin: 0 0 0.65rem; font-size: 0.95rem; }}
    .ns-workflow-panel ol, .ns-workflow-panel p {{
        color: {p["body_muted"]}; font-size: 0.88rem; line-height: 1.55;
    }}

    .ns-home-gap {{ height: 2.75rem; }}

    /* Home — open Contra-style hero (no boxed panel) */
    .ns-home-page {{
        margin-top: -0.35rem;
        position: relative;
    }}
    .stApp:has(.ns-home-page),
    .stApp:has(.ns-home-page) [data-testid="stAppViewContainer"],
    .stApp:has(.ns-home-page) .main {{
        background: {"linear-gradient(165deg, #d4dce6 0%, #e2e9f0 28%, #eef2f6 55%, #e8edf3 100%)" if theme == "light" else "linear-gradient(165deg, #0a101c 0%, #0f172a 50%, #0b1220 100%)"} !important;
        animation: none !important;
        background-size: 100% 100% !important;
    }}
    section.main .block-container:has(.ns-home-page) {{
        max-width: none !important;
        width: 100% !important;
        padding-left: clamp(0.65rem, 1.5vw, 1.15rem) !important;
        padding-right: clamp(0.65rem, 1.5vw, 1.15rem) !important;
        padding-top: 1rem !important;
        position: relative;
    }}
    .stApp .main .block-container:has(.ns-home-page),
    .stApp [data-testid="stMainBlockContainer"]:has(.ns-home-page) {{
        max-width: none !important;
        width: 100% !important;
    }}
    section.main:has(.ns-home-page) {{
        padding-left: 0 !important;
        padding-right: 0 !important;
        padding-top: 0 !important;
        background: {"linear-gradient(165deg, #d4dce6 0%, #e2e9f0 28%, #eef2f6 55%, #e8edf3 100%)" if theme == "light" else "linear-gradient(165deg, #0a101c 0%, #0f172a 50%, #0b1220 100%)"};
    }}
    section.main:has(.ns-home-page) .ns-app-top-chrome {{
        position: absolute;
        top: 0.15rem;
        right: clamp(0.65rem, 1.5vw, 1.15rem);
        z-index: 30;
        width: min(340px, 48vw);
        margin: 0 !important;
        padding: 0 !important;
        pointer-events: none;
    }}
    section.main:has(.ns-home-page) .ns-app-top-chrome [data-testid="column"] {{
        pointer-events: auto;
    }}
    section.main:has(.ns-home-page) .ns-app-top-chrome [data-testid="stHorizontalBlock"] {{
        gap: 0 !important;
        margin: 0 !important;
    }}
    section.main:has(.ns-home-page) .ns-app-top-chrome [data-testid="stHorizontalBlock"] > div[data-testid="column"]:first-child {{
        display: none !important;
    }}
    section.main:has(.ns-home-page) .ns-app-top-chrome [data-testid="stHorizontalBlock"] > div[data-testid="column"]:last-child {{
        width: 100% !important;
        min-width: 0 !important;
        flex: 1 1 100% !important;
    }}
    section.main:has(.ns-home-page) .ns-topbar-row {{
        margin-bottom: 0 !important;
    }}
    section.main:has(.ns-home-page) .ns-search-block input {{
        background: {"rgba(255, 255, 255, 0.78)" if theme == "light" else "rgba(30, 41, 59, 0.72)"} !important;
        backdrop-filter: blur(10px);
        border: 1px solid {p["border_strong"]} !important;
    }}
    .ns-theme-light section.main:has(.ns-home-page) .block-container {{
        padding-top: 1rem !important;
    }}
    .ns-home-landing {{
        position: relative;
        padding: 0 0 1rem;
        width: 100%;
        margin-top: -1.85rem;
    }}
    .ns-home-bg-decor {{
        position: absolute;
        top: -5.5rem;
        left: 0;
        right: 0;
        height: min(780px, 98vh);
        pointer-events: none;
        overflow: visible;
        z-index: 0;
        width: 100%;
        perspective: 900px;
        perspective-origin: 55% 35%;
    }}
    .ns-home-glass {{
        position: absolute;
        pointer-events: none;
        transform-style: preserve-3d;
        opacity: {"1" if home_glass_show else "0.4"};
    }}
    .ns-home-glass--torus::before {{
        content: "";
        position: absolute;
        inset: 0;
        border-radius: 50%;
        padding: clamp(14px, 2.2vw, 26px);
        background: conic-gradient(
            from 210deg,
            rgba(165, 243, 252, 0.95),
            rgba(196, 181, 253, 0.9),
            rgba(251, 207, 232, 0.85),
            rgba(253, 230, 138, 0.88),
            rgba(153, 246, 228, 0.9),
            rgba(129, 140, 248, 0.92),
            rgba(165, 243, 252, 0.95)
        );
        -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
        -webkit-mask-composite: xor;
        mask-composite: exclude;
        box-shadow:
            inset 0 0 35px rgba(255, 255, 255, 0.75),
            inset -10px -14px 28px rgba(255, 255, 255, 0.45),
            0 28px 55px rgba(99, 102, 241, 0.18),
            0 12px 24px rgba(236, 72, 153, 0.08);
        filter: drop-shadow(0 18px 32px rgba(129, 140, 248, 0.22));
    }}
    .ns-home-glass--disc {{
        border-radius: 50%;
        background: radial-gradient(
            circle at 32% 28%,
            rgba(255, 255, 255, 0.95) 0%,
            rgba(186, 230, 253, 0.55) 28%,
            rgba(196, 181, 253, 0.42) 52%,
            rgba(251, 207, 232, 0.25) 72%,
            transparent 88%
        );
        box-shadow:
            inset 0 -8px 24px rgba(255, 255, 255, 0.5),
            inset 0 12px 20px rgba(255, 255, 255, 0.65),
            0 22px 45px rgba(99, 102, 241, 0.14);
        border: 1px solid rgba(255, 255, 255, 0.55);
    }}
    .ns-home-glass--1 {{
        width: min(340px, 42vw);
        height: min(340px, 42vw);
        top: 2%;
        right: -4%;
        transform: rotateX(58deg) rotateZ(-22deg);
    }}
    .ns-home-glass--2 {{
        width: min(220px, 28vw);
        height: min(220px, 28vw);
        top: 32%;
        right: 18%;
        transform: rotateX(52deg) rotateZ(18deg);
    }}
    .ns-home-glass--3 {{
        width: min(160px, 20vw);
        height: min(160px, 20vw);
        bottom: 12%;
        right: 6%;
        transform: rotateX(48deg) rotateZ(-8deg);
    }}
    .ns-home-glow--right {{
        position: absolute;
        top: -5%;
        right: -8%;
        width: min(62vw, 560px);
        height: min(62vw, 560px);
        border-radius: 50%;
        background: {"radial-gradient(circle at 40% 40%, rgba(186, 230, 253, 0.65) 0%, rgba(196, 181, 253, 0.28) 38%, rgba(253, 230, 138, 0.1) 58%, transparent 74%)" if theme == "light" else "radial-gradient(circle, rgba(0, 120, 212, 0.12), transparent 70%)"};
        filter: blur(12px);
        z-index: -1;
    }}
    .ns-home-hero-grid {{
        position: relative;
        z-index: 1;
        display: grid;
        grid-template-columns: minmax(0, 1.12fr) minmax(260px, 0.88fr);
        gap: clamp(0.75rem, 1.8vw, 1.35rem);
        align-items: start;
        width: 100%;
        min-height: 0;
        padding: 0;
    }}
    @media (max-width: 860px) {{
        .ns-home-hero-grid {{
            grid-template-columns: 1fr;
            min-height: 0;
        }}
        .ns-home-visual {{
            min-height: 300px !important;
        }}
        .ns-home-bg-decor {{
            height: 520px;
        }}
    }}
    .ns-home-hero-actions {{
        position: relative;
        z-index: 1;
        width: 100%;
        max-width: min(520px, 100%);
        padding: 0.25rem 0 0.5rem;
    }}
    .stApp:has(.ns-home-page) [data-testid="stPageLink"] {{
        width: fit-content !important;
        max-width: max-content !important;
        margin: 0.35rem 0 0.15rem;
    }}
    .stApp:has(.ns-home-page) [data-testid="stPageLink"] a {{
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        width: auto !important;
        max-width: max-content !important;
        background: #0c0c0c !important;
        background-color: #0c0c0c !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        text-decoration: none !important;
        border: none !important;
        border-radius: 999px !important;
        font-weight: 700 !important;
        font-size: 0.92rem !important;
        letter-spacing: -0.01em;
        padding: 0.72rem 1.65rem !important;
        min-height: 2.75rem;
        box-shadow: none !important;
        transition: background 0.15s ease, transform 0.15s ease, color 0.15s ease !important;
    }}
    .stApp:has(.ns-home-page) [data-testid="stPageLink"] a span,
    .stApp:has(.ns-home-page) [data-testid="stPageLink"] a p {{
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }}
    .stApp:has(.ns-home-page) [data-testid="stPageLink"] a:hover {{
        background: #1a1a1a !important;
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        border: none !important;
        transform: translateY(-1px);
    }}
    .ns-home-value-list {{
        margin: 1.1rem 0 0;
        padding: 0 0 0 1.15rem;
        color: {p["body_muted"]};
        font-size: 0.88rem;
        line-height: 1.55;
        max-width: 40rem;
    }}
    .ns-home-value-list li {{
        margin-bottom: 0.45rem;
    }}
    .ns-home-copy {{
        padding: 0.25rem 0;
        max-width: none;
        text-align: left;
    }}
    .ns-home-pill {{
        display: inline-block;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.02em;
        color: {p["text_muted"]};
        background: {p["chip_bg"]};
        border: 1px solid {p["border"]};
        border-radius: 999px;
        padding: 0.35rem 0.85rem;
        margin-bottom: 0.4rem;
    }}
    .ns-home-title {{
        margin: 0 0 0.85rem;
        padding: 0;
        font-weight: inherit;
        line-height: 1;
    }}
    .ns-home-title-line {{
        display: flex;
        flex-wrap: wrap;
        align-items: baseline;
        column-gap: 0.28em;
        row-gap: 0.08em;
        font-size: clamp(2.15rem, 4.8vw, 3.15rem);
        font-weight: 650;
        letter-spacing: -0.03em;
        color: {p["text"]};
    }}
    .ns-home-title-sans {{
        font-family: "Segoe UI", system-ui, -apple-system, Roboto, sans-serif;
        font-weight: 650;
        line-height: 1.05;
    }}
    .ns-home-title-em {{
        font-family: "Instrument Serif", Georgia, "Times New Roman", serif;
        font-style: italic;
        font-weight: 400;
        font-size: 1.02em;
        line-height: 1;
        letter-spacing: -0.02em;
        transform: translateY(0.02em);
    }}
    .ns-home-lead {{
        font-size: 1.02rem;
        line-height: 1.55;
        color: {p["text_muted"]};
        margin: 0 0 1.35rem;
        max-width: 38rem;
    }}
    .ns-home-proof {{
        font-size: 0.82rem;
        color: {p["text_muted"]};
        margin: 0.85rem 0 0;
    }}
    .ns-home-visual {{
        position: relative;
        min-height: 300px;
        height: auto;
        display: flex;
        align-items: flex-start;
        justify-content: flex-end;
        padding: 0.15rem 0 0;
        isolation: isolate;
    }}
    .ns-home-blob {{
        display: none;
    }}
    .ns-home-pro-stack {{
        position: relative;
        width: min(100%, 380px);
        z-index: 2;
        padding-bottom: 1.5rem;
    }}
    .ns-home-pro-card {{
        position: relative;
        z-index: 1;
        background: {"#ffffff" if theme == "light" else p["surface_elevated"]};
        border-radius: 20px;
        padding: 1.35rem 1.35rem 1.15rem;
        box-shadow: 0 22px 55px rgba(15, 23, 42, {shadow}), 0 2px 8px rgba(15, 23, 42, 0.04);
        border: 1px solid {"rgba(255,255,255,0.9)" if theme == "light" else p["border_strong"]};
    }}
    .ns-home-pro-head {{
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 0.75rem;
        margin-bottom: 1.1rem;
    }}
    .ns-home-pro-title {{
        margin: 0;
        font-family: "Plus Jakarta Sans", "Segoe UI", system-ui, -apple-system, sans-serif;
        font-size: clamp(1.85rem, 3.4vw, 2.25rem);
        font-weight: 800;
        letter-spacing: -0.04em;
        line-height: 1;
        background: {home_pro_wordmark_grad};
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
        -webkit-font-smoothing: antialiased;
        filter: drop-shadow(0 1px 0 rgba(255, 255, 255, 0.35));
    }}
    .ns-home-pro-badge {{
        font-size: 0.62rem;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        color: {p["text_muted"]};
        white-space: nowrap;
        padding-top: 0.35rem;
    }}
    .ns-home-pro-features {{
        list-style: none;
        margin: 0 0 1.25rem;
        padding: 0;
        display: flex;
        flex-direction: column;
        gap: 0.55rem;
    }}
    .ns-home-pro-features li {{
        position: relative;
        padding-left: 1.35rem;
        font-size: 0.86rem;
        line-height: 1.45;
        color: {p["body_muted"]};
    }}
    .ns-home-pro-features li::before {{
        content: "✓";
        position: absolute;
        left: 0;
        top: 0;
        color: #8b5cf6;
        font-weight: 800;
        font-size: 0.82rem;
    }}
    .ns-home-pro-foot {{
        display: grid;
        grid-template-columns: 1fr auto;
        gap: 0.65rem;
        align-items: end;
    }}
    .ns-home-pro-identity {{
        display: flex;
        align-items: center;
        gap: 0.55rem;
        min-width: 0;
    }}
    .ns-home-pro-avatar {{
        flex-shrink: 0;
        width: 2.35rem;
        height: 2.35rem;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.62rem;
        font-weight: 800;
        letter-spacing: 0.04em;
        color: #fff;
        background: linear-gradient(145deg, #7c3aed, #ec4899);
        box-shadow: 0 4px 14px rgba(124, 58, 237, 0.35);
    }}
    .ns-home-pro-identity-text {{
        display: flex;
        flex-direction: column;
        gap: 0.15rem;
        min-width: 0;
    }}
    .ns-home-pro-host {{
        font-size: 0.78rem;
        font-weight: 650;
        color: {p["text"]};
        background: {p["chip_bg"]};
        border: 1px solid {p["border"]};
        border-radius: 999px;
        padding: 0.2rem 0.55rem;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 11rem;
    }}
    .ns-home-pro-status {{
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        font-size: 0.72rem;
        color: {p["text_muted"]};
    }}
    .ns-home-pro-dot {{
        width: 0.45rem;
        height: 0.45rem;
        border-radius: 50%;
        background: #22c55e;
        box-shadow: 0 0 0 2px rgba(34, 197, 94, 0.25);
    }}
    .ns-home-pro-stat {{
        position: relative;
        min-width: 7.25rem;
        padding: 0.55rem 0.65rem;
        border-radius: 12px;
        background: {p["surface_elevated"]};
        box-shadow: 0 8px 24px rgba(0, 0, 0, {shadow});
    }}
    .ns-home-pro-stat::before {{
        content: "";
        position: absolute;
        inset: -2px;
        border-radius: 14px;
        z-index: -1;
        background: conic-gradient(from 200deg, #f97316, #ec4899, #8b5cf6, #38bdf8, #f97316);
        opacity: {"0.85" if theme == "light" else "0.55"};
    }}
    .ns-home-pro-stat-label {{
        display: block;
        font-size: 0.62rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: {p["text_muted"]};
    }}
    .ns-home-pro-stat-value {{
        display: block;
        font-size: 1.35rem;
        font-weight: 700;
        letter-spacing: -0.03em;
        color: {p["text"]};
        line-height: 1.15;
        margin: 0.1rem 0;
    }}
    .ns-home-pro-stat-sub {{
        display: block;
        font-size: 0.65rem;
        color: {p["text_muted"]};
    }}
    .ns-home-pro-float {{
        position: absolute;
        z-index: 2;
        background: {p["surface_elevated"]};
        border-radius: 14px;
        padding: 0.75rem 0.85rem;
        box-shadow: 0 14px 40px rgba(0, 0, 0, {shadow});
        border: 1px solid {p["border_strong"]};
    }}
    .ns-home-pro-float--ak {{
        left: -4%;
        bottom: -6%;
        width: 72%;
        max-width: 240px;
    }}
    .ns-home-pro-float-stars {{
        font-size: 0.62rem;
        letter-spacing: 0.1em;
        color: #f59e0b;
        margin-bottom: 0.3rem;
    }}
    .ns-home-pro-float-quote {{
        margin: 0 0 0.45rem;
        font-size: 0.76rem;
        line-height: 1.4;
        color: {p["body_muted"]};
    }}
    .ns-home-pro-float-id {{
        display: block;
        font-size: 0.82rem;
        font-weight: 700;
        color: {p["text"]};
    }}
    .ns-home-pro-float-role {{
        display: block;
        font-size: 0.68rem;
        color: {p["text_muted"]};
    }}
    .ns-home-section {{
        margin-top: 2.5rem;
    }}
    .ns-home-workflow-block {{
        position: relative;
        z-index: 1;
        margin-top: 2rem;
        clear: both;
        width: 100%;
    }}
    .ns-home-workflow-block .ns-flow-graph {{
        width: 100%;
        max-width: none;
        justify-content: space-between;
    }}
    .ns-home-section-title {{
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        color: {p["text_muted"]};
        margin: 0 0 0.85rem;
    }}
    .ns-home-wf-grid {{
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 0.65rem;
    }}
    @media (min-width: 720px) {{
        .ns-home-wf-grid {{
            grid-template-columns: repeat(4, minmax(0, 1fr));
        }}
    }}
    a.ns-home-wf-card {{
        display: block;
        text-decoration: none;
        color: inherit;
        background: {p["surface_elevated"]};
        border: 1px solid {p["border"]};
        border-radius: 12px;
        padding: 0.85rem 1rem;
        transition: border-color 0.18s ease, transform 0.18s ease, box-shadow 0.18s ease;
    }}
    a.ns-home-wf-card:hover {{
        border-color: rgba(0, 120, 212, 0.45);
        transform: translateY(-1px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, {shadow});
    }}
    .ns-home-wf-title {{
        display: block;
        font-size: 0.88rem;
        font-weight: 600;
        color: {p["text"]};
    }}
    .ns-home-wf-sub {{
        display: block;
        font-size: 0.75rem;
        color: {p["text_muted"]};
        margin-top: 0.2rem;
    }}
    .ns-home-health {{
        display: flex;
        align-items: center;
        gap: 0.55rem;
        margin-top: 1.75rem;
        padding: 0.65rem 0.85rem;
        border-radius: 10px;
        border: 1px solid {p["border"]};
        background: {p["chip_bg"]};
        font-size: 0.82rem;
        color: {p["body_muted"]};
    }}
    .ns-home-health-dot {{
        width: 0.55rem;
        height: 0.55rem;
        border-radius: 50%;
        flex-shrink: 0;
    }}
    .ns-home-health--green .ns-home-health-dot {{ background: #22c55e; }}
    .ns-home-health--yellow .ns-home-health-dot {{ background: #eab308; }}
    .ns-home-health--red .ns-home-health-dot {{ background: #ef4444; }}

    /* Animated workflow graph */
    a.ns-flow-node-link {{
        flex: 0 1 150px;
        text-decoration: none;
        color: inherit;
        cursor: pointer;
        border-radius: 8px;
        transition: transform 0.15s ease;
    }}
    a.ns-flow-node-link:hover {{
        transform: translateY(-2px);
    }}
    a.ns-flow-node-link:hover .ns-flow-title {{
        color: {p["accent"]};
    }}
    a.ns-flow-node-link:hover .ns-flow-ring {{
        border-color: {p["accent_hover"]};
        box-shadow: 0 0 0 6px {p["accent_soft"]};
    }}
    a.ns-flow-node-link:focus-visible {{
        outline: 2px solid {p["accent"]};
        outline-offset: 4px;
    }}
    .ns-flow-graph {{
        display: flex;
        align-items: flex-start;
        justify-content: center;
        gap: 0;
        padding: 1.25rem 0.25rem 0.5rem;
        margin-bottom: 0.25rem;
        flex-wrap: nowrap;
        overflow-x: auto;
    }}
    .ns-flow-node {{
        flex: 0 1 150px;
        text-align: center;
        animation: ns-node-in 0.6s ease backwards;
    }}
    @keyframes ns-node-in {{
        from {{ opacity: 0; transform: translateY(8px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    .ns-flow-ring {{
        width: 3rem;
        height: 3rem;
        margin: 0 auto 0.55rem;
        border-radius: 50%;
        border: 2px solid {p["accent"]};
        box-shadow: 0 0 0 4px {p["accent_soft"]};
        animation: ns-ring-pulse 2.4s ease-in-out infinite;
    }}
    @keyframes ns-ring-pulse {{
        0%, 100% {{ box-shadow: 0 0 0 4px {p["accent_soft"]}; }}
        50% {{ box-shadow: 0 0 0 8px transparent; }}
    }}
    .ns-flow-title {{
        font-size: 0.82rem;
        font-weight: 600;
        color: {p["text"]};
        line-height: 1.25;
    }}
    .ns-flow-sub {{
        font-size: 0.68rem;
        color: {p["text_muted"]};
        margin-top: 0.2rem;
        line-height: 1.3;
    }}
    .ns-flow-connector {{
        flex: 0 0 2.5rem;
        position: relative;
        height: 3rem;
        margin-top: 0.15rem;
        display: flex;
        align-items: center;
        justify-content: center;
    }}
    .ns-flow-line {{
        position: absolute;
        left: 0;
        right: 0;
        top: 50%;
        height: 2px;
        background: linear-gradient(90deg, {p["accent"]}, {p["border"]});
        transform: translateY(-50%);
    }}
    .ns-flow-packet {{
        position: absolute;
        top: 50%;
        width: 8px;
        height: 8px;
        margin-top: -4px;
        border-radius: 50%;
        background: {p["accent"]};
        box-shadow: 0 0 10px {p["accent"]};
        animation: ns-packet-move 1.8s ease-in-out infinite;
    }}
    @keyframes ns-packet-move {{
        0% {{ left: 0; opacity: 0; }}
        15% {{ opacity: 1; }}
        85% {{ opacity: 1; }}
        100% {{ left: calc(100% - 8px); opacity: 0; }}
    }}
    .ns-flow-chevron {{
        position: relative;
        z-index: 1;
        color: {p["accent"]};
        font-size: 1.25rem;
        font-weight: 700;
        opacity: 0.85;
    }}

    /* Lineage v2 — colorful vertical journey (not Home ns-flow) */
    .lg-v2 {{
        position: relative;
        margin: 0.75rem 0 1.5rem;
        padding: 1.35rem 1.1rem 1.1rem;
        border-radius: 20px;
        overflow: hidden;
        border: 1px solid {p["border"]};
        background: {p["surface_elevated"]};
        box-shadow: 0 12px 40px rgba(0, 0, 0, {shadow});
    }}
    .lg-v2-aurora {{
        position: absolute;
        inset: 0;
        pointer-events: none;
        overflow: hidden;
        opacity: {"0.55" if theme == "dark" else "0.85"};
    }}
    .lg-v2-blob {{
        position: absolute;
        border-radius: 50%;
        filter: blur(48px);
        animation: lg-v2-drift 14s ease-in-out infinite;
    }}
    .lg-v2-blob-a {{
        width: 220px; height: 220px;
        background: #a78bfa;
        top: -60px; left: -40px;
    }}
    .lg-v2-blob-b {{
        width: 200px; height: 200px;
        background: #38bdf8;
        top: 20%; right: -50px;
        animation-delay: -4s;
    }}
    .lg-v2-blob-c {{
        width: 180px; height: 180px;
        background: #f472b6;
        bottom: -40px; left: 35%;
        animation-delay: -8s;
    }}
    @keyframes lg-v2-drift {{
        0%, 100% {{ transform: translate(0, 0) scale(1); }}
        50% {{ transform: translate(12px, -18px) scale(1.08); }}
    }}
    .lg-v2-header {{
        position: relative;
        z-index: 1;
        margin-bottom: 1.25rem;
    }}
    .lg-v2-header-badge {{
        display: inline-block;
        font-size: 0.65rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        padding: 0.25rem 0.55rem;
        border-radius: 999px;
        background: linear-gradient(135deg, #6366f1, #ec4899);
        color: #fff;
        box-shadow: 0 4px 14px rgba(99, 102, 241, 0.45);
    }}
    .lg-v2-header-title {{
        margin: 0.55rem 0 0.2rem;
        font-size: 1.35rem;
        font-weight: 700;
        color: {p["text"]};
        letter-spacing: -0.02em;
    }}
    .lg-v2-header-sub {{
        margin: 0;
        font-size: 0.82rem;
        color: {p["text_muted"]};
    }}
    .lg-v2-track {{
        position: relative;
        z-index: 1;
        display: flex;
        flex-direction: column;
        gap: 0;
    }}
    .lg-v2-step {{
        display: grid;
        grid-template-columns: 3.25rem 1fr;
        gap: 0.85rem;
        align-items: stretch;
        animation: lg-v2-step-in 0.7s cubic-bezier(0.34, 1.2, 0.64, 1) both;
    }}
    @keyframes lg-v2-step-in {{
        from {{ opacity: 0; transform: translateX(-16px); }}
        to {{ opacity: 1; transform: translateX(0); }}
    }}
    .lg-v2-rail-col {{
        display: flex;
        flex-direction: column;
        align-items: center;
        min-height: 100%;
    }}
    .lg-v2-node {{
        position: relative;
        width: 3rem;
        height: 3rem;
        flex-shrink: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 2;
    }}
    .lg-v2-node-emoji {{
        font-size: 1.35rem;
        line-height: 1;
        z-index: 2;
        filter: drop-shadow(0 2px 4px rgba(0,0,0,0.15));
    }}
    .lg-v2-node-ring {{
        position: absolute;
        inset: 0;
        border-radius: 50%;
        border: 3px solid currentColor;
        animation: lg-v2-node-pulse 2.4s ease-in-out infinite;
    }}
    @keyframes lg-v2-node-pulse {{
        0%, 100% {{ transform: scale(1); opacity: 1; }}
        50% {{ transform: scale(1.12); opacity: 0.75; }}
    }}
    .lg-v2-connector {{
        flex: 1;
        width: 6px;
        min-height: 1.25rem;
        margin: 0.15rem 0;
        border-radius: 999px;
        background: {p["border"]};
        position: relative;
        overflow: hidden;
    }}
    .lg-v2-connector-fill {{
        position: absolute;
        inset: 0;
        background: linear-gradient(180deg, var(--lg-v2-a), var(--lg-v2-b));
        animation: lg-v2-fill-pulse 2s ease-in-out infinite;
    }}
    @keyframes lg-v2-fill-pulse {{
        0%, 100% {{ opacity: 0.65; }}
        50% {{ opacity: 1; }}
    }}
    .lg-v2-connector-spark {{
        position: absolute;
        left: 50%;
        width: 10px;
        height: 10px;
        margin-left: -5px;
        border-radius: 50%;
        background: #fff;
        box-shadow: 0 0 12px var(--lg-v2-b), 0 0 24px var(--lg-v2-a);
        animation: lg-v2-spark-drop 1.8s ease-in-out infinite;
    }}
    @keyframes lg-v2-spark-drop {{
        0% {{ top: 0; opacity: 0; }}
        15% {{ opacity: 1; }}
        85% {{ opacity: 1; }}
        100% {{ top: calc(100% - 10px); opacity: 0; }}
    }}
    .lg-v2-card {{
        position: relative;
        margin-bottom: 1rem;
        padding: 0;
        border-radius: 16px;
        overflow: hidden;
        border: 2px solid var(--lg-v2-b);
        background: {p["surface"]};
        box-shadow: 0 8px 28px rgba(0, 0, 0, {shadow});
        transition: transform 0.25s ease, box-shadow 0.25s ease;
    }}
    .lg-v2-card:hover {{
        transform: translateY(-3px) scale(1.01);
        box-shadow: 0 14px 36px rgba(0, 0, 0, calc({shadow} + 0.06));
    }}
    .lg-v2-card-shine {{
        position: absolute;
        top: 0; left: -100%;
        width: 60%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,{"0.12" if theme == "dark" else "0.35"}), transparent);
        animation: lg-v2-shine 4s ease-in-out infinite;
        pointer-events: none;
    }}
    @keyframes lg-v2-shine {{
        0% {{ left: -100%; }}
        40%, 100% {{ left: 140%; }}
    }}
    .lg-v2-card-cap {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.55rem 0.9rem;
        background: linear-gradient(120deg, var(--lg-v2-a), var(--lg-v2-b));
        color: #fff;
        font-weight: 700;
    }}
    .lg-v2-step-no {{
        font-size: 0.72rem;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        opacity: 0.95;
    }}
    .lg-v2-cap-emoji {{ font-size: 1.1rem; }}
    .lg-v2-card-title {{
        margin: 0;
        padding: 0.65rem 0.9rem 0.25rem;
        font-size: 1.02rem;
        font-weight: 700;
        color: {p["text"]};
    }}
    .lg-v2-card-detail {{
        margin: 0;
        padding: 0 0.9rem 0.65rem;
        font-size: 0.84rem;
        line-height: 1.5;
        color: {p["body_muted"]};
    }}
    .lg-v2-card-foot {{
        padding: 0.45rem 0.9rem 0.65rem;
        font-size: 0.7rem;
        color: {p["text_muted"]};
        border-top: 1px dashed {p["border"]};
    }}
    .lg-v2--question {{ --lg-v2-a: #7c3aed; --lg-v2-b: #c084fc; color: #7c3aed; }}
    .lg-v2--planner {{ --lg-v2-a: #2563eb; --lg-v2-b: #60a5fa; color: #2563eb; }}
    .lg-v2--draft {{ --lg-v2-a: #0891b2; --lg-v2-b: #22d3ee; color: #0891b2; }}
    .lg-v2--validation {{ --lg-v2-a: #059669; --lg-v2-b: #34d399; color: #059669; }}
    .lg-v2--review {{ --lg-v2-a: #d97706; --lg-v2-b: #fbbf24; color: #d97706; }}
    .lg-v2--approved {{ --lg-v2-a: #db2777; --lg-v2-b: #f472b6; color: #db2777; }}
    .lg-v2--sources {{ --lg-v2-a: #4f46e5; --lg-v2-b: #818cf8; color: #4f46e5; }}
    .lg-v2-chips {{
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin: 0.25rem 0 1rem;
    }}
    .lg-v2-chip {{
        font-size: 0.78rem;
        padding: 0.35rem 0.75rem;
        border-radius: 999px;
        background: {p["surface_elevated"]};
        border: 1px solid {p["border"]};
        color: {p["body_muted"]};
    }}
    .lg-v2-chip--ak {{
        background: linear-gradient(135deg, #ec4899, #8b5cf6);
        border: none;
        color: #fff;
        font-weight: 600;
    }}
    @media (prefers-reduced-motion: reduce) {{
        .lg-v2-blob, .lg-v2-step, .lg-v2-node-ring, .lg-v2-connector-fill,
        .lg-v2-connector-spark, .lg-v2-card-shine {{
            animation: none !important;
        }}
        .lg-v2-card:hover {{ transform: none; }}
    }}

    .ns-search-panel, .ns-result-card {{
        background: {p["surface_elevated"]};
        border: 1px solid {p["border"]};
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, {shadow});
        transition: border-color 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease;
    }}
    .ns-result-card.ns-anim-result {{
        animation: ns-fade-up 0.45s cubic-bezier(0.22, 1, 0.36, 1) both;
    }}
    .ns-result-card:hover {{
        border-color: rgba(0, 120, 212, 0.25);
        box-shadow: 0 6px 20px rgba(0, 0, 0, {shadow});
        transform: translateY(-1px);
    }}
    .ns-search-panel {{ padding: 1rem 1.15rem 0.25rem; margin-bottom: 1rem; }}
    .ns-result-card {{ padding: 1rem 1.15rem; margin-bottom: 0.35rem; }}
    .ns-result-title {{ color: {p["text"]}; font-weight: 600; }}
    .ns-result-score {{ color: {score_color}; font-weight: 600; }}
    .ns-result-snippet {{ color: {p["body_muted"]}; font-size: 0.88rem; }}
    .ns-snippet-hit {{
        background: {p["accent_soft"]}; color: {p["text"]};
        padding: 0 0.15rem; border-radius: 3px;
    }}
    .ns-chip {{
        background: {p["chip_bg"]}; border: 1px solid {p["border"]};
        color: {p["body_muted"]}; font-size: 0.72rem; padding: 0.2rem 0.55rem; border-radius: 4px;
    }}

    .ns-about-lead {{ color: {p["body_muted"]}; }}
    .ns-footer-note {{ color: {p["text_muted"]}; border-top: 1px solid {p["border"]}; }}

    div[data-testid="stExpander"] {{
        border: 1px solid {p["border"]};
        border-radius: 8px;
        background: {p["surface"]};
    }}

    /* Secondary / default buttons (Go to About, Preview planner JSON, etc.) */
    .stButton > button,
    .stButton > button[kind="secondary"],
    [data-testid="stBaseButton-secondary"] {{
        background-color: {btn_secondary_bg} !important;
        color: {btn_secondary_text} !important;
        border: 1px solid {btn_secondary_border} !important;
        font-weight: 500 !important;
        transition: transform 0.15s ease, box-shadow 0.15s ease, background-color 0.15s ease,
            border-color 0.15s ease, color 0.15s ease !important;
    }}
    .stButton > button:active {{
        transform: scale(0.98);
    }}
    .stButton > button p,
    .stButton > button span,
    .stButton > button div,
    [data-testid="stBaseButton-secondary"] p,
    [data-testid="stBaseButton-secondary"] span {{
        color: {btn_secondary_text} !important;
    }}
    .stButton > button:hover:not([kind="primary"]),
    [data-testid="stBaseButton-secondary"]:hover {{
        background-color: {btn_secondary_hover_bg} !important;
        color: {p["accent"]} !important;
        border-color: {p["accent"]} !important;
    }}
    .stButton > button[kind="primary"] {{
        background: {p["accent"]} !important;
        border-color: {p["accent"]} !important;
        color: {btn_primary_fg} !important;
    }}
    .stButton > button[kind="primary"] p,
    .stButton > button[kind="primary"] span,
    .stButton > button[kind="primary"] div {{
        color: {btn_primary_fg} !important;
    }}

    .ns-help-btn .stButton > button {{
        background-color: {btn_secondary_bg} !important;
        color: {btn_secondary_text} !important;
        border: 1px solid {btn_secondary_border} !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
    }}
    .ns-help-btn .stButton > button:hover {{
        background-color: {btn_secondary_hover_bg} !important;
        color: {p["accent"]} !important;
        border-color: {p["accent"]} !important;
    }}

    [data-testid="stLinkButton"] a {{
        color: {p["accent"]} !important;
        border: 1px solid {btn_secondary_border} !important;
        background: {btn_secondary_bg} !important;
    }}

    h1, h2, h3 {{ color: {p["text"]} !important; }}

    .ns-result-head {{
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 1rem;
        margin-bottom: 0.5rem;
    }}
    .ns-result-meta {{ display: flex; flex-wrap: wrap; gap: 0.35rem; margin-bottom: 0.65rem; }}
    .ns-chip-source {{
        background: {p["accent_soft"]};
        border-color: rgba(0, 120, 212, 0.35);
        color: {badge_accent_color};
    }}
    /* Home agent dashboard — minimal animated health */
    .ns-dash-row {{
        display: flex;
        flex-wrap: wrap;
        gap: 1.25rem 2rem;
        align-items: flex-end;
        margin: 0.15rem 0 0.65rem;
    }}
    .ns-dash-metric {{
        display: flex;
        flex-direction: column;
        gap: 0.35rem;
        min-width: 5.5rem;
    }}
    .ns-dash-metric-label {{
        font-size: 0.78rem;
        color: {p["text_muted"]};
        font-weight: 500;
    }}
    .ns-dash-metric-value {{
        font-size: 1.75rem;
        font-weight: 600;
        color: {p["text"]};
        line-height: 1.1;
        font-variant-numeric: tabular-nums;
    }}
    .ns-dash-health {{
        display: inline-flex;
        align-items: center;
        justify-content: flex-start;
        min-height: 1.75rem;
        padding: 0.1rem 0;
    }}
    .ns-dash-health-orb {{
        position: relative;
        width: 1.75rem;
        height: 1.75rem;
        flex-shrink: 0;
        cursor: default;
    }}
    .ns-dash-health-core {{
        position: absolute;
        inset: 5px;
        border-radius: 50%;
        background: var(--ns-health-color);
        box-shadow: 0 0 10px color-mix(in srgb, var(--ns-health-color) 55%, transparent);
    }}
    .ns-dash-health-orb::after {{
        content: "";
        position: absolute;
        inset: 0;
        border-radius: 50%;
        border: 2px solid var(--ns-health-color);
        opacity: 0.5;
        animation: ns-dash-health-ping 2.4s cubic-bezier(0, 0, 0.2, 1) infinite;
    }}
    @keyframes ns-dash-health-ping {{
        0% {{ transform: scale(1); opacity: 0.55; }}
        75%, 100% {{ transform: scale(2.2); opacity: 0; }}
    }}
    .ns-dash-health--green {{ --ns-health-color: #22c55e; }}
    .ns-dash-health--yellow {{ --ns-health-color: #eab308; }}
    .ns-dash-health--red {{ --ns-health-color: #ef4444; }}

    /* Analytics page — subtle motion (not home flow / lineage journey) */
    .ns-analytics-page {{
        --ns-analytics-accent: {p["accent"]};
    }}
    .ns-analytics-header {{
        margin-bottom: 1.1rem;
        animation: ns-analytics-fade 0.65s ease-out both;
    }}
    .ns-analytics-title {{
        margin: 0;
        font-size: 1.65rem;
        font-weight: 600;
        color: {p["text"]};
        letter-spacing: -0.02em;
    }}
    .ns-analytics-sub {{
        margin: 0.35rem 0 0;
        font-size: 0.9rem;
        color: {p["body_muted"]};
        line-height: 1.45;
        max-width: 42rem;
    }}
    .ns-analytics-rule {{
        margin-top: 0.85rem;
        height: 2px;
        max-width: 5.5rem;
        border-radius: 2px;
        background: linear-gradient(90deg, var(--ns-analytics-accent), transparent);
        transform-origin: left center;
        animation: ns-analytics-rule-in 0.9s ease-out 0.15s both;
    }}
    @keyframes ns-analytics-rule-in {{
        from {{ transform: scaleX(0); opacity: 0; }}
        to {{ transform: scaleX(1); opacity: 1; }}
    }}
    @keyframes ns-analytics-fade {{
        from {{ opacity: 0; transform: translateY(5px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    .ns-analytics-kpi-row {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 0.65rem;
        margin-bottom: 1.25rem;
    }}
    .ns-analytics-kpi {{
        padding: 0.85rem 1rem;
        border-radius: 8px;
        background: {p["surface_elevated"]};
        border: 1px solid {p["border"]};
        animation: ns-analytics-kpi-in 0.5s ease-out both;
    }}
    @keyframes ns-analytics-kpi-in {{
        from {{ opacity: 0; transform: translateY(4px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    .ns-analytics-kpi-value {{
        font-size: 1.5rem;
        font-weight: 600;
        color: {p["text"]};
        font-variant-numeric: tabular-nums;
        line-height: 1.15;
    }}
    .ns-analytics-kpi-label {{
        margin-top: 0.2rem;
        font-size: 0.76rem;
        color: {p["text_muted"]};
        font-weight: 500;
    }}
    .ns-analytics-kpi-hint {{
        display: block;
        margin-top: 0.25rem;
        font-size: 0.68rem;
        color: {p["body_muted"]};
    }}
    .ns-analytics-panel {{
        animation: ns-analytics-panel-in 0.55s ease-out both;
    }}
    @keyframes ns-analytics-panel-in {{
        from {{ opacity: 0; }}
        to {{ opacity: 1; }}
    }}
    .ns-analytics-page [data-testid="stTabs"] {{
        animation: ns-analytics-fade 0.45s ease-out 0.08s both;
    }}
    .ns-analytics-page [data-testid="stTabContent"] {{
        animation: ns-analytics-tab-in 0.4s ease-out both;
    }}
    @keyframes ns-analytics-tab-in {{
        from {{ opacity: 0.88; transform: translateY(3px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    .ns-analytics-page [data-testid="stMetric"] {{
        animation: ns-analytics-kpi-in 0.45s ease-out both;
    }}
    .ns-analytics-page [data-testid="stMetric"]:nth-of-type(2) {{
        animation-delay: 0.05s;
    }}
    .ns-analytics-page [data-testid="stMetric"]:nth-of-type(3) {{
        animation-delay: 0.1s;
    }}
    .ns-analytics-page [data-testid="stMetric"]:nth-of-type(4) {{
        animation-delay: 0.15s;
    }}
    .ns-analytics-page [data-testid="stDataFrame"],
    .ns-analytics-page [data-testid="stArrowDataFrame"] {{
        animation: ns-analytics-panel-in 0.5s ease-out 0.12s both;
    }}

    /* Governed Ask */
    .ns-gov-strip {{
        margin: 0 0 1.15rem;
        position: relative;
    }}
    .ns-gov-strip-track {{
        height: 3px;
        border-radius: 3px;
        background: {p["border"]};
        margin-bottom: 0.85rem;
        overflow: hidden;
    }}
    .ns-gov-strip-fill {{
        height: 100%;
        width: var(--ns-gov-progress, 0%);
        background: linear-gradient(90deg, {p["accent"]}, color-mix(in srgb, {p["accent"]} 60%, transparent));
        border-radius: 3px;
        transition: width 0.45s ease;
    }}
    .ns-gov-strip-steps {{
        display: flex;
        justify-content: space-between;
        gap: 0.5rem;
    }}
    .ns-gov-step {{
        flex: 1;
        text-align: center;
        animation: ns-analytics-fade 0.45s ease-out both;
    }}
    .ns-gov-step-dot {{
        width: 10px;
        height: 10px;
        margin: 0 auto 0.35rem;
        border-radius: 50%;
        border: 2px solid {p["border"]};
        background: {p["surface"]};
    }}
    .ns-gov-step--active .ns-gov-step-dot {{
        border-color: {p["accent"]};
        background: {p["accent"]};
        box-shadow: 0 0 0 4px {p["accent_soft"]};
    }}
    .ns-gov-step--done .ns-gov-step-dot {{
        border-color: {p["accent"]};
        background: {p["accent"]};
    }}
    .ns-gov-step-label {{
        font-size: 0.78rem;
        font-weight: 600;
        color: {p["text"]};
    }}
    .ns-gov-step-sub {{
        font-size: 0.65rem;
        color: {p["text_muted"]};
        margin-top: 0.1rem;
    }}
    .ns-review-row {{
        border-left: 3px solid {p["border"]};
        padding-left: 0.65rem;
        margin-bottom: 0.5rem;
        animation: ns-analytics-kpi-in 0.45s ease-out both;
    }}
    .ns-review-row--pending {{ border-left-color: #eab308; }}
    .ns-review-row--approved {{ border-left-color: #22c55e; }}
    .ns-review-row--rejected {{ border-left-color: #ef4444; }}
    .ns-review-row--edited {{ border-left-color: #3b82f6; }}
    .ns-triage-zone [data-testid="stExpander"] {{
        animation: ns-analytics-panel-in 0.4s ease-out both;
    }}
    .ns-governed-page [data-testid="stTabContent"] {{
        animation: ns-analytics-tab-in 0.35s ease-out both;
    }}

    /* Automations */
    .ns-schedule-block .ns-analytics-rule {{
        margin-bottom: 1rem;
    }}
    .ns-run-list {{
        display: flex;
        flex-direction: column;
        gap: 0.45rem;
    }}
    .ns-run-row {{
        display: flex;
        align-items: center;
        gap: 0.65rem;
        padding: 0.55rem 0.7rem;
        border-radius: 8px;
        border: 1px solid {p["border"]};
        background: {p["surface_elevated"]};
        animation: ns-analytics-kpi-in 0.4s ease-out both;
    }}
    .ns-run-dot {{
        position: relative;
        width: 0.65rem;
        height: 0.65rem;
        flex-shrink: 0;
    }}
    .ns-run-dot-core {{
        position: absolute;
        inset: 1px;
        border-radius: 50%;
        background: var(--ns-run-color, #94a3b8);
    }}
    .ns-run-dot--green {{ --ns-run-color: #22c55e; }}
    .ns-run-dot--yellow {{ --ns-run-color: #eab308; }}
    .ns-run-dot--red {{ --ns-run-color: #ef4444; }}
    .ns-run-dot--green::after, .ns-run-dot--yellow::after {{
        content: "";
        position: absolute;
        inset: 0;
        border-radius: 50%;
        border: 1px solid var(--ns-run-color);
        animation: ns-dash-health-ping 2.6s ease-out infinite;
        opacity: 0.45;
    }}
    .ns-run-body {{ flex: 1; min-width: 0; }}
    .ns-run-title {{
        font-size: 0.82rem;
        font-weight: 600;
        color: {p["text"]};
    }}
    .ns-run-meta {{
        font-size: 0.68rem;
        color: {p["text_muted"]};
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }}
    .ns-run-end {{
        text-align: right;
        font-size: 0.68rem;
        color: {p["text_muted"]};
    }}
    .ns-run-status {{
        display: block;
        text-transform: capitalize;
        font-weight: 600;
        color: {p["body_muted"]};
    }}

    /* Search */
    .ns-empty-state {{
        padding: 1rem 1.1rem;
        border-radius: 8px;
        border: 1px dashed {p["border"]};
        background: {p["surface_elevated"]};
        animation: ns-analytics-fade 0.55s ease-out both;
        margin: 0.5rem 0 1rem;
    }}
    .ns-empty-msg {{
        margin: 0;
        font-size: 0.88rem;
        color: {p["body_muted"]};
    }}
    .ns-empty-hint {{
        margin: 0.35rem 0 0;
        font-size: 0.78rem;
        color: {p["text_muted"]};
    }}
    .ns-search-skeleton {{
        margin: 0.75rem 0 1rem;
        animation: ns-analytics-fade 0.3s ease-out both;
    }}
    .ns-search-skel-line {{
        height: 10px;
        border-radius: 4px;
        background: linear-gradient(90deg, {p["border"]}, {p["surface_elevated"]}, {p["border"]});
        background-size: 200% 100%;
        animation: ns-skel-shimmer 1.2s ease-in-out infinite;
        margin-bottom: 0.5rem;
    }}
    .ns-search-skel-line--a {{ width: 42%; }}
    .ns-search-skel-line--b {{ width: 68%; }}
    .ns-search-skel-block {{
        height: 52px;
        border-radius: 8px;
        background: linear-gradient(90deg, {p["border"]}, {p["surface_elevated"]}, {p["border"]});
        background-size: 200% 100%;
        animation: ns-skel-shimmer 1.2s ease-in-out infinite;
        margin-bottom: 0.45rem;
    }}
    .ns-search-skel-block--short {{ height: 36px; width: 88%; }}
    @keyframes ns-skel-shimmer {{
        0% {{ background-position: 100% 0; }}
        100% {{ background-position: -100% 0; }}
    }}

    /* Ingest jobs */
    .ns-job-progress {{
        margin: 0.65rem 0 1rem;
        animation: ns-analytics-fade 0.4s ease-out both;
    }}
    .ns-job-progress-label {{
        font-size: 0.76rem;
        color: {p["text_muted"]};
        margin-bottom: 0.35rem;
    }}
    .ns-job-progress-track {{
        height: 6px;
        border-radius: 6px;
        background: {p["border"]};
        overflow: hidden;
    }}
    .ns-job-progress-fill {{
        height: 100%;
        border-radius: 6px;
        background: {p["accent"]};
        transition: width 0.35s ease;
    }}
    .ns-job-progress--active .ns-job-progress-fill {{
        animation: ns-job-pulse 1.4s ease-in-out infinite;
    }}
    @keyframes ns-job-pulse {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.65; }}
    }}
    .ns-job-progress--failed .ns-job-progress-fill {{
        background: #ef4444;
    }}
    .ns-job-progress--done .ns-job-progress-fill {{
        background: #22c55e;
    }}
    .ns-ingest-steps {{
        display: flex;
        align-items: center;
        gap: 0;
        margin: 0.5rem 0 0.85rem;
        font-size: 0.72rem;
        color: {p["text_muted"]};
    }}
    .ns-ingest-step {{
        display: flex;
        align-items: center;
        gap: 0.35rem;
    }}
    .ns-ingest-step-mark {{
        width: 1.25rem;
        height: 1.25rem;
        line-height: 1.25rem;
        text-align: center;
        border-radius: 50%;
        font-size: 0.65rem;
        font-weight: 700;
        border: 1px solid {p["border"]};
    }}
    .ns-ingest-step--done .ns-ingest-step-mark {{
        background: #22c55e;
        border-color: #22c55e;
        color: #fff;
    }}
    .ns-ingest-step--active .ns-ingest-step-mark {{
        border-color: {p["accent"]};
        color: {p["accent"]};
    }}
    .ns-ingest-step--failed .ns-ingest-step-mark {{
        background: #ef4444;
        border-color: #ef4444;
        color: #fff;
    }}
    .ns-ingest-step-line {{
        flex: 1;
        min-width: 1.5rem;
        height: 2px;
        background: {p["border"]};
        margin: 0 0.35rem;
    }}

    /* Onboarding wizard */
    .ns-wizard-strip {{
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        gap: 0.25rem 0;
        margin: 0.75rem 0 1.1rem;
        padding-bottom: 0.25rem;
    }}
    .ns-wiz-step {{
        display: flex;
        align-items: center;
        gap: 0.35rem;
        animation: ns-analytics-fade 0.4s ease-out both;
    }}
    .ns-wiz-num {{
        width: 1.35rem;
        height: 1.35rem;
        line-height: 1.35rem;
        text-align: center;
        border-radius: 50%;
        font-size: 0.68rem;
        font-weight: 700;
        border: 1px solid {p["border"]};
        color: {p["text_muted"]};
    }}
    .ns-wiz-step--active .ns-wiz-num {{
        border-color: {p["accent"]};
        background: {p["accent_soft"]};
        color: {p["accent"]};
    }}
    .ns-wiz-step--done .ns-wiz-num {{
        background: {p["accent"]};
        border-color: {p["accent"]};
        color: #fff;
    }}
    .ns-wiz-label {{
        font-size: 0.72rem;
        font-weight: 500;
        color: {p["body_muted"]};
    }}
    .ns-wiz-step--active .ns-wiz-label {{
        color: {p["text"]};
        font-weight: 600;
    }}
    .ns-wiz-connector {{
        width: 1.25rem;
        height: 1px;
        background: {p["border"]};
        margin: 0 0.15rem;
    }}
    .ns-onboarding-page [data-testid="stTabContent"] {{
        animation: ns-analytics-tab-in 0.38s ease-out both;
    }}

    /* Document viewer — knowledge path */
    .kp-wrap.kp-wrap-animate {{
        animation: ns-analytics-fade 0.5s ease-out both;
    }}

    .ns-status-ok {{
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.55rem 1rem;
        border-radius: 8px;
        background: rgba(34, 197, 94, 0.12);
        border: 1px solid rgba(34, 197, 94, 0.3);
        color: {status_ok_color};
        font-size: 0.85rem;
    }}
    .ns-status-dot {{
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #22c55e;
        box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.55);
        animation: ns-status-pulse 2s ease-in-out infinite;
    }}
    @keyframes ns-status-pulse {{
        0%, 100% {{ box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.45); }}
        50% {{ box-shadow: 0 0 0 6px rgba(34, 197, 94, 0); }}
    }}

    @media (prefers-reduced-motion: reduce) {{
        .stApp,
        .ns-hero.ns-anim-hero,
        .ns-hero.ns-anim-hero::after,
        .ns-badge,
        .ns-glass-metric.ns-anim-metric,
        .ns-workflow-panel.ns-anim-panel,
        .ns-about-panel.ns-anim-fade-up,
        .ns-page-header.ns-anim-page-in,
        .ns-section-label.ns-anim-section::after,
        .ns-flow-node,
        .ns-flow-ring,
        .ns-flow-packet,
        .ns-result-card.ns-anim-result,
        .ns-status-dot,
        .ns-dash-health-orb::after,
        .ns-analytics-header,
        .ns-analytics-kpi,
        .ns-analytics-panel,
        .ns-analytics-page [data-testid="stTabs"],
        .ns-analytics-page [data-testid="stTabContent"],
        .ns-analytics-page [data-testid="stMetric"],
        .ns-analytics-page [data-testid="stDataFrame"],
        .ns-analytics-page [data-testid="stArrowDataFrame"],
        .ns-gov-step,
        .ns-review-row,
        .ns-run-row,
        .ns-run-dot::after,
        .ns-empty-state,
        .ns-search-skel-line,
        .ns-search-skel-block,
        .ns-job-progress--active .ns-job-progress-fill,
        .ns-wiz-step,
        .kp-wrap.kp-wrap-animate {{
            animation: none !important;
            transition: none !important;
        }}
        [data-testid="stSidebarNav"] a:hover,
        .ns-glass-metric.ns-anim-metric:hover,
        .ns-workflow-panel.ns-anim-panel:hover,
        .ns-result-card:hover,
        a.ns-flow-node-link:hover {{
            transform: none !important;
        }}
    }}
    .ns-about-panel {{ max-width: 680px; margin: 0 auto 1.5rem; text-align: center; }}
    .ns-result-spacer {{ height: 0.75rem; }}

    /* Home ingest CTA — black pill (overrides global stLinkButton / page link theme) */
    .stApp:has(.ns-home-page) [data-testid="stPageLink"] a,
    .stApp:has(.ns-home-page) [data-testid="stPageLink"] a span,
    .stApp:has(.ns-home-page) [data-testid="stPageLink"] a p {{
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }}
    .stApp:has(.ns-home-page) [data-testid="stPageLink"] a {{
        background: #0c0c0c !important;
        background-color: #0c0c0c !important;
        border: none !important;
        border-radius: 999px !important;
    }}
</style>
""",
        unsafe_allow_html=True,
    )
