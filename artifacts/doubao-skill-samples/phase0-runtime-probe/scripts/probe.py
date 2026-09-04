#!/usr/bin/env python3
"""Dependency-free Phase 0 runtime probe."""

from __future__ import annotations

import sys


def main() -> int:
    if len(sys.argv) != 3:
        print("RUNTIME_ERROR:expected-two-markers")
        return 2
    print(f"RUNTIME_OK:{sys.argv[1]}:{sys.argv[2]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
