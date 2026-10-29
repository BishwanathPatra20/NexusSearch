# Platform integration patterns (original NexusSearch code)

NexusSearch implements **ideas inspired by** open projects in Tiers 1–4. We do **not** copy or vendor AGPL/commercial code from those repos. All modules below are authored for NexusSearch (MIT-style project license).

| Inspiration (Tier) | NexusSearch module | What it does |
|---------------------|-------------------|--------------|
| **nexus-kb** (T1) | `governance_audit_service.py`, `/governance/audit` | Immutable audit events (search, review, sync) |
| **nexus-kb** (T1) | `/agent-tools/*`, `scripts/nexus_readonly_mcp.py` | Read-only agent/MCP bridge (search, docs, lineage) |
| **confluence2md / OpenDocuments** (T1) | `hybrid_rerank_service.py` | Post-FTS title/snippet overlap rerank (local, no cloud ML) |
| **Onyx / Gebo** (T2) | `confluence_schedule_service.py`, `/confluence/sync-schedule` | Scheduled PAT space/parent sync (APScheduler) |
| **Onyx** (T2) | Live Confluence search (existing) | PAT fetch; 403 surfaced as `confluence_live_error` |
| **Scribegate / OpenKB** (T3) | `knowledge_integrity_service.py` | SHA-256 on approved answers + source chunk IDs in lineage |
| **Haystack** (T6) | `hybrid_rerank_service.py` | Rerank stage after retrieval (lexical, office-safe) |

## Office-safe defaults

- No new cloud SDKs or embedding downloads in `requirements.txt`.
- MCP and agent-tools are **read-only**; optional `KNOWLEDGEPILOT_API_KEY` for localhost hardening.
- Confluence remains **HTTPS to your wiki only** via existing PAT settings.

## MCP setup (Cursor)

```json
{
  "mcpServers": {
    "nexussearch": {
      "command": "python3",
      "args": ["/path/to/NexusSearch/scripts/nexus_readonly_mcp.py"],
      "env": {
        "KNOWLEDGEPILOT_API_URL": "http://127.0.0.1:8000/api/v1"
      }
    }
  }
}
```

Start `./scripts/start-api.sh` first.

## Scheduled Confluence sync

```bash
curl -X PUT http://127.0.0.1:8000/api/v1/confluence/sync-schedule \
  -H 'Content-Type: application/json' \
  -d '{"enabled":true,"parent_page_id":"YOUR_ROOT_PAGE_ID","max_pages":80}'
```

Or set `space_key` instead of `parent_page_id`. Cron hour/minute: `KNOWLEDGEPILOT_CONFLUENCE_SCHEDULE_CRON_HOUR` / `_MINUTE` in `.env`.

## Governance audit

```bash
curl -s 'http://127.0.0.1:8000/api/v1/governance/audit?limit=20'
```

## Toggle hybrid rerank

`KNOWLEDGEPILOT_HYBRID_RERANK_ENABLED=false` in `.env` to disable.

## Local RAG bot (optional)

- Floating **Corpus assistant** on every UI page (green FAB, bottom-right).
- `POST /api/v1/rag/chat` — FTS retrieval + Ollama when reachable; extractive fallback otherwise.
- `GET /api/v1/rag/status` — Ollama reachability.
- Disable UI: `KNOWLEDGEPILOT_RAG_BOT_ENABLED=false`. Disable LLM only: `KNOWLEDGEPILOT_RAG_LLM_ENABLED=false`.
- Install [Ollama](https://ollama.com) locally and `ollama pull llama3.2` (or set `KNOWLEDGEPILOT_OLLAMA_MODEL`).
