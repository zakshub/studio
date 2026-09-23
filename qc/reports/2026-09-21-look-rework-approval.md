# Look rework and blocked approval QA - 2026-09-21

Result: PASS for rework/missing-evidence desktop states only. Not completion of Collection Studio.

Canonical file: https://www.figma.com/design/wdzD8DwmeulOeRUOqaQe64/fos-brain?node-id=50-191

| Object | Node |
| --- | --- |
| Rework look detail | 50:191 |
| Compare/refine - evidence unavailable | 50:230 |
| Blocked approval | 50:269 |
| External intelligence/fixture annotation | 51:288 |

## Evidence and behavior
Screenshots inspected for detail, comparison and blocked approval. Inter family and zero child overflow verified in all three screens and updated overview. No private provider/methodology terms appear in customer copy. Existing token-bound components reused; completed architecture unchanged.

Overview row 47:311 and button 50:491 open detail. Detail back 50:462 -> 47:120; compare 50:465 -> 50:230; approval status 50:468 -> 50:269. Compare back 50:472 -> 50:191; status 50:475 -> 50:269. Approval back 50:482 -> 50:191; inspect 50:485 -> 50:230. Verified by Figma API read-back.

Process correction 50:478 and Approve version 3 50:488 have no reactions and reduced opacity. No mutation or successful approval is implied. Preservation failure cannot be overridden. Missing source/result evidence, rights and reviewer confirmation are called out explicitly.

The embroidery issue and version number are fixtures inherited from the sample overview. No real imagery was used or compared. Preview-unavailable panels are designed error states, not completed image-backed comparisons. The 400 x 500 matching shells do not imply a crop policy for actual evidence; original source ratio must be respected when real images are integrated.

## Defects and limitations
No new overflow or font defects after verification. Previously discovered instance paint/width issues avoided using resolved token fallback colors and FILL text sizing. Collection/Look persistence and comparison data remain contract gaps. Successful image-backed path, refinement submission, approval/rejection/decision-history states, responsive layout, keyboard and full accessibility QA remain pending.

## Regression
Command from services/intelligence-api: `D:\codex\fos\.venv\Scripts\python.exe -m pytest -q`.
Result: **70 passed, 2 warnings in 6.57s** on Windows/Python 3.13.15. Warnings: Starlette httpx TestClient and AnyIO BlockingPortal deprecations. Backend code unchanged; no live provider execution proven.

STATUS, BACKLOG and CODEX-HANDOFF updated. Local changes uncommitted/unpushed.
