# Orchestration Architecture

## Purpose
Define how Studio Brain turns an input into an executable, auditable production decision without exposing private methodology to front-end users.

## Runtime sequence
1. Intake
2. Task classification
3. Source classification
4. Constraint extraction
5. Knowledge retrieval
6. Production planning
7. Execution strategy selection
8. Provider/model routing when generative inference is required
9. Execution
10. QC
11. Human decision where required
12. Provenance record
13. Learning-candidate extraction

## Separation of concerns
### Brain
Persistent reusable intelligence, production rules, research-derived rules, QC, preservation logic, routing evidence, and learning governance.

### Workspace context
Temporary client-specific constraints and assets. Never promoted to universal knowledge unless independently generalized and validated.

### Orchestrator
Combines task + sources + workspace context + relevant brain knowledge into a structured production plan.

### Executor
May be deterministic software, image-processing tooling, a generative model, a vision model, or another specialized service.

### QC
Evaluates output against task requirements and brain rules. The executor is not automatically trusted to grade itself.

## Decision discipline
Never use the entire repository blindly. Retrieve the smallest relevant rule set that is sufficient for the task.

## Failure handling
- Preserve the original source.
- Identify the failed dimension.
- Retry only the necessary stage where practical.
- Route to an alternate executor when evidence supports it.
- Never label a failed preservation edit as successful because it looks aesthetically stronger.
- Escalate uncertain production-critical values for human verification.