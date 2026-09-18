# Persistence Model v1

## Recommended logical stores

### 1. Relational database
Use for transactional product state:
- users
- workspaces
- context profiles
- tasks
- jobs
- approvals
- source records
- asset metadata
- asset versions
- QC results
- execution records
- audit events
- benchmark records
- learning candidates
- website source registry

PostgreSQL is a suitable default.

### 2. Object storage
Use for binary assets:
- source images
- derived images
- generated images
- video/keyframes when authorized
- thumbnails
- exports
- technical artifacts

Requirements:
- immutable originals
- content hashing
- workspace partitioning
- signed access URLs
- retention policies
- versioned derivatives

### 3. Search/index layer
Use for retrieval:
- Studio Brain document chunks
- normalized metadata
- source observations
- expert intelligence summaries
- research candidates

May begin with PostgreSQL full-text/vector extension or a dedicated index later.

### 4. Cache
Use for:
- current brain revision
- frequently retrieved rule bundles
- provider health
- routing evidence snapshots
- short-lived job state

Redis-compatible cache is suitable; cache is never the source of truth.

## Core tables

### workspaces
workspace_id PK
name
status
owner_user_id
created_at
updated_at

### tasks
task_id PK
workspace_id FK
objective
mode
status
priority
target_spec JSONB
quality_spec JSONB
approval_policy JSONB
created_by
created_at
updated_at

### source_assets
asset_id PK
workspace_id FK nullable
source_type
source_url
role
rights_status
mime_type
width
height
duration_ms nullable
content_hash
perceptual_hash nullable
storage_uri nullable
metadata JSONB
created_at

### task_assets
task_id FK
asset_id FK
usage_role

### production_plans
plan_id PK
task_id FK
version
brain_revision
plan_json JSONB
created_at

### execution_jobs
job_id PK
task_id FK
plan_id FK
status
route_id
retry_of_job_id nullable
started_at nullable
completed_at nullable
failure_code nullable

### execution_records
execution_id PK
job_id FK
record_json JSONB
created_at

### qc_results
qc_id PK
execution_id FK
status
dimensions JSONB
critical_failures JSONB
requires_rework
human_review_required
created_at

### approvals
approval_id PK
workspace_id FK
task_id FK
subject_type
subject_id
status
reason
requested_at
decided_at nullable
decided_by nullable

### asset_versions
version_id PK
asset_id FK
version_number
storage_uri
content_hash
status
origin_execution_id nullable
created_at

### asset_lineage
parent_version_id
child_version_id
relation_type

### audit_events
event_id PK
workspace_id nullable
event_type
entity_type
entity_id
actor_type
actor_id nullable
metadata JSONB
correlation_id
created_at

### learning_candidates
candidate_id PK
origin
comparison_status
confidence
decision_status
payload JSONB
created_at
decided_at nullable

### benchmark_records
benchmark_id PK
case_id
capability
provider_internal
model_internal
scores JSONB
latency_ms
cost_estimate nullable
human_outcome nullable
created_at

## Data rules
- Original source binaries are immutable.
- Deletion uses tombstone/retention workflow where audit/legal requirements apply.
- Internal provider/model fields are not joined into public API payloads.
- Every derived asset has lineage.
- Every completed task has at least one execution record and final QC state.
