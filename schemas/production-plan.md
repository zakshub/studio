# Production Plan Schema

Internal-only.

```yaml
plan_id: string
task_id: string
version: integer
brain_revision: internal-string
selected_domains: [string]
task_constraints: object
production_spec:
  subject: object|null
  environment: object|null
  camera: object|null
  lens: object|null
  lighting: object|null
  material: object|null
  color: object|null
  post: object|null
  delivery: object|null
executor_requirements:
  capabilities: [string]
  deterministic_preferred: boolean
  max_cost: number|null
  max_latency_ms: integer|null
qc_plan:
  required_dimensions: [string]
  critical_dimensions: [string]
fallback_policy: object
requires_human_review: boolean
created_at: datetime
```
