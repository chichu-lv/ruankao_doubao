from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any

from .validation import EVIDENCE_MAX_LEVEL


def derive_mastery(evidence: list[dict[str, Any]], topic_id: str) -> dict[str, Any]:
    """Derive an explainable 0-5 state without replacing raw evidence."""
    relevant = [item for item in evidence if item["topic_id"] == topic_id]
    if not relevant:
        return {
            "topic_id": topic_id,
            "level_0_to_5": 0,
            "confidence": 0.0,
            "last_verified_at": None,
            "next_review_at": None,
            "risk_flags": ["NO_RELIABLE_EVIDENCE"],
            "derivation": {"evidence_ids": [], "rule_version": "mastery-v1"},
        }

    by_level: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for item in relevant:
        ceiling = EVIDENCE_MAX_LEVEL[item["evidence_type"]]
        if item["score"] >= 0.6:
            by_level[ceiling].append(item)

    eligible_levels = []
    for candidate, items in by_level.items():
        if candidate == 3:
            items = [item for item in items if float(item["confidence"]) >= 0.6]
        minimum_count = 2 if candidate == 3 else 1
        if len(items) >= minimum_count:
            eligible_levels.append(candidate)
    level = max(eligible_levels, default=0)
    supporting = by_level.get(level, [])
    weighted = [float(item["score"]) * float(item["confidence"]) for item in supporting]
    confidence = round(sum(weighted) / len(weighted), 4) if weighted else 0.0
    last_verified_at = max((item["created_at"] for item in relevant), default=None)
    risk_flags: list[str] = []
    if any(float(item["confidence"]) < 0.6 for item in relevant):
        risk_flags.append("LOW_CONFIDENCE_EVIDENCE")
    if any(EVIDENCE_MAX_LEVEL[item["evidence_type"]] == 3 for item in relevant) and 3 not in eligible_levels:
        risk_flags.append("INSUFFICIENT_CHOICE_REPETITION")

    interval_days = (1, 1, 3, 7, 14, 30)[level]
    base = datetime.fromisoformat(last_verified_at.replace("Z", "+00:00"))
    next_review = (base + timedelta(days=interval_days)).astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    return {
        "topic_id": topic_id,
        "level_0_to_5": level,
        "confidence": confidence,
        "last_verified_at": last_verified_at,
        "next_review_at": next_review,
        "risk_flags": risk_flags,
        "derivation": {
            "evidence_ids": sorted(item["evidence_id"] for item in relevant),
            "rule_version": "mastery-v1",
        },
    }
