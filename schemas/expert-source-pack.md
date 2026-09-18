# Expert Source Pack Schema

```yaml
expert_id: string
source_pack_version: integer
sources:
  - source_id: string
    source_type: official_portfolio|project|interview|talk|process_material|book|article|credible_secondary
    title: string
    url_or_reference: string
    publisher_or_owner: string|null
    publication_date: date|null
    accessed_at: datetime
    authority: primary|secondary
    notes: string|null
coverage:
  career_phases: [string]
  domains: [string]
  methods: [string]
  projects: [string]
evidence_ready: boolean
reviewed_by: string|null
```

A profile cannot become active without an evidence-ready source pack.
