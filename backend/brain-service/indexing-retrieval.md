# Brain Indexing and Retrieval v1

## Knowledge unit
```yaml
unit_id: string
document_id: string
section_path: [string]
domain: string
authority: integer
scope: [string]
tags: [string]
source_revision: string
status: canonical|learned|candidate|deprecated
text: string
```

## Recommended domains
- constitution
- orchestration
- source_authority
- source_preservation
- photographic_reality
- anti_ai_realism
- production_intelligence
- fashion_editorial
- website_treatment
- qc
- learning_governance
- research_policy
- model_routing
- privacy

## Retrieval query
Derived from:
- task mode
- source roles
- requested changes
- hard locks
- reality class
- subject/product type
- platform/delivery
- QC requirements

## Retrieval stages
1. Hard filter by status/domain/scope.
2. Always include applicable invariants and preservation authority.
3. Semantic retrieval inside eligible domains.
4. Expand linked rules only when necessary.
5. De-duplicate overlapping chunks.
6. Apply authority ordering.
7. Return compact bundle within configured token/size budget.

## Conflict rule
If two rules conflict:
- preserve higher-authority invariant
- prefer narrower valid scope over generic learned rule
- preserve both with condition if context-dependent
- unresolved critical conflict blocks automatic execution

## Anti-hallucination
Retrieval result must carry exact unit IDs internally so later execution records can prove what was actually retrieved.
