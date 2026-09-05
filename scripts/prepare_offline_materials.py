#!/usr/bin/env python3
"""Register delivered files and build a reusable, relocated first-use index."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def save(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".pending")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def prepare(root, selected=()):
    from architectpass_materials import MaterialCatalog, MaterialImporter
    from architectpass_materials.models import MaterialContext, ResourceRecord, Segment

    bundle = root.parent
    manifest = load(bundle / "offline-manifest.json")
    materials = bundle / "private-materials"
    authorized = tuple(materials / name for name in manifest["authorized_roots"])
    index = root / "materials/index"
    entries, missing = [], []
    for item in manifest["materials"]:
        source = materials / item["path"]
        if not source.is_file() or source.stat().st_size != item["size_bytes"]:
            missing.append(item["path"])
            continue
        entries.append({**item, "source_path": str(source.resolve()), "type": source.suffix.lower().lstrip(".")})
    if missing:
        raise ValueError("资料未完整解压或大小不符：" + ", ".join(missing[:5]))

    catalog_path = index / "offline-catalog.json"
    catalog = MaterialCatalog()
    if catalog_path.is_file():
        old = load(catalog_path)
        for item in old["resources"]:
            resource = ResourceRecord(**item)
            catalog.resources[resource.resource_id] = resource
            catalog.by_checksum[resource.checksum] = resource.resource_id
        catalog.segments = {item["segment_id"]: Segment(**item) for item in old["segments"]}
        catalog.audits = old.get("audits", [])
    importer = MaterialImporter(catalog, authorized)
    pdfs = [item for item in entries if item["type"] == "pdf"]
    if selected:
        by_path = {item["path"]: item for item in pdfs}
        if any(item not in by_path for item in selected):
            raise ValueError("--file 必须是清单中 PDF 的相对路径")
        chosen = [by_path[item] for item in selected]
    else:
        chosen = []
        for name in manifest["authorized_roots"]:
            candidates = [item for item in pdfs if Path(item["path"]).parts[0] == name]
            preferred = [item for item in candidates if Path(item["path"]).name in {
                "202605-13.系统架构设计.pdf", "系统架构设计师考前指南.pdf",
            }]
            if candidates:
                chosen.append((preferred or sorted(candidates, key=lambda item: item["size_bytes"]))[0])
    imported = 0
    for item in chosen:
        source = Path(item["source_path"])
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        existing_id = catalog.by_checksum.get(digest)
        if existing_id:
            old_path = catalog.resources[existing_id].source_path
            catalog.resources[existing_id].source_path = str(source)
            for segment in catalog.segments.values():
                if segment.resource_id == existing_id:
                    segment.open_target = segment.open_target.replace(old_path, str(source), 1)
            continue
        context = MaterialContext("offline-pdf-" + digest, "audit-offline-pdf-" + digest, "current-user-bootstrap")
        importer.import_file(source, context=context, copyright_scope="private_personal_exam_study")
        imported += 1
    # Relocate every persisted PDF, including files indexed in earlier sessions.
    current_paths = {item["sha256"]: item["source_path"] for item in entries}
    for resource in catalog.resources.values():
        if resource.checksum in current_paths:
            old_path = resource.source_path
            resource.source_path = current_paths[resource.checksum]
            for segment in catalog.segments.values():
                if segment.resource_id == resource.resource_id:
                    segment.open_target = segment.open_target.replace(old_path, resource.source_path, 1)
    generation = hashlib.sha256(json.dumps(entries, sort_keys=True).encode()).hexdigest()[:20]
    context = {"request_id": "offline-inventory-" + generation, "audit_id": "audit-offline-inventory-" + generation, "actor": "current-user-bootstrap"}
    save(index / "offline-inventory.json", {"write_context": context, "material_file_count": len(entries), "materials": entries})
    save(catalog_path, {"write_context": context, "resources": [item.as_dict() for item in catalog.resources.values()],
                        "segments": [item.as_dict() for item in catalog.segments.values()], "audits": catalog.audits})
    return {"status": "PASS", "material_file_count": len(entries), "pdf_count": len(pdfs),
            "indexed_pdf_count": len(catalog.resources), "newly_indexed_pdf_count": imported,
            "page_count": len(catalog.segments), "ocr_pending_pages": sum(item.confidence < 1 for item in catalog.segments.values()),
            "unindexed_pdf_count": len(pdfs) - len({item.checksum for item in catalog.resources.values()}),
            "video_transcription": "按学习片段处理；未声称已全量转写", "catalog": str(catalog_path)}


def search(root, query):
    from architectpass_materials import MaterialCatalog, MaterialSearch
    from architectpass_materials.models import ResourceRecord, Segment
    data = load(root / "materials/index/offline-catalog.json")
    catalog = MaterialCatalog()
    catalog.resources = {item["resource_id"]: ResourceRecord(**item) for item in data["resources"]}
    catalog.segments = {item["segment_id"]: Segment(**item) for item in data["segments"]}
    return {"status": "PASS", "results": MaterialSearch(catalog).search(query, limit=5)}


def main():
    if sys.version_info < (3, 11):
        interpreter = ROOT / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python3")
        if interpreter.is_file():
            os.execv(str(interpreter), [str(interpreter), str(Path(__file__).resolve()), *sys.argv[1:]])
        raise SystemExit("请先运行 python3 scripts/bootstrap_local.py")
    sys.path.insert(0, str(ROOT / "backend"))
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", action="append", default=[], help="PDF path relative to private-materials; may repeat")
    parser.add_argument("--search", help="search the persisted page index")
    args = parser.parse_args()
    try:
        result = search(ROOT, args.search) if args.search else prepare(ROOT, args.file)
    except Exception as error:
        result = {"status": "FAIL", "error": str(error)}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result["status"] == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
