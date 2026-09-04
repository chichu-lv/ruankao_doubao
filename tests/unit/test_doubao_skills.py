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
        self.assertIn("https://github.com/chichu-lv/ruankao_doubao.git", readme)
        self.assertIn("main 分支", readme)
        self.assertIn("FETCH → VERIFY → BUILD → CREATE_PRIVATE_PROJECT", bootstrap)
        self.assertIn("01_豆包软考私教系统_Codex开发说明书.md", bootstrap)
        self.assertIn("04_验收清单.md", bootstrap)
        self.assertEqual("deployment/doubao/bootstrap-v1.md", project["bootstrap_protocol"])
        self.assertEqual(
            "https://github.com/chichu-lv/ruankao_doubao.git#main",
            project["delivery_source"],
        )
        self.assertEqual("current_git_checkout_root", project["local_folder_binding"]["path_strategy"])
        self.assertNotIn("/Users/", json.dumps(project))

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

    def test_weekly_schedule_matches_release_target(self) -> None:
        schedules = json.loads(
            (ROOT / "deployment" / "doubao" / "schedules-v1.json").read_text(encoding="utf-8")
        )
        weekly = next(
            item for item in schedules["jobs"]
            if item["name"] == "架构上岸教练-每周只读复盘-v1"
        )
        self.assertEqual("desired_active_user_confirmed", weekly["status"])
        self.assertEqual({
            "repeat": "weekly",
            "weekday": "saturday",
            "time": "20:00",
            "timezone": "Asia/Shanghai",
        }, weekly["schedule"])
        self.assertEqual([], weekly["write_operations"])

        prompt = (ROOT / weekly["prompt_file"]).read_text(encoding="utf-8")
        self.assertIn("ArchitectPass State v1", prompt)
        self.assertIn("每次必须重新只读统计", prompt)
        self.assertIn("workflow_test", prompt)
        self.assertIn("零状态写入、零审计写入", prompt)
        self.assertIn("不得显示或部分显示", prompt)
        self.assertIn("base_token", prompt)
        self.assertNotIn("manual_execution_evidence", weekly)

    def test_release_manifest_contains_no_private_feishu_identifiers(self) -> None:
        deployment = json.loads(
            (ROOT / "deployment" / "feishu" / "production-v1.json").read_text(encoding="utf-8")
        )
        self.assertNotIn("base_id", deployment)
        self.assertNotIn("base_url", deployment)
        self.assertEqual(15, len(deployment["tables"]))
        self.assertEqual("schemas/feishu-bitable-v1.json", deployment["table_contract"])

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

    def test_built_packages_use_named_skill_directory_format(self) -> None:
        output = ROOT / "dist" / "doubao-skills"
        manifest = json.loads((output / "build-manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(EXPECTED, {item["name"] for item in manifest["packages"]})
        for item in manifest["packages"]:
            with zipfile.ZipFile(output / item["package"]) as package:
                self.assertIn(f"{item['name']}/SKILL.md", package.namelist())
                self.assertFalse(any(name.startswith("/") or ".." in Path(name).parts for name in package.namelist()))


if __name__ == "__main__":
    unittest.main()
