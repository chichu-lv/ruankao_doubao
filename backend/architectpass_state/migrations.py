from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .errors import StateError


def load_migration(path: Path) -> dict[str, Any]:
    try:
        migration = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise StateError("INVALID_MIGRATION", f"cannot read migration {path.name}: {error}") from error
    required = {"migration_id", "from_version", "to_version", "backup_required", "operations", "rollback"}
    if not required.issubset(migration):
        raise StateError("INVALID_MIGRATION", f"migration {path.name} is missing required fields")
    if migration["to_version"] != migration["from_version"] + 1:
        raise StateError("INVALID_MIGRATION", f"migration {path.name} must advance exactly one version")
    if migration["backup_required"] is not True or not migration["rollback"]:
        raise StateError("UNSAFE_MIGRATION", f"migration {path.name} requires backup and rollback instructions")
    return migration


def migration_plan(directory: Path, current_version: int, target_version: int) -> list[dict[str, Any]]:
    if target_version < current_version:
        raise StateError("DOWNGRADE_NOT_PLANNED", "use an explicit rollback plan for downgrades")
    migrations = sorted((load_migration(path) for path in directory.glob("*.json")), key=lambda item: item["from_version"])
    plan = []
    version = current_version
    while version < target_version:
        matches = [item for item in migrations if item["from_version"] == version]
        if len(matches) != 1:
            raise StateError("MIGRATION_GAP", f"expected exactly one migration from version {version}")
        plan.append(matches[0])
        version = matches[0]["to_version"]
    return plan

