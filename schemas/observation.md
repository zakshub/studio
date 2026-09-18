# Observation Schema

```yaml
observation_id: string
origin_type: website|image|video|expert_work|interview|task|practice|qc|research
origin_id: string
source_ids: [string]
statement: string
epistemic_type: observed|expert_statement|inference|hypothesis
confidence: low|medium|high
domains: [string]
scope:
  geography: [string]
  market: [string]
  medium: [string]
  garment_or_product: [string]
observed_at: datetime|null
created_at: datetime
status: active|superseded|rejected
```

Rules:
- observed, stated, inferred, and hypothesized knowledge remain distinct.
- one observation is not a universal rule.
- duplicate/repost evidence does not increase independent-source count.
