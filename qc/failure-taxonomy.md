# Failure Taxonomy

## Source failures
- wrong target image
- wrong source role
- missing authorization
- low-resolution source
- corrupted/incomplete asset
- provenance unknown

## Preservation failures
- identity drift
- garment drift
- color drift
- pose drift
- environment drift
- text/logo corruption

## Physical realism failures
- anatomy
- contact
- garment physics
- material response
- perspective
- optics
- lighting causality
- reflections
- motion

## Instruction failures
- omitted constraint
- unauthorized change
- wrong crop/aspect
- wrong delivery format
- wrong reality class

## Executor failures
- timeout
- refusal
- malformed output
- provider unavailable
- unsupported operation
- partial edit

## QC failures
- evaluator uncertainty
- contradictory evaluators
- insufficient source for verification

## Retry policy
Retry only when the failure can reasonably be corrected without risking source authority. Otherwise escalate or require user input.

Never disguise a failed output as success.
