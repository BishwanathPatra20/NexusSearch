"""About NexusSearch — embedded in Settings."""

import streamlit as st


def render_about_section() -> None:
    st.markdown("### About NexusSearch")
    st.caption("Local-first knowledge governance prototype")

    st.markdown(
        """
NexusSearch helps teams **find**, **cite**, and **govern** answers from documents they already have —
PDFs, Word files, markdown repos, and **Confluence HTML exports** — all processed **on your machine**.
"""
    )

    st.markdown("#### What you can do")
    st.markdown(
        """
- **Ingest hub** — upload files, folder ingest, or Confluence sync into a local SQLite index  
- **Search** — citations and knowledge paths  
- **Governed Ask** — draft answers, human review, approved knowledge (`AK-XXXX`)  
- **Lineage** — trace approved answers back to source chunks  
- **Analytics** — search quality and corpus health  
"""
    )

    st.markdown("#### Office-safe by design")
    st.markdown(
        """
- API and UI bind to **127.0.0.1**  
- No cloud LLM calls in the default pipeline  
- Optional Confluence sync is HTTPS to your wiki only (see `docs/CONFLUENCE_PAT.md`)  
"""
    )

    st.markdown("#### Demo corpus")
    st.markdown(
        """
Try `samples/demo_corpus` via **Ingest hub → Folder ingest**, then search for `rollout` or `onboarding`.
"""
    )
