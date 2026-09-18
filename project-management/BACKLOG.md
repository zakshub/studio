# FashionOS Intelligence Integration — Backlog

Priority: P0 = blocking/core, P1 = important, P2 = enhancement, P3 = later.

## Epic A — Backend Contract
- [x] P0 Define Workspace entity
- [x] P0 Define Task entity
- [x] P0 Define SourceAsset entity
- [x] P0 Define ProductionPlan entity
- [x] P0 Define ExecutionRecord entity
- [x] P0 Define QCResult entity
- [x] P0 Define Approval entity
- [x] P0 Define AssetVersion entity
- [x] P0 Define task state machine
- [x] P0 Define public API schema
- [x] P0 Define internal API schema
- [x] P0 Define error contract
- [x] P0 Define permissions/admin model
- [x] P1 Define event/audit model

## Epic B — Brain Service
- [ ] P0 GitHub sync
- [ ] P0 local cache/index
- [ ] P0 domain tagging
- [ ] P0 retrieval service
- [ ] P0 precedence/conflict rules
- [ ] P1 cache freshness
- [ ] P1 health endpoint
- [ ] P1 rollback/version pinning

## Epic C — Executor Gateway
- [ ] P0 common executor interface
- [ ] P0 Gemini adapter
- [ ] P0 OpenAI adapter
- [ ] P0 deterministic-processing adapter
- [ ] P0 fallback routing
- [ ] P1 competitive routing
- [ ] P1 verifier mode
- [ ] P1 cost/latency capture
- [ ] P2 self-hosted adapter contract

## Epic D — Benchmarking
- [ ] P0 create benchmark cases
- [ ] P0 preservation benchmark
- [ ] P0 garment benchmark
- [ ] P0 generation benchmark
- [ ] P0 research benchmark
- [ ] P0 QC benchmark
- [ ] P1 scoring/history store
- [ ] P1 model-version re-benchmark trigger

## Epic E — Website / Source Intake
- [ ] P0 primary-site input
- [ ] P0 secondary-reference input
- [ ] P0 asset discovery
- [ ] P0 source URL capture
- [ ] P0 dedupe
- [ ] P0 quality screening
- [ ] P0 rights status
- [ ] P0 source role
- [ ] P1 batch selection
- [ ] P1 crawl exclusions
- [ ] P1 change detection

## Epic F — QC / Provenance
- [ ] P0 execution record
- [ ] P0 source lineage
- [ ] P0 preservation QC
- [ ] P0 anti-AI QC
- [ ] P0 pass/warn/fail
- [ ] P0 human review trigger
- [ ] P1 retry strategy
- [ ] P1 rollback
- [ ] P1 comparison viewer data

## Epic G — Product Design
- [ ] P0 page map
- [ ] P0 customer vs internal/admin UX boundary
- [ ] P0 Dashboard
- [ ] P0 Source Intake
- [ ] P0 Visualization Studio
- [ ] P0 Existing Image Treatment
- [ ] P0 Review/QC UI
- [ ] P0 Assets Library
- [ ] P1 Collection Studio
- [ ] P1 Campaign Studio
- [ ] P1 Internal Settings
- [ ] P1 component states
- [ ] P1 image-slot plan
- [ ] P2 design documentation

## Epic H — Backend MVP
- [ ] P0 orchestration service
- [ ] P0 task service
- [ ] P0 asset service
- [ ] P0 source service
- [ ] P0 brain service
- [ ] P0 executor service
- [ ] P0 QC service
- [ ] P0 approval service
- [ ] P0 provenance service

## Epic I — Frontend MVP
- [ ] P0 shell/navigation
- [ ] P0 workspace
- [ ] P0 task creation
- [ ] P0 source upload/import
- [ ] P0 job state
- [ ] P0 review/approve
- [ ] P0 asset library
- [ ] P0 errors/warnings
- [ ] P1 internal admin

## Epic J — Production Readiness
- [ ] P1 authentication/authorization
- [ ] P1 secret management
- [ ] P1 logging
- [ ] P1 monitoring
- [ ] P1 rate limits
- [ ] P1 cost budgets
- [ ] P1 backups
- [ ] P1 privacy/legal review
- [ ] P1 security review
- [ ] P2 multi-tenant hardening

## Epic K — Creative Organism Intelligence
- [x] P0 Define Creative Organism architecture
- [x] P0 Define Expert Intelligence architecture
- [x] P0 Define Sensory Harvester architecture
- [ ] P0 Create evidence-backed roster for 50 expert intelligences
- [ ] P0 Create expert-profile schema and source requirements
- [ ] P0 Research and populate first 10 expert profiles
- [ ] P1 Complete all 50 expert profiles
- [ ] P1 Implement expert councils
- [ ] P1 Implement expert aggregator
- [ ] P1 Implement visual sensory intake
- [ ] P1 Implement video intelligence intake
- [ ] P1 Implement novelty/weak-signal detection
- [ ] P1 Implement contamination/bias monitoring
- [ ] P2 Implement scheduled background synthesis
