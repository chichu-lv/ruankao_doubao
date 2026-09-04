import unittest
from datetime import date

from architectpass_controller import CaseCoach, EssayCoach, EssayFactBase, PlanGenerator, ReviewScheduler, TrainingController, WeeklyReporter
from architectpass_controller.errors import ControllerError
from architectpass_state import InMemoryStore, StateService, WriteContext


def ctx(number: int) -> WriteContext:
    return WriteContext(f"p4-req-{number}", f"p4-audit-{number}", "phase4-test")


def snapshot() -> dict:
    return {
        "observed_at": "2026-09-04T01:00:00Z",
        "profile": {"user_id": "u1"},
        "target_exam_date": "2026-11-08",
        "due_reviews": [{"topic_id": "t1"}],
        "score_windows": {"7d": 0.5, "14d": 0.55, "30d": 0.6},
        "video_progress": {"course": 0.25},
        "subject_ratios_14d": {"综合知识": 0.8, "案例分析": 0.15, "论文": 0.05},
        "days_since_subject": {"综合知识": 0, "案例分析": 2, "论文": 9},
        "prior_incomplete": [],
        "recent_error_types": ["K", "K", "G", "E"],
        "essay_fact_gaps": ["result"],
    }


def candidate(candidate_id: str, subject: str, minutes: int, **overrides) -> dict:
    row = {
        "candidate_id": candidate_id,
        "subject": subject,
        "estimated_minutes": minutes,
        "action": f"训练 {candidate_id}",
        "completion_standard": "产生可追溯证据",
        "syllabus_importance": 0.8,
        "weakness": 0.8,
        "due_factor": 0.8,
        "forgetting_risk": 0.8,
        "cross_subject_value": 0.8,
        "recent_error_severity": 0.8,
        "cognitive_load": "medium",
    }
    row.update(overrides)
    return row


class PlannerTests(unittest.TestCase):
    def test_plan_is_bounded_and_reserves_checkpoint_time(self) -> None:
        plan = PlanGenerator().generate(
            state_snapshot=snapshot(),
            candidates=[candidate("a", "综合知识", 35), candidate("b", "案例分析", 35), candidate("c", "论文", 20)],
            available_minutes=60,
            energy="medium",
        )
        self.assertLessEqual(plan["planned_minutes"], 60)
        self.assertEqual("checkpoint", plan["items"][-1]["candidate_id"])
        self.assertTrue(all(item.get("completion_standard") for item in plan["items"]))

    def test_state_must_be_observed_before_plan(self) -> None:
        with self.assertRaisesRegex(ControllerError, "snapshot"):
            PlanGenerator().generate(state_snapshot={}, candidates=[], available_minutes=30, energy="medium")

    def test_neglected_subject_receives_explainable_boost(self) -> None:
        plan = PlanGenerator().generate(
            state_snapshot=snapshot(),
            candidates=[candidate("knowledge", "综合知识", 20), candidate("essay", "论文", 20)],
            available_minutes=30,
            energy="medium",
        )
        self.assertEqual("essay", plan["items"][0]["candidate_id"])
        self.assertEqual(1.5, plan["items"][0]["priority_explanation"]["subject_balance_multiplier"])

    def test_low_energy_reduces_high_load_priority_without_cancelling_plan(self) -> None:
        plan = PlanGenerator().generate(
            state_snapshot=snapshot(),
            candidates=[
                candidate("hard", "综合知识", 15, cognitive_load="high"),
                candidate("light", "综合知识", 15, cognitive_load="low", due_factor=0.7),
            ],
            available_minutes=30,
            energy="low",
        )
        self.assertEqual("reduced", plan["load_mode"])
        self.assertEqual("light", plan["items"][0]["candidate_id"])


class StateMachineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.store = InMemoryStore()
        self.controller = TrainingController(self.store)

    def test_full_state_flow_waits_for_human_and_finishes_with_checkpoint(self) -> None:
        self.assertEqual("OBSERVE", self.controller.invoke(
            "start_session", session_id="s1", state_snapshot=snapshot(), available_minutes=60,
            energy="medium", context=ctx(1),
        )["data"]["record"]["phase"])
        self.controller.invoke("diagnose_session", session_id="s1", context=ctx(2))
        self.controller.invoke("create_plan", session_id="s1", candidates=[candidate("a", "综合知识", 20)], context=ctx(3))
        waiting = self.controller.invoke("begin_execution", session_id="s1", task_ref="cheko:visible-task", context=ctx(4))
        self.assertEqual("AWAITING_HUMAN", waiting["data"]["record"]["status"])
        self.controller.invoke("submit_human_output", session_id="s1", output_ref="cheko:submitted-result-1", context=ctx(5))
        self.controller.invoke("record_test", session_id="s1", result={
            "evidence_type": "choice_timed", "source_ref": "cheko:submitted-result-1"
        }, context=ctx(6))
        self.controller.invoke("record_state_update", session_id="s1", write_status={"status": "ok"}, context=ctx(7))
        self.controller.invoke("record_schedule", session_id="s1", next_due=[{
            "due_at": "2026-09-05T01:00:00Z", "reason": "1-day review"
        }], context=ctx(8))
        checkpoint = {
            "completed": ["a"], "incomplete": [], "discoveries": ["K"], "mastery_changes": [],
            "next_due": ["2026-09-05"], "resume_context": "continue t1", "write_status": "ok",
        }
        finished = self.controller.invoke("finish_checkpoint", session_id="s1", checkpoint=checkpoint, context=ctx(9))
        self.assertEqual("FINISHED", finished["data"]["record"]["status"])
        self.assertEqual("CHECKPOINT", finished["data"]["record"]["phase"])
        self.assertEqual(9, len(self.store.list("audit_log")))

    def test_invalid_transition_is_truthfully_failed_and_audited(self) -> None:
        self.controller.invoke("start_session", session_id="s2", state_snapshot=snapshot(), available_minutes=30, energy="low", context=ctx(10))
        result = self.controller.invoke("begin_execution", session_id="s2", task_ref="x", context=ctx(11))
        self.assertEqual("INVALID_PHASE_TRANSITION", result["error"]["code"])
        self.assertFalse(self.store.read("audit_log", "p4-audit-11")["success"])

    def test_transition_retry_is_idempotent(self) -> None:
        self.controller.invoke("start_session", session_id="s3", state_snapshot=snapshot(), available_minutes=30, energy="low", context=ctx(12))
        first = self.controller.invoke("diagnose_session", session_id="s3", context=ctx(13))
        second = self.controller.invoke("diagnose_session", session_id="s3", context=ctx(13))
        self.assertFalse(first["data"]["deduplicated"])
        self.assertTrue(second["data"]["deduplicated"])
        self.assertEqual(2, len(self.store.list("audit_log")))


class CoachingTests(unittest.TestCase):
    def test_case_grading_requires_user_submission(self) -> None:
        with self.assertRaisesRegex(ControllerError, "submitted"):
            CaseCoach().grade(submission_state="not_submitted", user_answer="", rubric=[])

    def test_case_feedback_has_four_dimensions_and_sources(self) -> None:
        result = CaseCoach().grade(
            submission_state="submitted_by_user",
            user_answer="一、应进行风险识别。二、补充无关叙述。",
            rubric=[{"point_id": "p1", "label": "识别风险", "match_terms": ["风险识别"], "source_ref": "pdf:r1#p12"}],
        )
        self.assertEqual(1, len(result["covered"]))
        self.assertTrue(result["redundant"])
        self.assertIn("expression", result)
        self.assertTrue(result["source_complete"])

    def test_essay_refuses_to_invent_missing_facts(self) -> None:
        fact = {
            "fact_id": "f1", "category": "role", "summary": "项目负责人", "source_ref": "user-confirmation:1",
            "confirmed_by_user": True, "redacted": True,
        }
        facts = EssayFactBase({"f1": fact})
        result = EssayCoach(facts).make_outline(topic="架构治理", fact_ids=["f1"])
        self.assertEqual("needs_facts", result["status"])
        self.assertFalse(result["fabrication_allowed"])

    def test_essay_submission_tracks_version_time_words_and_rubric(self) -> None:
        records = {}
        categories = {
            "project_background", "business_goal", "role", "responsibilities", "scale_constraints_metrics",
            "overall_architecture", "quality_attributes", "technical_decisions", "alternatives_tradeoffs",
            "costs_risks_failures", "implementation", "result", "applicable_topics",
        }
        for index, category in enumerate(sorted(categories)):
            records[f"f{index}"] = {
                "fact_id": f"f{index}", "category": category, "summary": category,
                "source_ref": f"user-confirmation:{index}", "confirmed_by_user": True, "redacted": True,
            }
        facts = EssayFactBase(records)
        coach = EssayCoach(facts)
        outline = coach.make_outline(topic="架构治理", fact_ids=list(facts.facts))
        self.assertEqual(
            ["topic", "facts", "outline", "partial_paragraph", "full_timed", "grading", "revision", "spaced_rewrite"],
            outline["workflow"],
        )
        score = coach.grade_submission(
            text="这是用户完成的论文草稿。", version=2, duration_minutes=55, claim_fact_ids=list(facts.facts),
            rubric_scores={"relevance": .8, "structure": .7, "professionalism": .8, "project_specificity": .9, "expression": .7},
        )
        self.assertEqual(2, score["version"])
        self.assertEqual(55, score["duration_minutes"])
        self.assertGreater(score["word_count"], 0)

    def test_case_and_essay_attempts_are_immutable_audited_writes(self) -> None:
        store = InMemoryStore()
        service = StateService(store)
        case = {
            "case_id": "c1", "question_source": {"resource_id": "r1", "pdf_page": 12},
            "user_answer": "已脱敏的用户答案", "rubric": [{"point_id": "p1", "source_ref": "pdf:r1#p12"}],
            "covered_points": ["p1"], "missing_points": ["p2"], "irrelevant_content": [], "time_used": 12,
            "score_estimate": .5, "review_due": "2026-09-05T01:00:00Z",
        }
        essay = {
            "essay_id": "e1", "topic": "架构治理", "outline_or_full": "full", "project_fact_ids": ["f1"],
            "word_count": 1800, "time_used": 45, "rubric_results": {"relevance": .8}, "factual_risks": [],
            "revision_history": [{"version": 1, "submission_ref": "local:redacted-essay-1"}],
        }
        self.assertEqual("ok", service.invoke("record_case_attempt", attempt=case, context=ctx(20))["status"])
        self.assertEqual("ok", service.invoke("record_essay_attempt", attempt=essay, context=ctx(21))["status"])
        self.assertEqual(2, len(store.list("audit_log")))


class WeeklyReportTests(unittest.TestCase):
    def test_review_scheduler_advances_risk_and_delays_stable_evidence(self) -> None:
        scheduler = ReviewScheduler()
        risky = scheduler.schedule(
            topic_id="t1", verified_at="2026-09-04T00:00:00Z", score=.5, confidence=.4,
            importance=.9, recent_error_severity=.8, exam_date="2026-11-08",
        )
        stable = scheduler.schedule(
            topic_id="t2", verified_at="2026-09-04T00:00:00Z", score=.9, confidence=.9,
            importance=.5, recent_error_severity=.1, exam_date="2026-11-08",
        )
        self.assertEqual([1, 3, 7, 14, 30], [item["interval_days"] for item in risky["reviews"]])
        self.assertEqual([3, 7, 14, 30], [item["interval_days"] for item in stable["reviews"]])

    def test_weekly_report_detects_underinvestment_and_dynamic_sprint(self) -> None:
        report = WeeklyReporter().build(
            events=[{"subject": "综合知识", "minutes": 80, "error_type": "K"}, {"subject": "案例分析", "minutes": 10}, {"subject": "论文", "minutes": 10}],
            exam_date=date(2026, 9, 20), today=date(2026, 9, 4), syllabus_progress=.8,
            metrics={"plan_completion_rate": .8, "due_review_completion_rate": .7, "case_point_gaps": ["p2"]},
        )
        self.assertEqual(["案例分析", "论文"], report["underinvestment"])
        self.assertTrue(report["sprint_mode"])
        self.assertEqual(18, report["sprint_threshold_days"])
        self.assertEqual(.8, report["plan_completion_rate"])
        self.assertEqual({"K": 1}, report["error_type_counts"])
        self.assertTrue(report["adjustment_basis"])
        self.assertEqual(3, len(report["next_week_priorities"]))


if __name__ == "__main__":
    unittest.main()
