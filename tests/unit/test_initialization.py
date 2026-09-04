import json
import unittest
from pathlib import Path

from architectpass_initialization import Phase6Builder
from architectpass_state import InMemoryStore, StateService, WriteContext


ROOT = Path(__file__).resolve().parents[2]


class Phase6InitializationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.bundle = Phase6Builder(ROOT).build()

    def test_history_is_not_required_and_no_history_is_in_profile(self) -> None:
        self.assertFalse(self.bundle["history_required"])
        profile = next(item for item in self.bundle["operations"] if item["table"] == "user_profile")
        self.assertNotIn("past_exam_scores", profile["record"])

    def test_only_traceable_authorized_real_evidence_is_planned(self) -> None:
        tables = {item["table"] for item in self.bundle["operations"]}
        self.assertEqual({"user_profile", "topics", "resources", "video_progress", "study_events"}, tables)
        self.assertEqual(2, sum(item["table"] == "resources" for item in self.bundle["operations"]))
        event = next(item for item in self.bundle["operations"] if item["table"] == "study_events")
        self.assertEqual("710358", event["record"]["source_ref"]["cheko_result_id"])
        self.assertFalse(event["record"]["payload"]["mastery_update_allowed"])

    def test_every_write_has_unique_request_and_audit_id(self) -> None:
        requests = [item["request_id"] for item in self.bundle["operations"]]
        audits = [item["audit_id"] for item in self.bundle["operations"]]
        self.assertEqual(len(requests), len(set(requests)))
        self.assertEqual(len(audits), len(set(audits)))

    def test_knowledge_map_does_not_infer_mastery_or_weights(self) -> None:
        topic_ops = [item for item in self.bundle["operations"] if item["table"] == "topics"]
        self.assertEqual(10, len(topic_ops))
        self.assertTrue(all(item["record"]["syllabus_weight"] is None for item in topic_ops))
        self.assertTrue(all(item["record"]["source_refs"] for item in topic_ops))

    def test_seven_day_plan_is_bounded_at_runtime(self) -> None:
        self.assertEqual(7, len(self.bundle["seven_day_plan"]["days"]))
        for day in self.bundle["seven_day_plan"]["days"]:
            total = sum(item["budget_fraction"] for item in day["tasks"])
            self.assertLessEqual(total + day["checkpoint_reserve_fraction"], 1.0)

    def test_project_fact_v1_is_explicitly_empty(self) -> None:
        self.assertEqual(0, self.bundle["project_facts"]["fact_count"])
        self.assertEqual("awaiting_user_confirmed_redacted_facts", self.bundle["project_facts"]["status"])

    def test_rendered_write_plan_matches_builder(self) -> None:
        rendered = json.loads(
            (ROOT / "deployment/phase6/initialization-write-plan-v1.json").read_text(encoding="utf-8")
        )
        self.assertEqual(self.bundle, rendered)

    def test_public_plan_replays_through_allowlisted_state_api(self) -> None:
        store = InMemoryStore()
        service = StateService(store)
        for item in self.bundle["operations"]:
            context = WriteContext(item["request_id"], item["audit_id"], "unit-test")
            record = item["record"]
            if item["operation"] == "update_profile":
                result = service.invoke(
                    "update_profile", user_id=item["record_id"],
                    patch={key: value for key, value in record.items() if key != "user_id"}, context=context,
                )
            elif item["operation"] == "upsert_topic":
                result = service.invoke("upsert_topic", topic=record, context=context)
            elif item["operation"] == "upsert_resource":
                result = service.invoke("upsert_resource", resource=record, context=context)
            elif item["operation"] == "update_video_progress":
                result = service.invoke(
                    "update_video_progress", video_id=item["record_id"], progress=record, context=context,
                )
            else:
                result = service.invoke("record_study_event", event=record, context=context)
            self.assertEqual("ok", result["status"], item["request_id"])
        self.assertEqual(15, len(store.list("audit_log")))
        self.assertEqual(10, len(store.list("topics")))

    def test_private_segments_replay_through_allowlisted_state_api(self) -> None:
        pdf_catalog = ROOT / "materials/index/phase2-real-pdf-ocr-catalog.json"
        video_catalog = ROOT / "materials/index/phase2-real-video-catalog-v3.json"
        if not pdf_catalog.is_file() or not video_catalog.is_file():
            self.skipTest("private runtime catalogs are intentionally absent from Git")
        private = Phase6Builder(ROOT).build_private_segments(pdf_catalog, video_catalog)
        store = InMemoryStore()
        service = StateService(store)
        for item in private["operations"]:
            context = WriteContext(item["request_id"], item["audit_id"], "unit-test")
            result = service.invoke("upsert_resource_segment", segment=item["record"], context=context)
            self.assertEqual("ok", result["status"], item["request_id"])
        self.assertEqual(49, len(store.list("resource_segments")))
        self.assertEqual(49, len(store.list("audit_log")))

    def test_private_runtime_segment_plan_has_page_and_time_anchors(self) -> None:
        pdf_catalog = ROOT / "materials/index/phase2-real-pdf-ocr-catalog.json"
        video_catalog = ROOT / "materials/index/phase2-real-video-catalog-v3.json"
        if not pdf_catalog.is_file() or not video_catalog.is_file():
            self.skipTest("private runtime catalogs are intentionally absent from Git")
        private = Phase6Builder(ROOT).build_private_segments(
            pdf_catalog,
            video_catalog,
        )
        self.assertFalse(private["git_commit_allowed"])
        self.assertEqual(49, len(private["operations"]))
        pdf = [item for item in private["operations"] if item["record"]["page_start"] is not None]
        video = [item for item in private["operations"] if item["record"]["time_start"] is not None]
        self.assertEqual(10, len(pdf))
        self.assertEqual(39, len(video))
        self.assertTrue(all("#page=" in item["record"]["citation_anchor"] for item in pdf))
        self.assertTrue(all("#t=" in item["record"]["citation_anchor"] for item in video))


if __name__ == "__main__":
    unittest.main()
