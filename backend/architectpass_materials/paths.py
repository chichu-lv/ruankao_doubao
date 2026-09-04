from __future__ import annotations

from pathlib import Path

from .errors import MaterialError


def resolve_authorized(path: Path, authorized_roots: tuple[Path, ...]) -> Path:
    resolved = path.resolve()
    for root in authorized_roots:
        resolved_root = root.resolve()
        if resolved == resolved_root or resolved_root in resolved.parents:
            return resolved
    raise MaterialError("PATH_NOT_AUTHORIZED", "material path is outside the authorized roots")


def safe_output(directory: Path, filename: str) -> Path:
    if Path(filename).name != filename or filename in ("", ".", ".."):
        raise MaterialError("PATH_NOT_AUTHORIZED", "output filename must not contain a path")
    root = directory.resolve()
    target = (root / filename).resolve()
    if target.parent != root:
        raise MaterialError("PATH_NOT_AUTHORIZED", "output path escaped its directory")
    return target
