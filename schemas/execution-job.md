# Execution Job Schema

```yaml
job_id: string
task_id: string
plan_id: string
status: QUEUED|RUNNING|VERIFYING|SUCCEEDED|FAILED|CANCELLED|SUPERSEDED
executor_route_id: string
input_asset_ids: [string]
output_asset_ids: [string]
started_at: datetime|null
completed_at: datetime|null
failure_code: string|null
retry_of_job_id: string|null
execution_record_id: string|null
```
