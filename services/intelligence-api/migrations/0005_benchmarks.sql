-- Capability-specific benchmark evidence

CREATE TABLE IF NOT EXISTS benchmark_records_runtime (
  benchmark_id VARCHAR(64) PRIMARY KEY,
  case_id VARCHAR(64) NOT NULL,
  capability VARCHAR(64) NOT NULL,
  executor_name VARCHAR(128) NOT NULL,
  scores JSONB NOT NULL DEFAULT '{}'::jsonb,
  latency_ms DOUBLE PRECISION,
  cost_estimate DOUBLE PRECISION,
  accepted BOOLEAN,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_benchmark_records_runtime_capability
  ON benchmark_records_runtime(capability, executor_name, created_at DESC);
