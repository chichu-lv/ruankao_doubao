#!/usr/bin/env python3
"""Install only this project's skills into Doubao's documented folder source.

Doubao must resolve --skill-root from its current official skill-creator guide.
This does not edit the client registry, create an account skill, or prove discovery.
"""
from __future__ import annotations

import argparse
import json
import uuid
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BINDING_NOTE = """
## 本机安装绑定（每次调用先读取）

先读取本技能目录下 `references/installation.json`，以其中 `project_root` 为本次安装根目录，
然后读取该根目录的 `deployment/doubao/system-instructions-v1.md` 和
`dist/deployment/project-state.json`。只使用这份实际绑定，不依赖当前聊天目录、旧对话、同名 Base
或开发电脑路径。文件缺失时报告绑定未完成，不擅自新建/切换状态库。其它相对项目路径均相对该根目录解析。
本技能由官方文件夹发现方式安装；文件存在不等于当前会话已发现，不等于账号云端技能已安装。

"""


def planned_files(project: Path, name: str) -> dict[Path, bytes]:
    source = project / "skills/doubao" / name
    files = {}
    for path in sorted(source.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"skill source contains a symlink: {name}")
        if path.is_file():
            files[path.relative_to(source)] = path.read_bytes()
    skill = files[Path("SKILL.md")].decode("utf-8")
    if not skill.startswith(f"---\nname: {name}\n"):
        raise ValueError(f"invalid skill name: {name}")
    end = skill.index("\n---\n", 4) + len("\n---\n")
    files[Path("SKILL.md")] = (skill[:end] + BINDING_NOTE + skill[end:]).encode("utf-8")
    binding = {
        "schema_version": 1,
        "project_root": str(project),
        "system_instructions": "deployment/doubao/system-instructions-v1.md",
        "state_binding": "dist/deployment/project-state.json",
        "installation_id": str(uuid.uuid5(uuid.NAMESPACE_URL, project.as_uri() + "/" + name)),
    }
    files[Path("references/installation.json")] = (json.dumps(binding, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    return files


def install(project: Path, skill_root: Path, request_id: str) -> dict:
    project = project.resolve(strict=True)
    if skill_root.is_symlink():
        raise ValueError("skill root must be the actual documented directory, not a symlink")
    skill_root = skill_root.resolve(strict=True)
    if skill_root.name != ".user_skills" or skill_root.parent.name != "workspace":
        raise ValueError("resolve the active official workspace/.user_skills directory first")
    if not skill_root.is_dir():
        raise ValueError("skill root is not a directory")
    for required in ("deployment/doubao/system-instructions-v1.md", "VERSION", "deployment/doubao/skills-v1.json"):
        if not (project / required).is_file():
            raise ValueError(f"incomplete project: {required}")
    manifest = json.loads((project / "deployment/doubao/skills-v1.json").read_text(encoding="utf-8"))
    names = [item["name"] for item in manifest["skills"]]
    if len(set(names)) != 9 or any(Path(name).name != name or name in (".", "..") for name in names):
        raise ValueError("expected nine distinct named project skills")
    plan = {name: planned_files(project, name) for name in names}
    reused = []
    # Preflight every target before writing any skill. Never replace unknown installs.
    for name, payload in plan.items():
        target = skill_root / name
        if target.is_symlink():
            raise ValueError(f"refusing existing symlink: {name}")
        if target.exists():
            if not target.is_dir() or any(p.is_symlink() for p in target.rglob("*")):
                raise ValueError(f"refusing unknown target: {name}")
            actual = {p.relative_to(target): p.read_bytes() for p in target.rglob("*") if p.is_file()}
            if actual != payload:
                raise ValueError(f"existing skill differs: {name}; no files replaced; confirm cleanup or use a new version")
            reused.append(name)
    audit_id = "folder-install-" + request_id
    result = {
        "status": "FILES_READY_DISCOVERY_UNVERIFIED",
        "request_id": request_id,
        "audit_id": audit_id,
        "project_root": str(project),
        "skill_root": str(skill_root),
        "created": [],
        "reused": reused,
        "account_registry_modified": False,
        "next_check": "Verify actual discovery and invocation in a new local Doubao task; never infer it from files alone.",
    }
    receipt = project / "dist/deployment/folder-installation.json"
    receipt.parent.mkdir(parents=True, exist_ok=True)
    result["status"] = "INSTALLING"
    receipt.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for name, payload in plan.items():
        if name in reused:
            continue
        target = skill_root / name
        target.mkdir()
        for relative, content in payload.items():
            destination = target / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(content)
        result["created"].append(name)
    result["status"] = "FILES_READY_DISCOVERY_UNVERIFIED"
    receipt.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill-root", type=Path, required=True)
    parser.add_argument("--request-id", default=str(uuid.uuid4()))
    args = parser.parse_args()
    try:
        print(json.dumps(install(ROOT, args.skill_root, args.request_id), ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, KeyError) as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc), "request_id": args.request_id}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
