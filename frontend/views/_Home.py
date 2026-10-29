import streamlit as st

from frontend.components.home_view import render_home
from frontend.components.motion_ui import page_shell_close, page_shell_open

page_shell_open("ns-home-page")

# Home only: use full main width (Streamlit defaults to max-width ~1080px centered).
st.markdown(
    """
<style>
  .stApp .appview-container .main .block-container,
  .stApp .main .block-container {
    max-width: none !important;
    width: 100% !important;
    padding-left: clamp(0.65rem, 1.5vw, 1.15rem) !important;
    padding-right: clamp(0.65rem, 1.5vw, 1.15rem) !important;
  }
  .stApp .appview-container .main section.main,
  .stApp .main section.main {
    padding-left: 0 !important;
    padding-right: 0 !important;
    padding-top: 0 !important;
  }
  .stApp .main .block-container {
    padding-top: 1rem !important;
  }
</style>
""",
    unsafe_allow_html=True,
)

api_ok = False
status = None
error = None

try:
    from frontend.api_client import health

    status = health()
    api_ok = True
except Exception as exc:
    error = str(exc)

render_home(api_ok=api_ok, status=status, error=error)
page_shell_close()
