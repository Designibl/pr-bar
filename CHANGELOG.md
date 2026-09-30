# Changelog

Format: [Keep a Changelog](https://keepachangelog.com), versioning: [SemVer](https://semver.org).

## [Unreleased]
### Added
- **Ready to merge** section for your approved PRs that have nothing left to fix.
- "Needs: …" line on PRs awaiting fixes explaining why.

### Changed
- **Awaiting fixes** now also includes PRs with unresolved review threads and merge conflicts. Only failing *required* checks count as blocking CI.

## [0.2.0] - 2026-09-30
### Added
- **Update PR Bar** menu item, with an indicator when your clone is behind `main`.
- Claude Squad (`cs`) support: start a session or open a review in the PR's local clone.
- Claude Code bundled with the desktop app is detected; `agent_paths` config override.
- Version shown in the menu footer.

## [0.1.0] - 2026-09-30
### Added
- SwiftBar menu bar tracker for your GitHub PRs, polled by a launch agent via `gh`.
- Sections for awaiting your review, ready for review, awaiting fixes and in draft.
- Per-PR files/lines, staleness, CI, merge and review status; Linear/GitHub issue and preview links.
- Copy summaries as Markdown, Slack or plain text; poll interval settings; Refresh now.
- Review or start sessions with installed agents; detects Claude Code from the desktop app.
