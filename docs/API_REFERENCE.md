# API reference (v1.1)

- **Base URL:** `http://127.0.0.1:8000`
- **Prefix:** `/api/v1`
- **Interactive docs:** http://127.0.0.1:8000/docs

---

## Health

- `GET /health` — Status and offline mode flag

---

## Documents

- `POST /documents/upload` — Upload one file (multipart)
- `POST /documents/ingest-folder` — Index a local folder (JSON body)
- `GET /documents` — List documents
- `GET /documents/{id}` — Document metadata
- `PATCH /documents/{id}` — Update status, tags, version, related ids
- `GET /documents/{id}/chunks` — Chunks for viewer
- `DELETE /documents/{id}` — Remove document

---

## Search

- `GET /search` — Query `q`; optional filters; response includes `confluence_live` (PAT)
- `GET /rag/status` — Local RAG bot / Ollama reachability
- `POST /rag/chat` — `{ "message", "history" }` — FTS retrieval + optional Ollama
- `POST /search/click` — Record click for analytics (JSON body)

---

## Governance audit

- `GET /governance/audit` — Immutable events (`limit`, optional `event_type`)

## Agent tools (read-only, optional Bearer API key)

- `GET /agent-tools/search`, `/documents`, `/lineage/index`, `/lineage/{id}`

See `docs/PLATFORM_INTEGRATIONS.md`.

---

## Ask and governance

- `GET /ask/plan` — Planner JSON only (query param `q`)
- `POST /ask` — Full pipeline; creates review item
- `GET /reviews` — List reviews (optional `status`)
- `GET /reviews/approved` — Approved knowledge library
- `GET /reviews/{id}` — Review detail
- `GET /reviews/{id}/audit` — Audit actions
- `POST /reviews/{id}/approve` — Approve draft
- `POST /reviews/{id}/reject` — Reject
- `POST /reviews/{id}/edit` — Edit and approve

---

## Lineage

- `GET /lineage` — Index of review items
- `GET /lineage/{review_item_id}` — Full lineage payload

---

## Analytics

- `GET /analytics/summary` — Search stats, `search_volume_by_day`, knowledge health, Confluence stats
- `GET /analytics/governance` — Review rates, validator, trusted docs

---

## Agents & automations

- `GET /agents` — Registry (interactive + automation agents)
- `POST /orchestrate` — Full governed pipeline (optional `Authorization: Bearer` if `KNOWLEDGEPILOT_API_KEY` set)
- `POST /automations/run` — Run corpus steward / new hire autopilot / search quality
- `GET /automations/schedule` / `PUT /automations/schedule` — UI weekly/daily schedule (UTC; API must stay running)
- `GET /automations/inbox` — Latest automation summaries + report paths
- `GET /reviews/triage` — Group similar pending reviews
- `GET /automations/runs` — Run history
- `GET /automations/runs/{execution_id}` — Run detail

Cron: `./scripts/run-automations.sh`

---

## Onboarding (new hire guide)

- `GET /onboarding/meta` — Import totals and source file
- `GET /onboarding/items` — Filter by `q`, `category`, `day`
- `POST /onboarding/import-file` — Upload KT workbook
- `POST /onboarding/import-default` — Import from `config/onboarding/`
- `GET /onboarding/link-health` — Parseable Confluence page IDs from guide URLs
- `POST /onboarding/sync-confluence` — Bulk sync guide Confluence pages into Search

---

## Jobs

- `GET /jobs/{id}` — Folder ingest job status
