# Risk Register

| ID | Risk | Impact | Likelihood | Mitigation |
|---|---|---:|---:|---|
| R-01 | Brain becomes brand-contaminated | High | Medium | strict memory layers, brand-neutral QA, runtime isolation |
| R-02 | Trade-secret methodology leaks through UI/API | High | Medium | public/private API separation, customer-safe response schema, review tests |
| R-03 | Research silently changes canonical behavior | High | Medium | candidate/promotion workflow, human/governed promotion |
| R-04 | Provider drift changes output quality | High | High | benchmark history, model-version detection, re-benchmark |
| R-05 | One provider becomes hidden single point of failure | High | Medium | common gateway, fallback routes, provider-neutral UI |
| R-06 | Strict edit regenerates locked content | High | High | preservation mode, hard locks, QC fail/rework |
| R-07 | Secondary reference is reused as production asset | High | Medium | source-role + rights-state enforcement |
| R-08 | Inferred factory/production facts presented as confirmed | High | Medium | source/confidence status, human verification |
| R-09 | Figma gets ahead of backend reality | Medium | High | freeze API/domain contract before full redesign |
| R-10 | Backend over-engineered before MVP | Medium | Medium | milestone scope, P0/P1 separation |
| R-11 | Cost doubles by running all tasks through both models | Medium | High | competitive mode only for high-value/uncertain cases |
| R-12 | QC model grades its own output too generously | Medium | Medium | independent verifier where practical, human review |
| R-13 | Repository rules contradict over time | Medium | Medium | retrieval precedence, contradiction log, deprecation policy |
| R-14 | User cannot understand system because methodology is hidden | Medium | Medium | expose outcomes, confidence, warnings, and decisions without exposing internals |
| R-15 | Crawling websites violates permissions or terms | High | Medium | authorization/rights state, scoped ingestion, legal review before production |
