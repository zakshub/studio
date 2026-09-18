# Creative Organism — Deliberative Cognition

## Purpose
Define the active reasoning loop used when the organism is working on a current objective.

## Deliberative cycle
1. ORIENT — identify current objective, context, constraints, source roles, risks, and approval policy.
2. ATTEND — select the most relevant knowledge, observations, memories, expert councils, and unresolved uncertainties.
3. FRAME — define the actual problem rather than merely restating the request.
4. RECALL — retrieve semantic, procedural, episodic, project, expert, and source memory.
5. DIVERGE — produce materially different approaches rather than cosmetic variants.
6. SIMULATE — predict likely consequences, failure modes, tradeoffs, and downstream dependencies.
7. CONSULT — request relevant expert-council intelligence when useful.
8. CRITIQUE — evaluate candidates against values, physical/world model, constraints, QC, originality, and evidence.
9. CONVERGE — select or combine the strongest approach.
10. DECIDE — create an auditable action decision.
11. EXECUTE — hand the approved plan to replaceable tools/executors.
12. VERIFY — run QC/provenance/constraint checks.
13. REFLECT — compare intended vs actual outcome.
14. LEARN — create scoped learning candidates; never auto-promote universal knowledge.

## Working memory
The active task frame should contain:
- objective
- task mode
- current source/reference set
- hard/soft locks
- allowed changes
- relevant retrieved knowledge IDs
- active hypotheses
- selected expert councils
- candidate approaches
- rejected approaches and reason codes
- uncertainties
- current decision
- required human approval
- execution/QC outcome

## Attention
Attention is allocated by:
- relevance to objective
- risk
- uncertainty
- novelty
- contradiction
- expected information gain
- user priority
- cost

## Stop conditions
The deliberative loop stops when:
- a valid decision is available and approval policy allows execution
- human approval/input is required
- required evidence is unavailable
- rights/security blocks work
- uncertainty exceeds configured threshold
- compute/time budget is reached

## Output
The reasoning loop emits a concise internal DecisionRecord, not raw hidden chain-of-thought.
