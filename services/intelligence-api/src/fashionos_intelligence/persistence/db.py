from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, JSON, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker
from sqlalchemy.pool import StaticPool


class Base(DeclarativeBase):
    pass


class TaskRow(Base):
    __tablename__ = "tasks"

    task_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    workspace_id: Mapped[str] = mapped_column(String(64), index=True)
    objective: Mapped[str] = mapped_column(Text)
    mode: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(32), index=True)
    created_by: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class MemoryRow(Base):
    __tablename__ = "memory_records"

    memory_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    memory_type: Mapped[str] = mapped_column(String(32), index=True)
    scope: Mapped[str] = mapped_column(String(128), index=True)
    content: Mapped[str] = mapped_column(Text)
    evidence_ids: Mapped[list[str]] = mapped_column(JSON, default=list)
    status: Mapped[str] = mapped_column(String(24), default="active", index=True)
    weight: Mapped[float] = mapped_column(Float, default=1.0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class DecisionRow(Base):
    __tablename__ = "decision_records"

    decision_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    task_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )


class PracticeSessionRow(Base):
    __tablename__ = "practice_sessions"

    session_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    target_principle: Mapped[str] = mapped_column(Text)
    mode: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(24), default="planned", index=True)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )


class ObservationRow(Base):
    __tablename__ = "observations"

    observation_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    source_id: Mapped[str] = mapped_column(String(64), index=True)
    media_type: Mapped[str] = mapped_column(String(24), index=True)
    dimension: Mapped[str] = mapped_column(String(64), index=True)
    value: Mapped[str] = mapped_column(Text)
    confidence: Mapped[str] = mapped_column(String(16))
    evidence_ref: Mapped[str | None] = mapped_column(Text, nullable=True)
    interpretation: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )


class LearningCandidateRow(Base):
    __tablename__ = "learning_candidates_runtime"

    candidate_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    observation: Mapped[str] = mapped_column(Text)
    proposed_principle: Mapped[str] = mapped_column(Text)
    scope: Mapped[str] = mapped_column(String(128), index=True)
    evidence_ids: Mapped[list[str]] = mapped_column(JSON, default=list)
    confidence: Mapped[str] = mapped_column(String(16))
    decision_status: Mapped[str] = mapped_column(String(24), default="pending", index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    decided_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )


def build_session_factory(database_url: str) -> sessionmaker[Session]:
    kwargs: dict[str, object] = {"future": True}
    if database_url.startswith("sqlite"):
        kwargs["connect_args"] = {"check_same_thread": False}
        if database_url.endswith(":memory:"):
            kwargs["poolclass"] = StaticPool
    engine = create_engine(database_url, **kwargs)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)