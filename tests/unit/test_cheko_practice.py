import json
import unittest
from pathlib import Path

from architectpass_cheko import ChekoPracticeService, ChekoUiContract, build_state_writes
from architectpass_state import InMemoryStore, StateService, WriteContext


ROOT = Path(__file__).resolve().parents[2]


def context(number: int) -> WriteContext:
    return WriteContext(f"cheko-req-{number}", f"cheko-audit-{number}", "unit-test")


def task(task_id: str = "practice-1") -> dict:
    return {
        "task_id": task_id,
        "subject": "系统架构设计师",
        "paper_type": "choice",
        "practice_mode": "chapter",
        "target": "数据库系统",
        "question_count": 15,
        "time_limit_minutes": 20,
        "completion_standard": "本人作答并提交15题，逐题记录置信度，提交后再导入结果。",
        "confidence_capture": "per_item",
        "navigation_target": {"name": "chapter_bank", "route": "/?subject=0"},
    }


def result(items: list[dict] | None = None) -> dict:
    return {
        "submission_state": "submitted",
        "import_method": "manual_summary",
        "cheko_result_id": "result-visible-1",
        "observed_at": "2026-09-04T05:10:00Z",
        "ui_contract_version": "cheko-ui-2026-09-04.1",
        "items": items or [
            {
                "visible_item_id": "item-1",
                "topic_id": "database-normalization",
                "correct": True,
                "confidence": 0.9,
                "duration_seconds": 45,
                "error_type": None,
            }
        ],
    }


def reach_awaiting(service: ChekoPracticeService, task_id: str = "practice-1", start: int = 1) -> dict:
    service.invoke("create_task", task=task(task_id), context=context(start))
    service.invoke(
        "prepare_navigation",
        task_id=task_id,
        observed_route="/?subject=0",
        ui_contract_version="cheko-ui-2026-09-04.1",
        context=context(start + 1),
    )
    return service.invoke("enter_awaiting_human", task_id=task_id, context=context(start + 2))


class ChekoPracticeTests(unittest.TestCase):
    def test_task_requires_count_limit_completion_and_allowlisted_route(self) -> None:
        service = ChekoPracticeService()
        created = service.invoke("create_task", task=task(), context=context(1))
        self.assertEqual("CREATED", created["data"]["task"]["status"])
        self.assertEqual(15, created["data"]["task"]["question_count"])
        self.assertEqual(20, created["data"]["task"]["time_limit_minutes"])
        blocked = task("unsafe")
        blocked["navigation_target"]["route"] = "https://example.com/arbitrary"
        result_value = service.invoke("create_task", task=blocked, context=context(2))
        self.assertEqual("NAVIGATION_NOT_ALLOWED", result_value["error"]["code"])
        mismatch = task("route-mismatch")
        mismatch["navigation_target"] = {"name": "error_book", "route": "/?subject=0"}
        result_value = service.invoke("create_task", task=mismatch, context=context(3))
        self.assertEqual("NAVIGATION_NOT_ALLOWED", result_value["error"]["code"])
        invalid_context = WriteContext("", "", "")
        result_value = service.invoke("create_task", task=task("invalid-context"), context=invalid_context)
        self.assertEqual("INVALID_WRITE_CONTEXT", result_value["error"]["code"])

    def test_verified_navigation_enters_awaiting_human_without_answer_content(self) -> None:
        service = ChekoPracticeService()
        awaiting = reach_awaiting(service)
        self.assertEqual("AWAITING_HUMAN", awaiting["data"]["task"]["status"])
        boundary = awaiting["data"]["task"]["human_boundary"]
        self.assertTrue(boundary["user_answers"])
        self.assertTrue(boundary["user_submits"])
        serialized = json.dumps(awaiting, ensure_ascii=False).casefold()
        self.assertNotIn("correct_answer", serialized)
        self.assertNotIn("question_text", serialized)

    def test_navigation_mismatch_fails_without_advancing_state(self) -> None:
        service = ChekoPracticeService()
        service.invoke("create_task", task=task(), context=context(5))
        failed = service.invoke(
            "prepare_navigation",
            task_id="practice-1",
            observed_route="/error_book?subject=0",
            ui_contract_version="cheko-ui-2026-09-04.1",
            context=context(6),
        )
        self.assertEqual("NAVIGATION_MISMATCH", failed["error"]["code"])
        self.assertEqual("CREATED", service.get_task("practice-1")["data"]["status"])
        self.assertFalse(service.audits[-1]["success"])

    def test_pre_submission_result_and_question_content_are_blocked(self) -> None:
        service = ChekoPracticeService()
        reach_awaiting(service, start=10)
        premature = result()
        premature["submission_state"] = "in_progress"
        blocked = service.invoke(
            "import_submitted_result", task_id="practice-1", result=premature, context=context(13)
        )
        self.assertEqual("PRE_SUBMISSION_RESULT_BLOCKED", blocked["error"]["code"])
        leaked = result()
        leaked["items"][0]["question_text"] = "forbidden"
        blocked = service.invoke(
            "import_submitted_result", task_id="practice-1", result=leaked, context=context(14)
        )
        self.assertEqual("QUESTION_CONTENT_NOT_ALLOWED", blocked["error"]["code"])
        unknown = result()
        unknown["raw_html"] = "<html>whole page</html>"
        blocked = service.invoke(
            "import_submitted_result", task_id="practice-1", result=unknown, context=context(15)
        )
        self.assertEqual("FIELD_NOT_ALLOWED", blocked["error"]["code"])
        mismatch = result()
        mismatch["summary"] = {"question_count": 99}
        blocked = service.invoke(
            "import_submitted_result", task_id="practice-1", result=mismatch, context=context(16)
        )
        self.assertEqual("RESULT_TASK_MISMATCH", blocked["error"]["code"])
        self.assertEqual("AWAITING_HUMAN", service.get_task("practice-1")["data"]["status"])

    def test_result_import_requires_awaiting_human(self) -> None:
        service = ChekoPracticeService()
        service.invoke("create_task", task=task(), context=context(20))
        blocked = service.invoke(
            "import_submitted_result", task_id="practice-1", result=result(), context=context(21)
        )
        self.assertEqual("RESULT_NOT_READY", blocked["error"]["code"])

    def test_wrong_and_low_confidence_correct_both_schedule_review(self) -> None:
        service = ChekoPracticeService()
        reach_awaiting(service, start=30)
        imported = service.invoke(
            "import_submitted_result",
            task_id="practice-1",
            result=result([
                {
                    "visible_item_id": "item-wrong",
                    "topic_id": "database-key",
                    "correct": False,
                    "confidence": 0.8,
                    "duration_seconds": 70,
                    "error_type": "K",
                },
                {
                    "visible_item_id": "item-guess",
                    "topic_id": "database-normalization",
                    "correct": True,
                    "confidence": 0.4,
                    "duration_seconds": 30,
                    "error_type": None,
                },
            ]),
            context=context(33),
        )
        imported_task = imported["data"]["task"]
        self.assertEqual(["item-wrong", "item-guess"], imported_task["imported_result"]["review_items"])
        self.assertEqual("G", imported_task["imported_result"]["items"][1]["error_type"])

        writes = build_state_writes(imported_task, review_due_at="2026-09-05T05:10:00Z")
        state_store = InMemoryStore()
        state = StateService(state_store)
        for number, write in enumerate(writes, start=40):
            response = state.invoke(
                write["operation"],
                **{write["payload_name"]: write["payload"]},
                context=context(number),
            )
            self.assertEqual("ok", response["status"])
        self.assertEqual(2, len(state_store.list("practice_attempts")))
        self.assertEqual(2, len(state_store.list("mastery_evidence")))
        self.assertEqual(2, len(state_store.list("review_queue")))
        errors = {item["error_type"] for item in state_store.list("practice_attempts")}
        self.assertEqual({"K", "G"}, errors)
        original = state_store.list("practice_attempts")[0]
        changed = {**original, "correct": not original["correct"], "error_type": None}
        overwrite = state.invoke("record_practice_attempt", attempt=changed, context=context(55))
        self.assertEqual("IMMUTABLE_RECORD", overwrite["error"]["code"])
        polluted = {
            **original,
            "attempt_id": "polluted-attempt",
            "source_evidence": {**original["source_evidence"], "question_text": "blocked"},
        }
        rejected = state.invoke("record_practice_attempt", attempt=polluted, context=context(56))
        self.assertEqual("FIELD_NOT_ALLOWED", rejected["error"]["code"])

    def test_reliable_correct_item_does_not_schedule_review(self) -> None:
        service = ChekoPracticeService()
        reach_awaiting(service, start=60)
        imported = service.invoke(
            "import_submitted_result", task_id="practice-1", result=result(), context=context(63)
        )
        writes = build_state_writes(imported["data"]["task"], review_due_at="2026-09-05T05:10:00Z")
        self.assertEqual(2, len(writes))
        self.assertNotIn("schedule_review", {item["operation"] for item in writes})

    def test_real_sanitized_aggregate_report_imports_without_question_body(self) -> None:
        fixture = json.loads(
            (ROOT / "tests" / "fixtures" / "cheko-submitted-report-sanitized.json").read_text(encoding="utf-8")
        )
        service = ChekoPracticeService()
        service.invoke("create_task", task=fixture["task"], context=context(70))
        service.invoke(
            "prepare_navigation",
            task_id=fixture["task"]["task_id"],
            observed_route="/test_log?subject=0",
            ui_contract_version=fixture["result"]["ui_contract_version"],
            context=context(71),
        )
        service.invoke("enter_awaiting_human", task_id=fixture["task"]["task_id"], context=context(72))
        imported = service.invoke(
            "import_submitted_result",
            task_id=fixture["task"]["task_id"],
            result=fixture["result"],
            context=context(73),
        )
        self.assertEqual("aggregate_only", imported["data"]["task"]["imported_result"]["detail_completeness"])
        self.assertEqual(55, imported["data"]["task"]["imported_result"]["summary"]["question_count"])
        serialized = json.dumps(imported, ensure_ascii=False).casefold()
        for forbidden in ("question_text", "correct_answer", "options"):
            self.assertNotIn(forbidden, serialized)

    def test_idempotent_result_replay_and_operation_allowlist(self) -> None:
        service = ChekoPracticeService()
        create_context = context(80)
        created = service.invoke("create_task", task=task(), context=create_context)
        service.invoke(
            "prepare_navigation",
            task_id="practice-1",
            observed_route="/?subject=0",
            ui_contract_version="cheko-ui-2026-09-04.1",
            context=context(81),
        )
        service.invoke("enter_awaiting_human", task_id="practice-1", context=context(82))
        write_context = context(83)
        first = service.invoke(
            "import_submitted_result", task_id="practice-1", result=result(), context=write_context
        )
        second = service.invoke(
            "import_submitted_result", task_id="practice-1", result=result(), context=write_context
        )
        self.assertEqual("ok", first["status"])
        self.assertTrue(second["data"]["deduplicated"])
        old_create_replay = service.invoke("create_task", task=task(), context=create_context)
        self.assertTrue(old_create_replay["data"]["deduplicated"])
        self.assertEqual("CREATED", created["data"]["task"]["status"])
        blocked = service.invoke("select_answer", task_id="practice-1", choice="A")
        self.assertEqual("OPERATION_NOT_ALLOWED", blocked["error"]["code"])

    def test_versioned_ui_contract_exposes_manual_fallbacks(self) -> None:
        contract = ChekoUiContract.load(ROOT / "deployment" / "cheko" / "ui-contract-v1.json")
        error_book = contract.target("error_book")
        self.assertEqual("/error_book?subject=0", error_book["target"]["route"])
        self.assertEqual("cheko-ui-2026-09-04.1", error_book["contract_version"])
        fallback = contract.fallback("dom_changed")
        methods = [item["method"] for item in fallback["steps"]]
        self.assertEqual(["official_export", "screenshot", "manual_summary"], methods)


if __name__ == "__main__":
    unittest.main()
