from __future__ import annotations

import re
from typing import Any

from .errors import ControllerError


class CaseCoach:
    """Grade only a user's already-submitted answer against sourced rubric points."""

    def grade(
        self,
        *,
        submission_state: str,
        user_answer: str,
        rubric: list[dict[str, Any]],
    ) -> dict[str, Any]:
        if submission_state != "submitted_by_user" or not user_answer.strip():
            raise ControllerError(
                "USER_ANSWER_REQUIRED",
                "case grading is unavailable until the user has submitted a non-empty answer",
            )
        if not rubric:
            raise ControllerError("INVALID_RUBRIC", "a sourced case rubric is required")

        covered: list[dict[str, Any]] = []
        missing: list[dict[str, Any]] = []
        for point in rubric:
            if not point.get("point_id") or not point.get("source_ref"):
                raise ControllerError("UNTRACEABLE_RUBRIC", "every rubric point needs point_id and source_ref")
            keywords = point.get("match_terms", [])
            if not keywords or not all(isinstance(term, str) and term for term in keywords):
                raise ControllerError("INVALID_RUBRIC", "every rubric point needs non-empty match_terms")
            matched = [term for term in keywords if term.lower() in user_answer.lower()]
            result = {
                "point_id": point["point_id"],
                "label": point.get("label", point["point_id"]),
                "source_ref": point["source_ref"],
                "matched_terms": matched,
            }
            (covered if matched else missing).append(result)

        sentences = [item.strip() for item in re.split(r"[。！？\n]+", user_answer) if item.strip()]
        relevant_terms = {term.lower() for point in rubric for term in point["match_terms"]}
        redundant = [sentence for sentence in sentences if not any(term in sentence.lower() for term in relevant_terms)]
        expression: list[str] = []
        if any(len(sentence) > 80 for sentence in sentences):
            expression.append("LONG_SENTENCE")
        if len(sentences) > 1 and not re.search(r"(^|[。\n])\s*[一二三四五六七八九十123456789][、.．]", user_answer):
            expression.append("STRUCTURE_COULD_BE_CLEARER")

        return {
            "gate": "post_submission_only",
            "question_intent": [point.get("intent", point.get("label", point["point_id"])) for point in rubric],
            "covered": covered,
            "missing": missing,
            "redundant": redundant,
            "expression": expression,
            "concise_rewrite_guidance": "仅重组用户已覆盖得分点；不得用标准答案覆盖用户思考过程",
            "next_transfer_practice": "选择同一考点的不同场景题，由用户先完整作答",
            "score_ratio": round(len(covered) / len(rubric), 4),
            "source_complete": True,
            "analysis_source": "submitted_user_answer",
        }
