"""Windows release smoke test with a relocated no-Git new-user directory.

Uses tiny generated PDF fixtures; private learning materials never enter CI.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    if os.name != "nt":
        raise SystemExit("This acceptance test requires real Windows")
    from tests.unit.test_materials import write_minimal_pdf, MARKER

    with tempfile.TemporaryDirectory(prefix="ap-accept-") as temporary:
        base = Path(temporary)
        bundle = base / "新用户 空格" / "ArchitectPass-offline"
        project = bundle / "project"
        project.mkdir(parents=True)
        source_zip = base / "source.zip"
        subprocess.run(["git", "archive", "--format=zip", "-o", str(source_zip), "HEAD"], cwd=ROOT, check=True)
        with zipfile.ZipFile(source_zip) as package:
            package.extractall(project)
        (project / "vendor").mkdir()
        shutil.copy2(ROOT / "vendor/python-windows-amd64.zip", project / "vendor")
        shutil.copytree(ROOT / "vendor/wheels-windows", project / "vendor/wheels-windows")
        assert not (project / ".git").exists()
        roots = json.loads((ROOT / "materials/manifests/authorized-sources-v1.json").read_text(encoding="utf-8"))["authorization"]["allowed_remote_roots"]
        records = []
        for root in roots:
            relative = root + "/新用户练习.pdf"
            pdf = bundle / "private-materials" / relative
            pdf.parent.mkdir(parents=True)
            write_minimal_pdf(pdf)
            records.append({"path": relative, "size_bytes": pdf.stat().st_size})
        (bundle / "offline-manifest.json").write_text(json.dumps({"materials": records, "authorized_roots": roots}), encoding="utf-8")
        environment = {**os.environ, "PYTHONUTF8": "1", "PIP_NO_INDEX": "1",
                       "HTTP_PROXY": "http://127.0.0.1:1", "HTTPS_PROXY": "http://127.0.0.1:1"}
        # Keep only Windows built-ins: no preinstalled Python, Git, uv, or PDF tools.
        environment["PATH"] = os.pathsep.join([os.environ["SystemRoot"], os.environ["SystemRoot"] + r"\System32",
                                              os.environ["SystemRoot"] + r"\System32\WindowsPowerShell\v1.0"])

        def run(command):
            result = subprocess.run(command, cwd=project, env=environment, text=True, encoding="utf-8", capture_output=True)
            print(result.stdout)
            print(result.stderr)
            if result.returncode:
                raise RuntimeError(f"command failed ({result.returncode}): {command}")
            return result

        run([environment["SystemRoot"] + r"\System32\cmd.exe", "/c", str(project / "scripts/start_windows.cmd")])
        report = json.loads((project / "dist/bootstrap/local-bootstrap-result.json").read_text(encoding="utf-8"))
        assert report["status"] in {"PASS", "PARTIAL"} and report["installer"] == "bundled_windows_wheels"
        interpreter = str(project / ".runtime/python/python.exe")
        run([interpreter, "-X", "utf8", "scripts/prepare_offline_materials.py"])
        first = json.loads(run([interpreter, "-X", "utf8", "scripts/prepare_offline_materials.py", "--search", MARKER]).stdout)
        assert first["results"] and first["results"][0]["page"] == 1
        run([interpreter, "-X", "utf8", "scripts/prepare_offline_materials.py"])
        relocated = base / "移动后的 新目录"
        shutil.move(str(bundle), relocated)
        project = relocated / "project"
        interpreter = str(project / ".runtime/python/python.exe")
        run([environment["SystemRoot"] + r"\System32\cmd.exe", "/c", str(project / "scripts/start_windows.cmd"), "--prepare-only"])
        run([interpreter, "-X", "utf8", "scripts/prepare_offline_materials.py"])
        final = json.loads(run([interpreter, "-X", "utf8", "scripts/prepare_offline_materials.py", "--search", MARKER]).stdout)
        assert str(relocated) in final["results"][0]["open_target"]
        result = {"status": "PASS", "platform": sys.platform, "python": sys.version,
                  "bootstrap": report, "checks": ["no_git", "no_python_on_path", "offline_bundled_dependencies",
                  "chinese_and_space_paths", "six_healthchecks", "pdf_index_and_search", "repeat_install", "relocated_restart"]}
    output = ROOT / "dist/acceptance/windows-clean-install.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
