from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ControllerError(Exception):
    code: str
    message: str

    def __str__(self) -> str:
        return self.message

    def as_dict(self) -> dict[str, str]:
        return {"code": self.code, "message": self.message}
