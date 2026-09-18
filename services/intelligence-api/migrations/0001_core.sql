-- FashionOS Intelligence Core Schema v1
-- PostgreSQL target. Originals are immutable by application policy.

CREATE TABLE IF NOT EXISTS workspaces (
  workspace_id VARCHAR(64) PRIMARY KEY,
  name TEXT NOT NULL,
  status VARCHAR(24) NOT NULL DEFAULT 'active',
  owner_user_id VARCHAR(64) NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS tasks (
  task_id VARCHAR(64) PRIMARY KEY,
  workspace_id VARCHAR(64) NOT NULL REFERENCES workspaces(workspace_id),
  objective TEXT NOT NULL,
  mode VARCHAR(64) NOT NULL,
  status VARCHAR(32) NOT NULL,
  priority VARCHAR(16) NOT NULL DEFAULT 'normal',
  target_spec JSONB NOT NULL DEFAULT '{}'::jsonb,
  quality_spec JSONB NOT NULL DEFAULT '{}'::jsonb,
  approval_policy JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_by VARCHAR(64),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_tasks_workspace_status
  ON tasks(workspace_id, status);

CREATE TABLE IF NOT EXISTS source_assets (
  asset_id VARCHAR(64) PRIMARY KEY,
  workspace_id VARCHAR(64) REFERENCES workspaces(workspace_id),
  source_type VARCHAR(32) NOT NULL,
  source_url TEXT,
  role VARCHAR(32) NOT NULL,
  rights_status VARCHAR(32) NOT NULL,
  mime_type VARCHAR(128),
  width INTEGER,
  height INTEGER,
  duration_ms BIGINT,
  content_hash VARCHAR(128),
  perceptual_hash VARCHAR(128),
  storage_uri TEXT,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  quality_flags JSONB NOT NULL DEFAULT '[]'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_source_assets_workspace
  ON source_assets(workspace_id);
CREATE INDEX IF NOT EXISTS idx_source_assets_content_hash
  ON source_assets(content_hash);

CREATE TABLE IF NOT EXISTS task_assets (
  task_id VARCHAR(64) NOT NULL REFERENCES tasks(task_id) ON DELETE CASCADE,
  asset_id VARCHAR(64) NOT NULL REFERENCES source_assets(asset_id),
  usage_role VARCHAR(32) NOT NULL,
  PRIMARY KEY (task_id, asset_id, usage_role)
);

CREATE TABLE IF NOT EXISTS production_plans (
  plan_id VARCHAR(64) PRIMARY KEY,
  task_id VARCHAR(64) NOT NULL REFERENCES tasks(task_id) ON DELETE CASCADE,
  version INTEGER NOT NULL,
  brain_revision VARCHAR(128) NOT NULL,
  plan_json JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE(task_id, version)
);

CREATE TABLE IF NOT EXISTS executor_routes (
  route_id VARCHAR(64) PRIMARY KEY,
  task_id VARCHAR(64) NOT NULL REFERENCES tasks(task_id) ON DELETE CASCADE,
  capability VARCHAR(64) NOT NULL,
  strategy VARCHAR(24) NOT NULL,
  executor_class VARCHAR(64) NOT NULL,
  provider_internal VARCHAR(128),
  model_internal VARCHAR(128),
  reason_code VARCHAR(128) NOT NULL,
  benchmark_snapshot_id VARCHAR(64),
  route_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS execution_jobs (
  job_id VARCHAR(64) PRIMARY KEY,
  task_id VARCHAR(64) NOT NULL REFERENCES tasks(task_id) ON DELETE CASCADE,
  plan_id VARCHAR(64) NOT NULL REFERENCES production_plans(plan_id),
  status VARCHAR(32) NOT NULL,
  route_id VARCHAR(64) REFERENCES executor_routes(route_id),
  retry_of_job_id VARCHAR(64) REFERENCES execution_jobs(job_id),
  started_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,
  failure_code VARCHAR(128)
);

CREATE INDEX IF NOT EXISTS idx_execution_jobs_task
  ON execution_jobs(task_id, status);

CREATE TABLE IF NOT EXISTS execution_records (
  execution_id VARCHAR(64) PRIMARY KEY,
  job_id VARCHAR(64) NOT NULL UNIQUE REFERENCES execution_jobs(job_id) ON DELETE CASCADE,
  record_json JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS qc_results (
  qc_id VARCHAR(64) PRIMARY KEY,
  execution_id VARCHAR(64) NOT NULL REFERENCES execution_records(execution_id) ON DELETE CASCADE,
  status VARCHAR(16) NOT NULL,
  dimensions JSONB NOT NULL DEFAULT '{}'::jsonb,
  critical_failures JSONB NOT NULL DEFAULT '[]'::jsonb,
  confidence VARCHAR(16),
  requires_rework BOOLEAN NOT NULL DEFAULT false,
  human_review_required BOOLEAN NOT NULL DEFAULT false,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS approvals (
  approval_id VARCHAR(64) PRIMARY KEY,
  workspace_id VARCHAR(64) NOT NULL REFERENCES workspaces(workspace_id),
  task_id VARCHAR(64) NOT NULL REFERENCES tasks(task_id) ON DELETE CASCADE,
  subject_type VARCHAR(32) NOT NULL,
  subject_id VARCHAR(64) NOT NULL,
  status VARCHAR(24) NOT NULL DEFAULT 'pending',
  reason TEXT,
  requested_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  decided_at TIMESTAMPTZ,
  decided_by VARCHAR(64)
);

CREATE INDEX IF NOT EXISTS idx_approvals_workspace_status
  ON approvals(workspace_id, status);

CREATE TABLE IF NOT EXISTS asset_versions (
  version_id VARCHAR(64) PRIMARY KEY,
  asset_id VARCHAR(64) NOT NULL REFERENCES source_assets(asset_id),
  version_number INTEGER NOT NULL,
  storage_uri TEXT NOT NULL,
  content_hash VARCHAR(128) NOT NULL,
  status VARCHAR(24) NOT NULL,
  origin_execution_id VARCHAR(64) REFERENCES execution_records(execution_id),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  approved_at TIMESTAMPTZ,
  UNIQUE(asset_id, version_number)
);

CREATE TABLE IF NOT EXISTS asset_lineage (
  parent_version_id VARCHAR(64) NOT NULL REFERENCES asset_versions(version_id),
  child_version_id VARCHAR(64) NOT NULL REFERENCES asset_versions(version_id),
  relation_type VARCHAR(32) NOT NULL DEFAULT 'derived_from',
  PRIMARY KEY(parent_version_id, child_version_id, relation_type),
  CHECK (parent_version_id <> child_version_id)
);

CREATE TABLE IF NOT EXISTS audit_events (
  event_id VARCHAR(64) PRIMARY KEY,
  workspace_id VARCHAR(64) REFERENCES workspaces(workspace_id),
  event_type VARCHAR(128) NOT NULL,
  entity_type VARCHAR(64) NOT NULL,
  entity_id VARCHAR(64) NOT NULL,
  actor_type VARCHAR(32) NOT NULL,
  actor_id VARCHAR(64),
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  correlation_id VARCHAR(128) NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_audit_entity_time
  ON audit_events(entity_type, entity_id, created_at DESC);

CREATE TABLE IF NOT EXISTS learning_candidates (
  candidate_id VARCHAR(64) PRIMARY KEY,
  origin VARCHAR(64) NOT NULL,
  comparison_status VARCHAR(32) NOT NULL,
  confidence VARCHAR(16) NOT NULL,
  decision_status VARCHAR(24) NOT NULL DEFAULT 'pending',
  payload JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  decided_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS benchmark_records (
  benchmark_id VARCHAR(64) PRIMARY KEY,
  case_id VARCHAR(64) NOT NULL,
  capability VARCHAR(64) NOT NULL,
  provider_internal VARCHAR(128),
  model_internal VARCHAR(128),
  scores JSONB NOT NULL DEFAULT '{}'::jsonb,
  latency_ms BIGINT,
  cost_estimate NUMERIC(18,6),
  human_outcome VARCHAR(32),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_benchmark_capability_time
  ON benchmark_records(capability, created_at DESC);
