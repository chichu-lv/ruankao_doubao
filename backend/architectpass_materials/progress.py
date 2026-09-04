from __future__ import annotations

from typing import Any

from .errors import MaterialError


def next_review_action(
    observation: dict[str, Any],
    *,
    weak_ranges: tuple[tuple[float, float], ...] = (),
) -> dict[str, Any]:
    """Choose diagnosis or bounded rewatch without equating playback to mastery."""
    if observation.get("status") != "played_unchecked":
        raise MaterialError("INVALID_VIDEO_PROGRESS", "video observation must remain played_unchecked before evidence")
    watched_until = float(observation.get("watched_until_seconds", -1))
    duration = float(observation.get("duration_seconds", 0))
    if watched_until < 0 or duration <= 0 or watched_until > duration:
        raise MaterialError("INVALID_VIDEO_PROGRESS", "video progress is outside its duration")
    if weak_ranges:
        normalized: list[dict[str, float]] = []
        for start, end in weak_ranges:
            if start < 0 or end <= start or end > watched_until:
                raise MaterialError("INVALID_REWATCH_RANGE", "rewatch ranges must be inside the watched portion")
            normalized.append({"start_seconds": start, "end_seconds": end})
        return {
            "action": "targeted_rewatch",
            "ranges": normalized,
            "restart_from_beginning": False,
            "mastery_changed": False,
            "next_evidence": "practice_or_recall",
        }
    return {
        "action": "diagnostic",
        "scope": "watched_portion",
        "restart_from_beginning": False,
        "mastery_changed": False,
        "next_evidence": "recall_then_practice",
    }
