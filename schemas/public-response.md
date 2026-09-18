# Public Response Schema

Customer/front-end-safe contract. It intentionally excludes trade-secret implementation detail.

```yaml
job_id: string
status: queued|working|ready|needs_review|blocked|failed
result:
  asset_ids: [string]
  summary: string|null
confidence: low|medium|high|null
preservation:
  required: boolean
  status: passed|warning|failed|not_applicable
warnings:
  - code: string
    message: string
approval:
  required: boolean
  status: pending|approved|rejected|not_required
user_actions:
  - id: string
    label: string
```

## Explicit exclusions
Do not return:
- repo/branch/commit
- prompt internals
- provider/model name by default
- routing reason
- proprietary rule IDs
- hidden reasoning
- score weights
- learning mechanics
