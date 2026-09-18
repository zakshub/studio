# FashionOS Intelligence MVP — Technical Stack

## Decision
Start as a modular monolith with strong internal boundaries, not microservices.

Reason:
- fastest path to an auditable MVP
- easier contract testing
- lower operational complexity
- modules can be split later when load/ownership justifies it

## Backend
- Python 3.13
- FastAPI
- Pydantic v2

Why:
- strong AI/vision ecosystem
- typed API contracts
- async-friendly
- straightforward provider integrations
- suitable for retrieval/QC/orchestration workloads

## Persistence
- PostgreSQL as system of record
- pgvector initially for semantic retrieval if needed
- object storage (S3-compatible) for binaries
- Redis-compatible cache for short-lived state/rule bundles/provider health

## Background work
Start with an application worker/queue layer; keep queue implementation replaceable.
Use asynchronous jobs for:
- website scans
- model execution
- video analysis
- QC
- research
- brain sync/indexing

## Frontend
Frontend stack is deliberately not frozen by this backend decision. It should consume the public v1 contract only.

## Architecture
Modular boundaries:
- api
- tasks
- assets
- sources
- brain
- orchestration
- executors
- qc
- approvals
- provenance
- learning
- benchmarks

## Deployment evolution
MVP: one API service + worker + PostgreSQL + object storage + cache.
Later: split heavy ingestion, model gateway, video analysis, or QC services only when justified.

## Non-negotiable
Public responses must never expose trade-secret methodology or provider internals.
