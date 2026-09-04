from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

from .errors import MaterialError
from .models import MaterialContext, ResourceRecord, Segment
from .paths import safe_output


class MaterialCatalog:
    """JSON reference catalog; production state metadata is synchronized to Feishu."""

    def __init__(self) -> None:
        self.resources: dict[str, ResourceRecord] = {}
        self.by_checksum: dict[str, str] = {}
        self.segments: dict[str, Segment] = {}
        self.requests: dict[str, tuple[str, dict[str, Any]]] = {}
        self.audits: list[dict[str, Any]] = []

    def commit(
        self,
        *,
        resource: ResourceRecord,
        segments: list[Segment],
        context: MaterialContext,
    ) -> tuple[dict[str, Any], bool]:
        context.validate()
        resource_for_fingerprint = resource.as_dict()
        for transient in ("created_at", "request_id", "audit_id"):
            resource_for_fingerprint.pop(transient, None)
        payload = {"resource": resource_for_fingerprint, "segments": [item.as_dict() for item in segments]}
        fingerprint = _hash_json(payload)
        prior = self.requests.get(context.request_id)
        if prior:
            if prior[0] != fingerprint:
                raise MaterialError("IDEMPOTENCY_CONFLICT", "request_id was reused with different material content")
            return copy.deepcopy(prior[1]), True
        if any(item["audit_id"] == context.audit_id for item in self.audits):
            raise MaterialError("AUDIT_ID_CONFLICT", "audit_id must be unique")
        if resource.checksum in self.by_checksum:
            existing_id = self.by_checksum[resource.checksum]
            result = {"resource": self.resources[existing_id].as_dict(), "duplicate_of": existing_id}
            self.requests[context.request_id] = (fingerprint, result)
            self._audit(context, "deduplicate", existing_id, True, None)
            return copy.deepcopy(result), True
        self.resources[resource.resource_id] = copy.deepcopy(resource)
        self.by_checksum[resource.checksum] = resource.resource_id
        for segment in segments:
            self.segments[segment.segment_id] = copy.deepcopy(segment)
        result = {"resource": resource.as_dict(), "segment_count": len(segments), "duplicate_of": None}
        self.requests[context.request_id] = (fingerprint, result)
        self._audit(context, "import", resource.resource_id, True, None)
        return copy.deepcopy(result), False

    def export(self, directory: Path, filename: str, context: MaterialContext) -> Path:
        context.validate()
        directory.mkdir(parents=True, exist_ok=True)
        target = safe_output(directory, filename)
        payload = {
            "write_context": {
                "request_id": context.request_id,
                "audit_id": context.audit_id,
                "actor": context.actor,
            },
            "resources": [item.as_dict() for item in self.resources.values()],
            "segments": [item.as_dict() for item in self.segments.values()],
            "audits": copy.deepcopy(self.audits),
        }
        serialized = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        if target.exists():
            existing = target.read_text(encoding="utf-8")
            if existing == serialized:
                return target
            raise MaterialError("CATALOG_EXPORT_CONFLICT", "catalog export target already exists with different content")
        target.write_text(serialized, encoding="utf-8")
        return target

    def _audit(self, context: MaterialContext, operation: str, resource_id: str, success: bool, error: str | None) -> None:
        self.audits.append({
            "request_id": context.request_id, "audit_id": context.audit_id, "actor": context.actor,
            "operation": operation, "resource_id": resource_id, "success": success, "error": error,
        })


def _hash_json(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
