# Expert Intelligence Profile Schema

Status values:
- candidate
- sourcing
- evidence_ready
- synthesized
- validated
- active
- deprecated

```yaml
expert_id: string
name: string
status: string
domains: [string]
primary_councils: [string]
geography_context: [string]
career_phases:
  - label: string
    date_range: string|null
source_pack:
  primary_sources: [string]
  secondary_sources: [string]
  interviews_talks: [string]
  behind_the_scenes: [string]
  books_or_longform: [string]
observations:
  - claim: string
    source_ids: [string]
    type: observed|stated_by_expert|inference
    confidence: low|medium|high
reusable_principles:
  - principle: string
    applies_when: string
    does_not_imply: string
    evidence_ids: [string]
anti_copy_constraints:
  - string
known_context_limits:
  - string
last_reviewed: date|null
```

## Rules
- Never flatten an expert into a style label.
- Separate documented statements from our inference.
- Extract methods and principles, not signature-style imitation instructions.
- Weight expertise by domain.
- Preserve disagreement between experts.
- No profile reaches active status without an evidence pack.
