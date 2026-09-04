from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from .catalog import MaterialCatalog
from .errors import MaterialError
from .models import MaterialContext, ResourceRecord
from .paths import resolve_authorized, safe_output
from .pdf import apply_local_ocr, extract_pdf_pages
from .subtitles import parse_subtitle
from .video import probe_video


class MaterialImporter:
    def __init__(self, catalog: MaterialCatalog, authorized_roots: tuple[Path, ...]) -> None:
        self.catalog = catalog
        self.authorized_roots = authorized_roots

    def import_file(
        self,
        path: Path,
        *,
        context: MaterialContext,
        copyright_scope: str,
        video_name: str | None = None,
        subtitle_offset_seconds: float = 0,
        video_source_id: str | None = None,
        transcript_confidence: float = 1.0,
        ocr_pages: tuple[int, ...] = (),
        tessdata_directory: Path | None = None,
    ) -> dict[str, object]:
        context.validate()
        source = resolve_authorized(path, self.authorized_roots)
        if not source.is_file():
            raise MaterialError("NOT_A_FILE", "material source is not a file")
        checksum = _sha256(source)
        resource_id = f"sha256:{checksum}"
        suffix = source.suffix.lower()
        if suffix == ".pdf":
            segments, metadata = extract_pdf_pages(source, resource_id)
            apply_local_ocr(
                source,
                segments,
                ocr_pages,
                tessdata_directory=tessdata_directory,
            )
            metadata["ocr_pages"] = sorted(page for page in ocr_pages)
            media_type = "pdf"
        elif suffix in {".srt", ".vtt"}:
            if not video_name:
                raise MaterialError("VIDEO_NAME_REQUIRED", "subtitle import requires its video filename")
            if video_source_id is not None and not video_source_id.startswith("sha256:"):
                raise MaterialError("INVALID_VIDEO_SOURCE_ID", "video source ID must be a SHA-256 resource ID")
            segments = parse_subtitle(
                source,
                resource_id,
                video_name,
                time_offset_seconds=subtitle_offset_seconds,
                video_source_id=video_source_id,
                confidence=transcript_confidence,
            )
            metadata = {
                "subtitle_format": suffix[1:],
                "segment_count": len(segments),
                "time_offset_seconds": subtitle_offset_seconds,
                "video_source_id": video_source_id,
                "confidence": transcript_confidence,
            }
            media_type = "transcript"
        elif suffix in {".mp4", ".mkv", ".mov", ".webm"}:
            segments = []
            metadata = probe_video(source)
            media_type = "video"
        else:
            raise MaterialError("UNSUPPORTED_MEDIA_TYPE", f"unsupported extension: {suffix or '<none>'}")
        record = ResourceRecord(
            resource_id=resource_id,
            checksum=checksum,
            filename=source.name,
            media_type=media_type,
            source_path=str(source),
            copyright_scope=copyright_scope,
            processing_status="indexed" if segments else "metadata_only",
            request_id=context.request_id,
            audit_id=context.audit_id,
            created_at=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            metadata=metadata,
        )
        result, duplicate = self.catalog.commit(resource=record, segments=segments, context=context)
        return {"status": "ok", "data": result, "error": None, "audit_id": context.audit_id, "deduplicated": duplicate}

    def import_with_quarantine_receipt(
        self,
        path: Path,
        *,
        context: MaterialContext,
        copyright_scope: str,
        quarantine_directory: Path,
        video_name: str | None = None,
        subtitle_offset_seconds: float = 0,
        video_source_id: str | None = None,
        transcript_confidence: float = 1.0,
        ocr_pages: tuple[int, ...] = (),
        tessdata_directory: Path | None = None,
    ) -> dict[str, object]:
        try:
            return self.import_file(
                path,
                context=context,
                copyright_scope=copyright_scope,
                video_name=video_name,
                subtitle_offset_seconds=subtitle_offset_seconds,
                video_source_id=video_source_id,
                transcript_confidence=transcript_confidence,
                ocr_pages=ocr_pages,
                tessdata_directory=tessdata_directory,
            )
        except MaterialError as error:
            quarantine_directory.mkdir(parents=True, exist_ok=True)
            receipt = safe_output(quarantine_directory, f"{context.audit_id}.json")
            payload = {
                "request_id": context.request_id,
                "audit_id": context.audit_id,
                "actor": context.actor,
                "source_filename": path.name,
                "status": "quarantined",
                "error_code": error.code,
                "error_message": error.message,
                "source_moved": False,
                "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            }
            if receipt.exists():
                prior = json.loads(receipt.read_text(encoding="utf-8"))
                stable_keys = ("request_id", "audit_id", "actor", "source_filename", "error_code", "source_moved")
                if any(prior.get(key) != payload.get(key) for key in stable_keys):
                    raise MaterialError(
                        "QUARANTINE_RECEIPT_CONFLICT",
                        "quarantine receipt already exists with different content",
                    ) from error
            else:
                receipt.write_text(
                    json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8",
                )
            return {
                "status": "error", "data": {"quarantine_receipt": str(receipt)},
                "error": {"code": error.code, "message": error.message}, "audit_id": context.audit_id,
            }


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
