#!/usr/bin/env python3
"""Index existing authorized course folders, not an entire Downloads directory."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from prepare_offline_materials import prepare, search


def prepare_downloaded(root: Path, source_parent: Path, selected=()):
    config = json.loads((root / "deployment/doubao/project-v1.json").read_text(encoding="utf-8"))
    names = config["materials"]["authorized_baidu_scopes"]
    if len(names) != 2 or any(Path(name).name != name for name in names):
        raise ValueError("expected exactly the two authorized course directory names")
    parent = source_parent.expanduser().resolve(strict=True)
    entries, absent = [], []
    # Never list parent: check only the two exact authorized children.
    for name in names:
        folder = parent / name
        if folder.is_symlink():
            raise ValueError(f"course folder is a symlink; request its explicit real location: {name}")
        if not folder.is_dir():
            absent.append(name)
            continue
        for path in sorted(folder.rglob("*")):
            if path.is_symlink():
                continue
            if path.is_file() and path.suffix.lower() in {".pdf", ".mp4", ".mkv", ".mov", ".srt", ".vtt"}:
                entries.append({"path": str(path.relative_to(parent)), "size_bytes": path.stat().st_size, "sha256": None})
    if absent:
        return {"status": "PARTIAL", "missing_authorized_roots": absent,
                "next_action": "Use the official client/browser to download the named course folders, or provide their actual parent; do not search other directories."}
    manifest = {"authorized_roots": names, "materials": entries}
    result = prepare(root, selected, source_root=parent, source_manifest=manifest, index_prefix="downloaded")
    result["source_mode"] = "existing_authorized_local_courses"
    result["baidu_remote_status"] = "UNVERIFIED_BY_THIS_LOCAL_IMPORT"
    if result["indexed_pdf_count"] == 0:
        result["status"] = "PARTIAL"
        result["next_action"] = "No readable PDF was indexed; obtain the current learning unit through the official source."
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-parent", type=Path, help="Parent of exactly the two authorized course folders")
    parser.add_argument("--file", action="append", default=[])
    parser.add_argument("--search")
    args = parser.parse_args()
    try:
        if args.search:
            result = search(ROOT, args.search, "downloaded")
        elif args.source_parent:
            result = prepare_downloaded(ROOT, args.source_parent, args.file)
        else:
            parser.error("--source-parent or --search is required")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1 if result["status"] == "FAIL" else 0
    except Exception as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
