from __future__ import annotations

from datetime import datetime
from typing import Any

from .errors import StateError


ERROR_TYPES = frozenset("KCM AQT EG".replace(" ", ""))
EVIDENCE_TYPES = {
    "viewed",
    "open_book_recall",
    "closed_book_recall",
    "choice_untimed",
    "choice_timed",
    "case_points",
    "essay_application",
    "timed_mock",
}
EVIDENCE_MAX_LEVEL = {
    "viewed": 1,
    "open_book_recall": 1,
    "closed_book_recall": 2,
    "choice_untimed": 3,
    "choice_timed": 3,
    "case_points": 4,
    "essay_application": 5,
    "timed_mock": 5,
}


def require_fields(record: dict[str, Any], fields: tuple[str, ...]) -> None:
    missing = [name for name in fields if record.get(name) in (None, "")]
    if missing:
        raise StateError("VALIDATION_ERROR", f"missing fields: {', '.join(missing)}")


def require_iso_datetime(value: str, field_name: str) -> None:
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, TypeError, ValueError) as exc:
        raise StateError("VALIDATION_ERROR", f"{field_name} must be ISO-8601") from exc


def validate_study_event(record: dict[str, Any]) -> None:
    require_fields(record, ("event_id", "event_type", "occurred_at", "source_ref"))
    require_iso_datetime(record["occurred_at"], "occurred_at")
    if not isinstance(record["source_ref"], dict) or not record["source_ref"]:
        raise StateError("UNTRACEABLE_SOURCE", "source_ref must contain a traceable anchor")


def validate_mastery_evidence(record: dict[str, Any]) -> None:
    require_fields(
        record,
        ("evidence_id", "topic_id", "evidence_type", "score", "confidence", "source_id", "created_at"),
    )
    if record["evidence_type"] not in EVIDENCE_TYPES:
        raise StateError("VALIDATION_ERROR", "unsupported evidence_type")
    for name in ("score", "confidence"):
        value = record[name]
        if not isinstance(value, (int, float)) or not 0 <= value <= 1:
            raise StateError("VALIDATION_ERROR", f"{name} must be between 0 and 1")
    require_iso_datetime(record["created_at"], "created_at")


def validate_review(record: dict[str, Any]) -> None:
    require_fields(record, ("review_id", "topic_id", "due_at", "review_type", "priority", "reason", "status"))
    require_iso_datetime(record["due_at"], "due_at")
    if not isinstance(record["priority"], (int, float)) or record["priority"] < 0:
        raise StateError("VALIDATION_ERROR", "priority must be non-negative")

