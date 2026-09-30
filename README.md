# PR Bar

A macOS menu bar tracker for your GitHub pull requests. A launch agent polls GitHub with the
[`gh` CLI](https://cli.github.com); a [SwiftBar](https://github.com/swiftbar/SwiftBar) plugin renders the result.

## What it shows

- Count of your open PRs (plus 👀 N for PRs awaiting **your** review — bound to your user, not your teams)
- Sections: **Awaiting your review**, **Ready for review**, **Awaiting fixes** (changes requested, failing CI or conflicts), **In draft**
- Per PR: files and +/- lines, age of latest commit (amber > 7d, red > 14d), CI status, merge status / conflicts, review decision
- Links found in the PR description/comments: Linear issues, GitHub issues, and previews (Vercel, Netlify, Cloudflare Pages…)
- Click a PR to open it, or use its submenu to **Review with** an installed agent (Claude Code, Codex, Gemini CLI, opencode) in Terminal
- **Start a session** with any detected agent
- **Copy summary** to the clipboard as Markdown, Slack or plain text — all PRs or only those needing your review
- **Settings**: poll interval (1m, 5m, 15m, 30m, 1h, 6h, day), enable/disable detected agents, and **Refresh now**
- Colours are light/dark pairs so they stay readable in both appearances

## Prerequisites

- macOS 13+
- [Homebrew](https://brew.sh)
- `gh` and SwiftBar (the installer installs them via Homebrew if missing):
  ```bash
  brew install gh
  brew install --cask swiftbar
  ```
- `python3` (ships with the Xcode Command Line Tools: `xcode-select --install`)
- Logged in to GitHub: `gh auth login`
- Launch SwiftBar once and pick a plugin folder
- Optional: an agent CLI such as `claude`, `codex`, `gemini` or `opencode` on your PATH

## Install

```bash
git clone https://github.com/Designibl/pr-bar.git
cd pr-bar
./install.sh
```

This symlinks the plugin into your SwiftBar plugin folder and loads the launch agent
(`~/Library/LaunchAgents/com.prbar.agent.plist`). Data is cached in `~/.config/prbar/`.

Uninstall with `./uninstall.sh`.

## Updating

The plugin is a symlink into your clone and the launch agent runs from it, so updating is just:

```bash
cd pr-bar
git checkout main && git pull
./install.sh   # optional, safe to re-run: reloads the launch agent
```

Your settings in `~/.config/prbar/` are kept. The current version is shown in the menu footer; see
[Releases](../../releases) and [CHANGELOG.md](CHANGELOG.md). To pin a version: `git checkout v0.1.0`.

## How it works

```
launchd (every N seconds) -> bin/prbar-fetch -> gh api graphql -> ~/.config/prbar/cache.json
SwiftBar (every minute)   -> plugin/prbar.1m.py reads cache.json and draws the menu
Menu actions              -> bin/prbar-ctl (refresh, interval, copy, agents)
```

The plugin never calls GitHub itself, so the menu stays instant. Changing the interval rewrites and reloads the launch agent.

## Troubleshooting

- Menu shows `!` — the last poll failed; the message is in the menu. Check `gh auth status` and `~/.config/prbar/fetch.log`.
- "No data yet" — run **Refresh now**, or `bin/prbar-ctl install-agent`.
- Agent missing from menu — agents are found on your PATH (`/opt/homebrew/bin`, `~/.local/bin`, `~/.npm-global/bin` are checked). Claude Code bundled with the Claude desktop app is detected automatically. For anything else, set a path in `~/.config/prbar/config.json`: `{"agent_paths": {"claude": "/path/to/claude"}}`.

## Development

```bash
python3 -m unittest discover -s tests -v
```

See [CONTRIBUTING.md](CONTRIBUTING.md). Maintainers: `scripts/setup-repo.sh <owner>/pr-bar` creates the public repo and applies protections.

## Licence

[MIT](LICENSE)
