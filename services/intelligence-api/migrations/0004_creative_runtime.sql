-- Creative Organism runtime records
-- Adds durable records for runtime cognition, sensory observations, QC/provenance and assets.

CREATE TABLE IF NOT EXISTS source_assets_runtime (
  asset_id VARCHAR(64) PRIMARY KEY,
  workspace_id VARCHAR(64),
  source_type VARCHAR(32) NOT NULL,
  source_url TEXT,
  role VARCHAR(32) NOT NULL,
  rights_status VARCHAR(32) NOT NULL,
  content_hash VARCHAR(128),
  storage_uri TEXT,
  metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_source_assets_runtime_workspace
  ON source_assets_runtime(workspace_id);
CREATE INDEX IF NOT EXISTS idx_source_assets_runtime_hash
  ON source_assets_runtime(content_hash);

CREATE TABLE IF NOT EXISTS execution_records_runtime (
  execution_id VARCHAR(64) PRIMARY KEY,
  task_id VARCHAR(64) NOT NULL,
  brain_revision VARCHAR(128) NOT NULL,
  source_asset_ids JSONB NOT NULL DEFAULT '[]'::jsonb,
  output_asset_ids JSONB NOT NULL DEFAULT '[]'::jsonb,
  knowledge_unit_ids JSONB NOT NULL DEFAULT '[]'::jsonb,
  executor_class VARCHAR(64),
  status VARCHAR(24) NOT NULL,
  payload JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_execution_records_runtime_task
  ON execution_records_runtime(task_id);

CREATE TABLE IF NOT EXISTS qc_results_runtime (
  qc_id VARCHAR(64) PRIMARY KEY,
  execution_id VARCHAR(64) NOT NULL,
  status VARCHAR(16) NOT NULL,
  dimensions JSONB NOT NULL DEFAULT '{}'::jsonb,
  critical_failures JSONB NOT NULL DEFAULT '[]'::jsonb,
  requires_rework BOOLEAN NOT NULL DEFAULT false,
  human_review_required BOOLEAN NOT NULL DEFAULT false,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_qc_results_runtime_execution
  ON qc_results_runtime(execution_id);

CREATE TABLE IF NOT EXISTS approvals_runtime (
  approval_id VARCHAR(64) PRIMARY KEY,
  workspace_id VARCHAR(64) NOT NULL,
  task_id VARCHAR(64) NOT NULL,
  subject_type VARCHAR(32) NOT NULL,
  subject_id VARCHAR(64) NOT NULL,
  status VARCHAR(24) NOT NULL DEFAULT 'pending',
  reason TEXT,
  decided_by VARCHAR(64),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  decided_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_approvals_runtime_task
  ON approvals_runtime(task_id, status);

CREATE TABLE IF NOT EXISTS provenance_records (
  provenance_id VARCHAR(64) PRIMARY KEY,
  execution_id VARCHAR(64) NOT NULL UNIQUE,
  task_id VARCHAR(64) NOT NULL,
  brain_revision VARCHAR(128) NOT NULL,
  source_asset_ids JSONB NOT NULL DEFAULT '[]'::jsonb,
  output_asset_ids JSONB NOT NULL DEFAULT '[]'::jsonb,
  knowledge_unit_ids JSONB NOT NULL DEFAULT '[]'::jsonb,
  qc_status VARCHAR(16) NOT NULL,
  lineage JSONB NOT NULL DEFAULT '[]'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS decision_records (
  decision_id VARCHAR(64) PRIMARY KEY,
  task_id VARCHAR(64),
  payload JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS practice_sessions (
  session_id VARCHAR(64) PRIMARY KEY,
  target_principle TEXT NOT NULL,
  mode VARCHAR(64) NOT NULL,
  status VARCHAR(24) NOT NULL DEFAULT 'planned',
  payload JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS observations (
  observation_id VARCHAR(64) PRIMARY KEY,
  source_id VARCHAR(64) NOT NULL,
  media_type VARCHAR(24) NOT NULL,
  dimension VARCHAR(64) NOT NULL,
  value TEXT NOT NULL,
  confidence VARCHAR(16) NOT NULL,
  evidence_ref TEXT,
  interpretation BOOLEAN NOT NULL DEFAULT false,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_observations_source_dimension
  ON observations(source_id, dimension);
