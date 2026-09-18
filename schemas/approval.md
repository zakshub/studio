# Approval Schema

```yaml
approval_id: string
workspace_id: string
task_id: string
subject_type: task|asset_version|context_profile|source_rights
subject_id: string
requested_from_user_ids: [string]
status: pending|approved|rejected|cancelled
reason: string|null
created_at: datetime
decided_at: datetime|null
decided_by: string|null
```
