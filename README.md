# PR Bar

A macOS menu bar tracker for your GitHub pull requests. A launch agent polls GitHub with the
[`gh` CLI](https://cli.github.com); a [SwiftBar](https://github.com/swiftbar/SwiftBar) plugin renders the result.

<img width="293" height="327" alt="Screenshot 2026-09-30 at 09 11 38" src="https://github.com/user-attachments/assets/9ee5e995-5cac-43cc-b136-78a55eb4420f" />

## What it shows

- Count of your open PRs (plus 👀 N for PRs awaiting your review, whether requested of you directly or of a team you're in)
- Sections: **Awaiting your review** (split into *Requested of you* and one group per team; team lookup needs the `read:org` scope on your `gh` token), **Ready to merge** (approved, nothing left to fix), **Ready for review**, **Awaiting fixes** (changes requested, unresolved comments, conflicts or failing required checks), **In draft**
- Per PR: files and +/- lines, age of latest commit (amber > 7d, red > 14d), CI status, merge status / conflicts, review decision
- Links found in the PR description/comments: Linear issues, GitHub issues, and previews (Vercel, Netlify, Cloudflare Pages…)
- Click a PR to open it, or use its submenu to **Review with** an installed agent (Claude Code, Codex, Gemini CLI, opencode) in Terminal
- **Start a session** with any detected agent
- **Copy summary** to the clipboard as Markdown, Slack or plain text — all PRs, only those needing your review, or only your PRs waiting on someone else's review
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
- Optional: an agent CLI such as `claude`, `codex`, `gemini`, `opencode` or [Claude Squad](https://github.com/smtg-ai/claude-squad) (`cs`) on your PATH

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

Use **Update PR Bar** in the menu (it shows how many commits you're behind), or do it by hand. It fast-forwards your clone's `main`, reloads the launch agent and refreshes; it refuses if the clone has local changes or isn't on `main`. The plugin is a symlink into your clone and the launch agent runs from it, so the manual steps are:

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

## Claude Squad

If `cs` (or `claude-squad`) is on your PATH it appears as an agent. Claude Squad runs sessions in tmux worktrees and can't be handed a prompt, so **Review with Claude Squad** opens it in the PR's local clone and copies the review prompt to your clipboard; paste it into a new session. PR Bar finds the clone by scanning `~/Developer`, `~/code`, `~/src`, `~/Projects` and `~/dev` for a matching `origin`. Override in `~/.config/prbar/config.json`:

```json
{"repo_dirs": {"owner/repo": "~/path/to/clone"}, "code_dirs": ["~/work"]}
```

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
