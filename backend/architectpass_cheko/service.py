from __future__ import annotations

import copy
import hashlib
import json
from datetime import datetime
from typing import Any

from architectpass_state import StateError, WriteContext

from .errors import ChekoError


ALLOWED_OPERATIONS = frozenset({
    "create_task",
    "prepare_navigation",
    "enter_awaiting_human",
    "import_submitted_result",
    "get_task",
})
ALLOWED_ROUTES = frozenset({
    "/home",
    "/?subject=0",
    "/test_log?subject=0",
    "/past_exam?subject=0",
    "/error_book?subject=0",
})
ROUTE_BY_TARGET = {
    "chapter_bank": "/?subject=0",
    "past_exam": "/past_exam?subject=0",
    "error_book": "/error_book?subject=0",
    "practice_log": "/test_log?subject=0",
}
IMPORT_METHODS = frozenset({"visible_submitted_report", "official_export", "screenshot", "manual_summary"})
WRONG_ERROR_TYPES = frozenset("KCMAQTE")
FORBIDDEN_CONTENT_KEYS = frozenset({
    "question",
    "question_text",
    "stem",
    "options",
    "answer",
    "correct_answer",
    "analysis",
    "explanation",
    "solution",
})


class ChekoPracticeService:
    """Reference lifecycle with explicit human-answer boundary and audited writes."""

    def __init__(self) -> None:
        self.tasks: dict[str, dict[str, Any]] = {}
        self.requests: dict[str, tuple[str, dict[str, Any]]] = {}
        self.audits: list[dict[str, Any]] = []

    def invoke(self, operation: str, **kwargs: Any) -> dict[str, Any]:
        if operation not in ALLOWED_OPERATIONS:
            return self._error(ChekoError("OPERATION_NOT_ALLOWED", f"operation is not allowlisted: {operation}"), None)
        try:
            return getattr(self, operation)(**kwargs)
        except ChekoError as error:
            context = kwargs.get("context")
            if isinstance(context, WriteContext):
                self._record_failure(operation, context, error)
                return self._error(error, context.audit_id)
            return self._error(error, None)
        except StateError as error:
            return self._error(error, None)

    def create_task(self, task: dict[str, Any], context: WriteContext) -> dict[str, Any]:
        replay = self._replay("create_task", {"task": task}, context)
        if replay is not None:
            return replay
        self._validate_task(task)
        task_id = task["task_id"]
        if task_id in self.tasks:
            raise ChekoError("TASK_ALREADY_EXISTS", "task ID already exists")
        record = {**copy.deepcopy(task), "status": "CREATED"}
        return self._commit("create_task", task_id, None, record, {"task": task}, context)

    def prepare_navigation(
        self,
        task_id: str,
        observed_route: str,
        ui_contract_version: str,
        context: WriteContext,
    ) -> dict[str, Any]:
        request_payload = {
            "task_id": task_id,
            "observed_route": observed_route,
            "ui_contract_version": ui_contract_version,
        }
        replay = self._replay("prepare_navigation", request_payload, context)
        if replay is not None:
            return replay
        current = self._require_task(task_id)
        if current["status"] != "CREATED":
            raise ChekoError("INVALID_STATE_TRANSITION", "navigation can only be prepared from CREATED")
        expected = current["navigation_target"]["route"]
        if observed_route != expected or observed_route not in ALLOWED_ROUTES:
            raise ChekoError("NAVIGATION_MISMATCH", "observed route does not match the task target")
        updated = {
            **current,
            "status": "NAVIGATION_READY",
            "navigation_evidence": {
                "observed_route": observed_route,
                "ui_contract_version": ui_contract_version,
            },
        }
        return self._commit("prepare_navigation", task_id, current, updated, request_payload, context)

    def enter_awaiting_human(self, task_id: str, context: WriteContext) -> dict[str, Any]:
        request_payload = {"task_id": task_id}
        replay = self._replay("enter_awaiting_human", request_payload, context)
        if replay is not None:
            return replay
        current = self._require_task(task_id)
        if current["status"] != "NAVIGATION_READY":
            raise ChekoError("INVALID_STATE_TRANSITION", "AWAITING_HUMAN requires verified navigation")
        updated = {
            **current,
            "status": "AWAITING_HUMAN",
            "human_boundary": {
                "user_answers": True,
                "user_submits": True,
                "assistant_must_not_answer": True,
                "assistant_must_not_submit": True,
                "pre_submit_explanation_allowed": False,
            },
        }
        return self._commit("enter_awaiting_human", task_id, current, updated, request_payload, context)

    def import_submitted_result(
        self,
        task_id: str,
        result: dict[str, Any],
        context: WriteContext,
    ) -> dict[str, Any]:
        request_payload = {"task_id": task_id, "result": result}
        replay = self._replay("import_submitted_result", request_payload, context)
        if replay is not None:
            return replay
        current = self._require_task(task_id)
        if current["status"] != "AWAITING_HUMAN":
            raise ChekoError("RESULT_NOT_READY", "result import requires AWAITING_HUMAN")
        normalized = self._normalize_result(result, expected_question_count=current["question_count"])
        updated = {**current, "status": "IMPORTED", "imported_result": normalized}
        return self._commit("import_submitted_result", task_id, current, updated, request_payload, context)

    def get_task(self, task_id: str) -> dict[str, Any]:
        return {"status": "ok", "data": self._require_task(task_id), "error": None, "audit_id": None}

    def _commit(
        self,
        operation: str,
        task_id: str,
        before: dict[str, Any] | None,
        after: dict[str, Any],
        request_payload: dict[str, Any],
        context: WriteContext,
    ) -> dict[str, Any]:
        context.validate()
        fingerprint = _hash({"operation": operation, "payload": request_payload})
        if any(item["audit_id"] == context.audit_id for item in self.audits):
            raise ChekoError("AUDIT_ID_CONFLICT", "audit ID must be unique")
        self.tasks[task_id] = copy.deepcopy(after)
        response = {
            "status": "ok",
            "data": {"task": copy.deepcopy(after), "deduplicated": False},
            "error": None,
            "audit_id": context.audit_id,
        }
        self.requests[context.request_id] = (fingerprint, copy.deepcopy(response))
        self.audits.append({
            "request_id": context.request_id,
            "audit_id": context.audit_id,
            "actor": context.actor,
            "operation": operation,
            "task_id": task_id,
            "before_hash": _hash(before) if before is not None else None,
            "after_hash": _hash(after),
            "success": True,
            "error": None,
        })
        return response

    def _replay(
        self,
        operation: str,
        request_payload: dict[str, Any],
        context: WriteContext,
    ) -> dict[str, Any] | None:
        context.validate()
        prior = self.requests.get(context.request_id)
        if prior is None:
            return None
        fingerprint = _hash({"operation": operation, "payload": request_payload})
        if prior[0] != fingerprint:
            raise ChekoError("IDEMPOTENCY_CONFLICT", "request ID was reused for another Cheko write")
        duplicate = copy.deepcopy(prior[1])
        duplicate["data"]["deduplicated"] = True
        return duplicate

    def _record_failure(self, operation: str, context: WriteContext, error: ChekoError) -> None:
        context.validate()
        if any(item["audit_id"] == context.audit_id for item in self.audits):
            return
        self.audits.append({
            "request_id": context.request_id,
            "audit_id": context.audit_id,
            "actor": context.actor,
            "operation": operation,
            "task_id": None,
            "before_hash": None,
            "after_hash": None,
            "success": False,
            "error": error.as_dict(),
        })

    @staticmethod
    def _validate_task(task: dict[str, Any]) -> None:
        allowed = {
            "task_id",
            "subject",
            "paper_type",
            "practice_mode",
            "target",
            "question_count",
            "time_limit_minutes",
            "completion_standard",
            "confidence_capture",
            "navigation_target",
        }
        _reject_unknown_fields(task, allowed, "practice task")
        required = allowed
        missing = sorted(name for name in required if task.get(name) in (None, ""))
        if missing:
            raise ChekoError("INVALID_PRACTICE_TASK", f"missing task fields: {', '.join(missing)}")
        if task["paper_type"] not in {"choice", "case", "essay"}:
            raise ChekoError("INVALID_PRACTICE_TASK", "paper_type is not supported")
        if task["subject"] != "系统架构设计师":
            raise ChekoError("INVALID_PRACTICE_TASK", "subject must be 系统架构设计师")
        if task["practice_mode"] not in {"chapter", "past_exam", "wrong_questions", "daily", "manual"}:
            raise ChekoError("INVALID_PRACTICE_TASK", "practice_mode is not supported")
        if not isinstance(task["question_count"], int) or not 1 <= task["question_count"] <= 100:
            raise ChekoError("INVALID_PRACTICE_TASK", "question_count must be between 1 and 100")
        if not isinstance(task["time_limit_minutes"], int) or not 1 <= task["time_limit_minutes"] <= 180:
            raise ChekoError("INVALID_PRACTICE_TASK", "time_limit_minutes must be between 1 and 180")
        if task["confidence_capture"] not in {"per_item", "per_group"}:
            raise ChekoError("INVALID_PRACTICE_TASK", "confidence capture must be per_item or per_group")
        navigation = task["navigation_target"]
        if not isinstance(navigation, dict) or navigation.get("route") not in ALLOWED_ROUTES:
            raise ChekoError("NAVIGATION_NOT_ALLOWED", "navigation route is not allowlisted")
        _reject_unknown_fields(navigation, {"name", "route"}, "navigation target")
        if ROUTE_BY_TARGET.get(navigation.get("name")) != navigation["route"]:
            raise ChekoError("NAVIGATION_NOT_ALLOWED", "navigation target name and route do not match")
        _reject_forbidden_content(task)

    @staticmethod
    def _normalize_result(result: dict[str, Any], *, expected_question_count: int) -> dict[str, Any]:
        _reject_unknown_fields(
            result,
            {"submission_state", "import_method", "cheko_result_id", "observed_at", "ui_contract_version", "summary", "items"},
            "submitted result",
        )
        _reject_forbidden_content(result)
        if result.get("submission_state") != "submitted":
            raise ChekoError("PRE_SUBMISSION_RESULT_BLOCKED", "only submitted results may be imported")
        method = result.get("import_method")
        if method not in IMPORT_METHODS:
            raise ChekoError("IMPORT_METHOD_NOT_ALLOWED", "result import method is not allowlisted")
        for name in ("cheko_result_id", "observed_at", "ui_contract_version"):
            if not isinstance(result.get(name), str) or not result[name].strip():
                raise ChekoError("INVALID_RESULT", f"{name} is required")
        try:
            datetime.fromisoformat(result["observed_at"].replace("Z", "+00:00"))
        except ValueError as error:
            raise ChekoError("INVALID_RESULT", "observed_at must be ISO-8601") from error
        if not result.get("items") and not result.get("summary"):
            raise ChekoError("INVALID_RESULT", "result requires item details or an aggregate summary")
        if result.get("summary") is not None:
            if not isinstance(result["summary"], dict):
                raise ChekoError("INVALID_RESULT", "summary must be an object")
            _reject_unknown_fields(
                result["summary"],
                {"practice_type", "topic", "created_at_display", "question_count", "score_display", "elapsed_display"},
                "result summary",
            )
            reported_count = result["summary"].get("question_count")
            if reported_count is not None and reported_count != expected_question_count:
                raise ChekoError("RESULT_TASK_MISMATCH", "result question count does not match the practice task")
        normalized = copy.deepcopy(result)
        normalized_items: list[dict[str, Any]] = []
        for item in result.get("items", []):
            normalized_items.append(_normalize_item(item))
        item_ids = [item["visible_item_id"] for item in normalized_items]
        if len(item_ids) != len(set(item_ids)):
            raise ChekoError("INVALID_RESULT", "visible item IDs must be unique")
        if len(normalized_items) > expected_question_count:
            raise ChekoError("RESULT_TASK_MISMATCH", "result contains more items than the practice task")
        normalized["items"] = normalized_items
        normalized["review_items"] = [
            item["visible_item_id"] for item in normalized_items if item["review_required"]
        ]
        if not normalized_items:
            normalized["detail_completeness"] = "aggregate_only"
        elif len(normalized_items) == expected_question_count:
            normalized["detail_completeness"] = "item_level_complete"
        else:
            normalized["detail_completeness"] = "item_level_partial"
        return normalized

    def _require_task(self, task_id: str) -> dict[str, Any]:
        task = self.tasks.get(task_id)
        if task is None:
            raise ChekoError("TASK_NOT_FOUND", "practice task does not exist")
        return copy.deepcopy(task)

    @staticmethod
    def _error(error: ChekoError | StateError, audit_id: str | None) -> dict[str, Any]:
        return {"status": "error", "data": None, "error": error.as_dict(), "audit_id": audit_id}


def _normalize_item(item: dict[str, Any]) -> dict[str, Any]:
    _reject_unknown_fields(
        item,
        {"visible_item_id", "topic_id", "correct", "confidence", "duration_seconds", "error_type"},
        "result item",
    )
    _reject_forbidden_content(item)
    required = ("visible_item_id", "topic_id", "correct", "confidence", "duration_seconds")
    missing = [name for name in required if item.get(name) in (None, "")]
    if missing:
        raise ChekoError("INVALID_RESULT_ITEM", f"missing result fields: {', '.join(missing)}")
    if not isinstance(item["correct"], bool):
        raise ChekoError("INVALID_RESULT_ITEM", "correct must be boolean")
    confidence = item["confidence"]
    if not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1:
        raise ChekoError("INVALID_RESULT_ITEM", "confidence must be between 0 and 1")
    duration = item["duration_seconds"]
    if not isinstance(duration, (int, float)) or duration < 0:
        raise ChekoError("INVALID_RESULT_ITEM", "duration_seconds must be non-negative")
    normalized = copy.deepcopy(item)
    if not item["correct"]:
        if item.get("error_type") not in WRONG_ERROR_TYPES:
            raise ChekoError("ERROR_TYPE_REQUIRED", "wrong items require K/C/M/A/Q/T/E")
        normalized["review_required"] = True
        normalized["review_reason"] = "wrong_answer"
    elif confidence < 0.6:
        normalized["error_type"] = "G"
        normalized["review_required"] = True
        normalized["review_reason"] = "low_confidence_correct"
    else:
        if item.get("error_type") not in (None, ""):
            raise ChekoError("INVALID_RESULT_ITEM", "reliable correct items cannot carry an error type")
        normalized["error_type"] = None
        normalized["review_required"] = False
        normalized["review_reason"] = None
    return normalized


def _reject_forbidden_content(value: Any) -> None:
    if isinstance(value, dict):
        forbidden = FORBIDDEN_CONTENT_KEYS.intersection(key.casefold() for key in value)
        if forbidden:
            raise ChekoError("QUESTION_CONTENT_NOT_ALLOWED", "question, answer or explanation content is blocked")
        for child in value.values():
            _reject_forbidden_content(child)
    elif isinstance(value, list):
        for child in value:
            _reject_forbidden_content(child)


def _reject_unknown_fields(value: dict[str, Any], allowed: set[str], label: str) -> None:
    unknown = sorted(set(value) - allowed)
    if unknown:
        raise ChekoError("FIELD_NOT_ALLOWED", f"{label} fields are not allowlisted: {', '.join(unknown)}")


def _hash(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()
