from fashionos_intelligence.services.coverage import CoverageMonitor
from fashionos_intelligence.services.executors import ExecutorGateway, ExecutionRequest
from fashionos_intelligence.services.expert_aggregator import (
    ExpertAggregator,
    ExpertContribution,
)
from fashionos_intelligence.services.observations import ObservationService
from fashionos_intelligence.services.qc_runtime import QCDimension, QCRuntime
from fashionos_intelligence.services.scheduler import BackgroundScheduler
from fashionos_intelligence.services.video_intelligence import VideoIntelligence, VideoSegment


def test_expert_aggregator_preserves_distinct_experts():
    result = ExpertAggregator().aggregate(
        [
            ExpertContribution("a", "lighting", "Prefer: motivated light", ("s1",), "high", 1.0),
            ExpertContribution("b", "lighting", "Avoid: unmotivated fill", ("s2",), "high", 0.9),
        ],
        ["lighting"],
    )
    assert result[0].expert_ids == ("a", "b")
    assert result[0].principles


def test_deterministic_executor_gateway():
    result = ExecutorGateway().run(
        ExecutionRequest(
            task_id="task_1",
            capability="fingerprint",
            operation="fingerprint",
            payload={"value": "x"},
        )
    )
    assert result.status == "succeeded"
    assert result.executor_class == "deterministic"


def test_qc_blocks_failed_preservation():
    outcome = QCRuntime().evaluate(
        [
            QCDimension("preservation", 2, critical=True),
            QCDimension("lighting", 4, critical=True),
        ],
        preservation_required=True,
    )
    assert outcome.status == "fail"
    assert outcome.requires_rework is True


def test_observation_normalization_keeps_inference_flag():
    rows = ObservationService().normalize(
        source_id="source_1",
        media_type="image",
        raw=[
            {
                "dimension": "lighting",
                "value": "soft side light",
                "confidence": "medium",
                "interpretation": True,
            }
        ],
    )
    assert rows[0].interpretation is True


def test_video_analysis_computes_average_shot():
    result = VideoIntelligence().analyze_structured(
        duration_ms=5000,
        segments=[
            VideoSegment(0, 1000, shot_type="wide"),
            VideoSegment(1000, 3000, shot_type="medium"),
        ],
    )
    assert result.average_shot_ms == 1500


def test_coverage_monitor_detects_dominance():
    report = CoverageMonitor().evaluate(
        [
            {"region": "A"},
            {"region": "A"},
            {"region": "A"},
            {"region": "B"},
        ],
        ["region"],
        dominance_threshold=0.7,
    )
    assert report.warnings


def test_scheduler_runs_due_job():
    scheduler = BackgroundScheduler()
    state = {"ran": False}

    def job():
        state["ran"] = True

    scheduler.register("synthesis", 60, job)
    result = scheduler.run_due()
    assert result["synthesis"] == "completed"
    assert state["ran"] is True
