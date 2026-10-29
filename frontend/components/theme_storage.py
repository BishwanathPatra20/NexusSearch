"""Persist light/dark theme in the browser (localStorage + query param)."""

from __future__ import annotations

import streamlit as st
import streamlit.components.v1 as components


def bootstrap_theme_from_browser() -> None:
    if st.session_state.get("_ns_theme_bootstrapped"):
        return
    qp = st.query_params
    if "ns_theme" in qp and qp["ns_theme"] in ("dark", "light"):
        st.session_state["ns_theme"] = str(qp["ns_theme"])
        st.session_state["_ns_theme_bootstrapped"] = True
        return

    components.html(
        """
<script>
(function () {
  try {
    const saved = localStorage.getItem('ns_theme');
    if (saved === 'dark' || saved === 'light') {
      const url = new URL(window.parent.location.href);
      if (url.searchParams.get('ns_theme') !== saved) {
        url.searchParams.set('ns_theme', saved);
        window.parent.location.replace(url.toString());
      }
    }
  } catch (e) {}
})();
</script>
        """,
        height=0,
    )
    st.session_state["_ns_theme_bootstrapped"] = True


def persist_theme_choice(theme: str) -> None:
    if theme not in ("dark", "light"):
        return
    st.query_params["ns_theme"] = theme
    components.html(
        f"""
<script>
try {{ localStorage.setItem('ns_theme', '{theme}'); }} catch (e) {{}}
</script>
        """,
        height=0,
    )
