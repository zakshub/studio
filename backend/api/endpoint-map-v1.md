# FashionOS API Endpoint Map v1

Base public API: /api/v1
Internal service API: /internal/v1

## Public/customer-facing endpoints

### Workspace
- GET /api/v1/workspaces/:workspaceId
- PATCH /api/v1/workspaces/:workspaceId
- GET /api/v1/workspaces/:workspaceId/context
- PUT /api/v1/workspaces/:workspaceId/context

### Tasks
- POST /api/v1/tasks
- GET /api/v1/tasks/:taskId
- GET /api/v1/tasks
- POST /api/v1/tasks/:taskId/cancel
- POST /api/v1/tasks/:taskId/retry

### Sources / assets
- POST /api/v1/assets/upload
- POST /api/v1/sources/websites
- GET /api/v1/sources/:sourceId
- GET /api/v1/assets
- GET /api/v1/assets/:assetId
- GET /api/v1/assets/:assetId/versions
- POST /api/v1/assets/:assetId/actions

### Jobs
- GET /api/v1/jobs/:jobId
- GET /api/v1/tasks/:taskId/jobs

### Review / approval
- GET /api/v1/reviews
- GET /api/v1/reviews/:reviewId
- POST /api/v1/reviews/:reviewId/approve
- POST /api/v1/reviews/:reviewId/reject

### Customer-safe QC
- GET /api/v1/jobs/:jobId/quality
Returns only safe summaries, warnings, preservation status, and review requirement.

## Internal endpoints

### Brain service
- POST /internal/v1/brain/retrieve
- POST /internal/v1/brain/sync
- GET /internal/v1/brain/health
- GET /internal/v1/brain/revision

### Orchestration
- POST /internal/v1/orchestrator/plan
- POST /internal/v1/orchestrator/dispatch
- POST /internal/v1/orchestrator/retry

### Executor gateway
- POST /internal/v1/executors/run
- POST /internal/v1/executors/compare
- POST /internal/v1/executors/verify
- GET /internal/v1/executors/health

### QC
- POST /internal/v1/qc/evaluate
- GET /internal/v1/qc/:qcId

### Provenance
- POST /internal/v1/provenance/executions
- POST /internal/v1/provenance/asset-lineage
- GET /internal/v1/provenance/tasks/:taskId

### Learning
- POST /internal/v1/learning/candidates
- GET /internal/v1/learning/candidates
- POST /internal/v1/learning/candidates/:candidateId/promote
- POST /internal/v1/learning/candidates/:candidateId/reject

### Benchmarks
- POST /internal/v1/benchmarks/runs
- GET /internal/v1/benchmarks/capabilities/:capability
- POST /internal/v1/benchmarks/recompute-routing

## Rules
- Public endpoints must never expose internal provider/model names by default.
- Internal endpoints require service authentication and are not browser-accessible.
- Repository paths/commits remain internal.
- Every mutating endpoint must emit an AuditEvent.
