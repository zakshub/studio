# Model and Executor Routing

## Principle
No provider is globally declared best. Routing is task-specific and evidence-driven.

## Executor classes
- deterministic image processing
- browser/search/research service
- language/reasoning model
- image generation model
- image editing model
- vision/QC model
- local/self-hosted model
- human specialist

## Capability dimensions
Benchmark independently:
- web research quality
- source extraction
- structured reasoning
- reference analysis
- identity preservation
- garment preservation
- product fidelity
- image editing
- new image generation
- typography rendering
- anatomy/hands
- material realism
- lighting realism
- prompt/brief adherence
- speed
- cost
- failure rate

## Routing modes
### Single-route
Use the historically strongest executor for the task.

### Competitive
Run two or more executors for high-value tasks and compare outputs.

### Verifier
One executor performs the task; a different evaluator checks it.

### Fallback
Primary executor fails availability/QC, then route to secondary.

## Evidence
Routing rules must be derived from logged task outcomes, not vendor reputation or intuition.

## Cold start
During early operation, use a representative benchmark set and parallel evaluation to establish per-capability evidence.

## Provider secrecy
Provider names and routing logic are backend details by default and are not exposed in ordinary customer UI.