from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from .errors import ControllerError


class ReviewScheduler:
    """Build an explainable dynamic schedule from the 1/3/7/14/30-day baseline."""

    def schedule(
        self,
        *,
        topic_id: str,
        verified_at: str,
        score: float,
        confidence: float,
        importance: float,
        recent_error_severity: float,
        exam_date: str,
    ) -> dict[str, Any]:
        for name, value in {
            "score": score,
            "confidence": confidence,
            "importance": importance,
            "recent_error_severity": recent_error_severity,
        }.items():
            if not isinstance(value, (int, float)) or not 0 <= value <= 1:
                raise ControllerError("INVALID_REVIEW_SIGNAL", f"{name} must be normalized to 0..1")
        try:
            base = datetime.fromisoformat(verified_at.replace("Z", "+00:00"))
            exam = datetime.fromisoformat(exam_date).replace(tzinfo=timezone.utc)
        except (AttributeError, TypeError, ValueError) as exc:
            raise ControllerError("INVALID_REVIEW_DATE", "verified_at and exam_date must be ISO dates") from exc

        baseline = [1, 3, 7, 14, 30]
        if score < 0.6 or confidence < 0.6 or recent_error_severity >= 0.8 or importance >= 0.9:
            intervals = baseline
            adjustment = "advanced_for_risk"
        elif score >= 0.85 and confidence >= 0.8 and recent_error_severity < 0.3:
            intervals = [3, 7, 14, 30]
            adjustment = "delayed_after_stable_evidence"
        else:
            intervals = [1, 3, 7, 14, 30]
            adjustment = "baseline"

        due = []
        for index, days in enumerate(intervals, start=1):
            due_at = base + timedelta(days=days)
            if due_at.date() > exam.date():
                continue
            due.append({
                "sequence": index,
                "topic_id": topic_id,
                "interval_days": days,
                "due_at": due_at.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
                "reason": adjustment,
            })
        return {
            "topic_id": topic_id,
            "baseline_days": baseline,
            "adjustment": adjustment,
            "signals": {
                "score": score,
                "confidence": confidence,
                "importance": importance,
                "recent_error_severity": recent_error_severity,
            },
            "reviews": due,
        }
