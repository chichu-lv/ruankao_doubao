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
    candidate = ROOT / ".venv" / "bin" / "python3"
    if candidate.is_file():
        os.execv(str(candidate), [str(candidate), str(Path(__file__).resolve())])
    raise SystemExit("FAIL: Python >=3.11 is required")


def main() -> int:
    rendered = subprocess.run(
        [sys.executable, str(ROOT / "scripts/render_phase6_initialization.py")],
        cwd=ROOT,
        check=False,
    )
    if rendered.returncode != 0:
        print("FAIL: render Phase 6 initialization plan")
        return 1
    sys.path.insert(0, str(ROOT / "backend"))
    from architectpass_initialization import Phase6Builder

    bundle = Phase6Builder(ROOT).build()
    checks = {
        "history is optional": bundle["history_required"] is False,
        "scheduled writes disabled": bundle["scheduled_writes_enabled"] is False,
        "seven runtime-budgeted days": len(bundle["seven_day_plan"]["days"]) == 7,
        "project facts truthfully empty": bundle["project_facts"] == {
            "status": "awaiting_user_confirmed_redacted_facts", "fact_count": 0,
        },
        "traceable initialization operations": all(
            item["request_id"] and item["audit_id"] and item["record_id"] for item in bundle["operations"]
        ),
    }
    private_result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/build_phase6_private_segments.py")],
        cwd=ROOT,
        check=False,
    )
    checks["private page/time segment plan"] = private_result.returncode in {0, 2}
    environment = dict(os.environ)
    environment["PYTHONPATH"] = str(ROOT / "backend")
    environment["PYTHONPYCACHEPREFIX"] = "/private/tmp/architectpass-phase6-pycache"
    tests = subprocess.run(
        [sys.executable, "-m", "unittest", "tests.unit.test_initialization", "-v"],
        cwd=ROOT,
        env=environment,
        check=False,
    )
    checks["Phase 6 initialization tests"] = tests.returncode == 0
    for label, passed in checks.items():
        print(f"{'PASS' if passed else 'FAIL'}: {label}")
    summary = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "operation_count": len(bundle["operations"]),
        "tables": sorted({item["table"] for item in bundle["operations"]}),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    ensure_project_python()
    raise SystemExit(main())
