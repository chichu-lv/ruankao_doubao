from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import Any


ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)
FILE_MODE = 0o100644
ARCHIVE_ROOT = Path("ArchitectPass-offline")
RUNTIME_ASSET_DIRS = ("models", "parsed")
SENSITIVE_NAME_PARTS = ("password", "passwd", "cookie", "token", "secret", "private-key")


class BundleError(ValueError):
    pass


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_files(root: Path) -> list[Path]:
    if not root.is_dir() or root.is_symlink():
        raise BundleError(f"material root must be a real directory: {root}")
    files: list[Path] = []
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise BundleError(f"symlinks are not allowed in an offline bundle: {path}")
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if any(part in {".", ".."} for part in relative.parts):
            raise BundleError(f"unsafe material path: {relative}")
        lowered = path.name.casefold()
        if lowered == ".env" or lowered.endswith((".pem", ".key", ".p12", ".pfx")):
            raise BundleError(f"credential-like file is not allowed: {relative}")
        if any(part in lowered for part in SENSITIVE_NAME_PARTS):
            raise BundleError(f"credential-like filename is not allowed: {relative}")
        files.append(path)
    return files


class OfflineBundleBuilder:
    def __init__(self, project_root: Path) -> None:
        self.root = project_root.resolve()
        self.project = json.loads((self.root / "deployment/doubao/project-v1.json").read_text(encoding="utf-8"))
        self.sources = json.loads((self.root / "materials/manifests/authorized-sources-v1.json").read_text(encoding="utf-8"))
        configured = self.project["materials"]["authorized_baidu_scopes"]
        authorized = self.sources["authorization"]["allowed_remote_roots"]
        if configured != authorized or len(authorized) != 2:
            raise BundleError("offline bundle requires the same two exact authorized material roots")
        self.authorized_roots: tuple[str, str] = tuple(authorized)

    def build(
        self,
        *,
        materials_root: Path,
        output_directory: Path,
        allow_incomplete: bool = False,
        include_runtime_assets: bool = True,
        enforce_release_git: bool = True,
    ) -> dict[str, Any]:
        materials_root = materials_root.resolve()
        output_directory = output_directory.resolve()
        if enforce_release_git:
            self._verify_release_git()
        material_files, missing_declared = self._collect_materials(materials_root)
        if missing_declared and not allow_incomplete:
            preview = ", ".join(missing_declared[:5])
            raise BundleError(
                f"{len(missing_declared)} declared material files are absent; refusing a misleading complete bundle: {preview}"
            )

        self._build_skills()
        tracked = self._tracked_files()
        runtime_assets = self._runtime_assets() if include_runtime_assets else []
        status = "PARTIAL" if missing_declared else "PASS"
        version = (self.root / "VERSION").read_text(encoding="utf-8").strip()
        suffix = "-PARTIAL" if status == "PARTIAL" else ""
        output_directory.mkdir(parents=True, exist_ok=True)
        target = output_directory / f"architectpass-offline-{version}{suffix}.zip"
        if target.exists():
            raise BundleError(f"output already exists; choose a new directory or move it first: {target}")

        material_records = [self._record(path, materials_root) for path in material_files]
        runtime_records = [self._record(path, self.root) for path in runtime_assets]
        manifest: dict[str, Any] = {
            "schema_version": 1,
            "status": status,
            "version": version,
            "source_commit": self._git_output("rev-parse", "HEAD") if enforce_release_git else "test-fixture",
            "privacy": "private_personal_offline_backup",
            "redistribution_allowed": False,
            "contains_credentials": False,
            "authorized_roots": list(self.authorized_roots),
            "declared_missing": missing_declared,
            "project_file_count": len(tracked),
            "material_file_count": len(material_records),
            "material_total_bytes": sum(item["size_bytes"] for item in material_records),
            "runtime_asset_file_count": len(runtime_records),
            "runtime_asset_total_bytes": sum(item["size_bytes"] for item in runtime_records),
            "materials": material_records,
            "runtime_assets": runtime_records,
            "entrypoint": "README-OFFLINE.md",
        }

        with zipfile.ZipFile(target, "w", allowZip64=True, compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            for path in tracked:
                self._write_file(archive, path, ARCHIVE_ROOT / "project" / path.relative_to(self.root))
            for path in sorted((self.root / "dist/doubao-skills").glob("*")):
                if path.is_file():
                    self._write_file(archive, path, ARCHIVE_ROOT / "prebuilt-skills" / path.name)
            for path in material_files:
                self._write_file(archive, path, ARCHIVE_ROOT / "private-materials" / path.relative_to(materials_root))
            for path in runtime_assets:
                self._write_file(archive, path, ARCHIVE_ROOT / "project" / path.relative_to(self.root))
            self._write_bytes(
                archive,
                ARCHIVE_ROOT / "offline-manifest.json",
                (json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8"),
            )
            self._write_bytes(archive, ARCHIVE_ROOT / "README-OFFLINE.md", self._offline_readme(status).encode("utf-8"))

        result = {
            "status": status,
            "archive": str(target),
            "sha256": _sha256(target),
            "size_bytes": target.stat().st_size,
            "declared_missing": missing_declared,
            "material_file_count": len(material_records),
            "runtime_asset_file_count": len(runtime_records),
        }
        return result

    def _verify_release_git(self) -> None:
        if self._git_output("branch", "--show-current") != "main":
            raise BundleError("offline release bundles must be built from main")
        for args in (("diff", "--quiet"), ("diff", "--cached", "--quiet")):
            result = subprocess.run(["git", *args], cwd=self.root, check=False)
            if result.returncode != 0:
                raise BundleError("offline release bundle requires a clean tracked worktree")

    def _tracked_files(self) -> list[Path]:
        result = subprocess.run(
            ["git", "ls-files", "-z"], cwd=self.root, capture_output=True, check=False
        )
        if result.returncode != 0:
            raise BundleError("could not enumerate release files")
        files = []
        for raw in result.stdout.split(b"\0"):
            if not raw:
                continue
            relative = Path(os.fsdecode(raw))
            path = (self.root / relative).resolve()
            if not path.is_file() or self.root not in path.parents:
                raise BundleError(f"tracked release path is missing or unsafe: {relative}")
            files.append(path)
        return sorted(files)

    def _collect_materials(self, materials_root: Path) -> tuple[list[Path], list[str]]:
        files: list[Path] = []
        for name in self.authorized_roots:
            files.extend(_safe_files(materials_root / name))
        declared = [
            item for item in self.sources["resources"]
            if item.get("kind") in {"pdf", "video"} and item.get("relative_path") not in {None, "."}
        ]
        missing = [
            f"{item['remote_root']}/{item['relative_path']}"
            for item in declared
            if not (materials_root / item["remote_root"] / item["relative_path"]).is_file()
        ]
        return sorted(files), sorted(missing)

    def _runtime_assets(self) -> list[Path]:
        files: list[Path] = []
        for name in RUNTIME_ASSET_DIRS:
            directory = self.root / "materials" / name
            if directory.is_dir():
                files.extend(_safe_files(directory))
        if (self.root / "vendor").is_dir():
            files.extend(_safe_files(self.root / "vendor"))
        return sorted(files)

    def _build_skills(self) -> None:
        result = subprocess.run(
            [os.fspath(Path(sys.executable)), "-X", "utf8", str(self.root / "scripts/build_doubao_skills.py")],
            cwd=self.root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        if result.returncode != 0:
            raise BundleError(f"skill package build failed: {result.stdout}{result.stderr}")

    def _git_output(self, *args: str) -> str:
        result = subprocess.run(["git", *args], cwd=self.root, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            raise BundleError(f"git {' '.join(args)} failed")
        return result.stdout.strip()

    @staticmethod
    def _record(path: Path, relative_root: Path) -> dict[str, Any]:
        return {
            "path": path.relative_to(relative_root).as_posix(),
            "size_bytes": path.stat().st_size,
            "sha256": _sha256(path),
        }

    @staticmethod
    def _write_file(archive: zipfile.ZipFile, source: Path, member: Path) -> None:
        compression = zipfile.ZIP_STORED if source.suffix.casefold() in {".mp4", ".mkv", ".mov", ".webm", ".zip"} else zipfile.ZIP_DEFLATED
        info = zipfile.ZipInfo(member.as_posix(), date_time=ZIP_TIMESTAMP)
        info.create_system = 3
        info.external_attr = FILE_MODE << 16
        info.compress_type = compression
        info.flag_bits |= 0x800
        with source.open("rb") as input_stream, archive.open(info, "w", force_zip64=True) as output_stream:
            shutil.copyfileobj(input_stream, output_stream, length=1024 * 1024)

    @staticmethod
    def _write_bytes(archive: zipfile.ZipFile, member: Path, payload: bytes) -> None:
        info = zipfile.ZipInfo(member.as_posix(), date_time=ZIP_TIMESTAMP)
        info.create_system = 3
        info.external_attr = FILE_MODE << 16
        info.compress_type = zipfile.ZIP_DEFLATED
        info.flag_bits |= 0x800
        archive.writestr(info, payload, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)

    @staticmethod
    def _offline_readme(status: str) -> str:
        return f"""# ArchitectPass 离线私有交付包

资料状态：`{status}`。如果状态是 `PARTIAL`，先查看 `offline-manifest.json` 的 `declared_missing`。该状态表示包内资料完整性，豆包项目是否安装完成须以真实安装结果为准。

Windows 10/11 64 位与 Apple 芯片 Mac 已附带 Python 3.12 和依赖，无需预装 Python 或 Git，也无需访问包源。Windows 建议解压至 `C:\\AP` 等短路径，在 project 目录运行 `scripts\\start_windows.cmd`；Mac 运行 `bash scripts/start_macos.sh`。豆包、飞书、芝士架构是在线服务，使用接收者自己的账号。

将整个 `ArchitectPass-offline` 目录解压到用户选择的私有本机目录。不要把本压缩包或课程资料上传到公开 Git、网盘、聊天附件或公共项目。

将本目录放在本地磁盘上，在豆包桌面客户端新建工作任务并选择「本地电脑」，发送以下提示词并提供目录位置。网页版默认的「云电脑」不能读取本机离线包。首次登录与系统权限弹窗需本人完成；安装与日常训练由豆包继续执行。

交给豆包的启动提示词：

```text
你就是当前执行部署的豆包，不是 Codex。不要打开另一个豆包或在虚拟桌面登录豆包。未明确要求恢复时只使用我提供的包目录，不要扫描主目录、Downloads 或开发仓库寻找旧部署；包路径缺失时直接问我。先确认工具操作我这台电脑；无法确认时停止安装，指导我在桌面客户端新建“本地电脑”任务。请使用本机已解压的 ArchitectPass-offline 目录部署“架构上岸教练”。先读取 project/deployment/doubao/execution-context-v1.md、README-OFFLINE.md，再执行 project/deployment/offline/bootstrap-v1.md。优先按你当前官方创建技能指南与 folder-skills-v1.md 自动安装九个技能文件夹和本机绑定；只有官方方式不可用时才让我完成具体点击，不找不存在的项目指令字段，不转用网页豆包。用包内代码、资料和九个技能完成部署；仅在本次包目录或官方九技能安装绑定确认本次部署后，对已有本次项目和状态先核对后继续，只有首次无档案时才建立独立空档案。连接我自己的飞书和芝士架构账号，完成真实健康检查后开始训练。我授权本次安装所需的项目内操作及九个官方技能目录的新增写入；第三方登录和系统授权由我本人完成，不重做 Codex 开发或能力审计。分别报告本机持久入口与原生侧边栏项目的真实状态。
```

换新任务时仍选择「本地电脑」。如果当前豆包没有项目级持久文件绑定入口，使用以下恢复提示词；不必重复提供账号标识或学习进度：

```text
从【本机实际 ArchitectPass-offline/project 路径】恢复架构上岸教练，先读取 deployment/doubao/system-instructions-v1.md 和 dist/deployment/project-state.json，再回读最近检查点继续训练。
```
"""
