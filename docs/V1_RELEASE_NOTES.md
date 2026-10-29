# Release notes — v1.0.0

**Status:** Feature freeze · local-first knowledge governance prototype

---

## Included in v1.0

- Multi-format ingestion (PDF, DOCX, TXT, MD, HTML) and folder ingest
- Hybrid chunking and FTS5 search with citations
- Synonyms and search filters; explainable ranking
- Document lifecycle, relationships, knowledge health
- Agent pipeline (planner, search, extractive summary, validator) without cloud LLMs
- Review queue, audit trail, approved knowledge (`AK-XXXX`)
- Lineage API/UI and governance metrics
- Confluence **export** HTML: optional **source_link** on documents (open wiki in browser; no live API)

---

## Not included

- Production SSO, multi-tenant, live Confluence/GitHub connectors (PAT/API — revisit when IT approves)
- Semantic search / RAG / Ollama (optional v2.0, IT-gated)

---

## Roadmap after v1.0

- **v1.1** — UI polish, charts, export reports
- **v2.0** — Optional embeddings and local LLM (only if IT approves)

---

## Git tag (when you publish)

```bash
git tag -a v1.0.0 -m "NexusSearch v1.0 — knowledge governance feature freeze"
git push origin v1.0.0
```

---

## Documentation

Index: [docs/README.md](README.md)
