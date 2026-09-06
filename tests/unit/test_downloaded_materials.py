import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
spec = importlib.util.spec_from_file_location("downloaded_materials", ROOT / "scripts/prepare_downloaded_materials.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
from tests.unit.test_materials import write_minimal_pdf


class DownloadedMaterialsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        base = Path(self.temp.name)
        self.project = base / "project"
        shutil.copytree(ROOT / "deployment/doubao", self.project / "deployment/doubao")
        self.source = base / "Downloads"
        self.source.mkdir()
        self.names = json.loads((ROOT / "deployment/doubao/project-v1.json").read_text())["materials"]["authorized_baidu_scopes"]

    def test_only_two_scoped_folders_are_indexed_and_repeat_is_idempotent(self):
        for name in self.names:
            folder = self.source / name
            folder.mkdir()
            write_minimal_pdf(folder / "sample.pdf")
        (self.source / "unrelated-secret.txt").write_text("must not be indexed")
        first = module.prepare_downloaded(self.project, self.source)
        second = module.prepare_downloaded(self.project, self.source)
        self.assertEqual("PASS", first["status"])
        self.assertEqual(2, first["material_file_count"])
        self.assertGreater(first["page_count"], 0)
        self.assertEqual(0, second["newly_indexed_pdf_count"])
        self.assertEqual("UNVERIFIED_BY_THIS_LOCAL_IMPORT", first["baidu_remote_status"])
        self.assertFalse((self.source / "offline-manifest.json").exists())
        inventory = (self.project / "materials/index/downloaded-inventory.json").read_text()
        self.assertNotIn("unrelated-secret", inventory)
        self.assertTrue(module.search(self.project, "architecture", "downloaded")["status"] == "PASS")

    def test_missing_sources_are_partial_not_remote_failure_or_success(self):
        result = module.prepare_downloaded(self.project, self.source)
        self.assertEqual("PARTIAL", result["status"])
        self.assertEqual(self.names, result["missing_authorized_roots"])
        self.assertFalse((self.project / "materials/index").exists())

    def test_bootstrap_bounds_tool_discovery_and_separates_browser_gui(self):
        context = (ROOT / "deployment/doubao/execution-context-v1.md").read_text()
        self.assertIn("最多检索两次", context)
        self.assertIn("CONNECTOR_NOT_CALLABLE", context)
        self.assertIn("电脑 GUI 不可用不代表独立浏览器工具也不可用", context)
        bootstrap = (ROOT / "deployment/doubao/bootstrap-v1.md").read_text()
        self.assertIn("prepare_downloaded_materials.py", bootstrap)
        self.assertIn("不以这次人工创建为前置条件", bootstrap)

    def test_local_course_bootstrap_does_not_depend_on_netdisk_tool_discovery(self):
        for filename in ("deployment/doubao/bootstrap-v1.md", "skills/doubao/ruankao-materials-v1/SKILL.md", "skills/doubao/ruankao-healthcheck-v1/SKILL.md"):
            text = (ROOT / filename).read_text()
            self.assertIn("DEFERRED_NOT_REQUIRED_FOR_LOCAL_STUDY", text)
        self.assertIn("不要检索或调用百度网盘连接器", (ROOT / "README.md").read_text())
