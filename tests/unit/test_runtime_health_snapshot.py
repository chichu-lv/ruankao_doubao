import importlib.util
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("runtime_health", ROOT / "scripts/runtime_health_snapshot.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class RuntimeHealthSnapshotTests(unittest.TestCase):
    def fixture(self):
        return ({"materials": [{"path": "a.pdf", "source_path": "/a.pdf", "type": "pdf"}]},
                {"resources": [{"media_type": "pdf", "source_path": "/a.pdf"}],
                 "segments": [{"text": "architecture", "confidence": 1}]})

    def test_complete_pdf_only_scope(self):
        inventory, catalog = self.fixture()
        self.assertEqual("PASS", module.summarize_index(inventory, catalog)["status"])

    def test_registered_but_unindexed_is_partial(self):
        inventory, catalog = self.fixture()
        inventory["materials"].append({"path": "b.pdf", "source_path": "/b.pdf"})
        result = module.summarize_index(inventory, catalog)
        self.assertEqual("PARTIAL", result["status"])
        self.assertEqual(1, result["unindexed_pdf_files"])
        self.assertTrue(result["usable_for_page_search"])

    def test_pending_ocr_and_video_never_mean_complete(self):
        inventory, catalog = self.fixture()
        catalog["segments"].append({"text": "", "confidence": 0})
        inventory["materials"].append({"path": "lesson.mp4"})
        result = module.summarize_index(inventory, catalog)
        self.assertEqual(1, result["ocr_pending_pages"])
        self.assertFalse(result["coverage_complete"])

    def test_snapshot_is_readonly_and_cannot_certify_external_services(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = module.snapshot(root)
            self.assertEqual("PARTIAL", result["overall_status"])
            self.assertFalse(result["state_binding_present"])
            self.assertEqual([], list(root.iterdir()))

    def test_current_session_rules_separate_simulation_from_diagnosis(self):
        for filename in ("deployment/doubao/system-instructions-v1.md", "skills/doubao/ruankao-controller-v1/SKILL.md", "skills/doubao/ruankao-assessment-v1/SKILL.md"):
            text = (ROOT / filename).read_text()
            self.assertIn("mastery_eligible=false", text)
            self.assertIn("NOT_ASSESSED", text)
        self.assertIn("runtime_health_snapshot.py", (ROOT / "skills/doubao/ruankao-healthcheck-v1/SKILL.md").read_text())

    def test_checked_at_is_current_clock_with_explicit_timezone(self):
        before = datetime.now(timezone.utc).replace(microsecond=0)
        with tempfile.TemporaryDirectory() as directory:
            result = module.snapshot(Path(directory))
        checked = datetime.fromisoformat(result["checked_at"])
        self.assertIsNotNone(checked.utcoffset())
        self.assertGreaterEqual(checked, before)
        self.assertLessEqual(checked, datetime.now(timezone.utc))
        health = (ROOT / "skills/doubao/ruankao-healthcheck-v1/SKILL.md").read_text()
        self.assertIn("checked_at", health)
        self.assertIn("不得手写", health)

    def test_empty_profile_is_unassessed_not_knowledge_deficit(self):
        for filename in ("deployment/doubao/system-instructions-v1.md", "skills/doubao/ruankao-controller-v1/SKILL.md", "skills/doubao/ruankao-assessment-v1/SKILL.md"):
            rules = (ROOT / filename).read_text()
            self.assertIn("空档案", rules)
            self.assertIn("不填 0 级", rules)
            self.assertIn("NOT_ASSESSED", rules)

    def test_material_filename_is_not_segment_content_evidence(self):
        rules = (ROOT / "skills/doubao/ruankao-materials-v1/SKILL.md").read_text()
        self.assertIn("视频文件名和总时长不能证明", rules)
        self.assertIn("不写已观看进度", rules)
