import json
import importlib.util
import tempfile
import unittest
import zipfile
import shutil
import hashlib
from unittest import mock
from types import SimpleNamespace
from pathlib import Path

from architectpass_offline import BundleError, OfflineBundleBuilder


ROOT = Path(__file__).resolve().parents[2]
AUTHORIZED_ROOTS = (
    "00、【推荐】【26年10月】wen老师架构课程（第二版）",
    "5、【2026年05月】芝士架构系统架构设计师",
)


class OfflineBundleTests(unittest.TestCase):
    def test_generated_offline_prompt_prevents_nested_doubao_login(self) -> None:
        readme = OfflineBundleBuilder._offline_readme("COMPLETE")
        for required in (
            "你就是当前执行部署的豆包", "不要打开另一个豆包",
            "在虚拟桌面登录豆包", "execution-context-v1.md",
            "具体点击", "已有本次项目和状态先核对后继续",
        ):
            self.assertIn(required, readme)

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.base = Path(self.temporary.name)
        self.materials = self.base / "materials"
        for name in AUTHORIZED_ROOTS:
            (self.materials / name).mkdir(parents=True)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_complete_label_is_refused_when_declared_files_are_missing(self) -> None:
        with self.assertRaisesRegex(BundleError, "declared material files are absent"):
            OfflineBundleBuilder(ROOT).build(
                materials_root=self.materials,
                output_directory=self.base / "output",
                enforce_release_git=False,
                include_runtime_assets=False,
            )

    def test_partial_bundle_is_private_self_describing_and_installable(self) -> None:
        (self.materials / AUTHORIZED_ROOTS[0] / "sample.mp4").write_bytes(b"private-video-fixture")
        (self.materials / AUTHORIZED_ROOTS[1] / "sample.pdf").write_bytes(b"private-pdf-fixture")
        result = OfflineBundleBuilder(ROOT).build(
            materials_root=self.materials,
            output_directory=self.base / "output",
            allow_incomplete=True,
            enforce_release_git=False,
            include_runtime_assets=False,
        )
        self.assertEqual("PARTIAL", result["status"])
        self.assertIn("PARTIAL", Path(result["archive"]).name)
        self.assertGreater(len(result["declared_missing"]), 0)
        second = OfflineBundleBuilder(ROOT).build(
            materials_root=self.materials,
            output_directory=self.base / "output-second",
            allow_incomplete=True,
            enforce_release_git=False,
            include_runtime_assets=False,
        )
        self.assertEqual(result["sha256"], second["sha256"])
        spec = importlib.util.spec_from_file_location("verify_offline_bundle", ROOT / "scripts/verify_offline_bundle.py")
        verifier = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(verifier)
        verified = verifier.verify_bundle(Path(result["archive"]))
        self.assertEqual("PARTIAL", verified["status"])
        self.assertEqual(9, verified["skill_count"])
        self.assertEqual([], verified["errors"])
        with zipfile.ZipFile(result["archive"]) as archive:
            names = archive.namelist()
            self.assertIn("ArchitectPass-offline/README-OFFLINE.md", names)
            self.assertIn("ArchitectPass-offline/offline-manifest.json", names)
            self.assertIn("ArchitectPass-offline/project/README.md", names)
            self.assertIn("ArchitectPass-offline/project/deployment/doubao/execution-context-v1.md", names)
            self.assertIn("ArchitectPass-offline/project/deployment/doubao/folder-skills-v1.md", names)
            self.assertIn("ArchitectPass-offline/project/scripts/install_doubao_folder_skills.py", names)
            self.assertEqual(9, len([name for name in names if name.startswith("ArchitectPass-offline/prebuilt-skills/") and name.endswith(".zip")]))
            manifest = json.loads(archive.read("ArchitectPass-offline/offline-manifest.json"))
            self.assertEqual("private_personal_offline_backup", manifest["privacy"])
            self.assertFalse(manifest["redistribution_allowed"])
            self.assertFalse(manifest["contains_credentials"])
            self.assertEqual(2, manifest["material_file_count"])
            self.assertTrue(all(item.date_time == (1980, 1, 1, 0, 0, 0) for item in archive.infolist()))

    def test_credential_like_file_is_rejected(self) -> None:
        (self.materials / AUTHORIZED_ROOTS[0] / "account-token.txt").write_text("not-a-real-token", encoding="utf-8")
        with self.assertRaisesRegex(BundleError, "credential-like filename"):
            OfflineBundleBuilder(ROOT).build(
                materials_root=self.materials,
                output_directory=self.base / "output",
                allow_incomplete=True,
                enforce_release_git=False,
                include_runtime_assets=False,
            )


class BootstrapContractTests(unittest.TestCase):
    def test_private_pip_is_seeded_offline_only_when_missing(self):
        spec = importlib.util.spec_from_file_location("bootstrap_local_pip", ROOT / "scripts/bootstrap_local.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        interpreter = ROOT / ".venv/bin/python3"
        with mock.patch.object(module.subprocess, "run", return_value=SimpleNamespace(returncode=0)) as run:
            module.ensure_private_pip(interpreter)
            self.assertEqual(1, run.call_count)
        with mock.patch.object(module.subprocess, "run", side_effect=[SimpleNamespace(returncode=1), SimpleNamespace(returncode=0)]) as run:
            module.ensure_private_pip(interpreter)
            self.assertEqual([str(interpreter), "-m", "ensurepip", "--upgrade"], run.call_args_list[1].args[0])
        with mock.patch.object(module.subprocess, "run", return_value=SimpleNamespace(returncode=1)):
            with self.assertRaisesRegex(module.BootstrapError, "no system Python was modified"):
                module.ensure_private_pip(interpreter)

    def test_public_windows_source_entry_needs_no_git_or_python(self):
        launcher = (ROOT / "scripts/install_public_windows.ps1").read_text(encoding="utf-8")
        self.assertIn("https://codeload.github.com/chichu-lv/ruankao_doubao/zip/refs/heads/main", launcher)
        self.assertIn("$FetchOnly", launcher)
        self.assertIn("public-source.json", launcher)
        self.assertIn("does not overwrite or upgrade", launcher)
        self.assertNotIn("git clone", launcher)
        self.assertNotIn("Set-ExecutionPolicy", launcher)
        self.assertIn("download_windows_runtime.ps1", launcher)
        self.assertIn("start_windows.ps1", launcher)

    def test_public_bootstrap_keeps_source_and_material_archives_distinct(self):
        guide = (ROOT / "deployment/doubao/bootstrap-v1.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertNotIn("私有 Git 仓库", readme)
        self.assertIn("源码 ZIP 没有课程原文件", guide)
        self.assertIn("源码 ZIP 不检查 .git", guide)
        self.assertIn("客户端会话与浏览器会话不视为共享", guide)
        self.assertIn("不代表可以继承原用户观看进度", guide)

    def test_public_windows_acceptance_retains_readonly_actions(self):
        workflow = (ROOT / ".github/workflows/windows-acceptance.yml").read_text(encoding="utf-8")
        probe = (ROOT / "scripts/test_windows_public_install.ps1").read_text(encoding="utf-8")
        self.assertIn("contents: read", workflow)
        self.assertNotIn("contents: write", workflow)
        self.assertIn("test_windows_public_install.ps1", workflow)
        self.assertIn("raw.githubusercontent.com", probe)
        self.assertIn("Unexpected preinstalled tool", probe)
        self.assertIn("repeat_preserves_source_and_user_file", probe)

    def test_windows_download_contract_pins_the_complete_wheelhouse(self):
        manifest = json.loads((ROOT / "deployment/offline/windows-runtime-v1.json").read_text(encoding="utf-8"))
        self.assertEqual(8, len(manifest["wheels"]))
        self.assertEqual(8, len({item["filename"] for item in manifest["wheels"]}))
        self.assertTrue(manifest["python_url"].startswith("https://www.python.org/"))
        self.assertTrue(all(item["filename"].endswith(("win_amd64.whl", "none-any.whl")) for item in manifest["wheels"]))

    def test_new_user_bootstrap_requires_verified_idempotent_live_writes(self):
        protocol = (ROOT / "deployment/feishu/write-protocol-v1.md").read_text(encoding="utf-8")
        self.assertIn("data.fields", protocol)
        self.assertIn("data.data", protocol)
        self.assertIn("需新增 0 行", protocol)
        for name in ("deployment/offline/bootstrap-v1.md", "deployment/doubao/bootstrap-v1.md"):
            self.assertIn("write-protocol-v1.md", (ROOT / name).read_text(encoding="utf-8"))
        health = (ROOT / "skills/doubao/ruankao-healthcheck-v1/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("不把账号下其他项目的提醒计入本项目", health)
        self.assertIn("不因未登录网盘降低离线安装状态", health)

    def test_windows_vendored_dependencies_are_relocatable_and_repeatable(self):
        spec = importlib.util.spec_from_file_location("bootstrap_local", ROOT / "scripts/bootstrap_local.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as directory:
            runtime = Path(directory) / "project/.runtime/python"
            wheels = Path(directory) / "wheels"
            wheels.mkdir()
            with zipfile.ZipFile(wheels / "fixture.whl", "w") as wheel:
                wheel.writestr("fixture/__init__.py", "VALUE = 42\n")
            module.install_windows_wheels(runtime, wheels)
            module.install_windows_wheels(runtime, wheels)
            self.assertEqual("VALUE = 42\n", (runtime / "Lib/site-packages/fixture/__init__.py").read_text())
            paths = (runtime / "python312._pth").read_text()
            self.assertIn("../../backend", paths)
            self.assertIn("../../", paths.splitlines())
            self.assertNotIn("../..", paths.splitlines())
            self.assertNotIn(directory, paths)

    def test_readme_uses_the_python39_compatible_bootstrap_entry(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        bootstrap = (ROOT / "deployment/doubao/bootstrap-v1.md").read_text(encoding="utf-8")
        launcher = (ROOT / "scripts/bootstrap_local.py").read_text(encoding="utf-8")
        self.assertIn("python3 scripts/bootstrap_local.py", readme)
        self.assertIn("python3 scripts/bootstrap_local.py", bootstrap)
        self.assertIn("Python 3.9", launcher)
        self.assertIn("UV_CACHE_DIR", launcher)
        self.assertIn(".runtime", launcher)

    def test_healthcheck_classifier_ignores_partial_word_inside_descriptions(self) -> None:
        spec = importlib.util.spec_from_file_location("bootstrap_local", ROOT / "scripts/bootstrap_local.py")
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        self.assertEqual("PASS", module.classify_healthcheck(0, '"description": "outputs PASS/PARTIAL/FAIL"'))
        self.assertEqual("PARTIAL", module.classify_healthcheck(0, "PARTIAL live connector: login deferred"))
        self.assertEqual("FAIL", module.classify_healthcheck(1, "SUMMARY: PASS"))


class OfflineFirstUseTests(unittest.TestCase):
    def test_relocated_package_indexes_searches_and_replays_without_duplicates(self):
        from tests.unit.test_materials import write_minimal_pdf, MARKER
        spec = importlib.util.spec_from_file_location("prepare_offline_materials", ROOT / "scripts/prepare_offline_materials.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as directory:
            bundle = Path(directory) / "中文 空格 delivery"
            project = bundle / "project"
            project.mkdir(parents=True)
            resources = []
            for name in AUTHORIZED_ROOTS:
                relative = name + "/sample.pdf"
                path = bundle / "private-materials" / relative
                path.parent.mkdir(parents=True)
                write_minimal_pdf(path)
                resources.append({"path": relative, "size_bytes": path.stat().st_size,
                                  "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
            (bundle / "offline-manifest.json").write_text(json.dumps({"authorized_roots": AUTHORIZED_ROOTS, "materials": resources}))
            first = module.prepare(project)
            self.assertEqual(2, first["material_file_count"])
            self.assertEqual(1, first["page_count"])
            second = module.prepare(project)
            self.assertEqual(0, second["newly_indexed_pdf_count"])
            renamed = bundle.with_name("移动 后")
            shutil.move(str(bundle), renamed)
            module.prepare(renamed / "project")
            hits = module.search(renamed / "project", MARKER)["results"]
            self.assertEqual(1, hits[0]["page"])
            self.assertTrue(hits[0]["open_target"].startswith(str(renamed.resolve())))
            catalog = module.load(renamed / "project/materials/index/offline-catalog.json")
            self.assertEqual(1, len(catalog["audits"]))


if __name__ == "__main__":
    unittest.main()
