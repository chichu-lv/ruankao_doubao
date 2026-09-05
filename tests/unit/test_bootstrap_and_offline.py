import json
import importlib.util
import tempfile
import unittest
import zipfile
import shutil
import hashlib
from pathlib import Path

from architectpass_offline import BundleError, OfflineBundleBuilder


ROOT = Path(__file__).resolve().parents[2]
AUTHORIZED_ROOTS = (
    "00、【推荐】【26年10月】wen老师架构课程（第二版）",
    "5、【2026年05月】芝士架构系统架构设计师",
)


class OfflineBundleTests(unittest.TestCase):
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
