# Asset Version Schema

```yaml
version_id: string
asset_id: string
parent_version_ids: [string]
version_number: integer
origin_execution_id: string|null
status: draft|approved|superseded|rejected
storage_uri: internal-string
content_hash: string
created_at: datetime
approved_at: datetime|null
```

Rules:
- Original source versions are immutable.
- Every derivative points to parent version(s).
- Approved versions are never overwritten; later changes create a new version.
