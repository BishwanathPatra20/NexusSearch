"""NexusSearch + system-search.webp (expanded sidebar + collapsed rail)."""

import streamlit as st

from frontend.brand import brand_icon_data_uri


def _markup(css_class: str) -> str:
    icon = brand_icon_data_uri()
    if not icon:
        title = "<span class='ns-brand-wordmark'>NexusSearch</span>"
    else:
        title = (
            f"<span class='ns-brand-wordmark'>NexusSearch</span>"
            f"<img class='ns-brand-icon' src='{icon}' alt='' />"
        )
    return f"""
<div class="{css_class}" aria-hidden="true">
  <div class="ns-brand-title-row">{title}</div>
  <div class="ns-brand-caption">v1.1 · office-safe</div>
</div>
"""


def render_sidebar_brand() -> None:
    st.markdown(_markup("ns-brand-expanded") + _markup("ns-brand-collapsed"), unsafe_allow_html=True)
