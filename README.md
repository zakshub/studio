# Studio Image Production Intelligence

Canonical repository for universal image generation, editing, retouching, grading, photographic realism, anti-AI realism, source-preservation, research, orchestration, provider routing, provenance, delivery, QC, and governed learning.

## Identity
Studio Brain is **brand-agnostic** and **provider-agnostic** by default.

It must not carry the identity, taste, terminology, visual signature, campaign language, or production constraints of any specific brand unless that context is explicitly supplied at runtime for a task or workspace.

Client/workspace context is temporary specialization layered on top of the universal brain. It must not silently mutate canonical intelligence.

## Operating contract
For every imagery task, use this repository as the canonical production brain before generating or editing.

Required sequence:
1. Classify the task mode.
2. Classify sources and their roles.
3. Extract hard locks, soft locks, and allowed changes.
4. Select the photographic reality class.
5. Retrieve only the relevant production intelligence.
6. Build the production plan.
7. Select the execution strategy and provider/model only if needed.
8. Execute.
9. Run preservation + forensic anti-AI QC.
10. Store internal provenance.
11. Request human approval where required.
12. Extract learning candidates from outcomes without silently changing canonical knowledge.

## Scope
This is not fashion-only and not tied to one brand. It covers:
- new image generation
- existing image editing
- strict preservation enhancement
- selective editing
- retouching
- relighting
- grading and LUT/look development
- face-led model creation
- outfit-led model creation
- fashion/editorial/lifestyle
- portraiture
- documentary
- product/commercial
- cinematic stills
- mobile/social photography realism
- website-source treatment
- reference research
- source acquisition
- provider routing
- QC and provenance
- governed learning

## Core architecture
- [Operating Constitution](./architecture/operating-constitution.md)
- [Orchestration](./architecture/orchestration.md)
- [Private Methodology Boundary](./architecture/privacy-trade-secret-boundary.md)
- [Model / Executor Routing](./architecture/model-routing.md)
- [Source Acquisition](./architecture/source-acquisition.md)
- [Learning Loop](./architecture/learning-loop.md)
- [Runtime Contract](./architecture/runtime-contract.md)
- [Memory Layers](./architecture/memory-layers.md)
- [Retrieval Policy](./architecture/retrieval-policy.md)

## Core production files
- [SKILL.md](./SKILL.md)
- [170 Protocol Summary](./knowledge/production-intelligence/170-protocol-summary.md)
- [Photographic Reality Engine](./knowledge/photographic-reality/photographic-reality-engine.md)
- [Anti-AI Realism](./knowledge/anti-ai-realism/anti-ai-realism.md)
- [Source Preservation](./knowledge/source-preservation/source-preservation.md)
- [Universal Image Workflow](./workflows/universal-image-workflow.md)
- [Website Source Treatment](./workflows/website-source-treatment.md)
- [Forensic Reality QC](./qc/forensic-reality-qc.md)
- [Repository QA Checklist](./qc/repository-qa-checklist.md)
- [Benchmark Framework](./qc/benchmark-framework.md)
- [Failure Taxonomy](./qc/failure-taxonomy.md)
- [Image Task Report Template](./templates/image-task-report.md)

## Runtime schemas
- [Task Context](./schemas/task-context.md)
- [Execution Record](./schemas/execution-record.md)
- [Learning Candidate](./schemas/learning-candidate.md)
- [Public Response](./schemas/public-response.md)
- [Source Record](./schemas/source-record.md)
- [QC Result](./schemas/qc-result.md)

## Research
- [Research Policy](./research/research-policy.md)

Research produces **candidate knowledge**, not automatic canonical truth.

New observations must be compared with existing intelligence, classified, validated, and explicitly promoted before they become durable rules. Client-specific preferences and one-off campaign decisions must remain scoped and must not contaminate the universal brain.

## Trade-secret boundary
Internal methodology is private backend logic.

Ordinary front-end users must not be shown repository details, internal prompts, rule-retrieval methods, model-routing formulas, provider benchmarks, scoring weights, hidden reasoning, or learning/promotion mechanics.

Front-end users should see only product-appropriate outcomes: recommendations, status, confidence, warnings, approvals, source-facing information, and results.

## Relationship to the 170-Protocol Manual
The supplied Production Intelligence Engine 170-Protocol Manual remains the master production architecture. This repo extends it with deeper photographic-reality controls, source-preservation, provider-neutral orchestration, source acquisition, provenance, learning governance, and forensic anti-AI QC.

## Approval principle
A result is not approved because it is attractive. It is approved only when it is coherent with the task intent, respects locks and source authority, and can be explained as a plausible production/capture/edit/delivery chain for the selected reality class.

## Project management
- [Project Charter](./project-management/PROJECT-CHARTER.md)
- [Master Roadmap](./project-management/MASTER-ROADMAP.md)
- [Current Status](./project-management/STATUS.md)
- [Backlog](./project-management/BACKLOG.md)
- [Definition of Done](./project-management/DEFINITION-OF-DONE.md)
- [Risk Register](./project-management/RISK-REGISTER.md)
- [Decision Log](./project-management/DECISION-LOG.md)

## Backend implementation
- [MVP Technical Stack](./backend/TECH-STACK.md)
- [Backend Domain Model](./backend/domain-model.md)
- [API Contract Freeze](./backend/API-CONTRACT-V1-FREEZE.md)
- [Endpoint Map](./backend/api/endpoint-map-v1.md)
- [Public API](./backend/api/public-api-v1.md)
- [Internal API](./backend/api/internal-api-v1.md)
- [Task Lifecycle](./backend/state-machines/task-lifecycle.md)
- [Persistence Model](./backend/storage/persistence-model.md)
- [Intelligence API Service](./services/intelligence-api/README.md)

## Creative Organism
- [Creative Organism Architecture](./architecture/creative-organism.md)
- [Expert Intelligence System](./architecture/expert-intelligence-system.md)
- [Sensory Harvester](./architecture/sensory-harvester.md)
- [Expert Candidate Roster](./expert-intelligence/roster-v1.md)
- [Expert Profile Schema](./expert-intelligence/profile-schema.md)
