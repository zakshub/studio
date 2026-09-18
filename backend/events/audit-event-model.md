# Audit Event Model v1

## Purpose
Provide traceability without exposing private methodology to normal users.

## Event shape
```yaml
event_id: string
timestamp: datetime
correlation_id: string
workspace_id: string|null
actor:
  type: user|service|system|admin
  id: string|null
event_type: string
entity:
  type: string
  id: string
metadata: object
visibility: internal|workspace_safe
```

## Core event types
- workspace.created
- workspace.context.updated
- task.created
- task.validated
- task.blocked
- task.planned
- task.execution.started
- task.execution.failed
- task.qc.completed
- task.review.requested
- task.approved
- task.rejected
- task.completed
- source.registered
- source.asset.discovered
- source.asset.deduplicated
- source.rights.changed
- asset.version.created
- asset.version.approved
- brain.synced
- brain.retrieval.completed
- executor.route.selected
- benchmark.completed
- learning.candidate.created
- learning.candidate.promoted
- learning.candidate.rejected
- security.access.denied

## Visibility
workspace_safe events may be transformed into customer activity feed items.
internal events may include proprietary or operational metadata and must not be exposed directly.

## Immutability
Audit events are append-only. Corrections create a new event rather than editing historical events.
