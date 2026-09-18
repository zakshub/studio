# Benchmark Framework

## Purpose
Evaluate executors and workflows using repeatable tasks rather than subjective provider preference.

## Benchmark families
- strict source preservation
- selective image editing
- identity preservation
- garment/detail preservation
- product geometry/label fidelity
- new editorial generation
- lifestyle realism
- material realism
- lighting realism
- anatomy/hands/contact
- typography/text rendering
- research/source extraction
- structured reasoning
- QC/vision evaluation

## Record per run
- benchmark case ID
- executor/provider/model
- task mode
- source set
- constraints
- output
- latency
- estimated/actual cost when available
- QC dimension scores
- human acceptance/rejection
- failure type

## Decision rule
Do not produce one global provider score.

Maintain capability-specific evidence and route by task.

## Re-benchmark triggers
- provider/model version changes
- repeated production failures
- significant quality shift
- new task class
- new cost/latency constraints

## Bias control
Use the same source, task contract, locks, and target criteria when comparing executors.
