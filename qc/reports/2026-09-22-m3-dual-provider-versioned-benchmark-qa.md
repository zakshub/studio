# FashionOS M3 Dual Provider and Versioned Benchmark QA

Date: 2026-09-22
Scope: PR #1, executor gateway, image edit transports, verifier routing, benchmark evidence versioning.

## Result

PASS for the credential independent runtime layer.

Latest automated validation:
75 passed
2 warnings
0 failed

GitHub Actions run:
35686768510

## Implemented and validated

OpenAI image generation runtime
OpenAI image edit runtime
Gemini image generation runtime
Gemini image edit runtime
OpenAI multimodal visual QC runtime
Gemini multimodal visual QC runtime
cross provider verifier preference
same provider verifier fallback
source to candidate preservation context propagation
hard lock and allowed change propagation
benchmark latency capture
optional benchmark cost capture
executor and model version attribution
stale benchmark evidence exclusion after model version change
B 001 through B 010 benchmark case catalog aligned with runtime capability names

## Defects found during this batch

1. Preservation context was not reaching the executor and verifier consistently.
Fix: pass hard locks, allowed changes, preservation requirement, source storage references and generator provider through the organism loop.

2. A regression test edit temporarily introduced a duplicate execution payload argument.
Fix: corrected before merge and reran the complete test suite.

3. Benchmark evidence lacked model version attribution.
Risk: a new provider model could inherit routing evidence from an older model.
Fix: persist executor version and route only on evidence matching the currently configured version.

4. Benchmark catalog used image_editing while the runtime contract uses image_edit.
Fix: aligned the catalog to the runtime capability name.

## Not proven

No credential backed OpenAI or Gemini production call has completed in this repository yet.
No dual provider live cross provider verification has completed.
No representative fashion benchmark source asset set has been run.
No real provider cost or latency evidence has been collected.
PostgreSQL migrations have not been validated against a real PostgreSQL server.

These remain open and must not be described as production proven.
