#!/usr/bin/env python3
"""Prepare a private project runtime and run local bootstrap health checks.

This launcher intentionally remains compatible with Python 3.9 so a fresh macOS
machine can use its system Python to discover or provision the required 3.11+
project interpreter.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_ROOT = ROOT / ".runtime"
VENV = ROOT / ".venv"
MINIMUM = (3, 11)
HEALTHCHECKS = (
    "phase1_healthcheck.py",
    "phase2_healthcheck.py",
    "phase3_healthcheck.py",
    "phase4_healthcheck.py",
    "phase5_healthcheck.py",
    "phase6_healthcheck.py",
)


class BootstrapError(RuntimeError):
    pass


def project_python() -> Path:
    if os.name == "nt":
        return VENV / "Scripts" / "python.exe"
    return VENV / "bin" / "python3"


def python_version(executable: Path) -> Optional[Tuple[int, int, int]]:
    if not executable.is_file():
        return None
    result = subprocess.run(
        [str(executable), "-c", "import sys; print('.'.join(map(str, sys.version_info[:3])))"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    try:
        parts = tuple(int(item) for item in result.stdout.strip().split("."))
    except ValueError:
        return None
    return parts if len(parts) == 3 else None


def compatible(executable: Path) -> bool:
    version = python_version(executable)
    return version is not None and version[:2] >= MINIMUM


def candidate_pythons() -> List[Path]:
    candidates: List[Path] = []
    override = os.environ.get("ARCHITECTPASS_PYTHON")
    if override:
        candidates.append(Path(override).expanduser())
    candidates.append(project_python())
    for name in ("python3.14", "python3.13", "python3.12", "python3.11", "python3"):
        found = shutil.which(name)
        if found:
            candidates.append(Path(found))
    for prefix in (Path("/opt/homebrew/bin"), Path("/usr/local/bin")):
        for name in ("python3.14", "python3.13", "python3.12", "python3.11", "python3"):
            candidates.append(prefix / name)
    unique: List[Path] = []
    seen = set()
    for candidate in candidates:
        key = str(candidate)
        if key not in seen:
            unique.append(candidate)
            seen.add(key)
    return unique


def uv_environment() -> Dict[str, str]:
    environment = dict(os.environ)
    environment["UV_CACHE_DIR"] = str(RUNTIME_ROOT / "uv-cache")
    environment["UV_PYTHON_INSTALL_DIR"] = str(RUNTIME_ROOT / "uv-python")
    environment["UV_NO_PROGRESS"] = "1"
    return environment


def create_venv() -> Tuple[Path, str]:
    existing = project_python()
    if compatible(existing):
        return existing, "existing_project_venv"

    source = next((path for path in candidate_pythons() if path != existing and compatible(path)), None)
    if source is not None:
        result = subprocess.run([str(source), "-m", "venv", str(VENV)], cwd=ROOT, check=False)
        if result.returncode != 0:
            raise BootstrapError(f"compatible Python was found but could not create .venv: {source}")
        return project_python(), f"venv_from:{source}"

    uv = shutil.which("uv")
    if uv is None:
        raise BootstrapError(
            "Python 3.11+ was not found. Install Python 3.12 or uv through an official source, "
            "then rerun: python3 scripts/bootstrap_local.py"
        )
    RUNTIME_ROOT.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        [uv, "venv", "--python", "3.12", "--managed-python", str(VENV)],
        cwd=ROOT,
        env=uv_environment(),
        check=False,
    )
    if result.returncode != 0 or not compatible(project_python()):
        raise BootstrapError("uv could not provision the private Python 3.12 runtime")
    return project_python(), "uv_managed_python_3.12"


def install_project(interpreter: Path, offline: bool) -> str:
    uv = shutil.which("uv")
    wheelhouse = ROOT / "vendor" / "wheels"
    if uv:
        command = [uv, "pip", "install", "--python", str(interpreter)]
        if offline:
            if not wheelhouse.is_dir():
                raise BootstrapError("offline dependency wheelhouse is absent from this package")
            command.extend(["--offline", "--no-index", "--find-links", str(wheelhouse)])
        command.extend(["--editable", str(ROOT)])
        result = subprocess.run(command, cwd=ROOT, env=uv_environment(), check=False)
        if result.returncode == 0:
            return "uv"
    command = [str(interpreter), "-m", "pip", "install"]
    if offline:
        if not wheelhouse.is_dir():
            raise BootstrapError("offline dependency wheelhouse is absent from this package")
        command.extend(["--no-index", "--find-links", str(wheelhouse)])
    command.extend(["--editable", str(ROOT)])
    result = subprocess.run(command, cwd=ROOT, check=False)
    if result.returncode != 0:
        raise BootstrapError("project dependencies could not be installed into the private .venv")
    return "pip"


def run_healthchecks(interpreter: Path) -> Tuple[str, List[Dict[str, object]]]:
    results: List[Dict[str, object]] = []
    for name in HEALTHCHECKS:
        result = subprocess.run(
            [str(interpreter), str(ROOT / "scripts" / name)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        output = (result.stdout + result.stderr).strip()
        if output:
            print(output)
        status = classify_healthcheck(result.returncode, output)
        results.append({"name": name, "status": status, "returncode": result.returncode})
    overall = "FAIL" if any(item["status"] == "FAIL" for item in results) else (
        "PARTIAL" if any(item["status"] == "PARTIAL" for item in results) else "PASS"
    )
    return overall, results


def classify_healthcheck(returncode: int, output: str) -> str:
    if returncode != 0:
        return "FAIL"
    lines = [line.strip() for line in output.splitlines()]
    if any(line.startswith("PARTIAL") or line.startswith("SUMMARY: PARTIAL") for line in lines):
        return "PARTIAL"
    return "PASS"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prepare-only", action="store_true", help="prepare .venv without running health checks")
    parser.add_argument("--offline", action="store_true", help="install dependencies only from vendor/wheels")
    args = parser.parse_args()

    try:
        interpreter, runtime_source = create_venv()
        installer = install_project(interpreter, args.offline)
        version = python_version(interpreter)
        if args.prepare_only:
            report = {
                "status": "PASS",
                "python": str(interpreter),
                "python_version": ".".join(str(item) for item in version or ()),
                "runtime_source": runtime_source,
                "installer": installer,
            }
        else:
            status, checks = run_healthchecks(interpreter)
            report = {
                "status": status,
                "python": str(interpreter),
                "python_version": ".".join(str(item) for item in version or ()),
                "runtime_source": runtime_source,
                "installer": installer,
                "healthchecks": checks,
            }
    except BootstrapError as error:
        report = {"status": "FAIL", "error": str(error)}

    output = ROOT / "dist" / "bootstrap" / "local-bootstrap-result.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if report["status"] == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
