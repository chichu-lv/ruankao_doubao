from __future__ import annotations

import csv
import hashlib
import io
import json
from pathlib import Path
from typing import Any

from .errors import StateError
from .models import WriteContext
from .store import InMemoryStore


SCHEMA_VERSION = 1


def build_backup(snapshot: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    data_hash = hashlib.sha256(
        json.dumps(snapshot, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return {"schema_version": SCHEMA_VERSION, "sha256": data_hash, "data": snapshot}


def verify_backup(backup: dict[str, Any]) -> None:
    if backup.get("schema_version") != SCHEMA_VERSION:
        raise StateError("UNSUPPORTED_SCHEMA_VERSION", "backup schema version is not supported")
    expected = hashlib.sha256(
        json.dumps(backup.get("data"), ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    if backup.get("sha256") != expected:
        raise StateError("BACKUP_CHECKSUM_MISMATCH", "backup checksum does not match its contents")


def export_json(backup: dict[str, Any]) -> str:
    verify_backup(backup)
    return json.dumps(backup, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def export_csv_tables(backup: dict[str, Any]) -> dict[str, str]:
    verify_backup(backup)
    result: dict[str, str] = {}
    for table, rows in backup["data"].items():
        fields = sorted({key for row in rows for key in row})
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: _flat(row.get(key)) for key in fields})
        result[table] = output.getvalue()
    return result


def export_markdown(backup: dict[str, Any]) -> str:
    verify_backup(backup)
    lines = ["# ArchitectPass state export", ""]
    for table, rows in backup["data"].items():
        lines.extend((f"## {table}", "", f"Records: {len(rows)}", ""))
        for row in rows:
            lines.append(f"- `{json.dumps(row, ensure_ascii=False, sort_keys=True)}`")
        lines.append("")
    return "\n".join(lines)


def safe_backup_path(root: Path, filename: str) -> Path:
    if not filename.endswith(".json") or Path(filename).name != filename:
        raise StateError("PATH_NOT_ALLOWED", "backup filename must be a plain .json filename")
    resolved_root = root.resolve()
    target = (resolved_root / filename).resolve()
    if target.parent != resolved_root:
        raise StateError("PATH_NOT_ALLOWED", "backup target must stay inside the allowlisted backup directory")
    return target


def restore_backup(
    store: InMemoryStore,
    *,
    target_backup: dict[str, Any],
    current_backup: dict[str, Any],
    context: WriteContext,
) -> None:
    """Restore only after confirming both a valid target and a current rollback backup."""
    verify_backup(target_backup)
    verify_backup(current_backup)
    actual_current = build_backup(store.snapshot())
    if actual_current["sha256"] != current_backup["sha256"]:
        raise StateError("STALE_PRE_RESTORE_BACKUP", "current backup does not match current store state")
    store.restore_snapshot(target_backup["data"], context=context, rollback_ref=current_backup["sha256"])


def _flat(value: Any) -> Any:
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return value
