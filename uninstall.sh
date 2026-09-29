#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"$ROOT/bin/prbar-ctl" uninstall-agent || true
PLUGIN_DIR="$(defaults read com.ameba.SwiftBar PluginDirectory 2>/dev/null || true)"
PLUGIN_DIR="${PLUGIN_DIR/#\~/$HOME}"
[[ -n "$PLUGIN_DIR" ]] && rm -f "$PLUGIN_DIR/prbar.1m.py"
open -g "swiftbar://refreshallplugins" || true
echo "Removed. Config/cache remain in ~/.config/prbar (delete it if you like)."
