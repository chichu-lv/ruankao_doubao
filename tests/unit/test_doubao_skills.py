import json
import re
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SKILLS_ROOT = ROOT / "skills" / "doubao"
EXPECTED = {
    "ruankao-controller-v1",
    "ruankao-materials-v1",
    "cheko-practice-v1",
    "ruankao-assessment-v1",
    "ruankao-case-coach-v1",
    "ruankao-essay-coach-v1",
    "ruankao-review-scheduler-v1",
    "ruankao-research-verifier-v1",
    "ruankao-healthcheck-v1",
}


class DoubaoSkillPackageTests(unittest.TestCase):
    def test_git_bootstrap_is_the_documented_delivery_entry(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        bootstrap = (ROOT / "deployment" / "doubao" / "bootstrap-v1.md").read_text(encoding="utf-8")
        project = json.loads((ROOT / "deployment" / "doubao" / "project-v1.json").read_text(encoding="utf-8"))
        self.assertIn("豆包一键初始化", readme)
        self.assertIn("<你的私有 Git 仓库链接>", readme)
        self.assertIn("FETCH → VERIFY → BUILD → CREATE_PRIVATE_PROJECT", bootstrap)
        self.assertIn("01_豆包软考私教系统_Codex开发说明书.md", bootstrap)
        self.assertIn("04_验收清单.md", bootstrap)
        self.assertEqual("deployment/doubao/bootstrap-v1.md", project["bootstrap_protocol"])
        self.assertIn("private Git", project["delivery_source"])

    def test_exact_nine_versioned_single_responsibility_skills(self) -> None:
        actual = {path.name for path in SKILLS_ROOT.iterdir() if path.is_dir()}
        self.assertEqual(EXPECTED, actual)
        for name in actual:
            text = (SKILLS_ROOT / name / "SKILL.md").read_text(encoding="utf-8")
            self.assertRegex(text, rf"\A---\nname: {re.escape(name)}\ndescription: .+\n---\n")
            self.assertIn("## 输出", text)
            self.assertIn("## 安全边界", text)

    def test_manifest_is_private_minimum_permission_and_no_scheduled_writes(self) -> None:
        manifest = json.loads((ROOT / "deployment" / "doubao" / "skills-v1.json").read_text(encoding="utf-8"))
        self.assertEqual("private_only", manifest["visibility"])
        self.assertEqual("zip_with_named_skill_directory", manifest["package_format"])
        self.assertEqual(EXPECTED, {item["name"] for item in manifest["skills"]})
        self.assertFalse(json.loads(
            (ROOT / "deployment" / "doubao" / "schedules-v1.json").read_text(encoding="utf-8")
        )["scheduled_writes_enabled"])
        health = next(item for item in manifest["skills"] if item["name"] == "ruankao-healthcheck-v1")
        self.assertEqual([], health["writes"])

    def test_sensitive_and_cheko_operations_are_forbidden(self) -> None:
        manifest = json.loads((ROOT / "deployment" / "doubao" / "skills-v1.json").read_text(encoding="utf-8"))
        forbidden = set(manifest["forbidden_capabilities"])
        self.assertTrue({
            "cheko_select_answer", "cheko_submit_answer", "pre_submission_answer_read",
            "private_api_reverse_engineering", "public_publish", "unconfirmed_delete",
        } <= forbidden)

    def test_rendered_system_instructions_have_no_deployment_placeholders(self) -> None:
        text = (ROOT / "deployment" / "doubao" / "system-instructions-v1.md").read_text(encoding="utf-8")
        self.assertNotIn("{{", text)
        self.assertNotIn("最终系统指令模板", text)
        for name in EXPECTED:
            self.assertIn(name, text)
        self.assertIn("ArchitectPass State v1", text)
        self.assertIn("历史成绩均为可选信息", text)
        self.assertIn("历史成绩不属于必问信息", text)

    def test_project_onboarding_does_not_require_exam_history(self) -> None:
        project = json.loads((ROOT / "deployment" / "doubao" / "project-v1.json").read_text(encoding="utf-8"))
        self.assertFalse(project["onboarding"]["past_exam_attempts_required"])
        self.assertFalse(project["onboarding"]["past_exam_scores_required"])

    def test_built_packages_use_observed_named_skill_directory_format(self) -> None:
        output = ROOT / "dist" / "doubao-skills"
        manifest = json.loads((output / "build-manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(EXPECTED, {item["name"] for item in manifest["packages"]})
        for item in manifest["packages"]:
            with zipfile.ZipFile(output / item["package"]) as package:
                self.assertIn(f"{item['name']}/SKILL.md", package.namelist())
                self.assertFalse(any(name.startswith("/") or ".." in Path(name).parts for name in package.namelist()))


if __name__ == "__main__":
    unittest.main()
