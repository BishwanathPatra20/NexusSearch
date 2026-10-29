# v2.0 — optional local AI (design sketch)

**Purpose:** IT-gated path to semantic search and richer Ask drafts without sending corpus data to public cloud APIs.

---

## Goals

- Hybrid retrieval: FTS5 (today) + local embeddings index
- Optional local LLM for draft generation (Ollama, llama.cpp, or approved on-prem endpoint)
- Same governance: validator, review queue, lineage, `AK-XXXX`

---

## IT checklist (before build)

| Item | Question for security / architecture |
|------|--------------------------------------|
| Model hosting | Approved on-laptop (Ollama) vs shared GPU server vs none |
| Network | Embeddings/LLM must stay on `127.0.0.1` or approved VPC only |
| Data residency | Confirm indexed chunks never leave boundary during embed/infer |
| Supply chain | Approved model artifacts; no HuggingFace pull from laptop if blocked |
| Audit | Log model id, prompt hash, source chunk ids per Ask (extend lineage) |
| Fallback | Feature flag: `KNOWLEDGEPILOT_LOCAL_LLM_ENABLED=false` default |

---

## Proposed architecture

```text
Search / Ask
  → Planner (unchanged)
  → Retrieval: FTS + vector (sqlite-vec or sidecar FAISS under data/)
  → Summary: extractive (v1) OR local LLM with citation-only context (v2)
  → Validator (stricter when LLM used)
  → Review → AK-XXXX
```

---

## Phased delivery

1. **Embeddings only** — re-rank FTS hits; no new draft model
2. **Local LLM drafts** — behind flag; max context from top-N chunks only
3. **Metrics** — embedding coverage %, LLM vs extractive approval rates

---

## Non-goals for v2.0

- Multi-tenant SaaS
- Confluence write-back
- Unreviewed auto-publish to production wiki
