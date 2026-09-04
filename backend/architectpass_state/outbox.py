from __future__ import annotations

import copy
import hashlib
import json
import os
from collections.abc import Callable
from pathlib import Path
from typing import Any

from .errors import StateError
from .models import WriteContext


OUTBOX_SCHEMA_VERSION = 1
OUTBOX_WRITE_OPERATIONS = frozenset({
    "update_profile",
    "record_study_event",
    "upsert_topic",
    "upsert_resource",
    "upsert_resource_segment",
    "update_video_progress",
    "record_practice_attempt",
    "record_mastery_evidence",
    "recompute_topic_state",
    "schedule_review",
    "record_case_attempt",
    "record_essay_attempt",
    "finish_session",
})


class OfflineOutbox:
    """Legacy in-process test helper; deployments should use PersistentOfflineOutbox."""

    def __init__(self) -> None:
        self._pending: dict[str, dict[str, Any]] = {}

    def enqueue(self, request_id: str, operation: str, payload: dict[str, Any]) -> None:
        self._pending.setdefault(request_id, {"request_id": request_id, "operation": operation, "payload": copy.deepcopy(payload)})

    def replay(self, sender: Callable[[dict[str, Any]], Any]) -> list[Any]:
        results = []
        for request_id in list(self._pending):
            item = self._pending[request_id]
            result = sender(copy.deepcopy(item))
            results.append(result)
            if isinstance(result, dict) and result.get("status") == "ok":
                del self._pending[request_id]
        return results

    def pending(self) -> list[dict[str, Any]]:
        return copy.deepcopy(list(self._pending.values()))


class PersistentOfflineOutbox:
    """Crash-safe local outbox restricted to one caller-authorized directory."""

    def __init__(self, root: Path, filename: str = "architectpass-outbox.json") -> None:
        self.path = _safe_outbox_path(root, filename)
        self._pending = self._load()

    def enqueue(
        self,
        operation: str,
        payload: dict[str, Any],
        context: WriteContext,
    ) -> dict[str, Any]:
        context.validate()
        if operation not in OUTBOX_WRITE_OPERATIONS:
            raise StateError("OPERATION_NOT_ALLOWED", f"outbox operation is not allowlisted: {operation}")
        item = {
            "request_id": context.request_id,
            "audit_id": context.audit_id,
            "actor": context.actor,
            "operation": operation,
            "payload": copy.deepcopy(payload),
        }
        fingerprint = _hash(item)
        existing = self._pending.get(context.request_id)
        if existing is not None:
            if existing["fingerprint"] != fingerprint:
                raise StateError("IDEMPOTENCY_CONFLICT", "request ID was reused for another offline write")
            return {"queued": True, "deduplicated": True, "request_id": context.request_id}
        self._pending[context.request_id] = {**item, "fingerprint": fingerprint}
        self._persist()
        return {"queued": True, "deduplicated": False, "request_id": context.request_id}

    def replay(self, sender: Callable[[dict[str, Any]], Any]) -> list[Any]:
        results: list[Any] = []
        for request_id in list(self._pending):
            item = copy.deepcopy(self._pending[request_id])
            item.pop("fingerprint", None)
            result = sender(item)
            results.append(result)
            if isinstance(result, dict) and result.get("status") == "ok":
                del self._pending[request_id]
                self._persist()
        return results

    def pending(self) -> list[dict[str, Any]]:
        result = copy.deepcopy(list(self._pending.values()))
        for item in result:
            item.pop("fingerprint", None)
        return result

    def _load(self) -> dict[str, dict[str, Any]]:
        if not self.path.exists():
            return {}
        try:
            document = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise StateError("OUTBOX_CORRUPT", "offline outbox cannot be read") from error
        if document.get("schema_version") != OUTBOX_SCHEMA_VERSION:
            raise StateError("UNSUPPORTED_SCHEMA_VERSION", "offline outbox schema version is not supported")
        pending = document.get("pending")
        if not isinstance(pending, list) or document.get("sha256") != _hash(pending):
            raise StateError("OUTBOX_CHECKSUM_MISMATCH", "offline outbox checksum does not match its contents")
        loaded: dict[str, dict[str, Any]] = {}
        for item in pending:
            if not isinstance(item, dict) or not isinstance(item.get("request_id"), str):
                raise StateError("OUTBOX_CORRUPT", "offline outbox contains an invalid item")
            if item.get("operation") not in OUTBOX_WRITE_OPERATIONS:
                raise StateError("OPERATION_NOT_ALLOWED", "offline outbox contains a non-allowlisted operation")
            expected = _hash({key: value for key, value in item.items() if key != "fingerprint"})
            if item.get("fingerprint") != expected or item["request_id"] in loaded:
                raise StateError("OUTBOX_CHECKSUM_MISMATCH", "offline outbox item integrity check failed")
            loaded[item["request_id"]] = copy.deepcopy(item)
        return loaded

    def _persist(self) -> None:
        pending = list(self._pending.values())
        document = {
            "schema_version": OUTBOX_SCHEMA_VERSION,
            "sha256": _hash(pending),
            "pending": pending,
        }
        temporary = self.path.with_name(f".{self.path.name}.tmp")
        encoded = json.dumps(document, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        try:
            temporary.write_text(encoded, encoding="utf-8")
            os.chmod(temporary, 0o600)
            temporary.replace(self.path)
        except OSError as error:
            raise StateError("OUTBOX_PERSIST_FAILED", "offline outbox could not be persisted") from error


def _safe_outbox_path(root: Path, filename: str) -> Path:
    if not filename.endswith(".json") or Path(filename).name != filename:
        raise StateError("PATH_NOT_ALLOWED", "outbox filename must be a plain .json filename")
    resolved_root = root.resolve()
    if not resolved_root.is_dir():
        raise StateError("PATH_NOT_ALLOWED", "allowlisted outbox directory must already exist")
    target = (resolved_root / filename).resolve()
    if target.parent != resolved_root:
        raise StateError("PATH_NOT_ALLOWED", "outbox target must stay inside the allowlisted directory")
    return target


def _hash(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()
