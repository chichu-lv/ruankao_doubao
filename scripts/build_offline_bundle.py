#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from architectpass_offline import BundleError, OfflineBundleBuilder


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a private ArchitectPass offline delivery ZIP")
    parser.add_argument("--materials-root", type=Path, required=True, help="parent containing the two exact authorized folders")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "dist/offline")
    parser.add_argument("--allow-incomplete", action="store_true", help="build an unmistakably PARTIAL archive")
    parser.add_argument("--exclude-runtime-assets", action="store_true", help="exclude private local models/indexes/transcripts")
    args = parser.parse_args()
    try:
        result = OfflineBundleBuilder(ROOT).build(
            materials_root=args.materials_root,
            output_directory=args.output_dir,
            allow_incomplete=args.allow_incomplete,
            include_runtime_assets=not args.exclude_runtime_assets,
        )
    except BundleError as error:
        print(json.dumps({"status": "FAIL", "error": str(error)}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
