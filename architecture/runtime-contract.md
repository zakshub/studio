# Runtime Contract

## Required input object
Every task should resolve to:
- objective
- task mode
- source assets
- reference assets
- source role
- workspace/client context if supplied
- hard locks
- soft locks
- allowed changes
- target output
- delivery platform
- quality requirements
- approval requirements

## Required internal plan
The orchestrator should produce:
- selected knowledge domains
- applicable rules
- production specification
- executor class
- routing decision
- fallback strategy
- QC plan

## Required output
- result asset or structured recommendation
- customer-facing status
- customer-facing warnings
- approval requirement
- internal provenance record
- QC record
- optional learning candidate

## Modes
Core visual modes:
- NEW_GENERATION
- STRICT_PRESERVATION_EDIT
- SELECTIVE_EDIT
- CREATIVE_REGENERATION
- RETOUCH_ONLY
- RELIGHT
- COLOR_GRADE
- LUT_LOOK_APPLICATION
- SOURCE_WEBSITE_TREATMENT
- REFERENCE_RESEARCH
- PRODUCT_IMAGE
- PORTRAIT
- FASHION_EDITORIAL
- LIFESTYLE_DOCUMENTARY
- CINEMATIC_STILL
- MOBILE_SOCIAL_REALISM

## Invariants
- no unauthorized source mutation
- no silent lock violation
- no universal learning from client-specific preference
- no production approval solely from aesthetic quality
- no front-end exposure of private methodology
- no fabricated provenance
- no claim of verification when verification did not occur