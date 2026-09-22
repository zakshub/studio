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
- [x] P0 GitHub sync / remote mirror bootstrap
- [x] P0 local cache/index bootstrap (in-memory index; persistent cache still pending)
- [x] P0 domain tagging
- [x] P0 retrieval service bootstrap
- [x] P0 precedence/conflict integration into retrieval
- [x] P1 cache freshness / stale health bootstrap
- [x] P1 health endpoint
- [x] P1 in-process rollback/version pinning bootstrap
- [x] P1 durable revision snapshot persistence

## Epic C — Executor Gateway
- [x] P0 common executor interface bootstrap
- [x] P0 Gemini adapter runtime (live credential validation pending)
- [x] P0 OpenAI image-generation + vision-QC adapter runtime (live credential validation pending)
- [x] P0 deterministic-processing adapter bootstrap
- [x] P0 fallback-capable executor gateway bootstrap
- [x] P1 competitive routing bootstrap
- [x] P1 separate visual verifier mode integrated into organism loop
- [x] P1 cost/latency capture runtime bootstrap (real provider evidence pending)
- [ ] P2 self-hosted adapter contract

## Epic D — Benchmarking
- [x] P0 create benchmark cases (B-001 through B-010 catalog defined; source assets pending)
- [ ] P0 preservation benchmark
- [ ] P0 garment benchmark
- [ ] P0 generation benchmark
- [ ] P0 research benchmark
- [ ] P0 QC benchmark
- [x] P1 scoring/history store bootstrap
- [x] P1 model-version re-benchmark trigger via version-scoped routing evidence

## Epic E — Website / Source Intake
- [ ] P0 primary-site input
- [ ] P0 secondary-reference input
- [x] P0 asset discovery bootstrap (HTML media discovery)
- [x] P0 source URL capture bootstrap
- [x] P0 exact URL/media dedupe bootstrap
- [ ] P0 quality screening
- [x] P0 rights status field/runtime gate
- [x] P0 source role/authority metadata bootstrap
- [ ] P1 batch selection
- [ ] P1 crawl exclusions
- [x] P1 deterministic change detection bootstrap

## Epic F — QC / Provenance
- [x] P0 QC policy runtime bootstrap
- [x] P0 provenance/lineage runtime bootstrap
- [x] P0 execution record persistence bootstrap
- [x] P0 source lineage/provenance bootstrap
- [ ] P0 preservation QC (source-aware model comparison bootstrap exists; production identity/garment/embroidery verifier still pending)
- [ ] P0 anti-AI QC
- [x] P0 pass/warn/fail policy runtime
- [x] P0 human review trigger runtime
- [ ] P1 retry strategy
- [ ] P1 rollback
- [ ] P1 comparison viewer data

## Epic G — Product Design
- [x] P0 page map
- [x] P0 customer vs internal/admin UX boundary
- [x] P0 Dashboard
- [x] P0 Source Intake
- [ ] P0 Visualization Studio
- [ ] P0 Existing Image Treatment
- [x] P0 Review/QC UI
- [x] P0 Assets Library
- [ ] P1 Collection Studio
- [ ] P1 Campaign Studio
- [x] P1 Internal Settings
- [ ] P1 component states
- [x] P1 image-slot plan
- [x] P2 design documentation for completed pages

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
- [x] P1 internal endpoint authentication bootstrap
- [x] P1 public docs/OpenAPI disabled
- [x] P1 public/internal ingress boundary documented
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
- [x] P0 Create expert-profile schema and source requirements
- [x] P0 Research and populate first 10 expert profiles (10/10 synthesized, not validated)
- [ ] P1 Complete all 50 expert profiles
- [x] P1 Implement expert council selector runtime
- [x] P1 Implement expert aggregator bootstrap
- [x] P1 Implement production expert-profile loader/consultation bootstrap
- [x] P1 Implement normalized visual observation intake bootstrap
- [x] P1 Implement structured video intelligence intake bootstrap
- [ ] P1 Implement novelty/weak-signal detection (novelty + synthesis bootstrap done; production weak-signal pipeline pending)
- [x] P1 Implement contamination/bias monitoring bootstrap (source concentration + multidimensional coverage)
- [x] P2 Implement scheduled background synthesis bootstrap (in-process scheduler; production worker pending)

## Epic L — Creative Cognition Runtime
- [x] P0 Implement value-system gate
- [x] P0 Implement deliberative cognition planner
- [x] P0 Implement attention prioritization
- [x] P0 Implement metacognition checks
- [x] P0 Implement curiosity-question generation
- [x] P0 Implement internal practice planner
- [x] P0 Implement governed learning-candidate runtime
- [x] P0 Implement persistent memory bootstrap
- [x] P0 Implement memory decay/deprecation
- [x] P1 Implement failure-to-learning bootstrap
- [x] P1 Implement creative synthesis/divergence bootstrap
- [x] P1 Implement structured conflict resolver
- [x] P1 Implement concise decision records
- [x] P1 Implement sensory registry + change detection
- [x] P1 Implement background synthesis service
- [x] P1 Add in-process scheduler bootstrap for background synthesis
- [ ] P1 Replace bootstrap scheduler with durable production worker
- [ ] P1 Connect practice engine to real executors + QC
- [ ] P1 Connect creativity engine to real generation/editing executors
- [x] P1 Persist DecisionRecord, PracticeSession and Observation records
- [x] P1 Build multidimensional bias/coverage monitor

## Epic M — Closed Creative Organism Loop
- [x] P0 Brain retrieval -> cognition -> expert consultation
- [x] P0 Creative divergence -> evidence routing
- [x] P0 Deterministic execution -> QC
- [x] P0 Execution/provenance persistence
- [x] P0 Episodic memory write
- [x] P0 Failed-QC learning-candidate path
- [x] P0 Hard-lock conflict blocks before execution
- [x] P0 Connect real image-generation executor transport/runtime path (live credential validation pending)
- [x] P0 Connect real image-editing executor runtime for OpenAI + Gemini (live credential validation pending)
- [x] P0 Connect model-backed visual QC transport/runtime path (live credential validation pending)
- [ ] P0 Run first credential-backed live image E2E (workflow exists; current run blocked because OPENAI_API_KEY secret is absent)
- [x] P1 Add cross-provider verifier execution preference + fallback (live dual-provider validation pending)
- [ ] P1 Connect production source harvester
- [ ] P1 Connect Figma execution body