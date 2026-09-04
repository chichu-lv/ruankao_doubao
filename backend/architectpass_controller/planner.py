from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .errors import ControllerError


FACTOR_NAMES = (
    "syllabus_importance",
    "weakness",
    "due_factor",
    "forgetting_risk",
    "cross_subject_value",
    "recent_error_severity",
)
SUBJECTS = frozenset({"综合知识", "案例分析", "论文"})


@dataclass(frozen=True)
class PlanGenerator:
    """Generate a bounded and explainable plan from already-observed state."""

    minimum_reserve_minutes: int = 5
    maximum_reserve_minutes: int = 10

    def generate(
        self,
        *,
        state_snapshot: dict[str, Any],
        candidates: list[dict[str, Any]],
        available_minutes: int,
        energy: str,
    ) -> dict[str, Any]:
        if not state_snapshot.get("observed_at"):
            raise ControllerError("STATE_NOT_OBSERVED", "a timestamped state snapshot is required before planning")
        if not isinstance(available_minutes, int) or available_minutes < 10:
            raise ControllerError("INVALID_TIME_BUDGET", "available_minutes must be an integer of at least 10")
        if energy not in {"low", "medium", "high"}:
            raise ControllerError("INVALID_ENERGY", "energy must be low, medium or high")

        reserve = min(self.maximum_reserve_minutes, max(self.minimum_reserve_minutes, available_minutes // 10))
        work_budget = available_minutes - reserve
        ranked = [self._score_candidate(item, state_snapshot, energy) for item in candidates]
        ranked.sort(key=lambda item: (-item["priority_score"], item["estimated_minutes"], item["candidate_id"]))

        selected: list[dict[str, Any]] = []
        used = 0
        for item in ranked:
            duration = item["estimated_minutes"]
            if used + duration <= work_budget:
                selected.append(item)
                used += duration

        if not selected and ranked:
            fitting = [item for item in ranked if item["estimated_minutes"] <= work_budget]
            if fitting:
                selected = [fitting[0]]
                used = fitting[0]["estimated_minutes"]

        selected.append({
            "candidate_id": "checkpoint",
            "subject": "跨科",
            "action": "复盘并写入状态与 checkpoint",
            "completion_standard": "完成本次证据、到期复习和恢复上下文写入",
            "estimated_minutes": reserve,
            "priority_score": None,
            "priority_explanation": {"reserved": True},
        })
        return {
            "available_minutes": available_minutes,
            "energy": energy,
            "load_mode": "reduced" if energy == "low" else "normal",
            "items": selected,
            "planned_minutes": used + reserve,
            "unallocated_minutes": available_minutes - used - reserve,
            "state_observed_at": state_snapshot["observed_at"],
            "ranking_rule": "product(normalized_factors × subject_balance × energy_fit) / estimated_minutes",
        }

    def _score_candidate(
        self, item: dict[str, Any], state_snapshot: dict[str, Any], energy: str
    ) -> dict[str, Any]:
        required = {"candidate_id", "subject", "estimated_minutes", "action", "completion_standard", *FACTOR_NAMES}
        missing = sorted(name for name in required if item.get(name) in (None, ""))
        if missing:
            raise ControllerError("INVALID_PLAN_CANDIDATE", f"candidate missing fields: {', '.join(missing)}")
        if item["subject"] not in SUBJECTS:
            raise ControllerError("INVALID_PLAN_CANDIDATE", "subject must be 综合知识, 案例分析 or 论文")
        minutes = item["estimated_minutes"]
        if not isinstance(minutes, int) or minutes <= 0:
            raise ControllerError("INVALID_PLAN_CANDIDATE", "estimated_minutes must be a positive integer")

        factors: dict[str, float] = {}
        for name in FACTOR_NAMES:
            value = item[name]
            if not isinstance(value, (int, float)) or not 0 <= value <= 1:
                raise ControllerError("INVALID_PLAN_CANDIDATE", f"{name} must be normalized to 0..1")
            factors[name] = float(value)

        subject_ratios = state_snapshot.get("subject_ratios_14d", {})
        days_since = state_snapshot.get("days_since_subject", {}).get(item["subject"], 0)
        ratio = float(subject_ratios.get(item["subject"], 0))
        subject_balance = 1.5 if days_since >= 7 or ratio < 0.15 else 1.0
        load = item.get("cognitive_load", "medium")
        energy_fit = 0.45 if energy == "low" and load == "high" else 1.0

        product = 1.0
        for value in factors.values():
            product *= value
        base_score = product / minutes
        score = round(base_score * subject_balance * energy_fit, 8)
        result = dict(item)
        result["priority_score"] = score
        result["priority_explanation"] = {
            "normalized_factors": factors,
            "base_formula_score": round(base_score, 8),
            "subject_balance_multiplier": subject_balance,
            "energy_fit_multiplier": energy_fit,
            "estimated_minutes_divisor": minutes,
            "due_or_high_risk": factors["due_factor"] >= 0.8 or factors["recent_error_severity"] >= 0.8,
        }
        return result
