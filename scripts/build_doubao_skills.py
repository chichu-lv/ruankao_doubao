#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import shutil
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "skills" / "doubao"
OUTPUT = ROOT / "dist" / "doubao-skills"
EXPECTED = {
    "ruankao-controller-v1",
    "ruankao-materials-v1",
    "cheko-practice-v1",
    "ruankao-assessment-v1",
    "ruankao-case-coach-v1",
    "ruankao-essay-coach-v1",
    "ruankao-review-scheduler-v1",
    "ruankao-research-verifier-v1",
    "ruankao-healthcheck-v1",
}
SECRET_PATTERNS = {
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "bearer token": re.compile(r"(?i)authorization\s*:\s*bearer\s+\S+"),
    "cookie": re.compile(r"(?i)(?:^|\s)cookie\s*:\s*\S+"),
    "generic secret": re.compile(r"(?i)(?:api[_-]?key|access[_-]?token|password)\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{12,}"),
}
ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)
ZIP_FILE_MODE = 0o100644


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_skill(directory: Path) -> dict[str, object]:
    skill = directory / "SKILL.md"
    if not skill.is_file():
        raise ValueError(f"{directory.name}: missing SKILL.md")
    text = skill.read_text(encoding="utf-8")
    match = re.match(r"\A---\nname:\s*([^\n]+)\ndescription:\s*([^\n]+)\n---\n", text)
    if not match:
        raise ValueError(f"{directory.name}: invalid Doubao skill frontmatter")
    if match.group(1).strip() != directory.name:
        raise ValueError(f"{directory.name}: name does not match directory")
    for label, pattern in SECRET_PATTERNS.items():
        if pattern.search(text):
            raise ValueError(f"{directory.name}: possible {label}")
    if "发布到公共" in text and "禁止" not in text:
        raise ValueError(f"{directory.name}: unsafe publishing instruction")
    return {"name": directory.name, "description": match.group(2).strip(), "files": 1}


def main() -> int:
    names = {path.name for path in SOURCE.iterdir() if path.is_dir()}
    if names != EXPECTED:
        print(json.dumps({"status": "error", "missing": sorted(EXPECTED - names), "unexpected": sorted(names - EXPECTED)}, ensure_ascii=False))
        return 1
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    OUTPUT.mkdir(parents=True)

    packages = []
    for directory in sorted(path for path in SOURCE.iterdir() if path.is_dir()):
        metadata = validate_skill(directory)
        package = OUTPUT / f"{directory.name}.zip"
        files = sorted(path for path in directory.rglob("*") if path.is_file())
        with zipfile.ZipFile(package, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for path in files:
                member = (Path(directory.name) / path.relative_to(directory)).as_posix()
                info = zipfile.ZipInfo(member, date_time=ZIP_TIMESTAMP)
                info.create_system = 3
                info.external_attr = ZIP_FILE_MODE << 16
                info.compress_type = zipfile.ZIP_DEFLATED
                info.flag_bits |= 0x800
                archive.writestr(
                    info,
                    path.read_bytes(),
                    compress_type=zipfile.ZIP_DEFLATED,
                    compresslevel=9,
                )
        metadata["files"] = len(files)
        metadata["package"] = package.name
        metadata["sha256"] = sha256(package)
        packages.append(metadata)

    manifest = {
        "status": "ok",
        "format": "zip_with_named_skill_directory",
        "visibility": "private_only",
        "packages": packages,
    }
    (OUTPUT / "build-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
