from __future__ import annotations

from datetime import datetime
from typing import Any

from .errors import StateError
from .mastery import derive_mastery
from .models import WriteContext, response, utc_now
from .store import InMemoryStore
from .validation import (
    validate_case_attempt,
    validate_essay_attempt,
    validate_mastery_evidence,
    validate_practice_attempt,
    validate_resource,
    validate_resource_segment,
    validate_review,
    validate_study_event,
    validate_topic,
    validate_video_progress,
)


class StateService:
    """Allowlisted logical API that can be mapped to Feishu tables."""

    def __init__(self, store: InMemoryStore) -> None:
        self.store = store

    def invoke(self, operation: str, **kwargs: Any) -> dict[str, Any]:
        """External boundary: only named operations are callable and errors are truthful."""
        allowed = {
            "get_system_health", "get_profile", "update_profile", "record_study_event",
            "upsert_topic", "upsert_resource", "upsert_resource_segment", "update_video_progress",
            "record_practice_attempt", "record_mastery_evidence", "recompute_topic_state", "get_topic_state",
            "schedule_review", "get_due_reviews", "record_case_attempt", "record_essay_attempt", "finish_session",
        }
        if operation not in allowed:
            error = StateError("OPERATION_NOT_ALLOWED", f"operation is not allowlisted: {operation}")
            return {"status": "error", "data": None, "error": error.as_dict(), "audit_id": None}
        try:
            return getattr(self, operation)(**kwargs)
        except StateError as error:
            context = kwargs.get("context")
            if isinstance(context, WriteContext):
                self.store.record_failure(operation=operation, context=context, error=error)
                audit_id = context.audit_id
            else:
                audit_id = None
            return {"status": "error", "data": None, "error": error.as_dict(), "audit_id": audit_id}

    def get_system_health(self) -> dict[str, Any]:
        return response(data={"status": "PASS", "adapter": type(self.store).__name__, "authoritative": False})

    def get_profile(self, user_id: str) -> dict[str, Any]:
        return response(data=self.store.read("user_profile", user_id))

    def update_profile(self, user_id: str, patch: dict[str, Any], context: WriteContext) -> dict[str, Any]:
        allowed = {
            "user_id", "target_exam", "target_exam_date", "timezone", "weekday_minutes",
            "weekend_minutes", "past_exam_scores", "preferred_study_time", "current_video_progress", "constraints",
        }
        self._reject_unknown(patch, allowed)
        current = self.store.read("user_profile", user_id) or {"user_id": user_id}
        updated = {**current, **patch, "user_id": user_id}
        result, duplicate = self.store.write(
            table="user_profile", record_id=user_id, record=updated, operation="update_profile", context=context
        )
        result["deduplicated"] = duplicate
        return response(data=result, audit_id=result["audit_id"])

    def record_study_event(self, event: dict[str, Any], context: WriteContext) -> dict[str, Any]:
        result, duplicate = self.store.write(
            table="study_events", record_id=event.get("event_id", ""), record=event,
            operation="record_study_event", context=context, validate=validate_study_event,
        )
        result["deduplicated"] = duplicate
        return response(data=result, audit_id=result["audit_id"])

    def upsert_topic(self, topic: dict[str, Any], context: WriteContext) -> dict[str, Any]:
        result, duplicate = self.store.write(
            table="topics", record_id=topic.get("topic_id", ""), record=topic,
            operation="upsert_topic", context=context, validate=validate_topic,
        )
        result["deduplicated"] = duplicate
        return response(data=result, audit_id=result["audit_id"])

    def upsert_resource(self, resource: dict[str, Any], context: WriteContext) -> dict[str, Any]:
        result, duplicate = self.store.write(
            table="resources", record_id=resource.get("resource_id", ""), record=resource,
            operation="upsert_resource", context=context, validate=validate_resource,
        )
        result["deduplicated"] = duplicate
        return response(data=result, audit_id=result["audit_id"])

    def upsert_resource_segment(self, segment: dict[str, Any], context: WriteContext) -> dict[str, Any]:
        result, duplicate = self.store.write(
            table="resource_segments", record_id=segment.get("segment_id", ""), record=segment,
            operation="upsert_resource_segment", context=context, validate=validate_resource_segment,
        )
        result["deduplicated"] = duplicate
        return response(data=result, audit_id=result["audit_id"])

    def update_video_progress(self, video_id: str, progress: dict[str, Any], context: WriteContext) -> dict[str, Any]:
        if progress.get("video_id") != video_id:
            raise StateError("VALIDATION_ERROR", "video_id must match progress record")
        result, duplicate = self.store.write(
            table="video_progress", record_id=video_id, record=progress,
            operation="update_video_progress", context=context, validate=validate_video_progress,
        )
        result["deduplicated"] = duplicate
        return response(data=result, audit_id=result["audit_id"])

    def record_mastery_evidence(self, evidence: dict[str, Any], context: WriteContext) -> dict[str, Any]:
        result, duplicate = self.store.write(
            table="mastery_evidence", record_id=evidence.get("evidence_id", ""), record=evidence,
            operation="record_mastery_evidence", context=context, validate=validate_mastery_evidence,
        )
        result["deduplicated"] = duplicate
        return response(data=result, audit_id=result["audit_id"])

    def record_practice_attempt(self, attempt: dict[str, Any], context: WriteContext) -> dict[str, Any]:
        result, duplicate = self.store.write(
            table="practice_attempts",
            record_id=attempt.get("attempt_id", ""),
            record=attempt,
            operation="record_practice_attempt",
            context=context,
            validate=validate_practice_attempt,
        )
        result["deduplicated"] = duplicate
        return response(data=result, audit_id=result["audit_id"])

    def recompute_topic_state(self, topic_id: str, context: WriteContext) -> dict[str, Any]:
        derived = derive_mastery(self.store.list("mastery_evidence"), topic_id)
        result, duplicate = self.store.write(
            table="mastery_state", record_id=topic_id, record=derived,
            operation="recompute_topic_state", context=context,
        )
        result["deduplicated"] = duplicate
        return response(data=result, audit_id=result["audit_id"])

    def get_topic_state(self, topic_id: str) -> dict[str, Any]:
        return response(data=self.store.read("mastery_state", topic_id))

    def schedule_review(self, review: dict[str, Any], context: WriteContext) -> dict[str, Any]:
        for existing in self.store.list("review_queue"):
            if (
                existing["topic_id"] == review.get("topic_id")
                and existing["review_type"] == review.get("review_type")
                and existing["status"] == "pending"
            ):
                return response(data={"record": existing, "deduplicated": True}, audit_id=None)
        result, duplicate = self.store.write(
            table="review_queue", record_id=review.get("review_id", ""), record=review,
            operation="schedule_review", context=context, validate=validate_review,
        )
        result["deduplicated"] = duplicate
        return response(data=result, audit_id=result["audit_id"])

    def get_due_reviews(self, now: str) -> dict[str, Any]:
        cutoff = datetime.fromisoformat(now.replace("Z", "+00:00"))
        due = [
            item for item in self.store.list("review_queue")
            if item["status"] == "pending" and datetime.fromisoformat(item["due_at"].replace("Z", "+00:00")) <= cutoff
        ]
        due.sort(key=lambda item: (-float(item["priority"]), item["due_at"], item["review_id"]))
        return response(data=due)

    def record_case_attempt(self, attempt: dict[str, Any], context: WriteContext) -> dict[str, Any]:
        result, duplicate = self.store.write(
            table="case_attempts", record_id=attempt.get("case_id", ""), record=attempt,
            operation="record_case_attempt", context=context, validate=validate_case_attempt,
        )
        result["deduplicated"] = duplicate
        return response(data=result, audit_id=result["audit_id"])

    def record_essay_attempt(self, attempt: dict[str, Any], context: WriteContext) -> dict[str, Any]:
        result, duplicate = self.store.write(
            table="essay_attempts", record_id=attempt.get("essay_id", ""), record=attempt,
            operation="record_essay_attempt", context=context, validate=validate_essay_attempt,
        )
        result["deduplicated"] = duplicate
        return response(data=result, audit_id=result["audit_id"])

    def finish_session(self, session_id: str, checkpoint: dict[str, Any], context: WriteContext) -> dict[str, Any]:
        required = {"completed", "incomplete", "discoveries", "mastery_changes", "next_due", "resume_context", "write_status"}
        missing = sorted(required - checkpoint.keys())
        if missing:
            raise StateError("INCOMPLETE_CHECKPOINT", f"missing checkpoint fields: {', '.join(missing)}")
        record = self.store.read("study_sessions", session_id) or {"session_id": session_id}
        record.update({"status": "finished", "end": utc_now(), "checkpoint": checkpoint})
        result, duplicate = self.store.write(
            table="study_sessions", record_id=session_id, record=record,
            operation="finish_session", context=context,
        )
        result["deduplicated"] = duplicate
        return response(data=result, audit_id=result["audit_id"])

    @staticmethod
    def _reject_unknown(payload: dict[str, Any], allowed: set[str]) -> None:
        unknown = sorted(set(payload) - allowed)
        if unknown:
            raise StateError("FIELD_NOT_ALLOWED", f"fields are not allowlisted: {', '.join(unknown)}")
