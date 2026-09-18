# Execution Record Schema

Internal-only provenance contract.

```yaml
execution_id: string
task_id: string
timestamp: datetime
brain_revision: internal-string
knowledge_domains: [string]
workspace_context_revision: string|null
source_asset_ids: [string]
mode: string
locks_applied: [string]
executor:
  class: string
  provider: internal-string|null
  model: internal-string|null
routing:
  strategy: single|competitive|verifier|fallback
  reason_code: internal-string
qc:
  status: pass|warn|fail
  dimensions:
    preservation: number|null
    anatomy: number|null
    garment_material: number|null
    camera_lens: number|null
    lighting: number|null
    color_post: number|null
    provenance: number|null
human_decision:
  required: boolean
  status: pending|approved|rejected|not_required
output_asset_ids: [string]
learning_candidate_ids: [string]
```

This record is not a customer-facing payload.