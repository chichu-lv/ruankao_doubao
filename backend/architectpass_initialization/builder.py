from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


class InitializationError(ValueError):
    pass


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _stable_id(prefix: str, value: str) -> str:
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()[:20]
    return f"{prefix}-{digest}"


class Phase6Builder:
    """Builds an auditable write plan from already-authorized, traceable evidence."""

    def __init__(self, root: Path) -> None:
        self.root = root.resolve()

    def build(self) -> dict[str, Any]:
        sources = _load(self.root / "materials/manifests/authorized-sources-v1.json")
        progress = _load(self.root / "materials/manifests/video-progress-v1.json")
        cheko = _load(self.root / "tests/fixtures/cheko-submitted-report-sanitized.json")
        knowledge = _load(self.root / "deployment/phase6/knowledge-map-v1.json")
        facts = _load(self.root / "deployment/phase6/project-facts-v1.json")
        seven_day = _load(self.root / "deployment/phase6/initial-seven-day-plan-v1.json")

        self._validate_sources(sources)
        self._validate_facts(facts)
        self._validate_plan(seven_day)
        operations: list[dict[str, Any]] = []

        operations.append(self._operation(
            "update_profile", "user_profile", "architectpass-user",
            {
                "user_id": "architectpass-user",
                "target_exam": "系统架构设计师",
                "timezone": "Asia/Shanghai",
                "current_video_progress": {
                    "course_scope": progress["course_scope"],
                    "reported_fraction": progress["reported_progress"]["approximate_fraction"],
                    "confidence": progress["reported_progress"]["confidence"],
                },
            },
            "phase6-profile-v1",
        ))

        for node in knowledge["nodes"]:
            operations.append(self._operation(
                "upsert_topic", "topics", node["topic_id"], node, f"phase6-topic-{node['topic_id']}"
            ))

        for item in sources["resources"]:
            if item["kind"] not in {"pdf", "video"} or not item.get("checksum"):
                continue
            checksum = item["checksum"].removeprefix("sha256:")
            resource_id = f"sha256:{checksum}"
            operations.append(self._operation(
                "upsert_resource", "resources", resource_id,
                {
                    "resource_id": resource_id,
                    "type": item["kind"],
                    "title": Path(item["relative_path"]).name,
                    "local_path_or_uri": f"baidunetdisk://{item['remote_root']}/{item['relative_path']}",
                    "copyright_scope": "private_personal_exam_study",
                    "processing_status": item["status"],
                    "checksum": item["checksum"],
                    "created_at": sources["generated_at"],
                },
                f"phase6-resource-{checksum[:16]}",
            ))

        for observation in progress["observations"]:
            video_key = f"{progress['course_scope']}/{observation['video']}"
            video_id = _stable_id("video", video_key)
            operations.append(self._operation(
                "update_video_progress", "video_progress", video_id,
                {
                    "video_id": video_id,
                    "watched_until": observation["watched_until_seconds"],
                    "status": observation["status"],
                    "last_watched_at": "2026-09-04T00:00:00Z",
                    "recall_checked": observation["recall_checked"],
                    "practice_checked": observation["practice_checked"],
                    "needs_rewatch": observation["needs_rewatch"],
                    "source_anchor": observation["source_anchor"],
                },
                f"phase6-progress-{video_id}",
            ))

        result = cheko["result"]
        summary = result["summary"]
        operations.append(self._operation(
            "record_study_event", "study_events", "phase6-cheko-baseline-710358",
            {
                "event_id": "phase6-cheko-baseline-710358",
                "event_type": "cheko_submitted_aggregate_baseline",
                "topic_ids": ["choice-databases"],
                "payload": {
                    "question_count": summary["question_count"],
                    "score_display": summary["score_display"],
                    "elapsed_display": summary["elapsed_display"],
                    "aggregate_only": True,
                    "mastery_update_allowed": False,
                },
                "source_ref": {
                    "cheko_result_id": result["cheko_result_id"],
                    "import_method": result["import_method"],
                    "ui_contract_version": result["ui_contract_version"],
                },
                "occurred_at": result["observed_at"],
            },
            "phase6-cheko-baseline-710358",
        ))

        return {
            "schema_version": 1,
            "status": "ready_for_verified_write",
            "history_required": False,
            "scheduled_writes_enabled": False,
            "operations": operations,
            "local_index_sources": [
                "materials/index/phase2-real-pdf-ocr-catalog.json",
                "materials/index/phase2-real-video-catalog-v3.json",
            ],
            "local_index_policy": "private runtime files; import segments only after exact-path and anchor validation",
            "project_facts": {"status": facts["status"], "fact_count": len(facts["facts"])},
            "seven_day_plan": seven_day,
        }

    def build_private_segments(self, pdf_catalog: Path, video_catalog: Path) -> dict[str, Any]:
        allowed = {
            (self.root / "materials/index/phase2-real-pdf-ocr-catalog.json").resolve(),
            (self.root / "materials/index/phase2-real-video-catalog-v3.json").resolve(),
        }
        supplied = {pdf_catalog.resolve(), video_catalog.resolve()}
        if supplied != allowed:
            raise InitializationError("private segment inputs must be the two exact allowlisted runtime catalogs")
        pdf = _load(pdf_catalog)
        video = _load(video_catalog)
        video_source = next(
            item["metadata"]["video_source_id"]
            for item in video["resources"]
            if item.get("media_type") == "transcript"
        )
        operations: list[dict[str, Any]] = []
        for kind, catalog in (("pdf", pdf), ("video", video)):
            for segment in catalog["segments"]:
                resource_id = segment["resource_id"] if kind == "pdf" else video_source
                record = {
                    "segment_id": segment["segment_id"],
                    "resource_id": resource_id,
                    "page_start": segment.get("page"),
                    "page_end": segment.get("page"),
                    "time_start": segment.get("start_seconds"),
                    "time_end": segment.get("end_seconds"),
                    "section": segment.get("section"),
                    "text": segment.get("text", ""),
                    "keywords": [],
                    "topic_ids": [],
                    "citation_anchor": segment["citation_anchor"],
                }
                operations.append(self._operation(
                    "upsert_resource_segment", "resource_segments", segment["segment_id"], record,
                    f"phase6-segment-{segment['segment_id']}",
                ))
        if len(operations) != 49:
            raise InitializationError(f"expected 49 private segments, got {len(operations)}")
        if len({item["record_id"] for item in operations}) != len(operations):
            raise InitializationError("private segment IDs must be unique")
        return {
            "schema_version": 1,
            "status": "private_runtime_only",
            "git_commit_allowed": False,
            "source_catalogs": [str(path.relative_to(self.root)) for path in sorted(supplied)],
            "operations": operations,
        }

    @staticmethod
    def _operation(operation: str, table: str, record_id: str, record: dict[str, Any], key: str) -> dict[str, Any]:
        return {
            "operation": operation,
            "table": table,
            "record_id": record_id,
            "record": record,
            "request_id": f"req-{key}",
            "audit_id": f"audit-{key}",
        }

    @staticmethod
    def _validate_sources(sources: dict[str, Any]) -> None:
        if sources.get("authorization", {}).get("privacy") != "private":
            raise InitializationError("material sources must remain private")
        if len(sources.get("authorization", {}).get("allowed_remote_roots", [])) != 2:
            raise InitializationError("exactly the two user-authorized source roots are required")

    @staticmethod
    def _validate_facts(facts: dict[str, Any]) -> None:
        for fact in facts.get("facts", []):
            if fact.get("confirmed_by_user") is not True or fact.get("redacted") is not True:
                raise InitializationError("project facts must be user-confirmed and redacted")

    @staticmethod
    def _validate_plan(plan: dict[str, Any]) -> None:
        if len(plan.get("days", [])) != 7:
            raise InitializationError("initial plan must contain seven days")
        for day in plan["days"]:
            total = sum(float(item["budget_fraction"]) for item in day["tasks"])
            total += float(day["checkpoint_reserve_fraction"])
            if total > 1.0 + 1e-9:
                raise InitializationError(f"day {day['day']} exceeds its runtime budget")
