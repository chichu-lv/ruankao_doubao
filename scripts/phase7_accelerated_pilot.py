#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from architectpass_acceptance import run_accelerated_pilot  # noqa: E402


if __name__ == "__main__":
    result = run_accelerated_pilot()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    raise SystemExit(0 if result["status"] == "PASS" else 1)
