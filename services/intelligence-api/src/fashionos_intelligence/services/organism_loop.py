from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4
from typing import Callable

from fashionos_intelligence.domain.enums import TaskMode
from fashionos_intelligence.domain.models import BrainRetrieveRequest
from fashionos_intelligence.persistence.runtime_records import (
    ExecutionRepository,
    QCRepository,
    StoredExecution,
    StoredQC,
)
from fashionos_intelligence.services.benchmarks import BenchmarkService
from fashionos_intelligence.services.brain import BrainIndex
from fashionos_intelligence.services.cognition import CognitionService
from fashionos_intelligence.services.creative_synthesis import CreativeSynthesisService
from fashionos_intelligence.services.executors import (
    ExecutionRequest,
    ExecutionResult,
    ExecutorAdapter,
    ExecutorGateway,
)
from fashionos_intelligence.services.expert_intelligence import ExpertIntelligenceService
from fashionos_intelligence.services.learning import LearningService
from fashionos_intelligence.services.memory import MemoryService
from fashionos_intelligence.services.provenance import ProvenanceService
from fashionos_intelligence.services.qc_runtime import QCDimension, QCOutcome, QCRuntime
from fashionos_intelligence.services.routing import EvidenceRouter


@dataclass(frozen=True)
class OrganismTask:
    task_id: str
    objective: str
    mode: TaskMode
    capability: str
    source_asset_ids: tuple[str, ...] = ()
    rights_statuses: tuple[str, ...] = ()
    hard_locks: tuple[str, ...] = ()
    allowed_changes: tuple[str, ...] = ()
    preservation_required: bool = False
    independent_source_count: int = 0
    contradiction_count: int = 0
    unknown_count: int = 0
    high_risk: bool = False
    high_value: bool = False
    execution_payload: dict | None = None


@dataclass(frozen=True)
class OrganismLoopResult:
    task_id: str
    status: str
    brain_revision: str
    knowledge_unit_ids: tuple[str, ...]
    selected_experts: tuple[str, ...]
    creative_direction_ids: tuple[str, ...]
    executor_classes: tuple[str, ...]
    qc_status: str | None
    provenance_id: str | None
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    human_review_required: bool
    verifier_class: str | None = None


class CreativeOrganismLoop:
    """Closes the MVP cognition -> action -> QC -> memory loop.

    The concrete model/tool adapters remain replaceable dependencies.
    """

    def __init__(
        self,
        *,
        brain: BrainIndex,
        cognition: CognitionService,
        experts: ExpertIntelligenceService,
        creativity: CreativeSynthesisService,
        benchmarks: BenchmarkService,
        executors: ExecutorGateway,
        qc: QCRuntime,
        provenance: ProvenanceService,
        memory: MemoryService,
        learning: LearningService,
        execution_repository: ExecutionRepository | None = None,
        qc_repository: QCRepository | None = None,
        visual_verifier: ExecutorAdapter | None = None,
    ) -> None:
        self.brain = brain
        self.cognition = cognition
        self.experts = experts
        self.creativity = creativity
        self.benchmarks = benchmarks
        self.router = EvidenceRouter(benchmarks)
        self.executors = executors
        self.qc = qc
        self.provenance = provenance
        self.memory = memory
        self.learning = learning
        self.execution_repository = execution_repository
        self.qc_repository = qc_repository
        self.visual_verifier = visual_verifier

    @staticmethod
    def _best_candidate(
        candidates: list[tuple[ExecutionResult, QCOutcome, ExecutionResult | None]],
    ) -> tuple[ExecutionResult, QCOutcome, ExecutionResult | None]:
        rank = {"pass": 3, "warn": 2, "fail": 1}
        return max(
            candidates,
            key=lambda item: (
                rank.get(item[1].status, 0),
                -len(item[1].critical_failures),
            ),
        )

    @staticmethod
    def _verifier_dimensions(verifier: ExecutionResult) -> list[QCDimension]:
        raw = verifier.output.get("dimensions", {})
        critical = {
            str(item)
            for item in verifier.output.get("criticalDimensions", [])
        }
        reasons = tuple(str(item) for item in verifier.output.get("reasons", []))
        dimensions: list[QCDimension] = []

        if isinstance(raw, dict):
            for name, value in raw.items():
                try:
                    score = float(value)
                except (TypeError, ValueError):
                    score = None
                dimensions.append(
                    QCDimension(
                        name=str(name),
                        score=score,
                        critical=str(name) in critical,
                        notes=reasons,
                    )
                )

        if verifier.output.get("accepted") is False:
            dimensions.append(
                QCDimension(
                    name="verifier_acceptance",
                    score=1.0,
                    critical=True,
                    notes=reasons,
                )
            )
        return dimensions

    def run(
        self,
        task: OrganismTask,
        *,
        qc_evaluator: Callable[[ExecutionResult], list[QCDimension]],
    ) -> OrganismLoopResult:
        retrieval_request = BrainRetrieveRequest(
            taskId=task.task_id,
            mode=task.mode,
            rightsStatuses=list(task.rights_statuses),
            hardLocks=list(task.hard_locks),
            allowedChanges=list(task.allowed_changes),
            preservationRequired=task.preservation_required,
            requiredCapabilities=[task.capability],
        )
        units = self.brain.retrieve(retrieval_request)
        structured_conflicts = self.brain.conflicts_for(retrieval_request)

        cognition = self.cognition.plan(
            mode=task.mode.value,
            capabilities=[task.capability],
            rights_statuses=list(task.rights_statuses),
            hard_locks=list(task.hard_locks),
            requested_changes=list(task.allowed_changes),
            preservation_required=task.preservation_required,
            evidence_count=len(units),
            independent_source_count=task.independent_source_count,
            contradiction_count=task.contradiction_count,
            unknown_count=task.unknown_count,
            high_risk=task.high_risk,
        )

        conflict_warnings = tuple(
            f"RULE_CONFLICT:{item['subject']}"
            for item in structured_conflicts
            if item.get("unresolvedRuleIds")
            or item.get("reason") == "HIGHER_AUTHORITY_OR_SPECIFICITY"
        )
        warnings = tuple(cognition.warnings) + conflict_warnings

        if not cognition.value_allowed:
            return OrganismLoopResult(
                task_id=task.task_id,
                status="blocked",
                brain_revision=self.brain.revision,
                knowledge_unit_ids=tuple(unit.unit_id for unit in units),
                selected_experts=(),
                creative_direction_ids=(),
                executor_classes=(),
                qc_status=None,
                provenance_id=None,
                blockers=tuple(cognition.blockers),
                warnings=warnings,
                human_review_required=True,
                verifier_class=None,
            )

        consultation = self.experts.consult(councils=list(cognition.councils))
        principles = [
            principle
            for insight in consultation.insights
            for principle in insight.principles
        ]
        if not principles:
            principles = [
                f"Serve the task objective: {task.objective}",
                "Preserve explicit constraints and physical coherence",
            ]

        directions = self.creativity.diverge(
            principles=principles,
            councils=list(cognition.councils),
            max_directions=4,
        )

        available = self.executors.available(task.capability)
        route = self.router.decide(
            capability=task.capability,
            available_executors=available,
            high_value=task.high_value,
            verifier_available=self.visual_verifier is not None,
            current_versions=self.executors.versions(task.capability),
        )
        if not route.ordered_executors:
            return OrganismLoopResult(
                task_id=task.task_id,
                status="failed",
                brain_revision=self.brain.revision,
                knowledge_unit_ids=tuple(unit.unit_id for unit in units),
                selected_experts=consultation.selected_experts,
                creative_direction_ids=tuple(d.direction_id for d in directions),
                executor_classes=(),
                qc_status=None,
                provenance_id=None,
                blockers=("EXECUTOR_UNAVAILABLE",),
                warnings=warnings,
                human_review_required=True,
                verifier_class=None,
            )

        request = ExecutionRequest(
            task_id=task.task_id,
            capability=task.capability,
            operation=task.mode.value,
            payload={
                "objective": task.objective,
                "creativeDirections": [
                    {
                        "id": direction.direction_id,
                        "principles": list(direction.principles),
                        "tension": direction.tension,
                    }
                    for direction in directions
                ],
                "hardLocks": list(task.hard_locks),
                "allowedChanges": list(task.allowed_changes),
                "preservationRequired": task.preservation_required,
                **(task.execution_payload or {}),
            },
            source_asset_ids=task.source_asset_ids,
        )

        raw = self.executors.run_decision(request, route)
        results = raw if isinstance(raw, list) else [raw]

        evaluated: list[tuple[ExecutionResult, QCOutcome, ExecutionResult | None]] = []
        for result in results:
            verifier_result: ExecutionResult | None = None
            dimensions: list[QCDimension]

            if (
                self.visual_verifier is not None
                and self.visual_verifier.supports("vision_qc")
                and result.output.get("storageUri")
            ):
                try:
                    verifier_result = self.visual_verifier.execute(
                        ExecutionRequest(
                            task_id=task.task_id,
                            capability="vision_qc",
                            operation="verify",
                            payload={
                                "candidateStorageUri": result.output.get("storageUri"),
                                "mimeType": result.output.get("mimeType", "image/png"),
                                "objective": task.objective,
                                "preservationRequired": task.preservation_required,
                                "hardLocks": list(task.hard_locks),
                                "generatorProvider": result.diagnostics.get("provider"),
                                "sourceStorageUris": (task.execution_payload or {}).get("sourceStorageUris", []),
                                "sourceMimeTypes": (task.execution_payload or {}).get("sourceMimeTypes", []),
                                "sourceStorageUri": (task.execution_payload or {}).get("sourceStorageUri"),
                                "sourceMimeType": (task.execution_payload or {}).get("sourceMimeType"),
                            },
                            source_asset_ids=task.source_asset_ids,
                        )
                    )
                    dimensions = self._verifier_dimensions(verifier_result)
                    if not dimensions:
                        dimensions = [
                            QCDimension(
                                "visual_verifier",
                                None,
                                critical=True,
                                notes=("Verifier returned no usable dimensions.",),
                            )
                        ]
                except Exception as exc:
                    dimensions = [
                        QCDimension(
                            "visual_verifier",
                            None,
                            critical=True,
                            notes=(f"Verifier failed: {type(exc).__name__}",),
                        )
                    ]
            else:
                dimensions = qc_evaluator(result)

            outcome = self.qc.evaluate(
                dimensions,
                preservation_required=task.preservation_required,
            )
            evaluated.append((result, outcome, verifier_result))

        selected_result, selected_qc, selected_verifier = self._best_candidate(evaluated)
        execution_id = f"exec_{uuid4().hex[:16]}"
        output_asset_ids = list(selected_result.output.get("assetIds", []))
        knowledge_ids = [unit.unit_id for unit in units]

        if self.execution_repository is not None:
            self.execution_repository.upsert(
                StoredExecution(
                    execution_id=execution_id,
                    task_id=task.task_id,
                    brain_revision=self.brain.revision,
                    source_asset_ids=list(task.source_asset_ids),
                    output_asset_ids=output_asset_ids,
                    knowledge_unit_ids=knowledge_ids,
                    executor_class=selected_result.executor_class,
                    status=selected_result.status,
                    payload={
                        "routingStrategy": route.strategy,
                        "routingReason": route.reason_code,
                        "visualVerifier": (
                            selected_verifier.executor_class
                            if selected_verifier is not None
                            else None
                        ),
                    },
                )
            )

        qc_id = f"qc_{uuid4().hex[:16]}"
        if self.qc_repository is not None:
            self.qc_repository.upsert(
                StoredQC(
                    qc_id=qc_id,
                    execution_id=execution_id,
                    status=selected_qc.status,
                    dimensions={
                        item.name: {
                            "score": item.score,
                            "critical": item.critical,
                            "notes": list(item.notes),
                        }
                        for item in selected_qc.dimensions
                    },
                    critical_failures=list(selected_qc.critical_failures),
                    requires_rework=selected_qc.requires_rework,
                    human_review_required=selected_qc.human_review_required,
                )
            )

        provenance = self.provenance.create_record(
            execution_id=execution_id,
            task_id=task.task_id,
            brain_revision=self.brain.revision,
            source_asset_ids=list(task.source_asset_ids),
            output_asset_ids=output_asset_ids,
            knowledge_unit_ids=knowledge_ids,
            qc_status=selected_qc.status,
        )

        self.memory.remember(
            memory_type="episodic",
            scope=f"task:{task.task_id}",
            content=(
                f"Task {task.task_id} executed via {selected_result.executor_class}; "
                f"QC={selected_qc.status}; brain={self.brain.revision}; "
                f"verifier={selected_verifier.executor_class if selected_verifier else 'none'}."
            ),
            evidence_ids=[execution_id, provenance.provenance_id],
            weight=1.0,
        )

        if selected_qc.status == "fail":
            self.learning.create(
                observation=(
                    f"Execution {execution_id} failed QC: "
                    + ", ".join(selected_qc.critical_failures)
                ),
                proposed_principle=(
                    "Investigate the failed execution pattern before changing canonical production rules."
                ),
                scope=f"task_mode:{task.mode.value}",
                evidence_ids=[execution_id, qc_id],
                confidence="medium",
            )

        human_review = (
            cognition.human_review_required
            or selected_qc.human_review_required
        )
        status = (
            "rework_required"
            if selected_qc.status == "fail"
            else "needs_review"
            if human_review
            else "completed"
        )

        return OrganismLoopResult(
            task_id=task.task_id,
            status=status,
            brain_revision=self.brain.revision,
            knowledge_unit_ids=tuple(knowledge_ids),
            selected_experts=consultation.selected_experts,
            creative_direction_ids=tuple(d.direction_id for d in directions),
            executor_classes=tuple(result.executor_class for result in results),
            qc_status=selected_qc.status,
            provenance_id=provenance.provenance_id,
            blockers=tuple(cognition.blockers),
            warnings=warnings,
            human_review_required=human_review,
            verifier_class=(
                selected_verifier.executor_class
                if selected_verifier is not None
                else None
            ),
        )