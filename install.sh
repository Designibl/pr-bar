#!/usr/bin/env bash
# Installs PR Bar: checks/installs prerequisites, links the SwiftBar plugin,
# and loads the launch agent that polls GitHub via the gh CLI.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ "$(uname)" != "Darwin" ]]; then
  echo "PR Bar only supports macOS." >&2; exit 1
fi
if ! command -v brew >/dev/null; then
  echo "Homebrew is required: https://brew.sh" >&2; exit 1
fi

command -v gh >/dev/null || { echo "Installing gh..."; brew install gh; }
[[ -d /Applications/SwiftBar.app || -d "$HOME/Applications/SwiftBar.app" ]] \
  || { echo "Installing SwiftBar..."; brew install --cask swiftbar; }

if ! gh auth status >/dev/null 2>&1; then
  echo "gh is not authenticated. Run: gh auth login" >&2; exit 1
fi

chmod +x "$ROOT/bin/prbar-ctl" "$ROOT/bin/prbar-fetch" "$ROOT/plugin/prbar.1m.py"

PLUGIN_DIR="$(defaults read com.ameba.SwiftBar PluginDirectory 2>/dev/null || true)"
if [[ -z "$PLUGIN_DIR" ]]; then
  echo "SwiftBar has no plugin folder yet. Open SwiftBar once, choose a plugin folder, then re-run ./install.sh" >&2
  open -a SwiftBar || true
  exit 1
fi
PLUGIN_DIR="${PLUGIN_DIR/#\~/$HOME}"
mkdir -p "$PLUGIN_DIR"
ln -sf "$ROOT/plugin/prbar.1m.py" "$PLUGIN_DIR/prbar.1m.py"

"$ROOT/bin/prbar-ctl" install-agent
open -g "swiftbar://refreshallplugins" || true
echo "Done. PR Bar is in your menu bar; first data arrives within a few seconds."
