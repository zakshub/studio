# Collection/Look persistence and authorization QA

Date: 2026-09-27

## Result

PASS for the additive draft Collection/Look runtime slice. This does not prove production authentication or PostgreSQL deployment.

## Delivered

- Explicit v2 extension document preserving the frozen v1 API.
- Workspace membership, Collection, Look and append-only mutation-event persistence.
- PostgreSQL migration `0007_collections.sql`.
- Workspace-scoped list/create/detail/update operations and nested Look operations.
- Reversible archive/restore; no destructive delete endpoint.
- Expected-revision checks on parent and child mutations.
- Idempotent caller-UUID create replay without duplicate audit events.
- Same-workspace, authorized primary/production source checks and same-workspace Task checks.
- Allowlisted customer responses that exclude source storage, arbitrary metadata and provider details.
- Fail-closed verified-identity dependency; spoofed user/role/workspace headers do not grant access.
- Five-minute HMAC-signed gateway assertions binding actor, timestamp, HTTP method and request path.

## Automated validation

Command: `D:\codex\fos\.venv\Scripts\python.exe -m pytest -q`

Result: **84 passed, 2 dependency deprecation warnings, 0 failed** in 11.29s after fast-forwarding to upstream `d0fbd8c`.

The focused suite verifies persistence across repository instances, exact replay, workspace isolation, Viewer draft restrictions, role revocation, source-rights rejection, task scope, original-source immutability, archive/restore, stale-write rollback, atomic audit counts, cursor pagination, strict input validation, safe validation errors, signed authentication, assertion expiry/path binding and fail-closed API behavior.

`compileall` and `git diff --check` also passed.

## Remaining evidence gates

- A deployment must configure a strong workspace-auth secret and terminate user authentication at a trusted identity provider or gateway; FashionOS validates the signed actor assertion but does not provide a user-login UI.
- Membership provisioning currently remains a trusted repository/service operation.
- PostgreSQL migration execution has not been tested against a real PostgreSQL instance.
- Approved viewer projections, immutable asset-version comparison and Approval workflow integration remain separate from draft organization.
- Figma form semantics, stale/error states, responsive behavior and complete accessibility checks remain open.
