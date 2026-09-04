#!/usr/bin/env python3
"""Verify an ArchitectPass private offline bundle without extracting it."""

from __future__ import annotations

import argparse
import hashlib
import json
import stat
import zipfile
from pathlib import Path, PurePosixPath
from typing import Dict, List


PREFIX = PurePosixPath("ArchitectPass-offline")


def member_sha256(archive: zipfile.ZipFile, name: str) -> str:
    digest = hashlib.sha256()
    with archive.open(name) as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_bundle(path: Path) -> Dict[str, object]:
    errors: List[str] = []
    with zipfile.ZipFile(path) as archive:
        members = archive.infolist()
        names = {item.filename for item in members}
        for item in members:
            member = PurePosixPath(item.filename)
            if member.is_absolute() or ".." in member.parts or not member.parts or member.parts[0] != PREFIX.name:
                errors.append(f"unsafe archive path: {item.filename}")
            mode = item.external_attr >> 16
            if stat.S_ISLNK(mode):
                errors.append(f"symlink archive member: {item.filename}")

        manifest_name = (PREFIX / "offline-manifest.json").as_posix()
        readme_name = (PREFIX / "README-OFFLINE.md").as_posix()
        if manifest_name not in names or readme_name not in names:
            return {"status": "FAIL", "errors": ["offline manifest or README is missing"]}
        manifest = json.loads(archive.read(manifest_name))
        if manifest.get("privacy") != "private_personal_offline_backup":
            errors.append("invalid privacy contract")
        if manifest.get("contains_credentials") is not False:
            errors.append("credential declaration is not false")
        for category, prefix in (
            ("materials", PREFIX / "private-materials"),
            ("runtime_assets", PREFIX / "project"),
        ):
            for record in manifest.get(category, []):
                name = (prefix / PurePosixPath(record["path"])).as_posix()
                if name not in names:
                    errors.append(f"declared member missing: {name}")
                elif member_sha256(archive, name) != record["sha256"]:
                    errors.append(f"checksum mismatch: {name}")
        skill_count = len(
            [name for name in names if name.startswith((PREFIX / "prebuilt-skills").as_posix() + "/") and name.endswith(".zip")]
        )
        if skill_count != 9:
            errors.append(f"expected 9 prebuilt skills, found {skill_count}")
        return {
            "status": "FAIL" if errors else manifest.get("status", "FAIL"),
            "errors": errors,
            "bundle_status": manifest.get("status"),
            "version": manifest.get("version"),
            "skill_count": skill_count,
            "material_file_count": manifest.get("material_file_count"),
            "declared_missing_count": len(manifest.get("declared_missing", [])),
        }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("archive", type=Path)
    args = parser.parse_args()
    try:
        result = verify_bundle(args.archive)
    except (OSError, zipfile.BadZipFile, json.JSONDecodeError, KeyError) as error:
        result = {"status": "FAIL", "errors": [str(error)]}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result["status"] == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
