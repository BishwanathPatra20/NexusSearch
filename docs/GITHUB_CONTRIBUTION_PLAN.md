# GitHub contribution plan (day-wise)

Incremental commits to [NexusSearch](https://github.com/BishwanathPatra20/NexusSearch) so history looks natural and CI stays green. **Do not** `git add .` in one shot.

## Rules

1. **One theme per commit** — subject line explains the slice (feat/chore/ci/docs).
2. **No Cursor on Contributors** — run `./scripts/install-git-hooks.sh` once; before every push run `./scripts/strip-cursor-attribution-from-unpushed.sh`. Verify:  
   `git log @{u}..HEAD --format=%B | grep -iE 'co-authored-by: cursor|made-with: cursor|cursoragent'` → empty.
3. **Cursor Settings** — Git & PRs → Attribution → Commit attribution **OFF**.
4. **Never commit** to the app repo: `settings.xml`, `effective-pom*.xml`, `dependency-tree.txt`, `.env` (only `.env.example`).
5. **CI** — pytest runs only after `tests/test_*.py` exists on the remote; until then workflow skips tests by design.

## Completed

| Day | Commits (summary) | On GitHub |
|-----|-------------------|-----------|
| 1 | Scaffold, README, merge, CI skip without tests | Yes |
| 2 | Config, constants, `backend/app/db/*`, `schemas/models.py`, CI v7/ubuntu-24.04, `config/synonyms.json` | Yes |
| — | Git hooks + agent rule (clean commit messages) | Yes |
| 3 | Ingestion parsers, chunker/fingerprint/base, Confluence export helper | Yes |

## Remaining schedule

| Day | Focus | Paths (typical) |
|-----|--------|-----------------|
| **4** | Documents & jobs | `document_service`, `job_service`, `text_snippet`, `routes/documents.py`, `routes/jobs.py` |
| **5** | Search & synonyms | `search_service`, `synonym_service`, `synonym_proposal_service`, `schemas/search_filters.py`, `routes/search.py`, `routes/synonyms.py` |
| **6** | Governed Ask & reviews | `agents/*`, `governance_service`, `orchestration_service`, `review_service`, `routes/ask.py`, `routes/reviews.py` |
| **7** | Lineage & analytics | `lineage_service`, `analytics_service`, `routes/lineage.py`, `routes/analytics.py` |
| **7b** | Extra schemas | `schemas/agents.py`, `schemas/confluence.py`, `schemas/onboarding.py` (split if large) |
| **8** | Automations | `services/automation/**`, `automation_scheduler`, `automation_schedule_service`, `agent_*`, `routes/agents.py` |
| **9** | Confluence & onboarding | `integrations/*`, `confluence_*`, `onboarding_*`, `onboarding_days.py`, `config/onboarding/README.md`, corpus markdown (defer large `.xlsx` or use LFS) |
| **10** | API entry | `main.py`, `api/agent_auth.py`, `api/routes/__init__.py` + any routes not yet pushed |
| **11** | Streamlit UI | `frontend/**`, `.streamlit/config.toml` tweaks if needed |
| **12** | Tests, docs, samples | `tests/`, `docs/` (including this file), `samples/demo_corpus`, `scripts/import_onboarding_xlsx.py`, `scripts/run-automations.sh` |

## Suggested commit count per day

- **2–4 commits** per day (e.g. Day 4: services → routes).
- Push at end of day after strip script + message check.

## Optional repo polish (any day)

- GitHub **About** description + topics (`fastapi`, `streamlit`, `knowledge-management`).
- Skip junk assets (e.g. stray `.webp` not in brand set).

## Local vs remote

As of last update, the **full runnable app** (API, services, UI, tests) may still be local-only until Days 4–12 land. Track progress with:

```bash
git status -sb
git ls-files | wc -l
```

## History rewrite

If a commit message must change on `main`, use `git filter-branch` / `filter-repo` on a range, then `git push --force-with-lease origin main`. Expect GitHub **Contributors** sidebar to lag after rewrites (cache, not always live git log).
