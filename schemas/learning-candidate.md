# Learning Candidate Schema

```yaml
candidate_id: string
created_at: datetime
origin: scheduled_research|manual_research|task_outcome|qc_failure|benchmark
observation: string
proposed_rule: string
scope: [string]
evidence:
  sources: [string]
  task_ids: [string]
comparison:
  status: already_known|duplicate|new_weak|new_repeatable|high_value|contradiction|provider_specific|task_specific|unsafe
  related_rules: [string]
confidence: low|medium|high
decision:
  status: pending|promoted|rejected|deprecated
  rationale: string
```

A candidate is not canonical intelligence until promoted.