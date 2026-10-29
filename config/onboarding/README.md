# KT onboarding workbook

Place your Excel file here:

`Personalization_KT_Onboarding_10Day.xlsx`

## Column headers (flexible)

The importer recognizes common names (case-insensitive), for example:

| Purpose | Example column names |
|--------|----------------------|
| Day / week | Day, Week, Phase, Timeline |
| Topic | Topic, Task, Module, Activity, Title |
| Notes | Description, Notes, Details |
| Confluence | Confluence link, Wiki, Page |
| Tickets | Jira, ServiceNow, Access request, Ticket link |
| Access | AD group, Global group, Entitlement, Role |
| Owner | POC, Contact, SME, Owner |

URLs in any cell are detected. Multiple sheets are supported (one tab per area is fine).

## Import options

1. **UI:** Sidebar → **New hire guide** → upload `.xlsx`
2. **CLI:** `PYTHONPATH=. .venv/bin/python scripts/import_onboarding_xlsx.py [path-to.xlsx]`
3. **Auto:** On API startup, if this folder contains the default filename and the DB has no onboarding rows yet

After import, NexusSearch builds a searchable markdown guide and indexes it for **Search**.
