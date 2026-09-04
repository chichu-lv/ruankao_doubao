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


def validate_topic(record: dict[str, Any]) -> None:
    allowed = {
        "topic_id", "parent_id", "name", "syllabus_weight", "choice_relevance", "case_relevance",
        "essay_relevance", "prerequisites", "source_refs",
    }
    unknown = sorted(set(record) - allowed)
    if unknown:
        raise StateError("FIELD_NOT_ALLOWED", f"topic fields are not allowlisted: {', '.join(unknown)}")
    require_fields(record, ("topic_id", "name", "choice_relevance", "case_relevance", "essay_relevance", "source_refs"))
    if not isinstance(record["source_refs"], list) or not record["source_refs"]:
        raise StateError("UNTRACEABLE_SOURCE", "topic requires source references")
    for name in ("choice_relevance", "case_relevance", "essay_relevance"):
        if not isinstance(record[name], (int, float)) or not 0 <= record[name] <= 1:
            raise StateError("VALIDATION_ERROR", f"{name} must be between 0 and 1")


def validate_resource(record: dict[str, Any]) -> None:
    allowed = {
        "resource_id", "type", "title", "local_path_or_uri", "copyright_scope",
        "processing_status", "checksum", "created_at",
    }
    unknown = sorted(set(record) - allowed)
    if unknown:
        raise StateError("FIELD_NOT_ALLOWED", f"resource fields are not allowlisted: {', '.join(unknown)}")
    require_fields(record, tuple(sorted(allowed)))
    require_iso_datetime(record["created_at"], "created_at")
    if record["type"] not in {"pdf", "video", "transcript", "web", "cheko", "note"}:
        raise StateError("VALIDATION_ERROR", "unsupported resource type")


def validate_resource_segment(record: dict[str, Any]) -> None:
    allowed = {
        "segment_id", "resource_id", "page_start", "page_end", "time_start", "time_end",
        "section", "text", "keywords", "topic_ids", "citation_anchor",
    }
    unknown = sorted(set(record) - allowed)
    if unknown:
        raise StateError("FIELD_NOT_ALLOWED", f"resource segment fields are not allowlisted: {', '.join(unknown)}")
    require_fields(record, ("segment_id", "resource_id", "citation_anchor"))
    has_page = record.get("page_start") is not None and record.get("page_end") is not None
    has_time = record.get("time_start") is not None and record.get("time_end") is not None
    if has_page == has_time:
        raise StateError("VALIDATION_ERROR", "segment requires exactly one page or time range")
    anchor = record["citation_anchor"]
    if has_page and "#page=" not in anchor:
        raise StateError("UNTRACEABLE_SOURCE", "PDF segment requires a page anchor")
    if has_time and "#t=" not in anchor:
        raise StateError("UNTRACEABLE_SOURCE", "video segment requires a time anchor")


def validate_video_progress(record: dict[str, Any]) -> None:
    allowed = {
        "video_id", "watched_until", "status", "last_watched_at", "recall_checked",
        "practice_checked", "needs_rewatch", "source_anchor",
    }
    unknown = sorted(set(record) - allowed)
    if unknown:
        raise StateError("FIELD_NOT_ALLOWED", f"video progress fields are not allowlisted: {', '.join(unknown)}")
    require_fields(record, ("video_id", "watched_until", "status", "last_watched_at", "source_anchor"))
    require_iso_datetime(record["last_watched_at"], "last_watched_at")
    if not isinstance(record["watched_until"], (int, float)) or record["watched_until"] < 0:
        raise StateError("VALIDATION_ERROR", "watched_until must be non-negative")
    if record["status"] not in {
        "unwatched", "played_unchecked", "recalled", "choice_converted", "case_essay_converted", "needs_rewatch"
    }:
        raise StateError("VALIDATION_ERROR", "unsupported video progress status")


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
    allowed = {
        "review_id", "topic_id", "due_at", "review_type", "priority", "reason", "status",
        "completed_at", "completion_evidence_ref",
    }
    unknown = sorted(set(record) - allowed)
    if unknown:
        raise StateError("FIELD_NOT_ALLOWED", f"review fields are not allowlisted: {', '.join(unknown)}")
    require_fields(record, ("review_id", "topic_id", "due_at", "review_type", "priority", "reason", "status"))
    require_iso_datetime(record["due_at"], "due_at")
    if not isinstance(record["priority"], (int, float)) or record["priority"] < 0:
        raise StateError("VALIDATION_ERROR", "priority must be non-negative")
    if record["status"] not in {"pending", "completed"}:
        raise StateError("VALIDATION_ERROR", "review status must be pending or completed")
    if record["status"] == "completed":
        require_fields(record, ("completed_at", "completion_evidence_ref"))
        require_iso_datetime(record["completed_at"], "completed_at")
    elif record.get("completed_at") is not None or record.get("completion_evidence_ref") is not None:
        raise StateError("VALIDATION_ERROR", "pending reviews cannot contain completion evidence")


def validate_case_attempt(record: dict[str, Any]) -> None:
    allowed = {
        "case_id", "question_source", "user_answer", "rubric", "covered_points", "missing_points",
        "irrelevant_content", "time_used", "score_estimate", "review_due",
    }
    unknown = sorted(set(record) - allowed)
    if unknown:
        raise StateError("FIELD_NOT_ALLOWED", f"case attempt fields are not allowlisted: {', '.join(unknown)}")
    required = tuple(sorted(allowed))
    require_fields(record, required)
    require_iso_datetime(record["review_due"], "review_due")
    if not isinstance(record["question_source"], dict) or not record["question_source"]:
        raise StateError("UNTRACEABLE_SOURCE", "case grading requires a structured question source")
    if not isinstance(record["rubric"], list) or not record["rubric"] or any(
        not isinstance(point, dict) or not point.get("source_ref") for point in record["rubric"]
    ):
        raise StateError("UNTRACEABLE_SOURCE", "every case rubric point requires a source reference")
    if not isinstance(record["score_estimate"], (int, float)) or not 0 <= record["score_estimate"] <= 1:
        raise StateError("VALIDATION_ERROR", "score_estimate must be between 0 and 1")
    if not isinstance(record["time_used"], (int, float)) or record["time_used"] < 0:
        raise StateError("VALIDATION_ERROR", "time_used must be non-negative")


def validate_essay_attempt(record: dict[str, Any]) -> None:
    allowed = {
        "essay_id", "topic", "outline_or_full", "project_fact_ids", "word_count", "time_used",
        "rubric_results", "factual_risks", "revision_history",
    }
    unknown = sorted(set(record) - allowed)
    if unknown:
        raise StateError("FIELD_NOT_ALLOWED", f"essay attempt fields are not allowlisted: {', '.join(unknown)}")
    required = tuple(sorted(allowed))
    require_fields(record, required)
    if not isinstance(record["project_fact_ids"], list) or not record["project_fact_ids"]:
        raise StateError("UNSUPPORTED_PROJECT_FACT", "essay requires at least one confirmed project fact ID")
    if not isinstance(record["revision_history"], list) or not record["revision_history"]:
        raise StateError("VALIDATION_ERROR", "essay revision_history must record at least one version")
    if not isinstance(record["word_count"], int) or record["word_count"] < 0:
        raise StateError("VALIDATION_ERROR", "word_count must be a non-negative integer")
    if not isinstance(record["time_used"], (int, float)) or record["time_used"] < 0:
        raise StateError("VALIDATION_ERROR", "time_used must be non-negative")
    if not isinstance(record["rubric_results"], dict) or not record["rubric_results"]:
        raise StateError("VALIDATION_ERROR", "rubric_results must contain scoring dimensions")
