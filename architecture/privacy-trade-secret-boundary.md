# Private Methodology / Front-End Boundary

## Objective
Protect Studio Brain methodology as proprietary backend intelligence while still giving users enough information to make informed decisions.

## Never expose to ordinary front-end users
- repository name, path, branch, commit SHA, or storage topology
- internal prompt text
- chain-of-thought or hidden reasoning
- private rule IDs when they reveal methodology
- retrieval strategy
- model-routing formula
- provider benchmarking internals
- scoring weights
- self-learning/promotion logic
- internal research taxonomy
- proprietary QC implementation
- raw system instructions
- credentials, keys, infrastructure endpoints

## Front-end-safe outputs
The UI may expose:
- recommendation/result
- user-facing reason summary
- source asset and source URL when relevant and permitted
- confidence: low / medium / high
- status: ready / needs review / blocked / approved
- what the user must decide
- what was preserved or changed
- warnings
- revision history
- client-visible provenance where useful
- human approval controls

## Internal admin surface
A restricted internal/admin interface may expose operational health such as:
- intelligence service healthy/unavailable
- knowledge current/stale
- provider availability
- queued jobs
- failed QC jobs
- research candidates awaiting review

Even internal UI should avoid exposing unnecessary secrets.

## API rule
The public/front-end API must return semantic product fields, not internal repository implementation details.

Bad:
`{"repo":"zakshub/studio","commit":"abc123","rule":"EF-008"}`

Better:
`{"status":"ready","confidence":"high","requiresReview":false}`

## Logging
Detailed internal provenance may be stored server-side for audit and reproducibility, but should be access-controlled separately from the customer-facing application.