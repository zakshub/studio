-- Additive draft organization; no original assets or frozen v1 tables are modified.
CREATE TABLE IF NOT EXISTS workspace_members_runtime (
  workspace_id VARCHAR(64) NOT NULL, actor_id VARCHAR(64) NOT NULL,
  role VARCHAR(24) NOT NULL, PRIMARY KEY (workspace_id, actor_id)
);
CREATE TABLE IF NOT EXISTS collections_runtime (
  collection_id VARCHAR(64) PRIMARY KEY, workspace_id VARCHAR(64) NOT NULL,
  name VARCHAR(160) NOT NULL, objective TEXT NOT NULL,
  hard_locks JSONB NOT NULL DEFAULT '[]'::jsonb,
  allowed_changes JSONB NOT NULL DEFAULT '[]'::jsonb,
  revision INTEGER NOT NULL DEFAULT 1, archived BOOLEAN NOT NULL DEFAULT FALSE
);
CREATE INDEX IF NOT EXISTS ix_collections_runtime_workspace_id ON collections_runtime(workspace_id);
CREATE TABLE IF NOT EXISTS looks_runtime (
  look_id VARCHAR(64) PRIMARY KEY, workspace_id VARCHAR(64) NOT NULL,
  collection_id VARCHAR(64) NOT NULL, name VARCHAR(160) NOT NULL,
  source_asset_id VARCHAR(64) NOT NULL, task_id VARCHAR(64), revision INTEGER NOT NULL DEFAULT 1
);
CREATE INDEX IF NOT EXISTS ix_looks_runtime_workspace_id ON looks_runtime(workspace_id);
CREATE INDEX IF NOT EXISTS ix_looks_runtime_collection_id ON looks_runtime(collection_id);
CREATE TABLE IF NOT EXISTS collection_events_runtime (
  event_id VARCHAR(64) PRIMARY KEY, workspace_id VARCHAR(64) NOT NULL,
  collection_id VARCHAR(64) NOT NULL, actor_id VARCHAR(64) NOT NULL,
  event_type VARCHAR(48) NOT NULL, subject_id VARCHAR(64) NOT NULL,
  revision INTEGER NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_collection_events_runtime_workspace_id ON collection_events_runtime(workspace_id);
CREATE INDEX IF NOT EXISTS ix_collection_events_runtime_collection_id ON collection_events_runtime(collection_id);
