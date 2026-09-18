# Task Context Schema

Conceptual backend contract.

```yaml
task_id: string
objective: string
mode: enum
workspace_context:
  supplied: boolean
  id: string|null
sources:
  - asset_id: string
    role: primary|secondary_reference|internal_approved|unknown
    source_url: string|null
    rights_status: authorized|reference_only|unknown
locks:
  hard: [string]
  soft: [string]
allowed_changes: [string]
target:
  type: string
  aspect_ratio: string|null
  platform: string|null
quality:
  reality_class: string|null
  preservation_required: boolean
approval:
  human_required: boolean
```

Do not include internal repository paths or proprietary rule logic in the front-end version of this object.