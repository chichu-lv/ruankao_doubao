#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_CAPTURE_KEYS = {
    "question",
    "question_text",
    "stem",
    "options",
    "answer",
    "correct_answer",
    "analysis",
    "explanation",
    "solution",
}


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
    print("FAIL: Python >=3.11 is required; configure .venv or the Codex workspace runtime")
    raise SystemExit(1)


def check(condition: bool, label: str) -> bool:
    print(f"{'PASS' if condition else 'FAIL'}: {label}")
    return condition


def keys(value: Any) -> set[str]:
    found: set[str] = set()
    if isinstance(value, dict):
        found.update(str(key).casefold() for key in value)
        for child in value.values():
            found.update(keys(child))
    elif isinstance(value, list):
        for child in value:
            found.update(keys(child))
    return found


def main() -> int:
    passed: list[bool] = []
    paths = (
        ROOT / "schemas" / "cheko-practice-v1.json",
        ROOT / "schemas" / "state-contract.schema.json",
        ROOT / "deployment" / "cheko" / "ui-contract-v1.json",
        ROOT / "tests" / "fixtures" / "cheko-submitted-report-sanitized.json",
        ROOT / "tests" / "fixtures" / "cheko-custom-paper-test-sanitized.json",
    )
    loaded: dict[str, Any] = {}
    for path in paths:
        try:
            loaded[path.name] = json.loads(path.read_text(encoding="utf-8"))
            passed.append(check(True, f"valid JSON {path.relative_to(ROOT)}"))
        except (OSError, json.JSONDecodeError):
            passed.append(check(False, f"valid JSON {path.relative_to(ROOT)}"))

    if len(loaded) != len(paths):
        return 1
    contract = loaded["ui-contract-v1.json"]
    fixture = loaded["cheko-submitted-report-sanitized.json"]
    custom_fixture = loaded["cheko-custom-paper-test-sanitized.json"]
    passed.append(
        check(
            contract["contract_version"] == custom_fixture["result"]["ui_contract_version"],
            "current fixture UI contract version",
        )
    )
    passed.append(
        check(
            fixture["result"]["ui_contract_version"] == "cheko-ui-2026-09-04.1",
            "historical fixture preserves observed UI contract version",
        )
    )
    passed.append(check(set(contract["forbidden_actions"]) >= {"select_answer", "submit_answer"}, "answer and submit actions forbidden"))
    passed.append(check(not (keys(fixture) & FORBIDDEN_CAPTURE_KEYS), "sanitized fixture contains no question or answer fields"))
    passed.append(check(not (keys(custom_fixture) & FORBIDDEN_CAPTURE_KEYS), "custom-paper fixture contains no question or answer fields"))
    passed.append(check(fixture["result"]["submission_state"] == "submitted", "fixture is post-submission only"))
    passed.append(check(custom_fixture["result"]["submission_state"] == "submitted", "custom-paper fixture is post-submission only"))
    summary = custom_fixture["result"]["summary"]
    passed.append(
        check(
            summary["main_question_count"] == 20 and summary["answer_item_count"] == 21,
            "custom-paper main-question and answer-item counts stay distinct",
        )
    )
    passed.append(check([item["method"] for item in contract["fallbacks"]] == ["official_export", "screenshot", "manual_summary"], "ordered DOM fallbacks"))

    cheko_source = "\n".join(
        path.read_text(encoding="utf-8") for path in (ROOT / "backend" / "architectpass_cheko").glob("*.py")
    )
    blocked_imports = ("import requests", "from requests", "import urllib", "from urllib")
    passed.append(check(not any(token in cheko_source for token in blocked_imports), "no private network API client"))

    environment = dict(os.environ)
    environment["PYTHONPATH"] = str(ROOT / "backend")
    environment["PYTHONPYCACHEPREFIX"] = "/private/tmp/architectpass-phase3-pycache"
    tests = subprocess.run(
        [sys.executable, "-m", "unittest", "tests.unit.test_cheko_practice", "-v"],
        cwd=ROOT,
        env=environment,
        check=False,
    )
    passed.append(check(tests.returncode == 0, "Phase 3 unit tests"))
    return 0 if all(passed) else 1


if __name__ == "__main__":
    ensure_project_python()
    raise SystemExit(main())
