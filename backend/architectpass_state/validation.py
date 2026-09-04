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


def validate_practice_attempt(record: dict[str, Any]) -> None:
    allowed = {
        "attempt_id",
        "platform",
        "question_or_set_id",
        "topic_ids",
        "correct",
        "confidence",
        "duration",
        "error_type",
        "source_evidence",
        "submitted_at",
    }
    unknown = sorted(set(record) - allowed)
    if unknown:
        raise StateError("FIELD_NOT_ALLOWED", f"practice attempt fields are not allowlisted: {', '.join(unknown)}")
    require_fields(
        record,
        (
            "attempt_id",
            "platform",
            "question_or_set_id",
            "topic_ids",
            "correct",
            "confidence",
            "duration",
            "source_evidence",
            "submitted_at",
        ),
    )
    if record["platform"] != "cheko":
        raise StateError("VALIDATION_ERROR", "practice platform must be cheko")
    if (
        not isinstance(record["topic_ids"], list)
        or not record["topic_ids"]
        or not all(isinstance(item, str) and item for item in record["topic_ids"])
        or len(record["topic_ids"]) != len(set(record["topic_ids"]))
    ):
        raise StateError("VALIDATION_ERROR", "topic_ids must be a non-empty list")
    if not isinstance(record["correct"], bool):
        raise StateError("VALIDATION_ERROR", "correct must be boolean for item-level attempts")
    confidence = record["confidence"]
    if not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1:
        raise StateError("VALIDATION_ERROR", "confidence must be between 0 and 1")
    if not isinstance(record["duration"], (int, float)) or record["duration"] < 0:
        raise StateError("VALIDATION_ERROR", "duration must be non-negative seconds")
    error_type = record.get("error_type")
    if error_type is not None and error_type not in ERROR_TYPES:
        raise StateError("VALIDATION_ERROR", "error_type must be one of K/C/M/A/Q/T/E/G")
    if not record["correct"] and error_type not in set("KCMAQTE"):
        raise StateError("VALIDATION_ERROR", "wrong attempts require K/C/M/A/Q/T/E")
    if record["correct"] and confidence < 0.6 and error_type != "G":
        raise StateError("VALIDATION_ERROR", "low-confidence correct attempts require G")
    if record["correct"] and confidence >= 0.6 and error_type is not None:
        raise StateError("VALIDATION_ERROR", "reliable correct attempts cannot carry an error type")
    source_evidence = record["source_evidence"]
    if not isinstance(source_evidence, dict) or not source_evidence.get("cheko_result_id"):
        raise StateError("UNTRACEABLE_SOURCE", "source_evidence requires a visible Cheko result ID")
    source_allowed = {"cheko_result_id", "visible_item_id", "import_method", "ui_contract_version"}
    source_unknown = sorted(set(source_evidence) - source_allowed)
    if source_unknown:
        raise StateError("FIELD_NOT_ALLOWED", f"source evidence fields are not allowlisted: {', '.join(source_unknown)}")
    if any(not isinstance(source_evidence.get(name), str) or not source_evidence[name] for name in source_allowed):
        raise StateError("UNTRACEABLE_SOURCE", "source evidence requires result, item, method and contract version")
    require_iso_datetime(record["submitted_at"], "submitted_at")


def validate_review(record: dict[str, Any]) -> None:
    require_fields(record, ("review_id", "topic_id", "due_at", "review_type", "priority", "reason", "status"))
    require_iso_datetime(record["due_at"], "due_at")
    if not isinstance(record["priority"], (int, float)) or record["priority"] < 0:
        raise StateError("VALIDATION_ERROR", "priority must be non-negative")
