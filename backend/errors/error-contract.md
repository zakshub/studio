# Error Contract v1

## Standard error envelope
```json
{
  "data": null,
  "meta": {
    "requestId": "req_x",
    "correlationId": "cor_x"
  },
  "error": {
    "code": "SOURCE_RIGHTS_UNKNOWN",
    "message": "This source cannot be used for production until usage rights are confirmed.",
    "retryable": false,
    "userAction": "confirm_rights"
  }
}
```

## Canonical error families

### Validation
- INVALID_REQUEST
- INVALID_TASK_MODE
- MISSING_REQUIRED_SOURCE
- INVALID_LOCK_CONFIGURATION
- INVALID_TARGET_SPEC

### Source
- SOURCE_NOT_FOUND
- SOURCE_UNAVAILABLE
- SOURCE_RIGHTS_UNKNOWN
- SOURCE_REFERENCE_ONLY
- SOURCE_LOW_QUALITY
- SOURCE_DUPLICATE
- SOURCE_TYPE_UNSUPPORTED

### State
- STATE_CONFLICT
- TASK_BLOCKED
- TASK_CANCELLED
- APPROVAL_REQUIRED
- REVIEW_ALREADY_DECIDED

### Brain
- BRAIN_UNAVAILABLE
- BRAIN_STALE
- KNOWLEDGE_RETRIEVAL_FAILED
- RULE_CONFLICT_UNRESOLVED

### Execution
- EXECUTOR_UNAVAILABLE
- EXECUTOR_TIMEOUT
- EXECUTOR_FAILED
- OUTPUT_INVALID
- OPERATION_UNSUPPORTED

### QC
- QC_FAILED
- PRESERVATION_FAILED
- IDENTITY_DRIFT
- GARMENT_DRIFT
- PRODUCT_FIDELITY_FAILED
- PROVENANCE_INCOMPLETE

### Security
- UNAUTHORIZED
- FORBIDDEN
- WORKSPACE_ACCESS_DENIED
- INTERNAL_ENDPOINT_FORBIDDEN

### System
- INTERNAL_ERROR
- RATE_LIMITED
- BUDGET_EXCEEDED
- DEPENDENCY_UNAVAILABLE

## Rules
- Customer messages are safe and non-proprietary.
- Internal logs may contain diagnostic detail, never secrets.
- Retryable errors explicitly say retryable=true.
- Do not leak provider names in customer-facing failures.
