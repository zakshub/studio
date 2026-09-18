# FashionOS Backend Domain Model v1

## Purpose
Canonical domain model for implementation. This document defines product entities and relationships so backend and frontend do not invent behavior independently.

## 1. Workspace
Represents one isolated customer/team context.

Fields:
- workspace_id
- name
- status: active|suspended|archived
- created_at
- updated_at
- owner_user_id
- context_profile_id|null
- settings_id
- retention_policy_id|null

Rules:
- A workspace may contain client-specific context.
- Workspace context never silently mutates universal Studio Brain intelligence.
- Cross-workspace asset access is forbidden unless explicitly shared.

## 2. ContextProfile
Optional workspace-specific context.

Fields:
- context_profile_id
- workspace_id
- version
- status: draft|active|archived
- attributes: structured key/value object
- source_asset_ids
- approved_reference_ids
- created_by
- approved_by|null
- created_at
- approved_at|null

Purpose:
Temporary specialization of FashionOS for a workspace.

## 3. Task
Top-level user/business request.

Fields:
- task_id
- workspace_id
- created_by
- objective
- mode
- status
- priority
- source_asset_ids
- reference_asset_ids
- hard_locks
- soft_locks
- allowed_changes
- target_spec
- quality_spec
- approval_policy
- created_at
- updated_at

One Task may produce multiple Jobs/Executions.

## 4. SourceAsset
Canonical record for every input or derivative asset.

Fields:
- asset_id
- workspace_id|null
- source_type
- source_url|null
- role
- rights_status
- parent_asset_ids
- mime_type
- dimensions
- duration|null
- content_hash
- perceptual_hash|null
- storage_uri|null
- metadata
- quality_flags
- created_at

## 5. ReferenceSource
Represents a reference that may influence analysis but is not automatically a production-owned asset.

Fields:
- reference_id
- workspace_id|null
- source_url
- source_platform
- creator_or_brand|null
- authority_level
- rights_status
- observed_at
- extracted_observations
- linked_asset_ids

## 6. ProductionPlan
Internal plan generated before execution.

Fields:
- plan_id
- task_id
- version
- selected_domains
- task_constraints
- production_spec
- executor_requirements
- qc_plan
- fallback_policy
- requires_human_review
- created_at

Customer UI does not receive proprietary retrieval details.

## 7. ExecutionJob
One attempt to execute all or part of a task.

Fields:
- job_id
- task_id
- plan_id
- status
- executor_route_id
- input_asset_ids
- output_asset_ids
- started_at|null
- completed_at|null
- failure_code|null
- retry_of_job_id|null
- execution_record_id|null

## 8. ExecutorRoute
Internal routing decision.

Fields:
- route_id
- task_id
- capability
- strategy: single|competitive|verifier|fallback
- executor_class
- provider_internal|null
- model_internal|null
- fallback_route_ids
- reason_code
- benchmark_snapshot_id|null
- created_at

Never expose provider/routing methodology in ordinary customer payloads.

## 9. QCResult
Verification record for an execution.

Fields:
- qc_id
- execution_id
- status: pass|warn|fail
- dimension_scores
- critical_failures
- confidence
- requires_rework
- human_review_required
- created_at

## 10. Approval
Human decision gate.

Fields:
- approval_id
- workspace_id
- task_id
- subject_type
- subject_id
- requested_from_user_ids
- status: pending|approved|rejected|cancelled
- reason|null
- created_at
- decided_at|null
- decided_by|null

## 11. AssetVersion
Immutable lineage record.

Fields:
- version_id
- asset_id
- parent_version_ids
- version_number
- origin_execution_id|null
- status: draft|approved|superseded|rejected
- storage_uri
- content_hash
- created_at
- approved_at|null

## 12. LearningCandidate
Unpromoted observation.

Fields:
- candidate_id
- origin
- observation
- proposed_rule
- scope
- evidence
- comparison_status
- confidence
- decision_status
- created_at
- decided_at|null

Never treat a candidate as canonical before promotion.

## 13. AuditEvent
Immutable event stream for material actions.

Fields:
- event_id
- workspace_id|null
- actor_type
- actor_id|null
- event_type
- entity_type
- entity_id
- timestamp
- metadata
- correlation_id

## 14. BenchmarkRecord
Internal evidence used for executor routing.

Fields:
- benchmark_id
- case_id
- capability
- executor_class
- provider_internal
- model_internal
- scores
- latency_ms
- cost_estimate|null
- human_outcome|null
- created_at

## Key relationships
- Workspace 1:N Task
- Workspace 1:N SourceAsset
- Workspace 1:N ContextProfile
- Task 1:N ProductionPlan
- Task 1:N ExecutionJob
- ExecutionJob 1:1 ExecutionRecord
- ExecutionJob 1:N QCResult
- Task 1:N Approval
- SourceAsset N:M SourceAsset through lineage/parent relationships
- ExecutionJob N:M SourceAsset through input/output asset IDs
- LearningCandidate may reference AuditEvent, Task, BenchmarkRecord, or ResearchSource

## Invariants
- Customer-visible APIs never expose provider internals, repo internals, private rules, prompts, hidden reasoning, or benchmark weights.
- Original source assets are immutable.
- Derived assets always preserve parent lineage.
- Critical preservation failure prevents auto-approval.
- Unknown authorization remains unknown.
- Workspace context never becomes universal knowledge without governed promotion.
