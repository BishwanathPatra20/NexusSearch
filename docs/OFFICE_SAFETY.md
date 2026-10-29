# Office-laptop safety

NexusSearch is designed to run on a **corporate laptop** without cloud AI or outbound data transfer at runtime.

Context: [STUDY_GUIDE.md](STUDY_GUIDE.md)

---

## Runtime guarantees

- **No cloud AI APIs** — No OpenAI/Azure/Anthropic SDKs in `requirements.txt`
- **No outbound network from the app** — Ingestion uses local files; search uses SQLite
- **Local bind only** — API `127.0.0.1:8000`, Streamlit `127.0.0.1:8501`
- **Data on disk** — `./data/knowledgepilot.db`, `./data/uploads/` (gitignored)
- **Limited CORS** — Streamlit origins only

Recommended:

```bash
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
```

---

## Install time (one-time)

- Use corporate **pip mirror** if required; pinned `requirements.txt`
- No `nltk.download()`, Hugging Face pulls, or Docker required

---

## Not in v1.0

- **sentence-transformers, FAISS, Ollama** — Optional v2.0, IT approval
- **LangChain, LangGraph** — Not used
- **Live Confluence / GitHub APIs** — Use exports + folder ingest; **source_link** from export HTML is display-only (no outbound call from the app)
- **PAT / API tokens in NexusSearch** — Deferred until security approves; use Cursor MCP separately if your team allows it
- **Runtime model downloads** — None

---

## Security review (short script)

1. After install, the app does not need internet to function.
2. Users choose which files to index (upload or folder path).
3. Draft answers need human review before approved knowledge.
4. Audit trail is in local SQLite (`review_actions`).
