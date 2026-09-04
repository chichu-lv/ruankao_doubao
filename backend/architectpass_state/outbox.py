from __future__ import annotations

import copy
from collections.abc import Callable
from typing import Any


class OfflineOutbox:
    """In-process reference outbox; persistence adapter is added after Feishu mapping validation."""

    def __init__(self) -> None:
        self._pending: dict[str, dict[str, Any]] = {}

    def enqueue(self, request_id: str, operation: str, payload: dict[str, Any]) -> None:
        self._pending.setdefault(request_id, {"request_id": request_id, "operation": operation, "payload": copy.deepcopy(payload)})

    def replay(self, sender: Callable[[dict[str, Any]], Any]) -> list[Any]:
        results = []
        for request_id in list(self._pending):
            item = self._pending[request_id]
            result = sender(copy.deepcopy(item))
            results.append(result)
            if isinstance(result, dict) and result.get("status") == "ok":
                del self._pending[request_id]
        return results

    def pending(self) -> list[dict[str, Any]]:
        return copy.deepcopy(list(self._pending.values()))
