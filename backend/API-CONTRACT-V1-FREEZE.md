# FashionOS Backend Contract v1 — Freeze Record

Status: FROZEN FOR MVP IMPLEMENTATION
Date: 2026-09-18

## Frozen scope
The following are canonical for MVP implementation:
- backend/domain-model.md
- backend/api/endpoint-map-v1.md
- backend/api/public-api-v1.md
- backend/api/internal-api-v1.md
- backend/state-machines/task-lifecycle.md
- backend/storage/persistence-model.md
- backend/security/permissions-model.md
- backend/errors/error-contract.md
- backend/events/audit-event-model.md

## Contract principles
1. FashionOS public API is product-semantic, not methodology-semantic.
2. Internal provider/model/repository details are private.
3. Visual tasks are asynchronous.
4. Source authority and rights state are explicit.
5. Original source assets are immutable.
6. Derived assets preserve lineage.
7. QC is part of completion, not an optional post-step.
8. Critical preservation failures block approval.
9. Workspace context is isolated from universal brain intelligence.
10. Internal learning candidates never auto-promote.

## Allowed v1 changes
- additive optional fields
- additional safe status codes
- additional internal endpoints
- implementation-specific storage changes that preserve contracts

## Breaking changes
Require a v2 or explicit contract migration:
- renaming/removing public fields
- changing public state meanings
- exposing previously private internals
- weakening source authority, QC, or approval guarantees

## M1 exit
A backend engineer can implement the MVP behavior from this contract without inventing product semantics.

M1 status: COMPLETE.
