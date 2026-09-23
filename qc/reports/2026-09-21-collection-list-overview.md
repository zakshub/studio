# Collection list and overview QA - 2026-09-21

Result: PASS for this bounded operational desktop design batch. Collection Studio remains IN PROGRESS.

## Deliverables
Canonical file: https://www.figma.com/design/wdzD8DwmeulOeRUOqaQe64/fos-brain?node-id=47-81

| Object | Node |
| --- | --- |
| Collections / List | 47:81 |
| Collection / Overview | 47:120 |
| Collections / Context setup from list | 48:278 |
| External intelligence/fixture annotation | 48:156 |

All screens are 1440 x 1024. Existing components and token system reused. Shared main components and prior entry screens unchanged. Lists contain illustrative fixture data, not actual customer or production results.

## Behavior and contract checks
- Three example collection rows show task/review progress.
- Overview shows three distinct situations: quality passed with human approval pending; preservation failure with approval unavailable; unknown source permission with production blocked.
- Collection names/grouping remain design concepts; frozen v1 still lacks Collection/Look persistence and CRUD. No new runtime behavior or endpoint invented.
- Text-list presentation is intentional for operational status; imagery and visual look-detail work remain open.
- New collection 47:278 -> setup 48:278 -> back 48:299 -> populated list 47:81.
- Open Studio collection 47:281 -> overview 47:120 -> back 47:320 -> list 47:81.
- Continue remains disabled with no reaction. Other collection/look rows are static. No save, approve or production action implemented.

## Visual and structural verification
Screenshots inspected for list, overview and list-origin setup. Read-back checks: only Inter; zero child overflow; Collections sole active sidebar item; no private provider/methodology terms in list/overview; no unfinished shimmer; action heights 48px. All six row text areas read back at 1072px width and white surfaces retain FOS variable bindings. Prototype destinations checked via Figma API, not an end-user browser interaction.

Defects found and fixed:
1. Summary instance text resize did not persist: changed instance text to FILL within auto-layout.
2. Aliased instance fills retained black fallback: resolved the existing light-mode token value into paint fallback and retained variable bindings.
3. Reusing original setup would return to the empty screen: added a list-origin setup clone with the correct back destination, preserving the old flow.

Full keyboard, contrast, dark-mode, responsive and component-state accessibility QA remains pending. No claim of a complete visual collection experience.

## Regression
From services/intelligence-api:
`D:\codex\fos\.venv\Scripts\python.exe -m pytest -q`

Python 3.13.15 on Windows. Result: **70 passed, 2 warnings in 4.28s**.
Warnings remain Starlette httpx TestClient and AnyIO BlockingPortal deprecations. Backend code unchanged. Tests do not establish live provider validation.

STATUS, BACKLOG and CODEX-HANDOFF updated. No commit or push performed. Next: look detail, compare/refine, approval.
