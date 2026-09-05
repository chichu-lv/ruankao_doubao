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
import platform
import tarfile
import zipfile
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
        if (ROOT / "vendor/python-windows-amd64.zip").is_file():
            return RUNTIME_ROOT / "python/python.exe"
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


def bundled_python() -> Optional[Path]:
    if os.name == "nt":
        archive = ROOT / "vendor/python-windows-amd64.zip"
        if not archive.is_file():
            return None
        destination = RUNTIME_ROOT / "python"
        if not (destination / "python.exe").is_file():
            destination.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(archive) as package:
                package.extractall(destination)
        return destination / "python.exe"
    if platform.system() != "Darwin" or platform.machine() != "arm64":
        return None
    archive = ROOT / "vendor/python-macos-arm64.tar.gz"
    if not archive.is_file():
        return None
    destination = RUNTIME_ROOT / "bundled-python"
    interpreter = destination / "bin/python3"
    if not interpreter.is_file():
        destination.mkdir(parents=True, exist_ok=True)
        with tarfile.open(archive) as package:
            package.extractall(destination)
    return interpreter if compatible(interpreter) else None


def create_venv(offline: bool = False) -> Tuple[Path, str]:
    existing = project_python()
    if compatible(existing):
        return existing, "existing_project_venv"

    source = bundled_python() or next((path for path in candidate_pythons() if path != existing and compatible(path)), None)
    if source is not None:
        if os.name == "nt" and source == RUNTIME_ROOT / "python/python.exe":
            return source, "bundled_windows_python"
        result = subprocess.run([str(source), "-m", "venv", str(VENV)], cwd=ROOT, check=False)
        if result.returncode != 0:
            raise BootstrapError(f"compatible Python was found but could not create .venv: {source}")
        return project_python(), f"venv_from:{source}"

    if offline:
        raise BootstrapError("No compatible local Python runtime. Install Python 3.12 for this platform, then retry.")
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


def install_windows_wheels(runtime: Path, wheelhouse: Path) -> None:
    """Vendor dependencies for Python's embeddable distribution (no pip needed)."""
    wheels = sorted(wheelhouse.glob("*.whl"))
    if not wheels:
        raise BootstrapError("Windows dependency wheels are absent from this package")
    destination = runtime / "Lib/site-packages"
    destination.mkdir(parents=True, exist_ok=True)
    marker = destination / "architectpass-installed.json"
    names = [wheel.name for wheel in wheels]
    installed = json.loads(marker.read_text(encoding="utf-8")) if marker.is_file() else []
    if installed != names:
        for wheel in wheels:
            with zipfile.ZipFile(wheel) as package:
                package.extractall(destination)
        marker.write_text(json.dumps(names), encoding="utf-8")
    # Relative paths remain valid after moving the complete unpacked directory.
    (runtime / "python312._pth").write_text(
        "python312.zip\n.\nLib/site-packages\n../../backend\n../../\nimport site\n", encoding="utf-8"
    )


def ensure_private_pip(interpreter: Path) -> None:
    """uv-created virtual environments may not include pip; seed it locally."""
    probe = subprocess.run([str(interpreter), "-c", "import pip"], cwd=ROOT, capture_output=True, check=False)
    if probe.returncode == 0:
        return
    seeded = subprocess.run([str(interpreter), "-m", "ensurepip", "--upgrade"], cwd=ROOT, check=False)
    if seeded.returncode != 0:
        raise BootstrapError("pip is absent and ensurepip could not seed it in the private .venv; no system Python was modified")


def install_project(interpreter: Path, offline: bool) -> str:
    if os.name == "nt" and interpreter == RUNTIME_ROOT / "python/python.exe":
        install_windows_wheels(interpreter.parent, ROOT / "vendor/wheels-windows")
        return "bundled_windows_wheels"
    uv = shutil.which("uv")
    wheelhouse = ROOT / "vendor" / "wheels"
    if offline:
        if not wheelhouse.is_dir():
            raise BootstrapError("offline dependency wheelhouse is absent from this package")
        ensure_private_pip(interpreter)
        base = [str(interpreter), "-m", "pip", "install", "--no-index", "--find-links", str(wheelhouse)]
        for command in (base + ["setuptools", "wheel"], base + ["--no-build-isolation", "--editable", str(ROOT)]):
            result = subprocess.run(command, cwd=ROOT, check=False)
            if result.returncode != 0:
                raise BootstrapError("bundled wheels could not be installed for this Python/platform")
        return "bundled_wheels"
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
            [str(interpreter), "-X", "utf8", str(ROOT / "scripts" / name)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            env={**os.environ, "PYTHONUTF8": "1"},
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
        use_offline = args.offline or (
            (ROOT / "vendor/python-macos-arm64.tar.gz").is_file()
            and platform.system() == "Darwin" and platform.machine() == "arm64"
        ) or (os.name == "nt" and (ROOT / "vendor/python-windows-amd64.zip").is_file())
        interpreter, runtime_source = create_venv(use_offline)
        installer = install_project(interpreter, use_offline)
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
