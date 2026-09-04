#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "deployment/phase6/initialization-write-plan-v1.json"


def ensure_project_python() -> None:
    if sys.version_info >= (3, 11):
        return
    candidate = ROOT / ".venv" / "bin" / "python3"
    if candidate.is_file():
        os.execv(str(candidate), [str(candidate), str(Path(__file__).resolve())])
    raise SystemExit("Python >=3.11 is required")


def main() -> int:
    sys.path.insert(0, str(ROOT / "backend"))
    from architectpass_initialization import Phase6Builder

    payload = Phase6Builder(ROOT).build()
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(TARGET.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    ensure_project_python()
    raise SystemExit(main())
