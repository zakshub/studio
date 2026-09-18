# FashionOS Intelligence Integration — Project Charter

## Program intent
Build FashionOS as a brand-agnostic fashion operating system powered by a private, persistent Studio Brain.

The Studio Brain is not a customer-facing brand and not a model provider. It is the canonical intelligence layer for visual production, research, source treatment, preservation, QC, routing, provenance, and governed learning.

FashionOS should:
- accept brand/client context only when a workspace explicitly supplies it
- remain neutral when no client context exists
- use one or more execution models/providers without exposing them to ordinary users
- support new generation, existing-image treatment, and website-source workflows
- preserve internal methodology as a trade secret
- improve through research and production evidence without uncontrolled self-modification
- record provenance and QC for every important output

## Product principle
FashionOS owns the workflow and intelligence. Models are replaceable executors.

## User-facing principle
Users should see:
- useful outputs
- recommendations
- status
- confidence
- warnings
- approvals
- source-facing facts
- revisions

Users should not see:
- repository topology
- internal prompts
- private rules
- routing formulas
- provider benchmarks
- hidden reasoning
- learning/promotion mechanics

## Success definition
The first successful end-to-end system must be able to:
1. receive a visual task
2. classify the task and sources
3. retrieve relevant Studio Brain knowledge
4. apply workspace/client context only if supplied
5. generate a production plan
6. select an executor or deterministic method
7. execute
8. run QC
9. record internal provenance
10. return a customer-safe result
11. capture learning evidence without silently rewriting canonical intelligence

## Core workflows
- New image generation
- Existing image strict-preservation treatment
- Selective image editing
- Website primary-source treatment
- Secondary-reference research
- Collection/campaign visual production
- QC and approval
- Asset lineage
- Model/executor benchmarking
- Scheduled research and learning-candidate creation

## Non-goals for the first MVP
- exposing internal methodology to customers
- uncontrolled autonomous self-modification
- building a proprietary foundation model from scratch
- forcing every task through generative AI
- hard-binding FashionOS to one provider
- treating public web availability as asset authorization

## Program owner roles
- Product Owner: defines business/product intent and approves major decisions
- Intelligence Architecture: Studio Brain rules, retrieval, routing policy, learning governance
- Backend Engineering: API, orchestration, integrations, persistence, security
- Product Design: Figma flows, screen architecture, interaction states, customer-safe UX
- QA: contract tests, regression, benchmark, provenance, end-to-end validation
