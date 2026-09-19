# FashionOS Intelligence Integration — Master Roadmap

## Current program state
Status: M2 COMPLETE / M3 EXECUTION + BENCHMARKING IN PROGRESS

The Studio Brain architecture and repository QA are complete enough to stop expanding abstract theory and begin system integration.

---

## Milestone M0 — Canonical Studio Brain Foundation
Status: COMPLETE

### Delivered
- Brand-agnostic operating constitution
- Provider-neutral architecture
- Universal imagery production rules
- 170-protocol production summary
- Photographic reality engine
- Source-preservation doctrine
- Anti-AI realism
- Forensic QC
- Source acquisition hierarchy
- Website-source treatment workflow
- Model/executor routing policy
- Governed learning loop
- Memory-layer separation
- Retrieval policy
- Runtime/public schemas
- Benchmark framework
- Failure taxonomy
- Research policy
- Trade-secret/front-end boundary
- Anti-hallucination rules
- Architecture QA report

### Exit criteria
- Required architecture files present
- No embedded target-brand identity
- Private methodology boundary documented
- Anti-hallucination safeguards documented
- QA PASS

Result: PASSED

---

## Milestone M1 — Backend Domain Model + API Contract
Status: COMPLETE

Goal: turn brain concepts into a concrete contract the frontend and backend can both implement.

### Tasks
1. Define core entities:
   - Workspace
   - Task
   - SourceAsset
   - ReferenceSource
   - TreatmentJob
   - GenerationJob
   - ProductionPlan
   - ExecutorRoute
   - QCResult
   - Approval
   - AssetVersion
   - LearningCandidate
2. Define internal API vs customer-facing API.
3. Define endpoint map.
4. Define request/response schemas.
5. Define error states.
6. Define job lifecycle/state machine.
7. Define permissions/admin boundary.
8. Define persistence needs.
9. Define event/audit log.
10. Freeze v1 API contract.

### Deliverables
- backend architecture document
- endpoint specification
- domain model
- state-machine specification
- public/private API boundary

### Exit criteria
A developer can implement the backend without inventing product behavior.

Result: PASSED — contract frozen in `backend/API-CONTRACT-V1-FREEZE.md` and QA recorded in `qc/reports/2026-09-18-m1-backend-contract-qa.md`.

---

## Milestone M2 — Studio Brain Service + Retrieval Layer
Status: COMPLETE
Depends on: M1

Goal: make the repository consumable by FashionOS programmatically.

### Tasks
- [x] Local brain sync/index runtime
- [x] Remote GitHub mirror refresh bootstrap with last-known-good fallback
- [x] GitHub pull/update strategy specification
- [x] Local normalized index implementation
- [x] Knowledge-domain indexing
- [x] Task-to-knowledge retrieval
- [x] Rule precedence + structured conflict integration
- [x] Brain-health/stale status
- [x] Durable revision snapshots
- [x] Rollback/version pinning bootstrap
- [ ] Semantic/vector retrieval enhancement
- [ ] Deployment-grade persistent cache/webhook refresh enhancement

### Creative Organism parallel track
- [x] Creative Organism architecture defined
- [x] Subconscious/value-system architecture defined
- [x] Deliberative cognition architecture defined
- [x] Child-learning cycle defined
- [x] Practice/simulation architecture defined
- [x] Memory/forgetting architecture defined
- [x] Creative synthesis architecture defined
- [x] Metacognition + curiosity architecture defined
- [x] Background synthesis architecture defined
- [x] Contamination/coverage architecture defined
- [x] Expert Intelligence system architecture defined
- [x] Sensory Harvester architecture defined
- [x] Value-system runtime bootstrap
- [x] Cognition + attention + council-selection runtime bootstrap
- [x] Metacognition + curiosity runtime bootstrap
- [x] Practice + memory + governed-learning runtime bootstrap
- [x] Novelty + contamination + failure-learning + background-synthesis bootstrap
- [x] Creative synthesis runtime bootstrap
- [x] Sensory source registry + change-detection bootstrap
- [x] First 10 expert source packs/profiles synthesized
- [ ] Validate and activate expert profiles
- [ ] Complete all 50 expert intelligence profiles
- [x] Build expert-content aggregator runtime bootstrap
- [ ] Build production visual/video sensory collector runtime
- [ ] Connect practice and creative synthesis to real executors/QC

### Exit criteria
Given a task context, the service returns the relevant intelligence without loading the entire repository.

Result: PASSED — local/remote sync path, traceable retrieval, structured conflict handling, durable revisions and rollback are implemented and regression-tested. QA: `qc/reports/2026-09-19-m2-hardening-organism-loop-qa.md`.

Semantic/vector retrieval and deployment-grade cache/webhook refresh remain enhancements rather than M2 blockers.

---

## Milestone M3 — Executor Gateway + Model Benchmarking
Status: IN PROGRESS
Depends on: M1, partially M2

Goal: use Gemini/OpenAI/other executors based on evidence, not preference.

### Tasks
- [x] Provider-neutral executor adapter interface
- [ ] Gemini adapter
- [ ] OpenAI adapter
- [x] Deterministic processing adapter bootstrap
- [ ] Optional future/self-hosted adapter contract
- [ ] Representative benchmark dataset
- [x] Benchmark evidence service
- [x] Capability-specific score/history persistence
- [x] Evidence-driven routing rules
- [x] Fallback-capable ordered execution
- [x] Competitive mode bootstrap
- [ ] Two-stage verifier execution
- [ ] End-to-end cost/latency telemetry

### Exit criteria
FashionOS can choose an executor by task type and recorded performance.

---

## Milestone M4 — Source Acquisition + Website Intake
Status: PLANNED
Depends on: M1

Goal: support existing customer imagery and secondary-reference websites.

### Tasks
- primary website input
- secondary reference input
- browser/crawler/asset collector
- image discovery
- source URL capture
- deduplication
- dimensions/quality detection
- source-role classification
- rights-status field
- primary-asset selection
- reference-only treatment
- source-lineage persistence

### Exit criteria
A client site can be scanned and its authorized imagery can enter the treatment pipeline without confusing references with production assets.

---

## Milestone M5 — QC + Provenance Runtime
Status: PLANNED
Depends on: M1, M2, M3

Goal: make every important output auditable and reject lock violations.

### Tasks
- QC service
- preservation comparison
- garment/material checks
- identity checks
- camera/light/realism checks
- anti-AI checks
- confidence and uncertainty handling
- fail/warn/pass contract
- human-review rules
- execution record
- asset lineage
- retry/rework policy

### Exit criteria
A failed preservation edit cannot be labeled successful, and every approved output has an internal execution/provenance record.

---

## Milestone M6 — Product Design / Figma v2
Status: PLANNED
Depends on: M1 contract; can overlap M2–M5

Goal: redesign the new Figma file around real backend contracts rather than decorative AI concepts.

### Pages/areas to design
- Cover / product positioning
- Product architecture
- Core user flows
- Design foundations
- Components
- Dashboard
- Source/website intake
- Collection Studio
- Design Intelligence
- Visualization Studio
- Existing-image treatment
- Campaign Studio
- Assets Library
- QC/review
- Internal admin/settings
- White-label/workspace settings where relevant

### UX rules
- no GitHub/provider/routing methodology exposed to ordinary users
- no internal brain version/commit exposed in customer UI
- customer sees only safe product-level state
- admin/internal surfaces may expose operational health
- generated imagery should be placed into designed image slots where practical

### Exit criteria
Every major screen maps to defined backend state and API data.

---

## Milestone M7 — Backend MVP
Status: PLANNED
Depends on: M1–M5

Goal: working orchestration without full production polish.

### MVP flow
Task -> classify -> retrieve -> plan -> route -> execute -> QC -> persist -> return safe response

### Exit criteria
At least one task from each MVP workflow completes end-to-end:
- strict preservation edit
- new generation
- website-source treatment
- research/reference analysis

---

## Milestone M8 — Frontend MVP
Status: PLANNED
Depends on: M6, M7

Goal: connect the designed FashionOS UI to the backend MVP.

### Tasks
- app shell
- auth/workspace context
- dashboard
- task creation
- source intake
- visualization/treatment flows
- job status
- review/approval
- asset library
- error/warning states
- internal admin controls

### Exit criteria
A user can complete the core workflows without seeing private methodology.

---

## Milestone M9 — End-to-End Pilot + QA
Status: PLANNED
Depends on: M7, M8

### Test scenarios
- strict identity + garment preservation
- outfit-led edit
- new editorial generation
- customer website treatment
- secondary reference research
- provider fallback
- QC failure and retry
- source permission unknown
- stale brain cache
- provider outage
- human approval/rejection
- asset version rollback

### Exit criteria
Critical workflows pass regression and provenance checks.

---

## Milestone M10 — Controlled Beta / Production Readiness
Status: LATER

### Tasks
- security review
- access controls
- rate limits
- observability
- backups
- cost controls
- deployment
- incident handling
- customer-safe logging
- privacy/legal review
- performance testing

### Exit criteria
System can support real customer work without exposing trade secrets or corrupting canonical intelligence.

---

## Continuous Track — Research + Learning
Status: ACTIVE

Existing weekly visual research remains active.

### Continuous rules
- research creates candidates
- candidates do not auto-promote
- duplicates rejected
- contradictions preserved and scoped
- client-specific taste never becomes universal by default
- promoted knowledge updates changelog
- routing benchmarks are re-run after provider/model changes