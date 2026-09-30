#!/usr/bin/env python3
# <swiftbar.hideAbout>true</swiftbar.hideAbout>
# <swiftbar.hideRunInTerminal>true</swiftbar.hideRunInTerminal>
# <swiftbar.hideLastUpdated>true</swiftbar.hideLastUpdated>
# <swiftbar.hideDisablePlugin>true</swiftbar.hideDisablePlugin>
"""SwiftBar plugin: renders the cache written by the PR Bar launch agent.

This script never calls GitHub itself; it only reads ~/.config/prbar/cache.json.
"""
import os
import sys
from datetime import datetime, timezone

# Resolve through the symlink SwiftBar's plugin folder points at.
HERE = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "bin"))
import prbar_common as c  # noqa: E402

CTL = str(c.BIN / "prbar-ctl")

# "light,dark" pairs, each chosen for contrast on both menu bar appearances.
RED = "#C62828,#FF6B6B"
GREEN = "#1B7F3B,#5CD07F"
AMBER = "#8A5A00,#F5C451"
BLUE = "#0B5CAD,#6CB2FF"
GRAY = "#5F6368,#A0A4AA"

BUCKET_COLOR = {"review": BLUE, "merge": GREEN, "ready": GREEN, "fixes": RED, "draft": GRAY}
BUCKET_ICON = {"review": "eye", "merge": "arrow.triangle.merge", "ready": "checkmark.circle", "fixes": "exclamationmark.triangle", "draft": "pencil.circle"}


def clean(s):
    return (s or "").replace("|", "¦").replace("\n", " ").strip()


def out(text, depth=0, **params):
    parts = ["%s=%s" % (k, v if " " not in str(v) else '"%s"' % v) for k, v in params.items()]
    print("%s%s%s" % ("--" * depth, text, (" | " + " ".join(parts)) if parts else ""))


def sep(depth=0):
    print("%s---" % ("--" * depth))


def ctl(text, *args, depth=0, refresh=False, **extra):
    params = {"bash": CTL, "terminal": "false", "refresh": "true" if refresh else "false"}
    for i, a in enumerate(args, 1):
        params["param%d" % i] = a
    params.update(extra)
    out(text, depth, **params)


def stale_color(secs):
    if secs is None:
        return GRAY
    if secs > 14 * 86400:
        return RED
    if secs > 7 * 86400:
        return AMBER
    return GRAY


def ci_line(pr):
    text = c.CI_TEXT.get(pr["ci"], "no CI")
    color = {"SUCCESS": GREEN, "FAILURE": RED, "ERROR": RED, "PENDING": AMBER, "EXPECTED": AMBER}.get(pr["ci"], GRAY)
    mark = {"SUCCESS": "✓", "FAILURE": "✗", "ERROR": "✗"}.get(pr["ci"], "◌" if pr["ci"] else "–")
    return "%s %s" % (mark, text), color


def render_pr(pr, key, agents):
    age = c.age_seconds(pr["last_change"])
    warn = " ⚠" if pr["mergeable"] == "CONFLICTING" else ""
    title = clean(pr["title"])
    if len(title) > 60:
        title = title[:59] + "…"
    out(
        "#%d %s  +%d/-%d · %s%s" % (pr["number"], title, pr["additions"], pr["deletions"], c.fmt_age(age), warn),
        1,
        href=pr["url"],
        color=BUCKET_COLOR[key],
    )
    # --- details submenu (depth 2)
    out("%s · %s" % (pr["repo"], pr["branch"] or "?"), 2, color=GRAY)
    if key == "fixes" and pr.get("fix_reasons"):
        out("Needs: %s" % ", ".join(pr["fix_reasons"]), 2, color=RED)
    if key == "review":
        out("Author: @%s" % pr["author"], 2, color=GRAY)
    out("%d files · +%d / -%d lines" % (pr["files"], pr["additions"], pr["deletions"]), 2)
    out("Last change %s ago" % c.fmt_age(age), 2, color=stale_color(age))
    text, color = ci_line(pr)
    out(text, 2, color=color)
    out("Merge: %s" % c.merge_text(pr), 2, color=RED if pr["mergeable"] == "CONFLICTING" else GRAY)
    if pr["review_decision"]:
        out("Review: %s" % pr["review_decision"].replace("_", " ").lower(), 2,
            color=RED if pr["review_decision"] == "CHANGES_REQUESTED" else GREEN)
    if pr["issues"] or pr["previews"]:
        sep(2)
        for i in pr["issues"]:
            out("Issue: %s" % i["label"], 2, href=i["url"])
        for p in pr["previews"]:
            out("Preview: %s" % p["label"], 2, href=p["url"])
    sep(2)
    out("Open on GitHub", 2, href=pr["url"])
    for binary, name, enabled, _path in agents:
        if enabled:
            ctl("Review with %s" % name, "review", binary, pr["url"], depth=2)
    out("Copy link", 2, bash="/bin/sh", param1="-c", param2="printf %s '" + pr["url"] + "' | pbcopy", terminal="false")


def main():
    cache = c.load_cache()
    cfg = c.load_config()
    agents = c.installed_agents()

    if not cache:
        out("PR –", sfimage="arrow.triangle.pull")
        sep()
        out("No data yet", color=GRAY)
        ctl("Refresh now", "refresh", refresh=True)
        ctl("Install / repair launch agent", "install-agent", refresh=True)
        return

    prs = cache["prs"]
    groups = c.group(prs)
    mine = len(prs) - len(groups["review"])
    todo = len(groups["review"])

    # --- menu bar title
    title = str(mine) + ("  👀" + str(todo) if todo else "")
    if cache.get("error"):
        title += " !"
    out(title, sfimage="arrow.triangle.pull")
    sep()

    if cache.get("error"):
        out("⚠ Last refresh failed: %s" % clean(cache["error"])[:80], color=RED)
        sep()

    # --- sections
    for key, label in c.SECTIONS:
        items = groups[key]
        out("%s (%d)" % (label, len(items)), color=BUCKET_COLOR[key], sfimage=BUCKET_ICON[key])
        for pr in items:
            render_pr(pr, key, agents)
        if not items:
            out("None", 1, color=GRAY)
    sep()

    # --- clipboard
    out("Copy summary", sfimage="doc.on.clipboard")
    for scope, scope_label in (("all", "All PRs"), ("review", "Needs my review"), ("mine-review", "My PRs needing review")):
        out(scope_label, 1)
        for fmt, fmt_label in (("md", "Markdown"), ("slack", "Slack"), ("text", "Plain text")):
            ctl(fmt_label, "copy", fmt, scope, depth=2)
    sep()

    # --- agents
    out("Start a session", sfimage="terminal")
    shown = False
    for binary, name, enabled, _path in agents:
        if enabled:
            ctl(name, "session", binary, depth=1)
            shown = True
    if not shown:
        out("No agents found (see Settings)", 1, color=GRAY)
    sep()

    # --- footer / settings
    fetched = cache.get("fetched_at")
    ago = c.fmt_age(c.age_seconds(fetched)) if fetched else "never"
    out("@%s · updated %s ago · v%s" % (cache.get("login") or "?", ago, c.version()), color=GRAY)
    ctl("Refresh now", "refresh", refresh=True, sfimage="arrow.clockwise")
    behind = cache.get("update_behind") or 0
    ctl("Update PR Bar" + (" (%d new commit%s)" % (behind, "" if behind == 1 else "s") if behind else ""),
        "update", refresh=True, sfimage="arrow.down.circle", **({"color": AMBER} if behind else {}))
    out("Settings", sfimage="gearshape")
    out("Poll interval", 1)
    for label, secs in c.INTERVALS:
        ctl(label, "set-interval", str(secs), depth=2, refresh=True, checked="true" if cfg["interval"] == secs else "false")
    out("Agents", 1)
    if agents:
        for binary, name, enabled, _path in agents:
            ctl(name, "toggle-agent", binary, depth=2, refresh=True, checked="true" if enabled else "false")
    else:
        out("None detected (claude, codex, gemini, opencode)", 2, color=GRAY)
    out("Open config folder", 1, bash="/usr/bin/open", param1=str(c.CONFIG_DIR), terminal="false")


if __name__ == "__main__":
    main()
