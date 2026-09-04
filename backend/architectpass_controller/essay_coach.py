from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .errors import ControllerError


REQUIRED_FACT_CATEGORIES = frozenset({
    "project_background",
    "business_goal",
    "role",
    "responsibilities",
    "scale_constraints_metrics",
    "overall_architecture",
    "quality_attributes",
    "technical_decisions",
    "alternatives_tradeoffs",
    "costs_risks_failures",
    "implementation",
    "result",
    "applicable_topics",
})
WORKFLOW = (
    "topic",
    "facts",
    "outline",
    "partial_paragraph",
    "full_timed",
    "grading",
    "revision",
    "spaced_rewrite",
)


@dataclass
class EssayFactBase:
    facts: dict[str, dict[str, Any]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        records = list(self.facts.values())
        self.facts = {}
        for fact in records:
            self._validate_and_load(fact)

    def _validate_and_load(self, fact: dict[str, Any]) -> None:
        required = {"fact_id", "category", "summary", "source_ref", "confirmed_by_user", "redacted"}
        missing = sorted(name for name in required if fact.get(name) in (None, ""))
        if missing:
            raise ControllerError("INVALID_ESSAY_FACT", f"fact missing fields: {', '.join(missing)}")
        if fact["category"] not in REQUIRED_FACT_CATEGORIES:
            raise ControllerError("INVALID_ESSAY_FACT", "unsupported essay fact category")
        if fact["confirmed_by_user"] is not True:
            raise ControllerError("UNCONFIRMED_PROJECT_FACT", "project facts must be confirmed by the user")
        if fact["redacted"] is not True:
            raise ControllerError("SENSITIVE_FACT_NOT_REDACTED", "project facts must be redacted before storage")
        self.facts[fact["fact_id"]] = dict(fact)

    def completeness(self) -> dict[str, Any]:
        present = {fact["category"] for fact in self.facts.values()}
        missing = sorted(REQUIRED_FACT_CATEGORIES - present)
        return {"ready": not missing, "present_categories": sorted(present), "missing_categories": missing}


class EssayCoach:
    def __init__(self, fact_base: EssayFactBase) -> None:
        self.fact_base = fact_base

    def make_outline(self, *, topic: str, fact_ids: list[str]) -> dict[str, Any]:
        if not topic.strip():
            raise ControllerError("INVALID_ESSAY_TOPIC", "essay topic is required")
        missing_ids = sorted(set(fact_ids) - set(self.fact_base.facts))
        if missing_ids:
            raise ControllerError("UNSUPPORTED_PROJECT_FACT", f"unknown fact ids: {', '.join(missing_ids)}")
        completeness = self.fact_base.completeness()
        if not completeness["ready"]:
            return {
                "status": "needs_facts",
                "topic": topic,
                "missing_categories": completeness["missing_categories"],
                "fabrication_allowed": False,
            }
        return {
            "status": "ready",
            "topic": topic,
            "workflow": list(WORKFLOW),
            "outline_slots": [
                {"category": category, "fact_ids": sorted(
                    fact_id for fact_id in fact_ids if self.fact_base.facts[fact_id]["category"] == category
                )}
                for category in sorted(REQUIRED_FACT_CATEGORIES)
            ],
            "fabrication_allowed": False,
        }

    def grade_submission(
        self,
        *,
        text: str,
        version: int,
        duration_minutes: int,
        claim_fact_ids: list[str],
        rubric_scores: dict[str, float],
    ) -> dict[str, Any]:
        if not text.strip() or not isinstance(version, int) or version < 1:
            raise ControllerError("INVALID_ESSAY_SUBMISSION", "non-empty text and positive version are required")
        if not isinstance(duration_minutes, int) or duration_minutes < 0:
            raise ControllerError("INVALID_ESSAY_SUBMISSION", "duration_minutes must be non-negative")
        unsupported = sorted(set(claim_fact_ids) - set(self.fact_base.facts))
        if unsupported:
            raise ControllerError("UNSUPPORTED_PROJECT_FACT", f"claims reference unknown facts: {', '.join(unsupported)}")
        required_dimensions = {"relevance", "structure", "professionalism", "project_specificity", "expression"}
        if set(rubric_scores) != required_dimensions or any(
            not isinstance(value, (int, float)) or not 0 <= value <= 1 for value in rubric_scores.values()
        ):
            raise ControllerError("INVALID_ESSAY_RUBRIC", "all five scoring dimensions must be normalized to 0..1")
        return {
            "version": version,
            "duration_minutes": duration_minutes,
            "word_count": len(text.replace("\n", "").replace(" ", "")),
            "fact_ids": sorted(set(claim_fact_ids)),
            "rubric_scores": dict(rubric_scores),
            "overall_score": round(sum(rubric_scores.values()) / len(rubric_scores), 4),
            "unsupported_fact_count": 0,
        }
