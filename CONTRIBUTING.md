# Contributing

Thanks for helping improve PR Bar!

1. **Open an issue first** for anything larger than a small fix, so we can agree on direction.
2. Fork the repo and create a branch from `main` (`feat/…`, `fix/…`).
3. Make your change. Keep it small and focused; match the surrounding style (standard-library Python 3.9+, no third-party dependencies).
4. Add or update tests in `tests/` for logic in `bin/prbar_common.py`.
5. Run `python3 -m unittest discover -s tests -v` and try the plugin against your own GitHub account.
6. Any colour you add must be a `light,dark` pair readable in both appearances.
7. Open a pull request describing what and why, with a screenshot for menu changes.

## Review and CI

- All changes land through pull requests; direct pushes to `main` are blocked.
- CI workflows from first-time and external contributors do **not** run until the maintainer approves them.
- A maintainer (code owner) must review and approve every merge.

## Local testing tips

Point the tool at a scratch config with `PRBAR_HOME=/tmp/prbar-test`, drop a hand-written `cache.json` there and run `python3 plugin/prbar.1m.py` to see the SwiftBar output.

## Licence

By contributing you agree your contributions are licensed under the MIT licence.
