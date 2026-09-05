import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("folder_install", ROOT / "scripts/install_doubao_folder_skills.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class FolderSkillInstallTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        base = Path(self.temp.name)
        self.project = base / "新用户 项目"
        self.project.mkdir()
        for path in ("skills/doubao", "deployment/doubao"):
            shutil.copytree(ROOT / path, self.project / path)
        shutil.copyfile(ROOT / "VERSION", self.project / "VERSION")
        self.skill_root = base / "runtime/workspace/.user_skills"
        self.skill_root.mkdir(parents=True)

    def test_install_binding_and_repeat_preserve_skills(self):
        first = module.install(self.project, self.skill_root, "req-1")
        self.assertEqual(9, len(first["created"]))
        self.assertEqual("FILES_READY_DISCOVERY_UNVERIFIED", first["status"])
        self.assertFalse(first["account_registry_modified"])
        binding = json.loads((self.skill_root / "ruankao-controller-v1/references/installation.json").read_text())
        self.assertEqual(str(self.project.resolve()), binding["project_root"])
        self.assertIn("references/installation.json", (self.skill_root / "ruankao-controller-v1/SKILL.md").read_text())
        second = module.install(self.project, self.skill_root, "req-2")
        self.assertEqual([], second["created"])
        self.assertEqual(9, len(second["reused"]))
        self.assertEqual("folder-install-req-2", second["audit_id"])
        self.assertEqual([], list(self.skill_root.rglob("*.sha*")))

    def test_conflict_preflight_does_not_partially_install(self):
        conflict = self.skill_root / "ruankao-healthcheck-v1"
        conflict.mkdir()
        (conflict / "SKILL.md").write_text("existing user's version")
        with self.assertRaisesRegex(ValueError, "existing skill differs"):
            module.install(self.project, self.skill_root, "conflict")
        self.assertEqual([conflict], list(self.skill_root.iterdir()))
        self.assertEqual("existing user's version", (conflict / "SKILL.md").read_text())

    def test_refuse_wrong_skill_root(self):
        with self.assertRaisesRegex(ValueError, "official workspace"):
            module.install(self.project, self.project, "wrong-root")

    def test_other_project_binding_cannot_be_overwritten(self):
        module.install(self.project, self.skill_root, "first")
        another = self.project.parent / "other-project"
        shutil.copytree(self.project, another)
        with self.assertRaisesRegex(ValueError, "existing skill differs"):
            module.install(another, self.skill_root, "different-project")

    def test_unrelated_skill_is_untouched(self):
        unrelated = self.skill_root / "unrelated"
        unrelated.mkdir()
        (unrelated / "SKILL.md").write_text("keep")
        module.install(self.project, self.skill_root, "unrelated")
        self.assertEqual("keep", (unrelated / "SKILL.md").read_text())

    def test_public_and_offline_entries_prefer_official_folder_route(self):
        for path in ("README.md", "deployment/doubao/bootstrap-v1.md", "deployment/offline/bootstrap-v1.md"):
            text = (ROOT / path).read_text()
            self.assertIn("folder-skills-v1.md", text)
        guide = (ROOT / "deployment/doubao/folder-skills-v1.md").read_text()
        self.assertIn("FILES_READY_DISCOVERY_UNVERIFIED", guide)
        self.assertIn("界面消失不等于文件夹源已消失", guide)
        self.assertIn("没有可见性选项", guide)

    def test_first_install_never_searches_home_for_developer_history(self):
        readme = (ROOT / "README.md").read_text()
        self.assertIn("未明确要求恢复时，按首次安装", readme)
        self.assertIn("不要扫描主目录", readme)
        context = (ROOT / "deployment/doubao/execution-context-v1.md").read_text()
        self.assertIn("首次安装不等于全盘找旧项目", context)
        self.assertIn("不存在恢复授权不能被解释", context)
