# Brain Health and Cache v1

## Health states
- healthy
- stale
- degraded
- unavailable

## Health payload (internal)
- state
- active_revision
- last_sync_at
- last_successful_sync_at
- index_document_count
- index_unit_count
- stale_after_seconds
- last_error_code|null

## Cache rules
Cache:
- normalized canonical documents
- common invariant bundle
- common task-mode rule bundles
- retrieval results keyed by brain revision + normalized task signature

Never cache:
- secrets
- cross-workspace private context in shared cache keys
- unapproved candidates as canonical

## Revision pinning
Each ProductionPlan stores brain_revision.
A retry may:
- reuse pinned revision for reproducibility
- use current revision only if explicitly re-planned

## Rollback
If new revision validation fails, continue with last known-good revision.
