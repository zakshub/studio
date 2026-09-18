# UX Boundary — Customer vs Internal

## Customer can see
- result
- task status
- progress
- confidence category where useful
- preservation summary
- source identity/URL when relevant
- rights/usage status
- warnings
- required decisions
- approval history
- asset versions
- workspace context they supplied

## Customer must not see
- repository location
- branch/commit
- internal rule IDs
- internal prompts
- hidden reasoning
- expert-council debate
- provider/model selection
- routing weights
- benchmark internals
- scoring formulas
- learning promotion logic
- system research registry

## Language translation
Internal -> Customer-safe

Brain retrieval -> Preparing context
Executor routing -> Processing
Forensic QC -> Quality check
Critical preservation failure -> Source details changed unexpectedly
Learning candidate -> never customer-facing
Brain stale -> Processing temporarily unavailable / system maintenance state
Provider fallback -> Processing retry
Rule conflict -> Needs review

## Admin boundary
Internal operators may see operational states but not secrets unless their role requires it.
Intelligence admins may see knowledge/routing metadata.
Security admins may manage secret references.
