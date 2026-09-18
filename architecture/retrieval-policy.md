# Intelligence Retrieval Policy

## Goal
Use the smallest sufficient set of relevant knowledge rather than dumping the entire brain into every task.

## Retrieval inputs
- task mode
- source role
- reality class
- subject/product type
- preservation requirements
- requested transformation
- delivery target
- workspace context availability
- known failure history

## Retrieval priority
1. Safety/source-authority constraints
2. Hard-lock and preservation rules
3. Task-specific production knowledge
4. Reality-class rules
5. Relevant learned rules
6. QC criteria
7. Delivery rules

## Exclusion
Do not retrieve unrelated:
- brand/client context
- research examples
- provider-specific rules
- aesthetics
- task histories

unless they materially apply.

## Conflict handling
When retrieved rules conflict:
- prefer higher-authority canonical rules
- preserve source locks
- scope learned rules to their valid conditions
- record unresolved conflict
- escalate rather than silently invent a compromise when consequences matter

## Traceability
Internally record which knowledge domains were retrieved. Customer-facing UI should not expose proprietary rule topology by default.
