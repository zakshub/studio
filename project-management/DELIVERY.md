# FashionOS delivery and remaining work

Date: 2026-09-22
Repository: https://github.com/zakshub/studio
Canonical branch: main
Figma: https://www.figma.com/design/wdzD8DwmeulOeRUOqaQe64/fos-brain

## What is delivered
- M0 canonical foundation, M1 frozen backend contract and M2 retrieval service.
- Regression-tested M3 dual-provider generation/edit/verifier and versioned benchmark foundations, and M4 governed intake/object storage foundations from upstream main.
- Collection Studio desktop entry/list/overview, blocked evidence review, image-backed demo approval/refinement, permission restrictions and rejection/history designs.
- Synthetic image fixtures, provenance, QA reports and reconciled canonical status documents.

This repository is a working intelligence service and product-design foundation, not a complete deployed FashionOS customer application. Figma screens are saved in Figma; Git contains their evidence, links and fixture assets, not a runnable frontend.

## Unresolved completion gates
| Area | Remaining work / prerequisite |
|---|---|
| M3 evidence | Configure provider secrets outside Git; run live generation/edit and dual-provider verification; authorized benchmark assets and actual cost/latency evidence |
| M4 evidence | Approved website/terms registration, live storage validation, quality screening/primary selection; separate remote work is not delivery until merged/tested |
| Persistence | Real PostgreSQL migration validation and storage/backup policy |
| Collection Studio | Semantic input and error/focus/filled states, responsive/accessibility QA, submission failure/stale decisions, Collection/Look contract and CRUD integration |
| Remaining product | Design Intelligence, Visualization, Image Treatment, Campaign, architecture/flow documentation, customer frontend/backend integration |
| Governance | Validate first 10 expert profiles with human approval; remaining 40 profiles; production access/security/deployment QA |

No secret values should be committed or pasted into a chat. No expert profile is ACTIVE.

## Windows pull and local regression
Run in a clean checkout; inspect local changes before pulling. Never reset away uncommitted work.

```powershell
cd D:\codex\fos
git status --short
git pull --ff-only origin main
.venv\Scripts\python.exe -m pip install -e './services/intelligence-api[test]'
cd services\intelligence-api
D:\codex\fos\.venv\Scripts\python.exe -m pytest -q
```

If the virtual environment does not exist, first create it with Python 3.13 or newer: `py -3.13 -m venv .venv`.
Latest local result: 80 passed, 2 known dependency deprecation warnings, 0 failed. This does not require live provider credentials and does not prove production integrations.
