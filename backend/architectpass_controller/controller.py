from __future__ import annotations

from typing import Any, Callable

from architectpass_state.errors import StateError
from architectpass_state.models import WriteContext, response, utc_now
from architectpass_state.store import InMemoryStore

from .diagnosis import diagnose
from .errors import ControllerError
from .planner import PlanGenerator


REQUIRED_OBSERVATION = {
    "observed_at",
    "profile",
    "target_exam_date",
    "due_reviews",
    "score_windows",
    "video_progress",
    "subject_ratios_14d",
    "prior_incomplete",
}


class TrainingController:
    """Audited OBSERVE→CHECKPOINT controller; it never answers external questions."""

    def __init__(self, store: InMemoryStore, planner: PlanGenerator | None = None) -> None:
        self.store = store
        self.planner = planner or PlanGenerator()

    def invoke(self, operation: str, **kwargs: Any) -> dict[str, Any]:
        allowed: dict[str, Callable[..., dict[str, Any]]] = {
            "start_session": self.start_session,
            "diagnose_session": self.diagnose_session,
            "create_plan": self.create_plan,
            "begin_execution": self.begin_execution,
            "submit_human_output": self.submit_human_output,
            "record_test": self.record_test,
            "record_state_update": self.record_state_update,
            "record_schedule": self.record_schedule,
            "finish_checkpoint": self.finish_checkpoint,
            "get_session": self.get_session,
        }
        if operation not in allowed:
            return {"status": "error", "data": None, "error": {
                "code": "OPERATION_NOT_ALLOWED", "message": f"operation is not allowlisted: {operation}"
            }, "audit_id": None}
        try:
            return allowed[operation](**kwargs)
        except (ControllerError, StateError) as error:
            context = kwargs.get("context")
            if isinstance(context, WriteContext):
                self.store.record_failure(operation=operation, context=context, error=StateError(error.code, error.message))
                audit_id = context.audit_id
            else:
                audit_id = None
            return {"status": "error", "data": None, "error": error.as_dict(), "audit_id": audit_id}

    def get_session(self, session_id: str) -> dict[str, Any]:
        return response(data=self.store.read("study_sessions", session_id))

    def start_session(
        self,
        *,
        session_id: str,
        state_snapshot: dict[str, Any],
        available_minutes: int,
        energy: str,
        context: WriteContext,
    ) -> dict[str, Any]:
        missing = sorted(REQUIRED_OBSERVATION - set(state_snapshot))
        if missing:
            raise ControllerError("INCOMPLETE_OBSERVATION", f"state snapshot missing: {', '.join(missing)}")
        if set(state_snapshot.get("score_windows", {})) < {"7d", "14d", "30d"}:
            raise ControllerError("INCOMPLETE_OBSERVATION", "score_windows must contain 7d, 14d and 30d")
        if set(state_snapshot.get("subject_ratios_14d", {})) < {"综合知识", "案例分析", "论文"}:
            raise ControllerError("INCOMPLETE_OBSERVATION", "subject_ratios_14d must contain all three subjects")
        if energy not in {"low", "medium", "high"}:
            raise ControllerError("INVALID_ENERGY", "energy must be low, medium or high")
        if not isinstance(available_minutes, int) or available_minutes < 10:
            raise ControllerError("INVALID_TIME_BUDGET", "available_minutes must be at least 10")
        if self.store.read("study_sessions", session_id):
            return self._retry_existing(session_id, "start_session", context)
        record = {
            "session_id": session_id,
            "phase": "OBSERVE",
            "status": "ACTIVE",
            "available_minutes": available_minutes,
            "energy": energy,
            "state_snapshot": state_snapshot,
            "started_at": utc_now(),
            "last_request_id": context.request_id,
        }
        return self._write(session_id, record, "start_session", context)

    def diagnose_session(self, *, session_id: str, context: WriteContext) -> dict[str, Any]:
        repeated = self._repeat(session_id, "diagnose_session", context)
        if repeated:
            return repeated
        current = self._require_phase(session_id, "OBSERVE", context)
        updated = {**current, "phase": "DIAGNOSE", "diagnosis": diagnose(current["state_snapshot"]),
                   "last_request_id": context.request_id}
        return self._write(session_id, updated, "diagnose_session", context)

    def create_plan(
        self, *, session_id: str, candidates: list[dict[str, Any]], context: WriteContext
    ) -> dict[str, Any]:
        repeated = self._repeat(session_id, "create_plan", context)
        if repeated:
            return repeated
        current = self._require_phase(session_id, "DIAGNOSE", context)
        plan = self.planner.generate(
            state_snapshot=current["state_snapshot"],
            candidates=candidates,
            available_minutes=current["available_minutes"],
            energy=current["energy"],
        )
        updated = {**current, "phase": "PLAN", "plan": plan, "last_request_id": context.request_id}
        return self._write(session_id, updated, "create_plan", context)

    def begin_execution(self, *, session_id: str, task_ref: str, context: WriteContext) -> dict[str, Any]:
        repeated = self._repeat(session_id, "begin_execution", context)
        if repeated:
            return repeated
        current = self._require_phase(session_id, "PLAN", context)
        if not task_ref:
            raise ControllerError("INVALID_TASK_REF", "task_ref is required")
        updated = {
            **current,
            "phase": "EXECUTE",
            "status": "AWAITING_HUMAN",
            "active_task_ref": task_ref,
            "last_request_id": context.request_id,
        }
        return self._write(session_id, updated, "begin_execution", context)

    def submit_human_output(self, *, session_id: str, output_ref: str, context: WriteContext) -> dict[str, Any]:
        repeated = self._repeat(session_id, "submit_human_output", context)
        if repeated:
            return repeated
        current = self._require_phase(session_id, "EXECUTE", context)
        if current.get("status") != "AWAITING_HUMAN":
            raise ControllerError("USER_OUTPUT_NOT_EXPECTED", "session is not waiting for user output")
        if not output_ref:
            raise ControllerError("USER_OUTPUT_REQUIRED", "a traceable user output reference is required")
        updated = {
            **current,
            "phase": "TEST",
            "status": "ACTIVE",
            "user_output_ref": output_ref,
            "last_request_id": context.request_id,
        }
        return self._write(session_id, updated, "submit_human_output", context)

    def record_test(self, *, session_id: str, result: dict[str, Any], context: WriteContext) -> dict[str, Any]:
        repeated = self._repeat(session_id, "record_test", context)
        if repeated:
            return repeated
        current = self._require_phase(session_id, "TEST", context)
        if not result.get("evidence_type") or not result.get("source_ref"):
            raise ControllerError("UNTRACEABLE_TEST", "test result needs evidence_type and source_ref")
        updated = {**current, "phase": "UPDATE", "test_result": result, "last_request_id": context.request_id}
        return self._write(session_id, updated, "record_test", context)

    def record_state_update(
        self, *, session_id: str, write_status: dict[str, Any], context: WriteContext
    ) -> dict[str, Any]:
        repeated = self._repeat(session_id, "record_state_update", context)
        if repeated:
            return repeated
        current = self._require_phase(session_id, "UPDATE", context)
        if write_status.get("status") not in {"ok", "partial", "failed"}:
            raise ControllerError("INVALID_WRITE_STATUS", "write status must truthfully be ok, partial or failed")
        updated = {**current, "phase": "SCHEDULE", "write_status": write_status,
                   "last_request_id": context.request_id}
        return self._write(session_id, updated, "record_state_update", context)

    def record_schedule(
        self, *, session_id: str, next_due: list[dict[str, Any]], context: WriteContext
    ) -> dict[str, Any]:
        repeated = self._repeat(session_id, "record_schedule", context)
        if repeated:
            return repeated
        current = self._require_phase(session_id, "SCHEDULE", context)
        if any(not item.get("due_at") or not item.get("reason") for item in next_due):
            raise ControllerError("INVALID_REVIEW_SCHEDULE", "every review needs due_at and reason")
        updated = {**current, "phase": "CHECKPOINT", "next_due": next_due,
                   "last_request_id": context.request_id}
        return self._write(session_id, updated, "record_schedule", context)

    def finish_checkpoint(
        self, *, session_id: str, checkpoint: dict[str, Any], context: WriteContext
    ) -> dict[str, Any]:
        repeated = self._repeat(session_id, "finish_checkpoint", context)
        if repeated:
            return repeated
        current = self._require_phase(session_id, "CHECKPOINT", context)
        required = {"completed", "incomplete", "discoveries", "mastery_changes", "next_due", "resume_context", "write_status"}
        missing = sorted(required - set(checkpoint))
        if missing:
            raise ControllerError("INCOMPLETE_CHECKPOINT", f"checkpoint missing: {', '.join(missing)}")
        updated = {
            **current,
            "status": "FINISHED",
            "checkpoint": checkpoint,
            "ended_at": utc_now(),
            "last_request_id": context.request_id,
        }
        return self._write(session_id, updated, "finish_checkpoint", context)

    def _require_phase(self, session_id: str, expected: str, context: WriteContext) -> dict[str, Any]:
        current = self.store.read("study_sessions", session_id)
        if not current:
            raise ControllerError("SESSION_NOT_FOUND", f"session not found: {session_id}")
        if current.get("phase") != expected:
            raise ControllerError("INVALID_PHASE_TRANSITION", f"expected {expected}, found {current.get('phase')}")
        return current

    def _retry_existing(self, session_id: str, operation: str, context: WriteContext) -> dict[str, Any]:
        current = self.store.read("study_sessions", session_id)
        if current and current.get("last_request_id") == context.request_id:
            return self._write(session_id, current, operation, context)
        raise ControllerError("SESSION_ALREADY_EXISTS", f"session already exists: {session_id}")

    def _repeat(self, session_id: str, operation: str, context: WriteContext) -> dict[str, Any] | None:
        current = self.store.read("study_sessions", session_id)
        if current and current.get("last_request_id") == context.request_id:
            return self._write(session_id, current, operation, context)
        return None

    def _write(
        self, session_id: str, record: dict[str, Any], operation: str, context: WriteContext
    ) -> dict[str, Any]:
        result, duplicate = self.store.write(
            table="study_sessions", record_id=session_id, record=record, operation=operation, context=context
        )
        result["deduplicated"] = duplicate
        return response(data=result, audit_id=result["audit_id"])
