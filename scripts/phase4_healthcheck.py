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
    print("FAIL: Python >=3.11 is required")
    raise SystemExit(1)


def check(condition: bool, label: str) -> bool:
    print(f"{'PASS' if condition else 'FAIL'}: {label}")
    return condition


def main() -> int:
    passed: list[bool] = []
    paths = (ROOT / "schemas" / "learning-controller-v1.json", ROOT / "schemas" / "state-contract.schema.json")
    loaded = []
    for path in paths:
        try:
            loaded.append(json.loads(path.read_text(encoding="utf-8")))
            passed.append(check(True, f"valid JSON {path.relative_to(ROOT)}"))
        except (OSError, json.JSONDecodeError):
            passed.append(check(False, f"valid JSON {path.relative_to(ROOT)}"))
    if len(loaded) != 2:
        return 1

    controller_contract = loaded[0]
    passed.append(check(
        controller_contract["state_order"] == ["OBSERVE", "DIAGNOSE", "PLAN", "EXECUTE", "TEST", "UPDATE", "SCHEDULE", "CHECKPOINT"],
        "fixed state-machine order",
    ))
    passed.append(check(controller_contract["review_baseline_days"] == [1, 3, 7, 14, 30], "review interval baseline"))
    source = "\n".join(path.read_text(encoding="utf-8") for path in (ROOT / "backend" / "architectpass_controller").glob("*.py"))
    passed.append(check("select_answer" not in source and "submit_answer" not in source, "no answer or submit operation"))
    passed.append(check('"fabrication_allowed": False' in source, "essay anti-fabrication guard present"))

    environment = dict(os.environ)
    environment["PYTHONPATH"] = str(ROOT / "backend")
    tests = subprocess.run(
        [sys.executable, "-X", "utf8", "-m", "unittest", "tests.unit.test_controller", "tests.unit.test_state_service", "-v"],
        cwd=ROOT,
        env=environment,
        check=False,
    )
    passed.append(check(tests.returncode == 0, "Phase 4 controller and state tests"))
    return 0 if all(passed) else 1


if __name__ == "__main__":
    ensure_project_python()
    raise SystemExit(main())
