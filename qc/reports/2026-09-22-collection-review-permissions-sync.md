# Collection Studio image-backed review and permission QA

Date: 2026-09-22
Scope: recover the previously unsaved image-backed batch, finish desktop permission/rejection variants, reconcile upstream backend work.

## Result
PASS for the listed desktop prototype and current credential-independent backend regression. Collection Studio and the overall product are not complete.

| Screen | Figma node |
|---|---|
| Image-backed detail | 53:288 |
| Source/result comparison | 53:327 |
| Approval confirmation | 53:366 |
| Approved history | 54:369 |
| Refinement request | 54:408 |
| Refinement requested | 55:554 |
| Contributor: approval restricted | 59:463 |
| Reject version | 59:622 |
| Rejected history | 59:669 |
| Viewer: pending review restricted | 60:551 |

Canonical file: https://www.figma.com/design/wdzD8DwmeulOeRUOqaQe64/fos-brain

## Checks and fixes
- Visually inspected the six image-backed screens in the prior batch and all four new role/rejection screens in this batch.
- Read-back of all ten screens: Inter only, no visible child overflow; source/result images use the expected hashes with FIT.
- Approval/refinement/rejection confirmations navigate to their matching demo outcomes; version-specific decisions never overwrite the source.
- Contributor approval has no reaction. Viewer has no pending image preview or decision action.
- Removed the viewer return route to the unrestricted fixture list, which would reveal pending items. This is a standalone role scenario, not working role-based authentication.
- Removed the inappropriate search icon from the refinement field; read-back shows only its text child.
- Corrected rejection/disabled-action node names. Reused the existing danger button component.
- Role scope follows backend/security/permissions-model.md. Rejection is a review decision label, not a newly invented Task state.
- The prior combined verification action timed out; its success was never assumed. Subsequent read-only verification succeeded, and this batch applied and verified the icon fix.
- GitHub main advanced from 00f81a1 to 0559388. Fast-forwarded and restored local design changes. Resolved two documentation conflicts preserving both backend and design progress.

## Regression
Windows, Python 3.13.15; updated declared dependencies installed.
Command: D:/codex/fos/.venv/Scripts/python.exe -m pytest -q
Working directory: services/intelligence-api
Result: 80 passed, 2 dependency deprecation warnings, 0 failed in 5.39s.
Warnings concern Starlette's httpx TestClient and AnyIO BlockingPortal. No runtime code was changed in this design synchronization batch.

## Remaining gates
- Static fields still need a semantic input component and focus/error/filled states.
- Responsive layouts, complete accessibility/contrast/keyboard checks and remaining state QA are unfinished.
- Collection/Look CRUD and comparison data are not defined by frozen v1. No live submission was wired.
- Role fixtures do not enforce authentication; server-side authorization and role-specific navigation must be implemented and tested.
- No live provider, website, S3 or PostgreSQL validation is claimed. Provider credentials and approved deployment/test resources remain external prerequisites.
- Synthetic fixture provenance: design/fixtures/collection-studio/README.md.
