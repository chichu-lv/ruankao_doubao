#!/usr/bin/env python3
"""Read only: distinguish registered files, searchable pages and complete coverage."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def summarize_index(inventory, catalog):
    files = inventory["materials"]
    resources, segments = catalog["resources"], catalog["segments"]
    pdfs = [item for item in files if item.get("type", Path(item["path"]).suffix.lstrip(".")).lower() == "pdf"]
    indexed_paths = {item["source_path"] for item in resources if item.get("media_type") == "pdf"}
    indexed = sum(item.get("source_path") in indexed_paths for item in pdfs)
    pending = sum(float(item.get("confidence", 0)) < 1 for item in segments)
    searchable = sum(bool(item.get("text", "").strip()) for item in segments)
    videos = sum(Path(item["path"]).suffix.lower() in {".mp4", ".mkv", ".mov"} for item in files)
    complete = bool(pdfs) and indexed == len(pdfs) and pending == 0 and searchable == len(segments) and searchable > 0 and videos == 0
    return {
        "status": "PASS" if complete else "PARTIAL",
        "registered_files": len(files), "pdf_files": len(pdfs),
        "indexed_pdf_files": indexed, "unindexed_pdf_files": len(pdfs) - indexed,
        "page_segments": len(segments), "searchable_page_segments": searchable,
        "ocr_pending_pages": pending, "video_files": videos,
        "video_transcription": "NOT_ASSESSED_BY_THIS_PDF_CATALOG" if videos else "NOT_APPLICABLE",
        "usable_for_page_search": searchable > 0,
        "coverage_complete": complete,
        "limitation": "文件登记不等于全文索引；部分页可检索不等于全量 OCR/ASR 完成。",
    }


def snapshot(root):
    indexes = {}
    for prefix in ("downloaded", "offline"):
        inventory = root / f"materials/index/{prefix}-inventory.json"
        catalog = root / f"materials/index/{prefix}-catalog.json"
        if not inventory.exists() and not catalog.exists():
            continue
        try:
            indexes[prefix] = summarize_index(json.loads(inventory.read_text()), json.loads(catalog.read_text()))
        except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
            indexes[prefix] = {"status": "FAIL", "error": type(exc).__name__, "coverage_complete": False}
    statuses = [item["status"] for item in indexes.values()]
    local_status = "FAIL" if "FAIL" in statuses else "PARTIAL" if not statuses or "PARTIAL" in statuses else "PASS"
    return {
        "read_only": True, "local_material_status": local_status, "indexes": indexes,
        "state_binding_present": (root / "dist/deployment/project-state.json").is_file(),
        "live_checks_required": ["skill_discovery", "state_read", "cheko_login_and_route", "reminder_configuration"],
        "overall_status": "PARTIAL", "overall_reason": "本脚本不验证外部连接；仍须本次工具回读，不能只凭本地文件报告整体 PASS。",
    }


if __name__ == "__main__":
    print(json.dumps(snapshot(ROOT), ensure_ascii=False, indent=2))
