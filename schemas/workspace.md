# Workspace Schema

```yaml
workspace_id: string
name: string
status: active|suspended|archived
owner_user_id: string
context_profile_id: string|null
settings_id: string|null
created_at: datetime
updated_at: datetime
```

Rules:
- Workspace identity is not universal Studio Brain identity.
- Workspace-bound entities must be access-filtered by membership.
