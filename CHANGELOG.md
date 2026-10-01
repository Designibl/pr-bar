# Changelog

Format: [Keep a Changelog](https://keepachangelog.com), versioning: [SemVer](https://semver.org).

## [Unreleased]

## [0.4.2] - 2026-10-01
### Fixed
- Section headers were greyed out and uncoloured after 0.4.1. They are enabled and coloured again, with the icon still showing.

## [0.4.1] - 2026-10-01
### Changed
- "Ready for review" is now orange so it stands apart from "Ready to merge".

### Fixed
- Section header icons not showing in the menu (tint with `sfcolor` instead of `color`).

## [0.4.0] - 2026-09-30
### Added
- **Copy summary → My PRs needing review**: your open PRs waiting on someone else's review.

## [0.3.0] - 2026-09-30
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
