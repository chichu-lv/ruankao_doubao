from __future__ import annotations

import hashlib
import re
from pathlib import Path

from .errors import MaterialError
from .models import Segment


TIMING = re.compile(r"(?P<start>\d{2}:\d{2}:\d{2}[,.]\d{3})\s+-->\s+(?P<end>\d{2}:\d{2}:\d{2}[,.]\d{3})")


def parse_subtitle(
    path: Path,
    resource_id: str,
    video_name: str,
    *,
    time_offset_seconds: float = 0,
    video_source_id: str | None = None,
    confidence: float = 1.0,
) -> list[Segment]:
    if time_offset_seconds < 0:
        raise MaterialError("INVALID_SUBTITLE_OFFSET", "subtitle time offset must be non-negative")
    if confidence < 0 or confidence > 1:
        raise MaterialError("INVALID_TRANSCRIPT_CONFIDENCE", "transcript confidence must be between 0 and 1")
    text = path.read_text(encoding="utf-8-sig")
    blocks = re.split(r"\n\s*\n", text.replace("\r\n", "\n").strip())
    segments: list[Segment] = []
    for block in blocks:
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        timing_index = next((index for index, line in enumerate(lines) if TIMING.search(line)), None)
        if timing_index is None:
            continue
        match = TIMING.search(lines[timing_index])
        assert match is not None
        body = " ".join(lines[timing_index + 1 :]).strip()
        if not body:
            continue
        start = _seconds(match.group("start")) + time_offset_seconds
        end = _seconds(match.group("end")) + time_offset_seconds
        if end <= start:
            raise MaterialError("INVALID_SUBTITLE_TIMING", "subtitle end must be after start")
        segment_id = hashlib.sha256(f"{resource_id}:{start:.3f}:{end:.3f}:{body}".encode()).hexdigest()[:24]
        citation_resource_id = video_source_id or resource_id
        segments.append(Segment(
            segment_id=segment_id,
            resource_id=resource_id,
            filename=video_name,
            section=None,
            text=body,
            confidence=confidence,
            citation_anchor=f"video:{citation_resource_id}#t={start:.3f},{end:.3f}",
            open_target=f"{video_name}@{_clock(start)}-{_clock(end)}",
            start_seconds=start,
            end_seconds=end,
        ))
    if not segments:
        raise MaterialError("SUBTITLE_PARSE_FAILED", "no timestamped subtitle segments found")
    return segments


def _seconds(value: str) -> float:
    hours, minutes, seconds = value.replace(",", ".").split(":")
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)


def _clock(value: float) -> str:
    total = int(value)
    return f"{total // 3600:02d}:{(total % 3600) // 60:02d}:{total % 60:02d}"
