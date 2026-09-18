# Memory Record Schema

```yaml
memory_id: string
memory_type: working|episodic|semantic|procedural|project|expert|failure
scope: string
workspace_id: string|null
project_id: string|null
content: string
evidence_ids: [string]
status: active|deprecated|archived
weight: number
created_at: datetime
updated_at: datetime
last_retrieved_at: datetime|null
```

Universal semantic/procedural memory must not inherit workspace-specific preferences without governed promotion.
