from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FailureLesson:
    failure_code: str
    likely_category: str
    remediation_questions: tuple[str, ...]
    create_learning_candidate: bool


class FailureLearningService:
    CATEGORY_MAP = {
        "IDENTITY_DRIFT": "preservation",
        "GARMENT_DRIFT": "preservation",
        "PRODUCT_FIDELITY_FAILED": "preservation",
        "PRESERVATION_FAILED": "preservation",
        "QC_FAILED": "quality",
        "OUTPUT_INVALID": "execution",
        "EXECUTOR_TIMEOUT": "execution",
        "PROVENANCE_INCOMPLETE": "provenance",
    }

    def analyze(self, failure_code: str, recurrence_count: int = 1) -> FailureLesson:
        category = self.CATEGORY_MAP.get(failure_code, "unknown")
        questions = (
            f"What condition produced {failure_code}?",
            "Which constraint or assumption failed?",
            "Would a different executor, workflow, or lock strategy prevent recurrence?",
        )
        return FailureLesson(
            failure_code=failure_code,
            likely_category=category,
            remediation_questions=questions,
            create_learning_candidate=recurrence_count >= 2,
        )
