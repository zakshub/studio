-- Track the concrete executor or provider model version behind benchmark evidence.
-- Older rows remain valid history but are not used for current version routing when
-- a current version is supplied by the executor gateway.

ALTER TABLE benchmark_records_runtime
  ADD COLUMN IF NOT EXISTS executor_version VARCHAR(128);

CREATE INDEX IF NOT EXISTS idx_benchmark_records_runtime_version
  ON benchmark_records_runtime(capability, executor_name, executor_version, created_at DESC);
