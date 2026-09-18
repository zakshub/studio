# Decision Record Schema

Internal concise rationale record. It stores decision factors, not raw hidden chain-of-thought.

```yaml
decision_id: string
task_id: string|null
objective: string
selected_option: string
alternatives_considered: [string]
retrieved_knowledge_ids: [string]
expert_councils: [string]
evidence_ids: [string]
constraints_preserved: [string]
value_gate:
  allowed: boolean
  blockers: [string]
  warnings: [string]
metacognition:
  confidence: low|medium|high
  flags: [string]
unresolved_risks: [string]
human_review_required: boolean
created_at: datetime
```
