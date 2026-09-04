from __future__ import annotations

from datetime import date
from typing import Any

from .diagnosis import ERROR_MEANINGS


class WeeklyReporter:
    def build(
        self,
        *,
        events: list[dict[str, Any]],
        exam_date: date,
        today: date,
        syllabus_progress: float,
        metrics: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        metrics = metrics or {}
        totals = {"综合知识": 0, "案例分析": 0, "论文": 0}
        for event in events:
            subject = event.get("subject")
            minutes = event.get("minutes", 0)
            if subject in totals and isinstance(minutes, (int, float)) and minutes >= 0:
                totals[subject] += minutes
        total = sum(totals.values())
        ratios = {subject: round(minutes / total, 4) if total else 0.0 for subject, minutes in totals.items()}
        underinvestment = [subject for subject in ("案例分析", "论文") if ratios[subject] < 0.2]

        progress = min(1.0, max(0.0, syllabus_progress))
        threshold_days = round(14 + 21 * (1 - progress))
        days_left = (exam_date - today).days
        sprint_mode = days_left <= threshold_days
        priorities = [f"提高{subject}投入" for subject in underinvestment]
        if sprint_mode:
            priorities.append("进入动态冲刺：提高限时整卷、案例与论文闭环占比")
        error_counts = {
            code: sum(1 for event in events if event.get("error_type") == code)
            for code in ERROR_MEANINGS
        }
        error_counts = {code: count for code, count in error_counts.items() if count}
        if error_counts:
            top_error = sorted(error_counts, key=lambda code: (-error_counts[code], code))[0]
            priorities.append(f"优先修复高频错误 {top_error}（{ERROR_MEANINGS[top_error]}）")
        if metrics.get("fastest_improving_topics"):
            priorities.append(f"巩固提升最快考点：{metrics['fastest_improving_topics'][0]}")
        while len(priorities) < 3:
            priorities.append("按到期队列完成闭卷复习并记录置信度")
        priorities = priorities[:3]
        stop_behaviors = []
        if metrics.get("long_video_without_recall_minutes", 0) > 0:
            stop_behaviors.append("停止无闭卷复述的连续长视频学习")
        if ratios["综合知识"] > 0.8 and underinvestment:
            stop_behaviors.append("停止继续扩大综合知识单科投入失衡")
        return {
            "minutes_by_subject": totals,
            "subject_ratios": ratios,
            "underinvestment": underinvestment,
            "days_left": days_left,
            "sprint_threshold_days": threshold_days,
            "sprint_mode": sprint_mode,
            "threshold_rule": "14 + 21 × remaining_syllabus_fraction",
            "next_week_priorities": priorities,
            "plan_completion_rate": metrics.get("plan_completion_rate"),
            "due_review_completion_rate": metrics.get("due_review_completion_rate"),
            "fastest_improving_topics": metrics.get("fastest_improving_topics", []),
            "largest_declining_topics": metrics.get("largest_declining_topics", []),
            "error_type_counts": error_counts,
            "timed_mock_trend": metrics.get("timed_mock_trend", []),
            "case_point_gaps": metrics.get("case_point_gaps", []),
            "essay_topic_coverage": metrics.get("essay_topic_coverage", []),
            "stop_low_value_behaviors": stop_behaviors,
            "adjustment_basis": {
                "subject_imbalance": underinvestment,
                "error_type_counts": error_counts,
                "progress": progress,
                "days_left": days_left,
            },
        }
