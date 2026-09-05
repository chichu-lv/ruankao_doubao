#!/bin/bash
set -e
cd "$(dirname "$0")/.."
if [ "$(uname -m)" = "arm64" ] && [ -f vendor/python-macos-arm64.tar.gz ]; then
    mkdir -p .runtime/bundled-python
    if [ ! -x .runtime/bundled-python/bin/python3 ]; then
        tar -xzf vendor/python-macos-arm64.tar.gz -C .runtime/bundled-python
    fi
    exec .runtime/bundled-python/bin/python3 scripts/bootstrap_local.py --offline "$@"
fi
exec python3 scripts/bootstrap_local.py "$@"
