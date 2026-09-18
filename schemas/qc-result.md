# QC Result Schema

```yaml
qc_id: string
execution_id: string
status: pass|warn|fail
dimensions:
  preservation:
    score: number|null
    notes: [string]
  human_realism:
    score: number|null
    notes: [string]
  garment_material:
    score: number|null
    notes: [string]
  camera_lens:
    score: number|null
    notes: [string]
  exposure_motion:
    score: number|null
    notes: [string]
  lighting:
    score: number|null
    notes: [string]
  environment:
    score: number|null
    notes: [string]
  color_post:
    score: number|null
    notes: [string]
  provenance:
    score: number|null
    notes: [string]
  anti_ai:
    score: number|null
    notes: [string]
critical_failures: [string]
requires_rework: boolean
human_review_required: boolean
```
