# Task Lifecycle State Machine v1

## Task states
- CREATED
- VALIDATING
- BLOCKED
- READY
- PLANNING
- EXECUTING
- QUALITY_CHECK
- NEEDS_REVIEW
- REWORK_REQUIRED
- APPROVED
- COMPLETED
- FAILED
- CANCELLED

## Main path
CREATED
-> VALIDATING
-> READY
-> PLANNING
-> EXECUTING
-> QUALITY_CHECK
-> NEEDS_REVIEW or APPROVED
-> COMPLETED

## Alternative paths

### Missing/invalid input
VALIDATING -> BLOCKED

BLOCKED may return to VALIDATING after user/system resolution.

### Execution failure
EXECUTING -> FAILED

Retry:
FAILED -> PLANNING
or
FAILED -> EXECUTING
depending on failure class.

### QC failure
QUALITY_CHECK -> REWORK_REQUIRED

REWORK_REQUIRED -> PLANNING or EXECUTING

### Human review
QUALITY_CHECK -> NEEDS_REVIEW
NEEDS_REVIEW -> APPROVED
NEEDS_REVIEW -> REWORK_REQUIRED
NEEDS_REVIEW -> CANCELLED

### Auto-approval
QUALITY_CHECK -> APPROVED only when:
- policy permits
- no critical QC failures
- human review is not required
- rights/source status is sufficient

### Completion
APPROVED -> COMPLETED after asset version/provenance persistence succeeds.

## Job states
- QUEUED
- RUNNING
- VERIFYING
- SUCCEEDED
- FAILED
- CANCELLED
- SUPERSEDED

## State-transition rules
- Transitions are append-only events.
- Invalid transition returns STATE_CONFLICT.
- Task state is derived from authoritative workflow events, not client-side assumptions.
- Critical preservation failure cannot transition directly to APPROVED.
- A task with unknown required rights state cannot transition to COMPLETED for production publication.
