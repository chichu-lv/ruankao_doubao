from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class MaterialContext:
    request_id: str
    audit_id: str
    actor: str

    def validate(self) -> None:
        if not all(isinstance(value, str) and value.strip() for value in (self.request_id, self.audit_id, self.actor)):
            from .errors import MaterialError
            raise MaterialError("INVALID_WRITE_CONTEXT", "request_id, audit_id and actor are required")


@dataclass
class ResourceRecord:
    resource_id: str
    checksum: str
    filename: str
    media_type: str
    source_path: str
    copyright_scope: str
    processing_status: str
    request_id: str
    audit_id: str
    created_at: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)

@dataclass
class Segment:
    segment_id: str
    resource_id: str
    filename: str
    section: str | None
    text: str
    confidence: float
    citation_anchor: str
    open_target: str
    page: int | None = None
    start_seconds: float | None = None
    end_seconds: float | None = None
    ocr: bool = False

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)
