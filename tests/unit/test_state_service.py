import unittest

from architectpass_state import InMemoryStore, StateService, WriteContext


def ctx(number: int, *, confirmed: bool = False) -> WriteContext:
    return WriteContext(f"req-{number}", f"audit-{number}", "unit-test", confirmed)


class StateServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.store = InMemoryStore()
        self.service = StateService(self.store)

    def test_profile_write_is_idempotent(self) -> None:
        first = self.service.invoke("update_profile", user_id="u1", patch={"timezone": "Asia/Shanghai"}, context=ctx(1))
        second = self.service.invoke("update_profile", user_id="u1", patch={"timezone": "Asia/Shanghai"}, context=ctx(1))
        self.assertEqual("ok", first["status"])
        self.assertTrue(second["data"]["deduplicated"])
        self.assertEqual(1, len(self.store.list("audit_log")))

    def test_request_id_cannot_be_reused_for_different_payload(self) -> None:
        self.service.invoke("update_profile", user_id="u1", patch={"timezone": "Asia/Shanghai"}, context=ctx(2))
        conflict_context = WriteContext("req-2", "audit-2-conflict", "unit-test")
        result = self.service.invoke("update_profile", user_id="u1", patch={"timezone": "UTC"}, context=conflict_context)
        self.assertEqual("error", result["status"])
        self.assertEqual("IDEMPOTENCY_CONFLICT", result["error"]["code"])
        self.assertEqual("Asia/Shanghai", self.store.read("user_profile", "u1")["timezone"])
        self.assertFalse(self.store.read("audit_log", "audit-2-conflict")["success"])

    def test_immutable_event_cannot_be_overwritten(self) -> None:
        event = {
            "event_id": "ev-1", "event_type": "recall", "occurred_at": "2026-09-04T00:00:00Z",
            "source_ref": {"resource_id": "r1", "pdf_page": 12},
        }
        self.assertEqual("ok", self.service.invoke("record_study_event", event=event, context=ctx(3))["status"])
        changed = {**event, "event_type": "changed"}
        result = self.service.invoke("record_study_event", event=changed, context=ctx(4))
        self.assertEqual("IMMUTABLE_RECORD", result["error"]["code"])

    def test_untraceable_event_is_rejected_and_failure_audited(self) -> None:
        event = {"event_id": "ev-2", "event_type": "read", "occurred_at": "2026-09-04T00:00:00Z", "source_ref": {}}
        result = self.service.invoke("record_study_event", event=event, context=ctx(5))
        self.assertEqual("UNTRACEABLE_SOURCE", result["error"]["code"])
        audit = self.store.read("audit_log", "audit-5")
        self.assertFalse(audit["success"])

    def test_viewing_alone_cannot_raise_mastery_above_one(self) -> None:
        evidence = {
            "evidence_id": "e1", "topic_id": "topic-1", "evidence_type": "viewed",
            "score": 1.0, "confidence": 1.0, "source_id": "video:v1@600", "created_at": "2026-09-04T00:00:00Z",
        }
        self.service.invoke("record_mastery_evidence", evidence=evidence, context=ctx(6))
        result = self.service.invoke("recompute_topic_state", topic_id="topic-1", context=ctx(7))
        self.assertEqual(1, result["data"]["record"]["level_0_to_5"])

    def test_low_confidence_correct_choice_stays_a_risk(self) -> None:
        evidence = {
            "evidence_id": "e2", "topic_id": "topic-2", "evidence_type": "choice_timed",
            "score": 1.0, "confidence": 0.4, "source_id": "cheko:test-1", "created_at": "2026-09-04T00:00:00Z",
        }
        self.service.invoke("record_mastery_evidence", evidence=evidence, context=ctx(8))
        result = self.service.invoke("recompute_topic_state", topic_id="topic-2", context=ctx(9))
        state = result["data"]["record"]
        self.assertEqual(0, state["level_0_to_5"])
        self.assertIn("LOW_CONFIDENCE_EVIDENCE", state["risk_flags"])
        self.assertIn("INSUFFICIENT_CHOICE_REPETITION", state["risk_flags"])

    def test_two_reliable_choice_results_can_establish_level_three(self) -> None:
        for number in (1, 2):
            evidence = {
                "evidence_id": f"choice-{number}", "topic_id": "topic-3", "evidence_type": "choice_timed",
                "score": 0.8, "confidence": 0.9, "source_id": f"cheko:test-{number}",
                "created_at": f"2026-09-0{number}T00:00:00Z",
            }
            self.service.invoke("record_mastery_evidence", evidence=evidence, context=ctx(20 + number))
        result = self.service.invoke("recompute_topic_state", topic_id="topic-3", context=ctx(23))
        self.assertEqual(3, result["data"]["record"]["level_0_to_5"])

    def test_two_low_confidence_correct_choices_do_not_establish_level_three(self) -> None:
        for number in (1, 2):
            evidence = {
                "evidence_id": f"guess-{number}", "topic_id": "topic-guess", "evidence_type": "choice_timed",
                "score": 1.0, "confidence": 0.4, "source_id": f"cheko:guess-{number}",
                "created_at": f"2026-09-0{number}T00:00:00Z",
            }
            self.service.invoke("record_mastery_evidence", evidence=evidence, context=ctx(30 + number))
        result = self.service.invoke("recompute_topic_state", topic_id="topic-guess", context=ctx(33))
        self.assertEqual(0, result["data"]["record"]["level_0_to_5"])
        self.assertIn("LOW_CONFIDENCE_EVIDENCE", result["data"]["record"]["risk_flags"])

    def test_review_queue_deduplicates_pending_topic_and_type(self) -> None:
        first = {
            "review_id": "rv1", "topic_id": "t1", "due_at": "2026-09-05T00:00:00Z",
            "review_type": "recall", "priority": 2, "reason": "decay", "status": "pending",
        }
        second = {**first, "review_id": "rv2"}
        self.service.invoke("schedule_review", review=first, context=ctx(10))
        result = self.service.invoke("schedule_review", review=second, context=ctx(11))
        self.assertTrue(result["data"]["deduplicated"])
        self.assertEqual(1, len(self.store.list("review_queue")))

    def test_checkpoint_requires_all_recovery_fields(self) -> None:
        result = self.service.invoke("finish_session", session_id="s1", checkpoint={"completed": []}, context=ctx(12))
        self.assertEqual("INCOMPLETE_CHECKPOINT", result["error"]["code"])

    def test_unknown_operation_is_blocked(self) -> None:
        result = self.service.invoke("execute_sql", sql="drop table x")
        self.assertEqual("OPERATION_NOT_ALLOWED", result["error"]["code"])

    def test_delete_requires_confirmation_and_backup(self) -> None:
        self.service.invoke("update_profile", user_id="u2", patch={"timezone": "UTC"}, context=ctx(13))
        with self.assertRaisesRegex(Exception, "confirmation and a backup"):
            self.store.delete(table="user_profile", record_id="u2", context=ctx(14), backup_ref=None)


if __name__ == "__main__":
    unittest.main()
