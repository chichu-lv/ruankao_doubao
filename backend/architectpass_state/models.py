from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from .errors import StateError


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class WriteContext:
    request_id: str
    audit_id: str
    actor: str
    user_confirmed: bool = False

    def validate(self) -> None:
        for field_name in ("request_id", "audit_id", "actor"):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise StateError("INVALID_WRITE_CONTEXT", f"{field_name} is required")


def response(*, data: Any = None, audit_id: str | None = None) -> dict[str, Any]:
    return {"status": "ok", "data": data, "error": None, "audit_id": audit_id}

