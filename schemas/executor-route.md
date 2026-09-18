# Executor Route Schema

Internal-only.

```yaml
route_id: string
task_id: string
capability: string
strategy: single|competitive|verifier|fallback
executor_class: deterministic|research|language|image_generation|image_editing|vision_qc|local|human
provider_internal: string|null
model_internal: string|null
fallback_route_ids: [string]
reason_code: string
benchmark_snapshot_id: string|null
created_at: datetime
```

Never expose provider/model/routing reason in ordinary customer UI.
