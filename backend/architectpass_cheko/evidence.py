from __future__ import annotations

from typing import Any

from .errors import ChekoError


def build_state_writes(imported_task: dict[str, Any], *, review_due_at: str) -> list[dict[str, Any]]:
    """Translate item-level submitted metadata into allowlisted state writes."""
    if imported_task.get("status") != "IMPORTED":
        raise ChekoError("RESULT_NOT_IMPORTED", "state writes require an imported result")
    if imported_task.get("paper_type") != "choice":
        raise ChekoError("UNSUPPORTED_RESULT_MAPPING", "case and essay results require their dedicated coaches")
    result = imported_task["imported_result"]
    writes: list[dict[str, Any]] = []
    for item in result.get("items", []):
        source_id = f"cheko:{result['cheko_result_id']}:{item['visible_item_id']}"
        attempt_id = f"{imported_task['task_id']}:{item['visible_item_id']}"
        source_evidence = {
            "cheko_result_id": result["cheko_result_id"],
            "visible_item_id": item["visible_item_id"],
            "import_method": result["import_method"],
            "ui_contract_version": result["ui_contract_version"],
        }
        writes.append({
            "operation": "record_practice_attempt",
            "payload_name": "attempt",
            "payload": {
                "attempt_id": attempt_id,
                "platform": "cheko",
                "question_or_set_id": item["visible_item_id"],
                "topic_ids": [item["topic_id"]],
                "correct": item["correct"],
                "confidence": item["confidence"],
                "duration": item["duration_seconds"],
                "error_type": item["error_type"],
                "source_evidence": source_evidence,
                "submitted_at": result["observed_at"],
            },
        })
        writes.append({
            "operation": "record_mastery_evidence",
            "payload_name": "evidence",
            "payload": {
                "evidence_id": f"evidence:{attempt_id}",
                "topic_id": item["topic_id"],
                "evidence_type": "choice_timed",
                "score": 1.0 if item["correct"] else 0.0,
                "confidence": item["confidence"],
                "difficulty": None,
                "timed": True,
                "source_id": source_id,
                "created_at": result["observed_at"],
                "expires_or_decay_rule": "mastery-v1",
            },
        })
        if item["review_required"]:
            writes.append({
                "operation": "schedule_review",
                "payload_name": "review",
                "payload": {
                    "review_id": f"review:{attempt_id}",
                    "topic_id": item["topic_id"],
                    "due_at": review_due_at,
                    "review_type": "cheko_result",
                    "priority": 3 if not item["correct"] else 2,
                    "reason": item["error_type"],
                    "status": "pending",
                },
            })
    return writes
