"""Shared helpers for PR Bar: paths, config, GitHub normalisation, formatting."""
import json
import os
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BIN = ROOT / "bin"
CONFIG_DIR = Path(os.environ.get("PRBAR_HOME", str(Path.home() / ".config" / "prbar")))
CONFIG_FILE = CONFIG_DIR / "config.json"
CACHE_FILE = CONFIG_DIR / "cache.json"
LABEL = "com.prbar.agent"


def version():
    try:
        return (ROOT / "VERSION").read_text().strip()
    except OSError:
        return "dev"


PLIST = Path.home() / "Library" / "LaunchAgents" / (LABEL + ".plist")

INTERVALS = [
    ("Every minute", 60),
    ("Every 5 minutes", 300),
    ("Every 15 minutes", 900),
    ("Every 30 minutes", 1800),
    ("Every hour", 3600),
    ("Every 6 hours", 21600),
    ("Every day", 86400),
]

# binary name -> display name. Detected via PATH; can be toggled off in settings.
AGENTS = {
    "claude": "Claude Code",
    "codex": "Codex CLI",
    "gemini": "Gemini CLI",
    "opencode": "opencode",
}

DEFAULT_CONFIG = {"interval": 300, "disabled_agents": []}

EXTRA_PATHS = [
    "/opt/homebrew/bin",
    "/usr/local/bin",
    str(Path.home() / ".local" / "bin"),
    str(Path.home() / ".claude" / "local"),
    str(Path.home() / ".npm-global" / "bin"),
    "/usr/bin",
    "/bin",
]


def full_path():
    parts = os.environ.get("PATH", "").split(":") + EXTRA_PATHS
    seen, out = set(), []
    for p in parts:
        if p and p not in seen:
            seen.add(p)
            out.append(p)
    return ":".join(out)


def load_config():
    cfg = dict(DEFAULT_CONFIG)
    try:
        cfg.update(json.loads(CONFIG_FILE.read_text()))
    except (OSError, ValueError):
        pass
    return cfg


def save_config(cfg):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(cfg, indent=2))


def load_cache():
    try:
        return json.loads(CACHE_FILE.read_text())
    except (OSError, ValueError):
        return None


def _desktop_claude():
    """Claude Code bundled with the Claude desktop app (not on PATH; path is versioned)."""
    base = Path.home() / "Library" / "Application Support" / "Claude" / "claude-code"
    best, best_key = None, None
    for d in base.glob("*/claude.app/Contents/MacOS/claude"):
        try:
            key = tuple(int(x) for x in d.parents[3].name.split("."))
        except ValueError:
            continue
        if os.access(str(d), os.X_OK) and (best_key is None or key > best_key):
            best, best_key = str(d), key
    return best


def resolve_agent(binary):
    """Absolute path for an agent: config override, then PATH, then known app bundles."""
    override = load_config().get("agent_paths", {}).get(binary)
    if override and os.access(os.path.expanduser(override), os.X_OK):
        return os.path.expanduser(override)
    found = shutil.which(binary, path=full_path())
    if found:
        return found
    return _desktop_claude() if binary == "claude" else None


def installed_agents():
    """Return [(binary, display, enabled, path)] for agents we can find."""
    disabled = set(load_config().get("disabled_agents", []))
    out = []
    for b, name in AGENTS.items():
        path = resolve_agent(b)
        if path:
            out.append((b, name, b not in disabled, path))
    return out


# ---------------------------------------------------------------- link parsing

_TRAIL = ".,;:!?)]}>'\""
LINEAR_RE = re.compile(r"https://linear\.app/[\w-]+/issue/[A-Z][A-Z0-9]*-\d+[^\s)>\]\"']*")
GH_ISSUE_RE = re.compile(r"https://github\.com/[\w.-]+/[\w.-]+/issues/\d+")
PREVIEW_RE = re.compile(
    r"https://[\w.-]+\.(?:vercel\.app|netlify\.app|pages\.dev|onrender\.com|surge\.sh)[^\s)>\]\"']*"
)


def _find(regex, text):
    out = []
    for m in regex.findall(text or ""):
        m = m.rstrip(_TRAIL)
        if m not in out:
            out.append(m)
    return out


def extract_links(*texts):
    """Find issue and preview links in PR body / comments."""
    blob = "\n".join(t for t in texts if t)
    issues = []
    for u in _find(LINEAR_RE, blob):
        m = re.search(r"/issue/([A-Z][A-Z0-9]*-\d+)", u)
        issues.append({"label": m.group(1), "url": u.split(m.group(1))[0] + m.group(1)})
    for u in _find(GH_ISSUE_RE, blob):
        parts = u.split("/")
        issues.append({"label": "%s/%s#%s" % (parts[3], parts[4], parts[6]), "url": u})
    previews = [
        {"label": re.sub(r"^https://", "", u).split("/")[0], "url": u}
        for u in _find(PREVIEW_RE, blob)
    ]
    return issues, previews


# ------------------------------------------------------------- classification

def _parse_ts(ts):
    return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


def age_seconds(ts, now=None):
    if not ts:
        return None
    now = now or datetime.now(timezone.utc)
    return max(0, int((now - _parse_ts(ts)).total_seconds()))


def fmt_age(secs):
    if secs is None:
        return "unknown"
    for unit, size in (("d", 86400), ("h", 3600), ("m", 60)):
        if secs >= size:
            return "%d%s" % (secs // size, unit)
    return "<1m"


def classify(pr):
    """Status bucket for a PR I authored: draft | fixes | ready."""
    if pr["draft"]:
        return "draft"
    if (
        pr["review_decision"] == "CHANGES_REQUESTED"
        or pr["ci"] in ("FAILURE", "ERROR")
        or pr["mergeable"] == "CONFLICTING"
    ):
        return "fixes"
    return "ready"


def normalise(node, review_requested=False):
    commit = ((node.get("commits") or {}).get("nodes") or [{}])[0].get("commit") or {}
    rollup = commit.get("statusCheckRollup") or {}
    comments = [c.get("body") or "" for c in (node.get("comments") or {}).get("nodes", [])]
    issues, previews = extract_links(node.get("body"), *comments)
    pr = {
        "number": node["number"],
        "title": node["title"],
        "url": node["url"],
        "repo": node["repository"]["nameWithOwner"],
        "branch": node.get("headRefName"),
        "author": (node.get("author") or {}).get("login", "ghost"),
        "draft": node["isDraft"],
        "additions": node.get("additions", 0),
        "deletions": node.get("deletions", 0),
        "files": node.get("changedFiles", 0),
        "last_change": commit.get("committedDate") or node.get("updatedAt"),
        "mergeable": node.get("mergeable"),
        "merge_state": node.get("mergeStateStatus"),
        "review_decision": node.get("reviewDecision"),
        "ci": rollup.get("state"),
        "issues": issues,
        "previews": previews,
        "review_requested": review_requested,
    }
    pr["bucket"] = classify(pr)
    return pr


SECTIONS = [
    ("review", "Awaiting your review"),
    ("ready", "Ready for review"),
    ("fixes", "Awaiting fixes"),
    ("draft", "In draft"),
]


def group(prs):
    """Return {bucket: [pr]}; 'review' = others' PRs requesting me."""
    out = {k: [] for k, _ in SECTIONS}
    for pr in prs:
        key = "review" if pr["review_requested"] else pr["bucket"]
        out[key].append(pr)
    return out


# ------------------------------------------------------------------ formatting

CI_TEXT = {
    "SUCCESS": "CI passing",
    "FAILURE": "CI failing",
    "ERROR": "CI failing",
    "PENDING": "CI running",
    "EXPECTED": "CI running",
    None: "no CI",
}


def merge_text(pr):
    if pr["mergeable"] == "CONFLICTING":
        return "conflicts with base"
    return {
        "CLEAN": "ready to merge",
        "BLOCKED": "blocked (reviews/checks required)",
        "BEHIND": "behind base branch",
        "UNSTABLE": "mergeable, checks unstable",
        "HAS_HOOKS": "ready to merge",
        "DRAFT": "draft",
    }.get(pr["merge_state"], "merge status pending")


def format_summary(prs, fmt="md", scope="all"):
    """Render PRs for the clipboard. fmt: md | slack | text. scope: all | review."""
    grouped = group(prs)
    lines = []
    for key, title in SECTIONS:
        if scope == "review" and key != "review":
            continue
        items = grouped[key]
        if not items:
            continue
        if fmt == "md":
            lines.append("**%s (%d)**" % (title, len(items)))
        elif fmt == "slack":
            lines.append("*%s (%d)*" % (title, len(items)))
        else:
            lines.append("%s (%d)" % (title, len(items)))
        for pr in items:
            meta = "%s, +%d/-%d, %s" % (
                pr["repo"], pr["additions"], pr["deletions"], CI_TEXT.get(pr["ci"], "no CI")
            )
            label = "#%d %s" % (pr["number"], pr["title"])
            if fmt == "md":
                lines.append("- [%s](%s) (%s)" % (label, pr["url"], meta))
            elif fmt == "slack":
                lines.append("• <%s|%s> (%s)" % (pr["url"], label.replace("|", "/"), meta))
            else:
                lines.append("- %s (%s) %s" % (label, meta, pr["url"]))
        lines.append("")
    return "\n".join(lines).strip() or "No open pull requests."
