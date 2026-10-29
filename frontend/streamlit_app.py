import streamlit as st

from frontend.components.enterprise_theme import get_theme, inject_enterprise_theme, render_theme_toggle
from frontend.components.theme_storage import bootstrap_theme_from_browser
from frontend.brand import ICON_PATH
from frontend.components.sidebar_brand import render_sidebar_brand
from frontend.components.sidebar_resize import inject_sidebar_resize
from frontend.components.top_chrome import render_top_right_tools
from frontend.components.rag_bot import inject_rag_fab_global_styles, render_rag_bot_dock

st.set_page_config(
    page_title="NexusSearch",
    page_icon=str(ICON_PATH),
    layout="wide",
    initial_sidebar_state="expanded",
)

if "ns_theme" not in st.session_state:
    st.session_state["ns_theme"] = "dark"

bootstrap_theme_from_browser()
inject_enterprise_theme(get_theme())
inject_rag_fab_global_styles()

pg = st.navigation(
    [
        st.Page("views/_Home.py", title="Home", default=True),
        st.Page("views/1_Upload.py", title="Ingest hub", icon="📤"),
        st.Page("views/7_Onboarding.py", title="New hire guide", icon="🧭", url_path="onboarding"),
        st.Page("views/2_Search.py", title="Search", icon="🔎", url_path="search"),
        st.Page("views/3_Document_Viewer.py", title="Document Viewer", icon="📄"),
        st.Page("views/4_Analytics.py", title="Analytics", icon="📊"),
        st.Page("views/5_Governed_Ask.py", title="Governed Ask", icon="🛡️", url_path="governed-ask"),
        st.Page("views/6_Lineage.py", title="Lineage", icon="🔗", url_path="lineage"),
        st.Page("views/8_Automations.py", title="Automations", icon="⚙️", url_path="automations"),
        st.Page("views/9_Settings.py", title="Settings", icon="🔧", url_path="settings"),
    ]
)

render_sidebar_brand()
inject_sidebar_resize()
st.markdown('<div class="ns-app-top-chrome">', unsafe_allow_html=True)
render_top_right_tools()
st.markdown("</div>", unsafe_allow_html=True)
pg.run()
render_rag_bot_dock()

with st.sidebar:
    render_theme_toggle()
