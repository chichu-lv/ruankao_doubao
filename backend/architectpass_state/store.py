from __future__ import annotations

import copy
import hashlib
import json
from typing import Any, Callable

from .errors import StateError
from .models import WriteContext, utc_now


IMMUTABLE_TABLES = frozenset({"study_events", "mastery_evidence", "audit_log"})
TABLES = (
    "user_profile",
    "exam_config",
    "topics",
    "resources",
    "resource_segments",
    "video_progress",
    "study_sessions",
    "practice_attempts",
    "study_events",
    "mastery_evidence",
    "mastery_state",
    "review_queue",
    "case_attempts",
    "essay_attempts",
    "audit_log",
)
PRIMARY_KEYS = {
    "user_profile": "user_id", "exam_config": "exam_name", "topics": "topic_id",
    "resources": "resource_id", "resource_segments": "segment_id", "video_progress": "video_id",
    "study_sessions": "session_id", "practice_attempts": "attempt_id", "study_events": "event_id",
    "mastery_evidence": "evidence_id", "mastery_state": "topic_id", "review_queue": "review_id",
    "case_attempts": "case_id", "essay_attempts": "essay_id", "audit_log": "audit_id",
}


def _stable_hash(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


class InMemoryStore:
    """Test/reference adapter. It is never an authoritative production store."""

    def __init__(self) -> None:
        self.tables: dict[str, dict[str, dict[str, Any]]] = {name: {} for name in TABLES}
        self._idempotency: dict[str, tuple[str, dict[str, Any]]] = {}

    def read(self, table: str, record_id: str) -> dict[str, Any] | None:
        self._require_table(table)
        value = self.tables[table].get(record_id)
        return copy.deepcopy(value) if value is not None else None

    def list(self, table: str) -> list[dict[str, Any]]:
        self._require_table(table)
        return copy.deepcopy(list(self.tables[table].values()))

    def write(
        self,
        *,
        table: str,
        record_id: str,
        record: dict[str, Any],
        operation: str,
        context: WriteContext,
        validate: Callable[[dict[str, Any]], None] | None = None,
    ) -> tuple[dict[str, Any], bool]:
        self._require_table(table)
        context.validate()
        if table == "audit_log":
            raise StateError("OPERATION_NOT_ALLOWED", "audit_log is append-only and internal")
        if validate:
            validate(record)

        payload_hash = _stable_hash({"table": table, "record_id": record_id, "record": record, "operation": operation})
        prior = self._idempotency.get(context.request_id)
        if prior:
            prior_hash, prior_result = prior
            if prior_hash != payload_hash:
                raise StateError("IDEMPOTENCY_CONFLICT", "request_id was already used for a different write")
            return copy.deepcopy(prior_result), True

        before = self.read(table, record_id)
        if table in IMMUTABLE_TABLES and before is not None:
            raise StateError("IMMUTABLE_RECORD", f"{table} records cannot be overwritten")

        stored = copy.deepcopy(record)
        self.tables[table][record_id] = stored
        result = {"record": copy.deepcopy(stored), "deduplicated": False, "audit_id": context.audit_id}
        self._append_audit(
            context=context,
            operation=operation,
            table=table,
            record_id=record_id,
            before=before,
            after=stored,
            success=True,
        )
        self._idempotency[context.request_id] = (payload_hash, result)
        return result, False

    def record_failure(self, *, operation: str, context: WriteContext, error: StateError) -> None:
        context.validate()
        if context.audit_id in self.tables["audit_log"]:
            return
        self.tables["audit_log"][context.audit_id] = {
            "audit_id": context.audit_id,
            "request_id": context.request_id,
            "actor": context.actor,
            "operation": operation,
            "table": None,
            "record_id": None,
            "before_hash": None,
            "after_hash": None,
            "success": False,
            "error": error.as_dict(),
            "user_confirmed": context.user_confirmed,
            "rollback_ref": None,
            "created_at": utc_now(),
        }

    def delete(self, *, table: str, record_id: str, context: WriteContext, backup_ref: str | None) -> None:
        self._require_table(table)
        context.validate()
        if table in IMMUTABLE_TABLES:
            raise StateError("IMMUTABLE_RECORD", f"{table} records cannot be deleted")
        if not context.user_confirmed or not backup_ref:
            raise StateError("CONFIRMATION_AND_BACKUP_REQUIRED", "deletion requires confirmation and a backup reference")
        before = self.read(table, record_id)
        if before is None:
            raise StateError("NOT_FOUND", f"{table}/{record_id} not found")
        del self.tables[table][record_id]
        self._append_audit(
            context=context,
            operation="delete",
            table=table,
            record_id=record_id,
            before=before,
            after=None,
            success=True,
            rollback_ref=backup_ref,
        )

    def snapshot(self) -> dict[str, list[dict[str, Any]]]:
        return {table: self.list(table) for table in TABLES}

    def restore_snapshot(self, snapshot: dict[str, list[dict[str, Any]]], *, context: WriteContext, rollback_ref: str) -> None:
        context.validate()
        if not context.user_confirmed:
            raise StateError("CONFIRMATION_AND_BACKUP_REQUIRED", "restore requires confirmation and a current backup")
        if set(snapshot) != set(TABLES):
            raise StateError("VALIDATION_ERROR", "restore snapshot must contain exactly the allowlisted tables")
        restored: dict[str, dict[str, dict[str, Any]]] = {name: {} for name in TABLES}
        for table, rows in snapshot.items():
            primary_key = PRIMARY_KEYS[table]
            for row in rows:
                record_id = row.get(primary_key)
                if not isinstance(record_id, str) or not record_id:
                    raise StateError("VALIDATION_ERROR", f"{table} restore row lacks {primary_key}")
                if record_id in restored[table]:
                    raise StateError("VALIDATION_ERROR", f"duplicate {table} primary key: {record_id}")
                restored[table][record_id] = copy.deepcopy(row)
        if context.audit_id in restored["audit_log"]:
            raise StateError("AUDIT_ID_CONFLICT", "restore audit_id already exists in backup")

        before = self.snapshot()
        self.tables = restored
        self._idempotency = {}
        for audit in self.tables["audit_log"].values():
            if (
                not audit.get("success")
                or audit.get("table") not in self.tables
                or not audit.get("record_id")
            ):
                continue
            record = self.tables[audit["table"]].get(audit["record_id"])
            if record is None or _stable_hash(record) != audit.get("after_hash"):
                continue
            fingerprint = _stable_hash({
                "table": audit["table"], "record_id": audit["record_id"], "record": record,
                "operation": audit["operation"],
            })
            self._idempotency[audit["request_id"]] = (
                fingerprint,
                {"record": copy.deepcopy(record), "deduplicated": False, "audit_id": audit["audit_id"]},
            )
        self._append_audit(
            context=context, operation="restore_backup", table="system", record_id="all",
            before=before, after=snapshot, success=True, rollback_ref=rollback_ref,
        )

    def _append_audit(
        self,
        *,
        context: WriteContext,
        operation: str,
        table: str,
        record_id: str,
        before: Any,
        after: Any,
        success: bool,
        rollback_ref: str | None = None,
    ) -> None:
        if context.audit_id in self.tables["audit_log"]:
            raise StateError("AUDIT_ID_CONFLICT", "audit_id must be unique")
        self.tables["audit_log"][context.audit_id] = {
            "audit_id": context.audit_id,
            "request_id": context.request_id,
            "actor": context.actor,
            "operation": operation,
            "table": table,
            "record_id": record_id,
            "before_hash": _stable_hash(before) if before is not None else None,
            "after_hash": _stable_hash(after) if after is not None else None,
            "success": success,
            "error": None,
            "user_confirmed": context.user_confirmed,
            "rollback_ref": rollback_ref,
            "created_at": utc_now(),
        }

    def _require_table(self, table: str) -> None:
        if table not in self.tables:
            raise StateError("OPERATION_NOT_ALLOWED", f"table is not allowlisted: {table}")
