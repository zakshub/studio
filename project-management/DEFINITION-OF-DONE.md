# Definition of Done

## Architecture item is DONE when
- purpose is explicit
- inputs/outputs are defined
- ownership is clear
- failure states are defined
- privacy/trade-secret boundary is checked
- dependency is recorded
- conflicting canonical rules are resolved or scoped

## Backend feature is DONE when
- API contract exists
- validation exists
- error states exist
- authorization boundary exists where needed
- logs/provenance are recorded
- automated tests pass
- failure/rollback behavior is known
- no private methodology leaks into customer response

## Model/executor integration is DONE when
- adapter conforms to common interface
- model/version is internally logged
- benchmark evidence exists
- timeout/error handling exists
- fallback behavior exists
- cost/latency are observable
- provider details remain hidden from customer UI by default

## Source workflow is DONE when
- source role is known
- URL/origin is recorded where applicable
- rights state is recorded
- original is preserved
- derivative lineage is stored
- reference-only assets cannot silently become production assets

## Image task is DONE when
- task mode is correct
- hard locks are explicit
- output is produced
- QC is run
- critical failures are not hidden
- approval state is recorded
- provenance exists

## Figma screen is DONE when
- it maps to a real backend state
- all states are represented
- customer-safe information only is exposed
- admin-only details are separated
- responsive/empty/loading/error states are considered
- image slots have defined dimensions/aspect ratios
- reusable components are used consistently

## Milestone is DONE when
- all P0 tasks are complete
- exit criteria are met
- QA evidence exists
- open risks are accepted or mitigated
- status document is updated
