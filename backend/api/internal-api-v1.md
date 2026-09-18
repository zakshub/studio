# Internal API Contract v1

## Security boundary
Internal APIs are service-to-service only. They may contain proprietary execution metadata and must never be exposed directly to customer clients.

## Brain retrieval
POST /internal/v1/brain/retrieve

Request:
```json
{
  "taskId": "task_123",
  "mode": "STRICT_PRESERVATION_EDIT",
  "sourceRoles": ["primary"],
  "realityClass": "professional_lifestyle",
  "requiredCapabilities": ["preservation","garment_material","lighting","qc"]
}
```

Response:
```json
{
  "brainRevision": "internal_revision",
  "domains": ["source-preservation","photographic-reality","anti-ai-realism","forensic-qc"],
  "ruleSet": [
    {"id":"internal_rule_id","priority":100,"payload":{}}
  ],
  "conflicts": []
}
```

## Orchestrator planning
POST /internal/v1/orchestrator/plan

Outputs:
- planId
- task constraints
- selected domains
- production specification
- capability requirements
- QC plan
- review policy

## Executor run
POST /internal/v1/executors/run

Input:
- planId
- capability
- executorClass
- providerInternal
- modelInternal
- sourceAssetIds
- operation spec
- time/cost budget

Output:
- executionId
- outputAssetIds
- raw status
- timing
- provider usage
- internal diagnostics

## QC evaluate
POST /internal/v1/qc/evaluate

Input:
- executionId
- sourceAssetIds
- outputAssetIds
- locks
- required dimensions

Output:
- qcId
- pass/warn/fail
- dimension scores
- critical failures
- rework flag
- human-review flag

## Provenance
POST /internal/v1/provenance/executions

Stores immutable execution record including:
- brain revision
- selected domains
- executor
- model
- routing strategy
- source lineage
- QC
- approval

## Learning candidate
POST /internal/v1/learning/candidates

No candidate may become canonical automatically through this endpoint.

## Internal invariants
- Internal payloads may reveal methodology only to authorized backend services/admin tools.
- No internal endpoint is callable with ordinary user credentials.
- Every internal mutation emits an AuditEvent.
- Secrets are referenced, never returned.
