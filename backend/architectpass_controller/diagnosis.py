from __future__ import annotations

from collections import Counter
from typing import Any


ERROR_MEANINGS = {
    "K": "knowledge_gap",
    "C": "concept_confusion",
    "M": "memory_decay",
    "A": "case_transfer_gap",
    "Q": "question_reading_gap",
    "T": "time_management_gap",
    "E": "expression_gap",
    "G": "low_confidence_guess_risk",
}


def diagnose(snapshot: dict[str, Any]) -> dict[str, Any]:
    errors = snapshot.get("recent_error_types", [])
    counts = Counter(code for code in errors if code in ERROR_MEANINGS)
    ranked = sorted(counts, key=lambda code: (-counts[code], code))
    bottlenecks = [
        {"error_type": code, "diagnosis": ERROR_MEANINGS[code], "count": counts[code]}
        for code in ranked
    ]
    if snapshot.get("essay_fact_gaps"):
        bottlenecks.append({"error_type": None, "diagnosis": "essay_material_shortage", "count": len(snapshot["essay_fact_gaps"])})
    return {
        "bottlenecks": bottlenecks,
        "highest_pass_bottleneck": bottlenecks[0] if bottlenecks else None,
        "based_on": {
            "observed_at": snapshot.get("observed_at"),
            "windows": ["7d", "14d", "30d"],
            "raw_error_count": len(errors),
        },
    }
