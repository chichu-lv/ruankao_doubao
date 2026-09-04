"""Incremental, source-traceable local material processing.

The public objects are loaded lazily so lightweight callers such as the
controller and acceptance runner do not require the optional PDF runtime.
"""

from importlib import import_module
from typing import Any


__all__ = ["MaterialCatalog", "MaterialImporter", "MaterialSearch", "next_review_action"]

_EXPORTS = {
    "MaterialCatalog": (".catalog", "MaterialCatalog"),
    "MaterialImporter": (".importer", "MaterialImporter"),
    "MaterialSearch": (".search", "MaterialSearch"),
    "next_review_action": (".progress", "next_review_action"),
}


def __getattr__(name: str) -> Any:
    try:
        module_name, attribute_name = _EXPORTS[name]
    except KeyError as error:
        raise AttributeError(name) from error
    value = getattr(import_module(module_name, __name__), attribute_name)
    globals()[name] = value
    return value
