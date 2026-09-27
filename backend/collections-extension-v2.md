# Collection Studio persistence extension v2

Status: explicit additive implementation decision, 2026-09-23. Frozen public v1 remains unchanged.

Collection Studio needs workspace-local organization that v1 did not define. This extension introduces draft Collection and Look records; it does not introduce a new generation engine, Task state, asset ownership claim or automatic approval.

## Domain and operations
- Collection: collectionId, workspaceId, name, objective, hardLocks, allowedChanges, revision, archived.
- Look: lookId, workspaceId, collectionId, name, sourceAssetId, optional taskId, revision.
- Sources and linked Tasks must already exist in the same workspace. Global/reference-only/unknown-rights source assets cannot be attached as production sources.
- Contributor, Approver and Admin may organize draft collections and looks. Viewer cannot read draft collection metadata or source associations; draft lists are empty and draft details are not found.
- Archive is reversible organization state, never physical deletion of originals, looks or audit events. Archived collections reject look mutations until restored.
- Every update requires an expected revision; stale updates return STATE_CONFLICT. Child writes also compare-and-increment the parent revision, preventing archive/edit races.
- Collection and Look create operations accept caller-generated UUID identifiers. Exact replay returns the existing record without a duplicate audit event; a different payload with the same ID returns STATE_CONFLICT.
- User inputs are typed, length-bounded and reject unexpected fields. Only allowlisted product fields are returned; no ORM object, source storage URI or arbitrary source metadata is serialized.
- Each mutation and its audit event commit atomically. Context remains scoped to the workspace and is never added to canonical brain knowledge.

## API boundary
New endpoints live at /api/v2/workspaces/{workspaceId}/collections, with nested /{collectionId}/looks. GET/POST list/create, GET/PATCH details. Collection PATCH includes archived for archive/restore. DELETE is deliberately absent to preserve records.

A trusted host may set a verified actor identity on `request.state.workspace_actor_id`. The standalone service also supports a signed gateway assertion using `X-FashionOS-Actor`, `X-FashionOS-Timestamp` and `X-FashionOS-Signature`, keyed by `FASHIONOS_WORKSPACE_AUTH_SECRET`. The signature covers actor, timestamp, HTTP method and path; assertions expire after five minutes. Raw X-User/X-Role/X-Workspace headers are never trusted. Persisted workspace membership is checked on every request. Missing or invalid verified identity returns UNAUTHORIZED; absent membership returns WORKSPACE_ACCESS_DENIED. This is a deployable authentication boundary, not a user-login or identity-provider implementation.

Membership provisioning is a trusted repository operation, not a customer endpoint. Roles cannot be set through collection payloads.

## Deferred boundaries
This slice is draft organization, not version review/approval or visual execution. Existing v1 Task/QC/Approval semantics remain authoritative. Approved viewer projections, immutable comparison versions, revision execution, full identity-provider integration and UI wiring remain separate work. SQL migration is authored for PostgreSQL; SQLite runtime tests do not prove PostgreSQL deployment.
