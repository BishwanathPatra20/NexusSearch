# Document ingestion guide

NexusSearch does **not** connect to Confluence, GitHub, or SharePoint over the network. You **bring files** (upload or local folder path).

Read first: [STUDY_GUIDE.md](STUDY_GUIDE.md)

---

## Golden rule

Index **before** you expect good Search or Ask results. Review only cites **already indexed** chunks.

```text
Attach files → Chunk → FTS index → Search / Ask
```

---

## Supported formats (v1.0)

- **PDF** — Policies, runbooks, scans
- **DOCX** — HR / ops Word docs
- **TXT** — Notes, exports
- **MD** — README, `docs/`, ADRs
- **HTML** — Confluence **export** (not live wiki)

**Not in v1.0:** YAML, JSON, Python (future parser plugins).

---

## How to attach

**Single upload**

- When: one file
- How: Upload tab or `POST /documents/upload`

**Folder ingest**

- When: repo `docs/`, wiki export folder
- How: Upload tab or `POST /documents/ingest-folder`

Folder ingest only reads the path **you** provide.

---

## Source-specific guidance

**Confluence**

- Do not use live API / PAT in NexusSearch until IT approves (optional future connector).
- Export space/pages → **HTML** (preferred) or PDF → folder ingest.
- HTML exports often include a wiki URL; NexusSearch stores it as **source_link** so Search and Document viewer show **Open original source** (you open Confluence in the browser yourself).

**Git / engineering docs**

- Ingest `README.md`, `docs/`, `wiki/`, `adr/`
- Exclude `.git/`, `node_modules/`, `dist/`, `target/`

**Release notes**

- One file per release; set `version_label` (e.g. `3.4`) and tags.

**Email / Teams**

- Export to PDF or TXT, then upload.

---

## Metadata best practices

- **Tags** — Search filters (e.g. `databricks`, `deployment`)
- **Status** — `active` vs `deprecated` affects ranking
- **version_label** — Health dashboard and filters
- **related_document_ids** — Linked docs on search hits

---

## Portfolio demo (synthetic)

1. Folder ingest `samples/demo_corpus`
2. Tags: `demo`, `databricks`, `deployment`
3. Search `rollout` → Governed Ask → Approve → Lineage

See [samples/demo_corpus/README.md](../samples/demo_corpus/README.md)

---

## When to re-ingest

- **New release doc** — Upload; deprecate old; update `version_label`
- **Wiki updated** — Re-export HTML; folder ingest again
- **Rejected review** — Fix source; re-ingest; ask again

---

## Office safety

- Data under `./data/` (gitignored)
- No runtime outbound network
- [OFFICE_SAFETY.md](OFFICE_SAFETY.md)
