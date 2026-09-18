# Practice Session Schema

```yaml
session_id: string
target_principle: string
mode: principle_drill|constraint_drill|counterfactual|failure_repair|cross_domain
source_evidence_ids: [string]
fixed_variables: [string]
controlled_variables: [string]
candidate_count: integer
evaluation_dimensions: [string]
candidate_results: [object]
outcome: incomplete|passed|failed|mixed
learning_candidate_ids: [string]
public_asset: false
created_at: datetime
completed_at: datetime|null
```

Practice output is internal by default.
