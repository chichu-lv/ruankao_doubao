#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shutil
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
    print("FAIL: Python >=3.11 is required; run python3 scripts/bootstrap_local.py")
    raise SystemExit(1)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def check(condition: bool, label: str, detail: str = "") -> bool:
    state = "PASS" if condition else "FAIL"
    suffix = f" — {detail}" if detail else ""
    print(f"{state}: {label}{suffix}")
    return condition


def main() -> int:
    required: list[bool] = []
    optional: list[bool] = []
    for binary in ("ffmpeg", "ffprobe", "whisper-cli", "pdftoppm", "tesseract"):
        present = shutil.which(binary) is not None
        print(f"{'PASS' if present else 'PARTIAL'}: binary {binary}")
        optional.append(present)

    config_path = ROOT / "deployment" / "models" / "local-processing-v1.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    model_paths = {
        "zh_timestamped_transcription": ROOT / "materials" / "models" / "ggml-medium-q5_0.bin",
        "simplified_chinese_page_ocr": ROOT / "materials" / "models" / "tessdata" / "chi_sim.traineddata",
    }
    for model in config["models"]:
        path = model_paths[model["purpose"]]
        present = path.is_file()
        print(f"{'PASS' if present else 'PARTIAL'}: local model {model['purpose']}")
        optional.append(present)
        if present:
            required.append(check(sha256(path) == model["sha256"], f"model hash {model['purpose']}"))

    manifest = json.loads((ROOT / "materials" / "manifests" / "authorized-sources-v1.json").read_text(encoding="utf-8"))
    progress = json.loads((ROOT / "materials" / "manifests" / "video-progress-v1.json").read_text(encoding="utf-8"))
    roots = set(manifest["authorization"]["allowed_remote_roots"])
    required.append(check(bool(roots), "authorized material roots are non-empty"))
    required.append(check(all(item["remote_root"] in roots for item in manifest["resources"]), "manifest resources stay in authorized roots"))
    required.append(check(all(manifest["write_context"].get(key) for key in ("request_id", "audit_id", "actor")), "manifest write context"))
    required.append(check(progress["learning_policy"] == "diagnose_then_targeted_rewatch_never_restart_by_default", "video progress policy"))
    required.append(check(all(item["status"] == "played_unchecked" for item in progress["observations"]), "watching does not imply mastery"))

    environment = dict(__import__("os").environ)
    environment["PYTHONPATH"] = str(ROOT / "backend")
    if importlib.util.find_spec("pdfplumber") is None:
        print("PARTIAL: Python dependency pdfplumber is unavailable; PDF indexing uses the official-UI/manual-page fallback")
        optional.append(False)
    else:
        tests = subprocess.run(
            [sys.executable, "-X", "utf8", "-m", "unittest", "tests.unit.test_materials", "-v"],
            cwd=ROOT,
            env=environment,
            check=False,
        )
        required.append(check(tests.returncode == 0, "Phase 2 unit tests"))

    if not all(required):
        print("SUMMARY: FAIL — material contracts or verified local artifacts are invalid")
        return 1
    if not all(optional):
        print("SUMMARY: PARTIAL — local OCR/ASR is incomplete; official UI with manual page/timestamp fallback remains available")
        return 0
    print("SUMMARY: PASS")
    return 0


if __name__ == "__main__":
    ensure_project_python()
    raise SystemExit(main())
