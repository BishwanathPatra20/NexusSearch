# 5-minute demo script

Presenter checklist for v1.0. Start API + UI first ([README](../README.md) Quick start).

**Opening (30 seconds)**  
*NexusSearch is a local-first knowledge governance prototype: cited search, draft answers, human review, approved knowledge with lineage and metrics—no cloud LLMs.*

---

## Steps

**1. Upload (~45s)**  
Folder ingest `samples/demo_corpus`; tags `demo`, `databricks`, `deployment`

**2. Search (~60s)**  
Query `rollout`; show synonyms, knowledge path, filters (active + tag)

**3. Document viewer (~30s)**  
Set `version_label` v3, status `active`

**4. Governed Ask (~90s)**  
Preview planner → ask about Databricks access → approve in queue

**5. Lineage (~60s)**  
Walk trace to `AK-XXXX` and source chunks

**6. Analytics (~45s)**  
Open Governance metrics tab

**Close (15 seconds)**  
*Prototype for governance patterns—not production SSO or live Confluence search. Confluence = export + ingest; HTML exports can show **Open original source**. Live PAT/API connector only if IT approves later.*


---

## Optional technical add-on

- http://127.0.0.1:8000/docs
- `GET /lineage/{id}` and `GET /analytics/governance`

---

## Related

- [SCREENSHOTS_AND_VIDEO.md](SCREENSHOTS_AND_VIDEO.md)
- [STUDY_GUIDE.md](STUDY_GUIDE.md)
