# NexusSearch

**Local-first knowledge governance platform** (v1.1) — ingest documents, search with citations, review draft answers, promote approved institutional knowledge, trace lineage, measure governance.

```text
Ingest → Index → Search → Plan → Draft → Validate → Review → Approve
  → AK-XXXX → Lineage → Metrics
```

---

## Documentation (start here to study)

**[docs/README.md](docs/README.md)** — reading order and full index.

- **[STUDY_GUIDE.md](docs/STUDY_GUIDE.md)** — Main learning guide
- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** — Diagrams and layers
- **[OFFICE_SAFETY.md](docs/OFFICE_SAFETY.md)** — Corporate / offline laptop
- **[DEMO_SCRIPT.md](docs/DEMO_SCRIPT.md)** — 5-minute live demo

---

## Quick start

```bash
cd NexusSearch
python3.11 -m venv .venv && source .venv/bin/activate   # 3.9+ supported; 3.11 recommended
pip install -r requirements.txt
export PYTHONPATH=.
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

./scripts/start-api.sh    # terminal 1
./scripts/start-ui.sh     # terminal 2
```

- **UI:** http://127.0.0.1:8501
- **API docs:** http://127.0.0.1:8000/docs

**Demo data:** folder-ingest `samples/demo_corpus` (synthetic).

---

## Elevator pitch

*NexusSearch is a local-first knowledge governance prototype: citation-backed search, extractive drafts, human review, auditable approved knowledge with lineage and metrics—without external AI APIs.*

---

## Version

- **v1.0** — Feature freeze
- **v1.1** — UI polish, analytics export, onboarding Confluence sync, CI (current)
- **v2.0** — Optional local AI (IT approval) — [docs/V2_LOCAL_AI_DESIGN.md](docs/V2_LOCAL_AI_DESIGN.md)

More: [docs/V1.1_RELEASE_NOTES.md](docs/V1.1_RELEASE_NOTES.md)

---

## License

MIT (adjust if internal-only).
