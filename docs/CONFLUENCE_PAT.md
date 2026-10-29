# Confluence PAT / API token integration

NexusSearch can **pull pages from Confluence Cloud** over HTTPS and index them locally (search, citations, **Open original source** links). This is **optional** and separate from offline folder export ingest.

## Security

- Store credentials only in **`.env`** on your machine (never commit `.env`).
- Traffic goes **only** to your `CONFLUENCE_BASE_URL` (Atlassian).
- No tokens are sent to cloud LLMs.
- Enable only if your **security / IT policy** allows Confluence API access from your laptop.

## 1. Create an Atlassian API token

1. Log in to Atlassian: https://id.atlassian.com/manage-profile/security/api-tokens  
2. **Create API token** (label e.g. `NexusSearch-local`).  
3. Copy the token — you will not see it again.

You need the **email** of the Atlassian account that owns the token.

## 2. Configure NexusSearch

Copy `.env.example` to `.env` in the project root and set:

```bash
KNOWLEDGEPILOT_CONFLUENCE_ENABLED=true
KNOWLEDGEPILOT_CONFLUENCE_BASE_URL=https://YOUR-SITE.atlassian.net/wiki
# Server/DC example: https://confluence.sys.cigna.com  (no /wiki)
KNOWLEDGEPILOT_CONFLUENCE_EMAIL=you@company.com
KNOWLEDGEPILOT_CONFLUENCE_API_TOKEN=your_api_token_here
```

**Base URL**

- Use your Confluence site root, with or without `/wiki` — NexusSearch normalizes it.  
- Examples:  
  - `https://cignatlp.atlassian.net/wiki`  
  - `https://your-org.atlassian.net`

Restart the API after changing `.env`:

```bash
./scripts/start-api.sh
```

## 3. Verify connection

```bash
curl -s http://127.0.0.1:8000/api/v1/confluence/status | python3 -m json.tool
```

Expect `"reachable": true` and your display name.

Or open **Ingest hub → Confluence** in the UI.

### Read-only / audit mode

To allow **status** and space browse without indexing from this laptop:

```bash
KNOWLEDGEPILOT_CONFLUENCE_SYNC_ENABLED=false
```

Sync endpoints return **403**; PAT stays in `.env` only (never commit).

## 4. Sync pages

**UI (Ingest hub → Confluence):**

- **Single page** — re-sync when wiki changes (`pageId` from URL)  
- **Multiple IDs / URLs** — paste a DEC/P360 list  
- **Parent + children** — sync a page tree (optional background job)  
- **Whole space** — e.g. `DEC` with limit + background job for 100+ pages  

**API (batch):**

```bash
curl -s -X POST http://127.0.0.1:8000/api/v1/confluence/sync-pages \
  -H "Content-Type: application/json" \
  -d '{"page_ids":["1512556436","1261308608"],"tags":["confluence","p360"],"replace_existing":true}'
```

**API (descendants):**

```bash
curl -s -X POST http://127.0.0.1:8000/api/v1/confluence/sync-descendants \
  -H "Content-Type: application/json" \
  -d '{"parent_page_id":"1512556436","max_pages":50,"include_parent":true}'
```

## 5. Sync a space

**Live search (no ingest):** On **Search**, NexusSearch can call Confluence with your PAT when you enter a **page id** (or URL with `pageId`) or a **title** — pages not yet ingested appear under **Live from Confluence (PAT)**. Use **Ingest this page** to add them to the local index for citations and review.

**UI:** Ingest hub → Confluence → **Whole space**

**API:**

```bash
curl -s -X POST http://127.0.0.1:8000/api/v1/confluence/sync \
  -H "Content-Type: application/json" \
  -d '{"space_key":"TEAM","limit":25,"tags":["confluence","team"],"replace_existing":true}'
```

- **`limit`**: max pages per run (1–100).  
- **`replace_existing`**: re-sync updates pages already imported (`confluence://page/<id>`).

Indexed pages get tags `confluence` and `space:<KEY>`. Search and Document viewer show **Open original source** when Confluence returns a web URL.

## Server / Data Center (e.g. `confluence.sys.cigna.com`)

Many corporate instances **disable Basic auth**. Use a **Personal Access Token** and:

```bash
KNOWLEDGEPILOT_CONFLUENCE_AUTH_MODE=bearer
KNOWLEDGEPILOT_CONFLUENCE_API_TOKEN=your_pat_here
```

Email is optional for Bearer PAT; keep it if your IT docs require it.  
`auto` (default) uses **bearer** for non-`atlassian.net` hosts.

## Troubleshooting

| Issue | Fix |
|--------|-----|
| 403 Basic Authentication disabled | Set `CONFLUENCE_AUTH_MODE=bearer` and use a PAT |
| 401 Unauthorized | Check email + token; token not expired |
| 404 / wrong host | Fix `CONFLUENCE_BASE_URL` (must be your Cloud wiki) |
| SSL errors | Corporate proxy — set `KNOWLEDGEPILOT_CONFLUENCE_VERIFY_SSL=false` only if IT allows |
| Empty pages | Page has no storage body (live docs / macros) — use export for those |

## Still use exports when

- IT blocks API from laptops  
- You need attachments or complex macros  
- You want a one-time snapshot with no live calls  

Folder-ingest HTML exports remains fully supported.
