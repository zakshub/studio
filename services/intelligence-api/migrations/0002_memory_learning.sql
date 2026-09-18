-- Creative Organism persistence v1

CREATE TABLE IF NOT EXISTS memory_records (
  memory_id VARCHAR(64) PRIMARY KEY,
  memory_type VARCHAR(32) NOT NULL,
  scope VARCHAR(128) NOT NULL,
  content TEXT NOT NULL,
  evidence_ids JSONB NOT NULL DEFAULT '[]'::jsonb,
  status VARCHAR(24) NOT NULL DEFAULT 'active',
  weight DOUBLE PRECISION NOT NULL DEFAULT 1.0,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_memory_type_scope_status
  ON memory_records(memory_type, scope, status);

CREATE TABLE IF NOT EXISTS learning_candidates_runtime (
  candidate_id VARCHAR(64) PRIMARY KEY,
  observation TEXT NOT NULL,
  proposed_principle TEXT NOT NULL,
  scope VARCHAR(128) NOT NULL,
  evidence_ids JSONB NOT NULL DEFAULT '[]'::jsonb,
  confidence VARCHAR(16) NOT NULL,
  decision_status VARCHAR(24) NOT NULL DEFAULT 'pending',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  decided_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_learning_runtime_scope_status
  ON learning_candidates_runtime(scope, decision_status);
