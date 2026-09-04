#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "dist/phase6-initialization/private-segments-v1.json"


def ensure_project_python() -> None:
    if sys.version_info >= (3, 11):
        return
    candidate = Path.home() / ".cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"
    if candidate.is_file():
        os.execv(str(candidate), [str(candidate), str(Path(__file__).resolve())])
    raise SystemExit("Python >=3.11 is required")


def main() -> int:
    sys.path.insert(0, str(ROOT / "backend"))
    from architectpass_initialization import Phase6Builder

    pdf = ROOT / "materials/index/phase2-real-pdf-ocr-catalog.json"
    video = ROOT / "materials/index/phase2-real-video-catalog-v3.json"
    if not pdf.is_file() or not video.is_file():
        print("PARTIAL: private PDF/video catalogs are absent; run the Phase 2 indexer on authorized files")
        return 2
    payload = Phase6Builder(ROOT).build_private_segments(pdf, video)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": "PASS",
        "output": str(OUTPUT.relative_to(ROOT)),
        "operation_count": len(payload["operations"]),
        "git_commit_allowed": payload["git_commit_allowed"],
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    ensure_project_python()
    raise SystemExit(main())
