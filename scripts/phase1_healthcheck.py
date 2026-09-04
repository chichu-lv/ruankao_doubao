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
    )
    for candidate in candidates:
        if candidate.is_file() and candidate.resolve() != Path(sys.executable).resolve():
            os.execv(str(candidate), [str(candidate), str(Path(__file__).resolve())])
    print("FAIL: Python >=3.11 is required; configure the project .venv")
    raise SystemExit(1)


def main() -> int:
    checks: list[tuple[str, bool, str]] = []
    for relative in (
        "schemas/state-contract.schema.json",
        "schemas/feishu-bitable-v1.json",
        "schemas/migrations/0001-initial.json",
    ):
        path = ROOT / relative
        try:
            json.loads(path.read_text(encoding="utf-8"))
            checks.append((relative, True, "valid JSON"))
        except (OSError, json.JSONDecodeError) as error:
            checks.append((relative, False, str(error)))

    deployment_path = ROOT / "deployment/feishu/production-v1.json"
    try:
        deployment = json.loads(deployment_path.read_text(encoding="utf-8"))
        valid_deployment = deployment.get("visibility") == "private_unshared" and len(deployment.get("tables", {})) == 15
        checks.append(("feishu_release_contract", valid_deployment, f"{len(deployment.get('tables', {}))} table mappings"))
    except (OSError, json.JSONDecodeError) as error:
        checks.append(("feishu_release_contract", False, str(error)))

    process = subprocess.run(
        [
            sys.executable,
            "-m",
            "unittest",
            "tests.unit.test_state_service",
            "tests.unit.test_backup_and_outbox",
            "tests.unit.test_migrations",
            "-v",
        ],
        cwd=ROOT,
        env={**__import__("os").environ, "PYTHONPATH": str(ROOT / "backend")},
        capture_output=True,
        text=True,
        check=False,
    )
    checks.append(("unit_tests", process.returncode == 0, process.stderr.strip().splitlines()[-1] if process.stderr.strip() else "no output"))

    failed = False
    for name, passed, detail in checks:
        status = "PASS" if passed else "FAIL"
        print(f"{status} {name}: {detail}")
        failed = failed or not passed
    print("PARTIAL live_feishu_probe: this local command verifies the release contract; live authentication runs during bootstrap")
    return 1 if failed else 0


if __name__ == "__main__":
    ensure_project_python()
    raise SystemExit(main())
