from __future__ import annotations

import time
from contextlib import ExitStack, contextmanager
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Iterator
from unittest.mock import patch

from architectpass_controller import CaseCoach, EssayCoach, EssayFactBase, TrainingController, WeeklyReporter
from architectpass_controller.essay_coach import REQUIRED_FACT_CATEGORIES
from architectpass_materials.progress import next_review_action
from architectpass_state import InMemoryStore, PersistentOfflineOutbox, StateService, WriteContext
from architectpass_state.backup import build_backup, export_csv_tables, export_json, export_markdown, verify_backup


BASE_TIME = datetime(2026, 9, 4, 12, 0, tzinfo=timezone.utc)
SUBJECTS = ("综合知识", "案例分析", "论文", "综合知识", "案例分析", "论文", "综合知识")
FORBIDDEN_PRACTICE_FIELDS = {
    "question", "question_body", "options", "answer", "correct_answer", "explanation",
}


class _ContextFactory:
    def __init__(self) -> None:
        self.counter = 0

    def new(self, label: str) -> WriteContext:
        self.counter += 1
        safe_label = label.replace("_", "-")
        return WriteContext(
            request_id=f"sim7-{self.counter:03d}-{safe_label}-req",
            audit_id=f"sim7-{self.counter:03d}-{safe_label}-audit",
            actor="accelerated-pilot-simulation",
        )


def _iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


@contextmanager
def _simulated_time(value: str) -> Iterator[None]:
    with ExitStack() as stack:
        stack.enter_context(patch("architectpass_state.store.utc_now", return_value=value))
        stack.enter_context(patch("architectpass_state.service.utc_now", return_value=value))
        stack.enter_context(patch("architectpass_controller.controller.utc_now", return_value=value))
        yield


def _must_ok(result: dict[str, Any], label: str) -> dict[str, Any]:
    if result.get("status") != "ok":
        raise AssertionError(f"{label} failed: {result.get('error')}")
    return result


def _candidate(candidate_id: str, subject: str) -> dict[str, Any]:
    return {
        "candidate_id": candidate_id,
        "subject": subject,
        "estimated_minutes": 20,
        "action": f"simulation-only:{candidate_id}",
        "completion_standard": "produce isolated traceable simulation evidence",
        "syllabus_importance": 0.8,
        "weakness": 0.8,
        "due_factor": 0.8,
        "forgetting_risk": 0.8,
        "cross_subject_value": 0.8,
        "recent_error_severity": 0.8,
        "cognitive_load": "medium",
    }


def _ratios(events: list[dict[str, Any]]) -> dict[str, float]:
    totals = {subject: 0.0 for subject in {"综合知识", "案例分析", "论文"}}
    for event in events:
        subject = event.get("subject")
        if subject in totals:
            totals[subject] += float(event.get("minutes", 0))
    total = sum(totals.values())
    return {subject: round(value / total, 4) if total else 0.0 for subject, value in totals.items()}


def _snapshot(store: InMemoryStore, service: StateService, now: str, day: int) -> dict[str, Any]:
    events = store.list("study_events")
    return {
        "observed_at": now,
        "profile": {"user_id": "simulation-only-user"},
        "target_exam_date": "2026-10-24",
        "due_reviews": _must_ok(service.invoke("get_due_reviews", now=now), "get_due_reviews")["data"],
        "score_windows": {"7d": 0.55, "14d": 0.52, "30d": 0.5},
        "video_progress": {"simulation-video": 0.33},
        "subject_ratios_14d": _ratios(events),
        "days_since_subject": {"综合知识": day % 2, "案例分析": max(0, 4 - day), "论文": max(0, 7 - day)},
        "prior_incomplete": [],
        "recent_error_types": [event["error_type"] for event in events if event.get("error_type")],
        "essay_fact_gaps": [] if day >= 6 else ["result"],
    }


def _practice_attempt(day: int, suffix: str, *, correct: bool, confidence: float, error_type: str | None, now: str) -> dict[str, Any]:
    return {
        "attempt_id": f"sim7-day-{day}-attempt-{suffix}",
        "platform": "cheko",
        "question_or_set_id": f"simulation-item-{day}-{suffix}",
        "topic_ids": ["choice-network"],
        "correct": correct,
        "confidence": confidence,
        "duration": 45,
        "error_type": error_type,
        "source_evidence": {
            "cheko_result_id": f"simulation-result-day-{day}",
            "visible_item_id": f"simulation-item-{day}-{suffix}",
            "import_method": "isolated_simulation_fixture",
            "ui_contract_version": "cheko-ui-2026-09-04.2",
        },
        "submitted_at": now,
    }


def _mastery_evidence(day: int, suffix: str, *, score: float, confidence: float, now: str) -> dict[str, Any]:
    return {
        "evidence_id": f"sim7-day-{day}-evidence-{suffix}",
        "topic_id": "choice-network",
        "evidence_type": "choice_timed",
        "score": score,
        "confidence": confidence,
        "source_id": f"simulation-result-day-{day}:{suffix}",
        "created_at": now,
    }


def run_accelerated_pilot() -> dict[str, Any]:
    """Exercise seven logical days without touching Doubao, Cheko or production Feishu state."""
    wall_started = time.perf_counter()
    store = InMemoryStore()
    service = StateService(store)
    controller = TrainingController(store)
    contexts = _ContextFactory()
    restart_recovered = False
    overdue_recovery_completed = False
    outbox_survived_restart = False
    outbox_retained_failure = False
    outbox_replayed_once = False
    targeted_rewatch: dict[str, Any] | None = None
    case_feedback: dict[str, Any] | None = None
    essay_gap_refusal: dict[str, Any] | None = None
    essay_outline: dict[str, Any] | None = None

    for day, subject in enumerate(SUBJECTS, start=1):
        moment = BASE_TIME + timedelta(days=day - 1)
        now = _iso(moment)
        session_id = f"sim7-day-{day}-session"
        with _simulated_time(now):
            snapshot = _snapshot(store, service, now, day)
            _must_ok(controller.invoke(
                "start_session",
                session_id=session_id,
                state_snapshot=snapshot,
                available_minutes=60,
                energy="medium",
                context=contexts.new(f"day-{day}-start"),
            ), f"day {day} start")
            _must_ok(controller.invoke(
                "diagnose_session", session_id=session_id, context=contexts.new(f"day-{day}-diagnose")
            ), f"day {day} diagnose")
            _must_ok(controller.invoke(
                "create_plan",
                session_id=session_id,
                candidates=[
                    _candidate(f"day-{day}-choice", "综合知识"),
                    _candidate(f"day-{day}-case", "案例分析"),
                    _candidate(f"day-{day}-essay", "论文"),
                ],
                context=contexts.new(f"day-{day}-plan"),
            ), f"day {day} plan")
            _must_ok(controller.invoke(
                "begin_execution",
                session_id=session_id,
                task_ref=f"simulation-only:day-{day}-task",
                context=contexts.new(f"day-{day}-execute"),
            ), f"day {day} execute")
            _must_ok(controller.invoke(
                "submit_human_output",
                session_id=session_id,
                output_ref=f"simulation-only:synthetic-user-output-day-{day}",
                context=contexts.new(f"day-{day}-output"),
            ), f"day {day} output")
            _must_ok(controller.invoke(
                "record_test",
                session_id=session_id,
                result={
                    "evidence_type": "isolated_simulation_metadata",
                    "source_ref": f"simulation-only:result-day-{day}",
                },
                context=contexts.new(f"day-{day}-test"),
            ), f"day {day} test")

            event = {
                "event_id": f"sim7-day-{day}-event",
                "event_type": "accelerated_pilot_simulation",
                "occurred_at": now,
                "source_ref": {"mode": "simulation_only", "day": day},
                "subject": subject,
                "minutes": 50,
                "error_type": "K" if day in {1, 4} else ("G" if day == 2 else None),
            }
            _must_ok(service.invoke(
                "record_study_event", event=event, context=contexts.new(f"day-{day}-event")
            ), f"day {day} event")

            if day == 1:
                for suffix, correct, confidence, error_type, score in (
                    ("wrong", False, 0.8, "K", 0.4),
                    ("guess", True, 0.4, "G", 0.7),
                ):
                    _must_ok(service.invoke(
                        "record_practice_attempt",
                        attempt=_practice_attempt(
                            day, suffix, correct=correct, confidence=confidence, error_type=error_type, now=now
                        ),
                        context=contexts.new(f"day-{day}-attempt-{suffix}"),
                    ), f"day {day} attempt {suffix}")
                    _must_ok(service.invoke(
                        "record_mastery_evidence",
                        evidence=_mastery_evidence(day, suffix, score=score, confidence=confidence, now=now),
                        context=contexts.new(f"day-{day}-evidence-{suffix}"),
                    ), f"day {day} evidence {suffix}")
                _must_ok(service.invoke(
                    "recompute_topic_state",
                    topic_id="choice-network",
                    context=contexts.new("day-1-mastery"),
                ), "day 1 mastery")
                _must_ok(service.invoke(
                    "schedule_review",
                    review={
                        "review_id": "sim7-review-1",
                        "topic_id": "choice-network",
                        "due_at": _iso(moment + timedelta(days=1)),
                        "review_type": "closed_book_recall",
                        "priority": 3,
                        "reason": "low-confidence correct and K error",
                        "status": "pending",
                    },
                    context=contexts.new("day-1-review"),
                ), "day 1 review")

            if day == 2:
                rubric = [
                    {"point_id": "p1", "label": "risk", "match_terms": ["风险识别"], "source_ref": "simulation.pdf#page=12"},
                    {"point_id": "p2", "label": "metric", "match_terms": ["量化指标"], "source_ref": "simulation.pdf#page=12"},
                ]
                case_feedback = CaseCoach().grade(
                    submission_state="submitted_by_user",
                    user_answer="SIMULATION_ONLY：一、进行风险识别。",
                    rubric=rubric,
                )
                _must_ok(service.invoke(
                    "record_case_attempt",
                    attempt={
                        "case_id": "sim7-case-1",
                        "question_source": {"resource_id": "simulation-case", "pdf_page": 12},
                        "user_answer": "SIMULATION_ONLY_REDACTED_USER_OUTPUT",
                        "rubric": rubric,
                        "covered_points": [item["point_id"] for item in case_feedback["covered"]],
                        "missing_points": [item["point_id"] for item in case_feedback["missing"]],
                        "irrelevant_content": case_feedback["redundant"],
                        "time_used": 20,
                        "score_estimate": case_feedback["score_ratio"],
                        "review_due": _iso(moment + timedelta(days=1)),
                    },
                    context=contexts.new("day-2-case"),
                ), "day 2 case")

            if day == 3:
                one_fact = {
                    "sim-fact-role": {
                        "fact_id": "sim-fact-role",
                        "category": "role",
                        "summary": "SIMULATION_ONLY",
                        "source_ref": "simulation-only:fact-role",
                        "confirmed_by_user": True,
                        "redacted": True,
                    }
                }
                essay_gap_refusal = EssayCoach(EssayFactBase(one_fact)).make_outline(
                    topic="simulation-only topic", fact_ids=list(one_fact)
                )

            if day == 4:
                targeted_rewatch = next_review_action(
                    {
                        "status": "played_unchecked",
                        "watched_until_seconds": 1200,
                        "duration_seconds": 3600,
                    },
                    weak_ranges=((420, 540),),
                )
                _must_ok(service.invoke(
                    "record_practice_attempt",
                    attempt=_practice_attempt(day, "reliable-1", correct=True, confidence=0.85, error_type=None, now=now),
                    context=contexts.new("day-4-attempt"),
                ), "day 4 attempt")
                _must_ok(service.invoke(
                    "record_mastery_evidence",
                    evidence=_mastery_evidence(day, "reliable-1", score=0.85, confidence=0.85, now=now),
                    context=contexts.new("day-4-evidence"),
                ), "day 4 evidence")
                _must_ok(service.invoke(
                    "recompute_topic_state",
                    topic_id="choice-network",
                    context=contexts.new("day-4-mastery"),
                ), "day 4 mastery")
                duplicate_review = _must_ok(service.invoke(
                    "schedule_review",
                    review={
                        "review_id": "sim7-review-duplicate",
                        "topic_id": "choice-network",
                        "due_at": _iso(moment + timedelta(days=1)),
                        "review_type": "closed_book_recall",
                        "priority": 2,
                        "reason": "repeat scheduling attempt",
                        "status": "pending",
                    },
                    context=contexts.new("day-4-review-dedup"),
                ), "day 4 review dedup")
                if duplicate_review["data"]["deduplicated"] is not True:
                    raise AssertionError("pending review was not deduplicated")

                with TemporaryDirectory() as directory:
                    offline_event = {
                        "event_id": "sim7-offline-event",
                        "event_type": "accelerated_pilot_offline_replay",
                        "occurred_at": now,
                        "source_ref": {"mode": "simulation_only", "failure": "transport_unavailable"},
                    }
                    offline_context = contexts.new("day-4-offline")
                    PersistentOfflineOutbox(Path(directory)).enqueue(
                        "record_study_event", {"event": offline_event}, offline_context
                    )
                    restarted_outbox = PersistentOfflineOutbox(Path(directory))
                    outbox_survived_restart = len(restarted_outbox.pending()) == 1
                    restarted_outbox.replay(lambda _: {"status": "error", "error": {"code": "SIMULATED_OUTAGE"}})
                    outbox_retained_failure = len(PersistentOfflineOutbox(Path(directory)).pending()) == 1

                    def sender(item: dict[str, Any]) -> dict[str, Any]:
                        context = WriteContext(item["request_id"], item["audit_id"], item["actor"])
                        return service.invoke(item["operation"], **item["payload"], context=context)

                    recovered_outbox = PersistentOfflineOutbox(Path(directory))
                    recovered_outbox.replay(sender)
                    outbox_replayed_once = (
                        not recovered_outbox.pending()
                        and len([row for row in store.list("study_events") if row["event_id"] == "sim7-offline-event"]) == 1
                    )

            if day == 5:
                due = _must_ok(service.invoke("get_due_reviews", now=now), "day 5 due reviews")["data"]
                target = next((item for item in due if item["review_id"] == "sim7-review-1"), None)
                overdue_recovery_completed = target is not None and (
                    moment - datetime.fromisoformat(target["due_at"].replace("Z", "+00:00"))
                ).days >= 3
                _must_ok(service.invoke(
                    "complete_review",
                    review_id="sim7-review-1",
                    completed_at=now,
                    completion_evidence_ref="simulation-only:day-5-closed-book-recall",
                    context=contexts.new("day-5-review-complete"),
                ), "day 5 review completion")
                _must_ok(service.invoke(
                    "schedule_review",
                    review={
                        "review_id": "sim7-review-2",
                        "topic_id": "choice-network",
                        "due_at": _iso(moment + timedelta(days=3)),
                        "review_type": "closed_book_recall",
                        "priority": 2,
                        "reason": "rescheduled after completion",
                        "status": "pending",
                    },
                    context=contexts.new("day-5-review-next"),
                ), "day 5 next review")

            if day == 6:
                fact_records = {
                    f"sim-fact-{index}": {
                        "fact_id": f"sim-fact-{index}",
                        "category": category,
                        "summary": f"SIMULATION_ONLY:{category}",
                        "source_ref": f"simulation-only:fact-{index}",
                        "confirmed_by_user": True,
                        "redacted": True,
                    }
                    for index, category in enumerate(sorted(REQUIRED_FACT_CATEGORIES), start=1)
                }
                essay_coach = EssayCoach(EssayFactBase(fact_records))
                essay_outline = essay_coach.make_outline(
                    topic="simulation-only architecture governance", fact_ids=list(fact_records)
                )
                essay_score = essay_coach.grade_submission(
                    text="SIMULATION_ONLY_REDACTED_DRAFT",
                    version=1,
                    duration_minutes=30,
                    claim_fact_ids=list(fact_records),
                    rubric_scores={
                        "relevance": 0.7,
                        "structure": 0.7,
                        "professionalism": 0.7,
                        "project_specificity": 0.7,
                        "expression": 0.7,
                    },
                )
                _must_ok(service.invoke(
                    "record_essay_attempt",
                    attempt={
                        "essay_id": "sim7-essay-1",
                        "topic": "simulation-only architecture governance",
                        "outline_or_full": "outline",
                        "project_fact_ids": essay_score["fact_ids"],
                        "word_count": essay_score["word_count"],
                        "time_used": essay_score["duration_minutes"],
                        "rubric_results": essay_score["rubric_scores"],
                        "factual_risks": [],
                        "revision_history": [{"version": 1, "submission_ref": "simulation-only:redacted-draft"}],
                    },
                    context=contexts.new("day-6-essay"),
                ), "day 6 essay")

            if day == 7:
                _must_ok(service.invoke(
                    "record_practice_attempt",
                    attempt=_practice_attempt(day, "reliable-2", correct=True, confidence=0.9, error_type=None, now=now),
                    context=contexts.new("day-7-attempt"),
                ), "day 7 attempt")
                _must_ok(service.invoke(
                    "record_mastery_evidence",
                    evidence=_mastery_evidence(day, "reliable-2", score=0.9, confidence=0.9, now=now),
                    context=contexts.new("day-7-evidence"),
                ), "day 7 evidence")
                _must_ok(service.invoke(
                    "recompute_topic_state",
                    topic_id="choice-network",
                    context=contexts.new("day-7-mastery"),
                ), "day 7 mastery")

            write_status = {"status": "ok", "scope": "isolated_simulation", "production_writes": 0}
            _must_ok(controller.invoke(
                "record_state_update",
                session_id=session_id,
                write_status=write_status,
                context=contexts.new(f"day-{day}-state-update"),
            ), f"day {day} state update")
            pending_reviews = [item for item in store.list("review_queue") if item["status"] == "pending"]
            next_due = [{"due_at": item["due_at"], "reason": item["reason"]} for item in pending_reviews]
            _must_ok(controller.invoke(
                "record_schedule",
                session_id=session_id,
                next_due=next_due,
                context=contexts.new(f"day-{day}-schedule"),
            ), f"day {day} schedule")
            _must_ok(controller.invoke(
                "finish_checkpoint",
                session_id=session_id,
                checkpoint={
                    "completed": [f"simulation-only:{subject}"],
                    "incomplete": [],
                    "discoveries": [f"simulation-day-{day}"],
                    "mastery_changes": [store.read("mastery_state", "choice-network") or {}],
                    "next_due": [item["due_at"] for item in pending_reviews],
                    "resume_context": f"simulation-only:resume-day-{day + 1}",
                    "write_status": write_status,
                },
                context=contexts.new(f"day-{day}-checkpoint"),
            ), f"day {day} checkpoint")

        if day == 3:
            controller = TrainingController(store)
            recovered = _must_ok(controller.invoke("get_session", session_id=session_id), "restart recovery")["data"]
            restart_recovered = recovered is not None and recovered.get("status") == "FINISHED"

    events = store.list("study_events")
    weekly = WeeklyReporter().build(
        events=events,
        exam_date=date(2026, 10, 24),
        today=date(2026, 9, 10),
        syllabus_progress=0.45,
        metrics={
            "plan_completion_rate": 1.0,
            "due_review_completion_rate": 1.0,
            "fastest_improving_topics": ["choice-network"],
            "largest_declining_topics": [],
            "timed_mock_trend": [0.4, 0.85, 0.9],
            "case_point_gaps": ["p2"] if case_feedback else [],
            "essay_topic_coverage": ["simulation-only architecture governance"] if essay_outline else [],
            "long_video_without_recall_minutes": 20,
        },
    )
    backup = build_backup(store.snapshot())
    verify_backup(backup)
    json_export = export_json(backup)
    csv_export = export_csv_tables(backup)
    markdown_export = export_markdown(backup)
    practice_rows = store.list("practice_attempts")
    sessions = store.list("study_sessions")
    reviews = store.list("review_queue")
    audits = store.list("audit_log")
    mastery = store.read("mastery_state", "choice-network")
    checks = {
        "seven_daily_checkpoints": len(sessions) == 7 and all(
            row.get("status") == "FINISHED" and row.get("checkpoint") for row in sessions
        ),
        "restart_checkpoint_recovery": restart_recovered,
        "low_confidence_correct_recorded_as_G": any(
            row["correct"] is True and row["confidence"] < 0.6 and row.get("error_type") == "G"
            for row in practice_rows
        ),
        "three_day_overdue_review_recovered": overdue_recovery_completed,
        "review_completion_and_reschedule": (
            len(reviews) == 2
            and len([row for row in reviews if row["status"] == "completed"]) == 1
            and len([row for row in reviews if row["status"] == "pending"]) == 1
        ),
        "no_review_queue_explosion": len(reviews) <= 2,
        "targeted_rewatch_only": bool(
            targeted_rewatch
            and targeted_rewatch["action"] == "targeted_rewatch"
            and targeted_rewatch["restart_from_beginning"] is False
            and targeted_rewatch["mastery_changed"] is False
        ),
        "case_post_submission_gate": bool(case_feedback and case_feedback["gate"] == "post_submission_only"),
        "essay_missing_facts_fail_closed": bool(
            essay_gap_refusal
            and essay_gap_refusal["status"] == "needs_facts"
            and essay_gap_refusal["fabrication_allowed"] is False
        ),
        "essay_complete_fact_flow": bool(
            essay_outline
            and essay_outline["status"] == "ready"
            and essay_outline["fabrication_allowed"] is False
            and len(store.list("essay_attempts")) == 1
        ),
        "all_three_subjects_exercised": all(weekly["minutes_by_subject"][subject] > 0 for subject in SUBJECTS[:3]),
        "weekly_report_generated": len(weekly["next_week_priorities"]) == 3,
        "offline_outbox_survived_restart": outbox_survived_restart,
        "offline_failure_not_acknowledged": outbox_retained_failure,
        "offline_recovery_replayed_once": outbox_replayed_once,
        "practice_has_no_answer_content": all(
            FORBIDDEN_PRACTICE_FIELDS.isdisjoint(row) for row in practice_rows
        ),
        "mastery_reproducibly_reaches_level_3": bool(mastery and mastery["level_0_to_5"] == 3),
        "unique_request_and_audit_ids": (
            len({row["request_id"] for row in audits}) == len(audits)
            and len({row["audit_id"] for row in audits}) == len(audits)
        ),
        "backup_exports_verified": bool(json_export and markdown_export and len(csv_export) == 15),
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    return {
        "status": status,
        "mode": "accelerated_simulation",
        "scope": "isolated_in_memory_state_and_temporary_outbox",
        "simulated_period": {"start": "2026-09-04", "end": "2026-09-10", "logical_days": 7},
        "wall_clock_elapsed_seconds": round(time.perf_counter() - wall_started, 4),
        "authoritative_learning_state": False,
        "production_writes": 0,
        "external_service_calls": 0,
        "cheko_answers_or_submissions": 0,
        "real_seven_day_independent_pilot_satisfied": False,
        "checks": checks,
        "counts": {
            "sessions": len(sessions),
            "practice_attempts": len(practice_rows),
            "mastery_evidence": len(store.list("mastery_evidence")),
            "review_queue": len(reviews),
            "case_attempts": len(store.list("case_attempts")),
            "essay_attempts": len(store.list("essay_attempts")),
            "study_events": len(events),
            "audit_log": len(audits),
        },
        "weekly_report": weekly,
        "issues": [
            {
                "id": "P7-SIM-001",
                "status": "FIXED_AND_REGRESSION_TESTED",
                "summary": "review_queue lacked an allowlisted completion transition, so due reviews could remain pending forever",
                "fix": "added complete_review with timestamp, evidence reference, audit and rescheduling support",
            },
            {
                "id": "P7-SIM-002",
                "status": "FIXED_AND_REGRESSION_TESTED",
                "summary": "the lightweight pilot import path unnecessarily required the optional PDF runtime",
                "fix": "made architectpass_materials public exports lazy and added an import regression without pdfplumber",
            },
        ],
        "limitations": [
            "This validates functional time progression, not seven days of real unattended reliability.",
            "Synthetic post-submission metadata was used; no external question was answered or submitted.",
            "Production Doubao, Feishu and Cheko were intentionally not mutated by this simulation.",
        ],
    }
