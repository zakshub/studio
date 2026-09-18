# Task Schema

```yaml
task_id: string
workspace_id: string
created_by: string
objective: string
mode: string
status: CREATED|VALIDATING|BLOCKED|READY|PLANNING|EXECUTING|QUALITY_CHECK|NEEDS_REVIEW|REWORK_REQUIRED|APPROVED|COMPLETED|FAILED|CANCELLED
priority: low|normal|high|urgent
source_asset_ids: [string]
reference_asset_ids: [string]
locks:
  hard: [string]
  soft: [string]
allowed_changes: [string]
target_spec: object
quality_spec: object
approval_policy: object
created_at: datetime
updated_at: datetime
```
