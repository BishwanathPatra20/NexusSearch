# NexusSearch study guide

**One sentence:** NexusSearch is a local-first **knowledge governance** prototype—search with citations, draft answers, human review, approved institutional knowledge, lineage, and metrics—without cloud LLMs.

---

## 1. Problem and solution

**Problem:** Enterprise knowledge lives in PDFs, wikis, runbooks, and repo docs. Search is slow; answers are hard to **trust**.

**Solution:** A full lifecycle on your laptop:

```text
Ingest → Index → Search → Plan → Draft → Validate → Review → Approve
  → Approved Knowledge (AK-XXXX) → Lineage → Measure
```

This is **not** a RAG chatbot. Governance (review, audit, promotion) is the differentiator.

---

## 2. What each UI page does

- **Upload** — Ingest PDF/DOCX/TXT/MD/HTML; folder ingest and background jobs
- **Search** — FTS5, synonyms (`config/synonyms.json`), filters, citations, knowledge path
- **Document viewer** — Status, version, related documents, chunks
- **Analytics** — Search stats, governance metrics, knowledge health
- **Governed Ask** — Planner → draft → review queue
- **Lineage** — End-to-end trace for one review item

---

## 3. Backend layers (mental model)

- **UI (Streamlit)** — Calls API only
- **API (FastAPI)** — Upload, search, ask, reviews, lineage, analytics
- **Ingestion** — Parser plugins + hybrid chunker → page/subchunk citations
- **Store (SQLite + FTS5)** — `documents`, `document_chunks`, FTS index
- **Search** — FTS5 + synonyms + filters + explainable scores
- **Agents (no LLM)** — Planner → Search → Summary → Validator
- **Governance** — Review queue, audit, `approved_knowledge`

Details: [ARCHITECTURE.md](ARCHITECTURE.md)

---

## 4. Governance flow (important for interviews)

1. User asks via `POST /api/v1/ask`
2. **Planner** returns structured JSON (`intent`, `action`, `requires_review`)
3. **Search** retrieves chunks (synonyms apply)
4. **Summary** builds an **extractive** draft with source lines
5. **Validator** scores overlap with chunks
6. **Review item** created (`pending`)
7. Human **approve** / **edit** / **reject** → `review_actions` audit log
8. On approve → **`approved_knowledge`** (display id `AK-XXXX`)
9. **Lineage** UI shows the full chain

Preview planner only: `GET /api/v1/ask/plan?q=...`

---

## 5. Search vs Governed Ask

**Search**

- Output: ranked chunks + snippets
- Governance: no
- Use when: finding passages

**Governed Ask**

- Output: draft answer + review item
- Governance: yes (review queue)
- Use when: proposing an official answer

---

## 6. Demo corpus (practice)

Use **synthetic** files only:

```text
samples/demo_corpus/
```

Folder-ingest that path, then try:

- Search: `rollout` (synonym → deployment)
- Ask: *How do I get Databricks access?*
- Approve → **Lineage** → **Governance metrics**

Script: [DEMO_SCRIPT.md](DEMO_SCRIPT.md)

---

## 7. Interview talking points

**Say**

- Local-first prototype demonstrating **governance patterns**
- Citations on every search hit (file, page, chunk)
- Human-in-the-loop before answers become **institutional knowledge**
- FTS5 first; vectors/LLM optional v2 if IT allows

**Avoid**

- “Production-ready enterprise platform”
- “Semantic understanding” (unless you add v2 embeddings)

**Tradeoffs**

- **FTS5 not vectors** — Office-safe, explainable; synonyms help keyword gaps
- **Extractive summary not GPT** — No API keys; honest limitations
- **SQLite not Postgres** — Single-laptop demo; easy setup
- **Review queue** — Trust and audit over raw generation

---

## 8. Out of scope for v1.0

- SSO, multi-tenant, live Confluence/GitHub APIs
- FAISS, Ollama, LangGraph (optional v2.0)
- YAML/code parsers (future plugins)

---

## 9. Next docs

- [OFFICE_SAFETY.md](OFFICE_SAFETY.md)
- [INGESTION_GUIDE.md](INGESTION_GUIDE.md)
- [API_REFERENCE.md](API_REFERENCE.md)
