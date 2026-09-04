#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def ensure_project_python() -> None:
    if sys.version_info >= (3, 11):
        return
    candidates = (
        ROOT / ".venv" / "bin" / "python3",
        Path.home() / ".cache" / "codex-runtimes" / "codex-primary-runtime" / "dependencies" / "python" / "bin" / "python3",
    )
    for candidate in candidates:
        if candidate.is_file() and candidate.resolve() != Path(sys.executable).resolve():
            os.execv(str(candidate), [str(candidate), str(Path(__file__).resolve())])
    raise SystemExit("FAIL: Python >=3.11 is required")


def check(condition: bool, label: str) -> bool:
    print(f"{'PASS' if condition else 'FAIL'}: {label}")
    return condition


def main() -> int:
    passed = []
    for script in ("render_doubao_system_instructions.py", "build_doubao_skills.py"):
        result = subprocess.run([sys.executable, str(ROOT / "scripts" / script)], cwd=ROOT, check=False)
        passed.append(check(result.returncode == 0, script))

    manifest = json.loads((ROOT / "deployment" / "doubao" / "skills-v1.json").read_text(encoding="utf-8"))
    schedules = json.loads((ROOT / "deployment" / "doubao" / "schedules-v1.json").read_text(encoding="utf-8"))
    passed.append(check(manifest["visibility"] == "private_only", "skills private by default"))
    passed.append(check(
        manifest["package_format"] == "zip_with_named_skill_directory",
        "observed named-directory ZIP format",
    ))
    passed.append(check(len(manifest["skills"]) == 9, "nine required skills packaged"))
    passed.append(check(not schedules["scheduled_writes_enabled"], "scheduled writes remain disabled"))
    rendered = (ROOT / "deployment" / "doubao" / "system-instructions-v1.md").read_text(encoding="utf-8")
    passed.append(check("{{" not in rendered and "}}" not in rendered, "system instruction placeholders resolved"))

    environment = dict(os.environ)
    environment["PYTHONPATH"] = str(ROOT / "backend")
    environment["PYTHONPYCACHEPREFIX"] = "/private/tmp/architectpass-phase5-pycache"
    tests = subprocess.run(
        [sys.executable, "-m", "unittest", "tests.unit.test_doubao_skills", "-v"],
        cwd=ROOT,
        env=environment,
        check=False,
    )
    passed.append(check(tests.returncode == 0, "Phase 5 package tests"))
    return 0 if all(passed) else 1


if __name__ == "__main__":
    ensure_project_python()
    raise SystemExit(main())
