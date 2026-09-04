from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .errors import ChekoError


class ChekoUiContract:
    def __init__(self, payload: dict[str, Any]) -> None:
        self.payload = payload
        if payload.get("schema_version") != "1.0.0" or not payload.get("contract_version"):
            raise ChekoError("UNSUPPORTED_UI_CONTRACT", "Cheko UI contract version is unsupported")

    @classmethod
    def load(cls, path: Path) -> "ChekoUiContract":
        return cls(json.loads(path.read_text(encoding="utf-8")))

    def target(self, name: str) -> dict[str, Any]:
        target = self.payload.get("targets", {}).get(name)
        if target is None:
            raise ChekoError("NAVIGATION_TARGET_UNKNOWN", "Cheko navigation target is not defined")
        return {
            "contract_version": self.payload["contract_version"],
            "target": copy_value(target),
            "fallbacks": copy_value(self.payload["fallbacks"]),
        }

    def fallback(self, reason: str) -> dict[str, Any]:
        return {
            "status": "manual_fallback",
            "reason": reason,
            "contract_version": self.payload["contract_version"],
            "steps": copy_value(self.payload["fallbacks"]),
        }


def copy_value(value: Any) -> Any:
    return json.loads(json.dumps(value, ensure_ascii=False))
